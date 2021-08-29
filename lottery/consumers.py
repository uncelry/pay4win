import json
import channels.layers
from channels.generic.websocket import AsyncWebsocketConsumer
from .forms import BuyTicketForm
from .models import SteamUser, LotteryGame
from asgiref.sync import sync_to_async, async_to_sync
from random import shuffle
from django.db.models import signals
from django.dispatch import receiver


class LotteryGameConsumer(AsyncWebsocketConsumer):
    """
    Обработка асинхронного сокета на странице игры
    """

    # ID лотереи
    lottery_id = None

    # ID группы (сокеты в одном розыгрыше)
    lottery_group_id = None

    # Текущий пользователь
    steam_user = None

    # ID пользователя
    steam_user_id = None

    # Текущая лотерея
    current_lottery = None

    # Ссылка на страницу пользователя
    user_page_url = None

    # Метод при подключении нового сокета
    async def connect(self):
        # Берем id текущей лотереи
        self.lottery_id = self.scope['url_route']['kwargs']['game_pk']
        # Создаем id группы из id лотереи
        self.lottery_group_id = 'chat_%s' % self.lottery_id

        # Если пользователь авторизован, то получаем его объект и ссылку на страницу
        if self.scope["user"].is_authenticated:
            self.steam_user = await get_steamuser_from_user(self.scope["user"])
            self.steam_user_id = self.steam_user.pk
            self.user_page_url = await call_user_get_absolute_url_method(self.steam_user)

        # Подключение к группе
        await self.channel_layer.group_add(
            self.lottery_group_id,
            self.channel_name
        )

        await self.accept()

    # Метод при отключении сокета
    async def disconnect(self, close_code):
        # Отключение от группы
        await self.channel_layer.group_discard(
            self.lottery_group_id,
            self.channel_name
        )

    # Метод при получении сообщения по сокетам
    async def receive(self, text_data):

        # Если пользователь авторизован, то получаем его объект и ссылку на страницу
        if self.scope["user"].is_authenticated:
            self.steam_user = await get_steam_user_via_id(self.steam_user.pk)
            self.steam_user_id = self.steam_user.pk
            self.user_page_url = await call_user_get_absolute_url_method(self.steam_user)

        # Получаем объект текущей лотереи
        self.current_lottery = await get_lottery_by_pk(self.lottery_id)

        # Собираем полученный от клиента json в объект
        text_data_json = json.loads(text_data)

        # Создаем объект форму, и загружаем туда данные от клиента
        form = BuyTicketForm(text_data_json)

        event_win_chance = None

        # Проверяем правильность заполнения формы
        if form.is_valid():
            if (0 < form.cleaned_data['amount'] <= self.current_lottery.tickets_left) and ((form.cleaned_data['amount'] * self.current_lottery.ticket_price) <= self.steam_user.money_current) and self.current_lottery.lottery_state == 'o':
                res = await call_lottery_buy_tickets_method(self.current_lottery, self.steam_user, form.cleaned_data['amount'])
                if res:
                    result_code = 'res_success'
                    parent_lottery = await get_parent_lottery_for_lottery(self.current_lottery)
                    event_win_chance = round(round(form.cleaned_data['amount'] / parent_lottery.tickets_amount, 2) * 100)
                else:
                    result_code = 'res_error'

            elif (form.cleaned_data['amount'] * self.current_lottery.ticket_price) > self.steam_user.money_current:
                # Недостаточно средств на счету
                result_code = 'res_low_balance'

            elif self.current_lottery.lottery_state != 'o':
                # Розыгрыш уже закрыт
                result_code = 'res_lottery_closed'

            elif (form.cleaned_data['amount'] <= 0) or (form.cleaned_data['amount'] > self.current_lottery.tickets_left):
                # Введено неверное кол-во билетов для покупки
                result_code = 'res_wrong_number'

            else:
                # Произошла ошибка, попробуйте ещё раз
                result_code = 'res_error'

        else:
            # Неверно заполнена форма, попробуйте ещё раз
            result_code = 'res_bad_form'

        # Проверяем закончилась ли лотерея
        if self.current_lottery.tickets_left != 0:
            lottery_finished = False
        else:
            lottery_finished = True

        # Генерируем и отправляем личное сообщение клиенту
        # Если всё прошло успешно, посылаем всю информацию клиенту и обновляем данные розыгрыша для всех
        if result_code == 'res_success':

            total_bought_for_user = await call_lottery_calculate_ticks_for_user_method(self.current_lottery, self.steam_user)

            is_user_new_in_lottery = False

            if total_bought_for_user == form.cleaned_data['amount']:
                is_user_new_in_lottery = True

            winner_pick_array = None
            winner_steamuser_id = None

            # Если лотерея закончилась, то высылаем список карточек участников для загрузки в карусель выбора победителя
            if lottery_finished:

                winner_pick_array = list()
                lottery_participants = await get_participants_of_lottery(self.current_lottery)
                for i in range(len(lottery_participants)):

                    win_chance_for_user = await call_lottery_calculate_win_chance_for_user_method(self.current_lottery, lottery_participants[i])
                    steam_usr_url = await call_user_get_absolute_url_method(lottery_participants[i])

                    tmp_list = [{
                        'user_card_name': lottery_participants[i].persona_name,
                        'user_card_avatar': lottery_participants[i].avatar_full,
                        'user_card_link': steam_usr_url,
                        'user_card_chance': win_chance_for_user
                    } for one_chance in range(win_chance_for_user)]

                    winner_pick_array.extend(tmp_list)

                # Теперь перемешиваем случайным образом
                shuffle(winner_pick_array)

                # На 0-ю позицию ставим победителя
                winner_link = await get_lottery_winner(self.current_lottery)
                winner_steamuser_id = winner_link.pk
                winner_link = await call_user_get_absolute_url_method(winner_link)

                for i in range(len(winner_pick_array)):
                    if winner_pick_array[i]['user_card_link'] == winner_link:
                        # На 0-ю позицию ставим текущую карточку победителя
                        tmp = winner_pick_array[i]
                        winner_pick_array[i] = winner_pick_array[0]
                        winner_pick_array[0] = tmp
                        break

            await self.send(json.dumps({
                'message_type': 'private',
                'result_code': result_code,
                'total_bought_for_user': total_bought_for_user,
                'steam_user_new_balance': self.steam_user.money_current,
                'is_user_in_lottery': await call_lottery_check_if_user_is_in_lottery_method(self.current_lottery, self.steam_user),
                'user_win_chance': await call_lottery_calculate_win_chance_for_user_method(self.current_lottery, self.steam_user)
            }))

            # Генерируем сообщение в ответ клиенту
            message = json.dumps({
                'message_type': 'public',
                'is_lottery_finished': lottery_finished,
                'tickets_left': self.current_lottery.tickets_left,
                'is_user_in_lottery': await call_lottery_check_if_user_is_in_lottery_method(self.current_lottery, self.steam_user),
                'user_win_chance': await call_lottery_calculate_win_chance_for_user_method(self.current_lottery, self.steam_user),
                'lottery_progress': self.current_lottery.lottery_progress,
                'tickets_bought': self.current_lottery.tickets_bought,
                'user_page_url': self.user_page_url,
                'lottery_player_avatar_full': self.steam_user.avatar_full,
                'persona_name': self.steam_user.persona_name,
                'steam_user_id': self.steam_user.pk,
                'event_win_chance': event_win_chance,
                'tickets_bought_this_event': form.cleaned_data['amount'],
                'right_spelling': await get_right_spelling_for_event_ticks(form.cleaned_data['amount']),
                'is_user_new_in_lottery': is_user_new_in_lottery,
                'winner_pick_array': winner_pick_array,
                'winner_steamuser_id': winner_steamuser_id
            })

            # Посылаем сообщение в группу розыгрыша
            await self.channel_layer.group_send(
                self.lottery_group_id,
                {
                    'type': 'lottery_response',
                    'message': message
                }
            )

        # Если что-то пошло не так, то просто отправляем сообщение с кодом ошибки клиенту
        else:
            await self.send(json.dumps({
                'message_type': 'private',
                'result_code': result_code
            }))

    # Получение сообщения из группы розыгрыша
    async def lottery_response(self, event):
        # Берем созданное сообщение
        message = event['message']

        # Отправляем сообщение по сокет-соединению (как json)
        await self.send(text_data=message)


class IndexConsumer(AsyncWebsocketConsumer):
    """
    Обработка асинхронного сокета на главной странице
    """

    # Текущий пользователь
    steam_user = None

    # ID пользователя
    steam_user_id = None

    # Метод при подключении нового сокета
    async def connect(self):

        # Если пользователь авторизован, то получаем его объект и ID
        if self.scope["user"].is_authenticated:
            self.steam_user = await get_steamuser_from_user(self.scope["user"])
            self.steam_user_id = self.steam_user.pk

            # Подключение сокета к группе
            await self.channel_layer.group_add(
                'ws-index-room-auth',
                self.channel_name
            )
        else:
            # Подключение сокета к группе
            await self.channel_layer.group_add(
                'ws-index-room-no-auth',
                self.channel_name
            )

        await self.accept()

    # Метод при отключении сокета
    async def disconnect(self, close_code):
        # Отключение от группы
        if self.scope["user"].is_authenticated:
            await self.channel_layer.group_discard(
                'ws-index-room-auth',
                self.channel_name
            )
        else:
            await self.channel_layer.group_discard(
                'ws-index-room-no-auth',
                self.channel_name
            )

    # Метод при получении сообщения по сокетам
    async def receive(self, text_data):

        # Если пользователь авторизован, то получаем его объект
        if self.scope["user"].is_authenticated:
            self.steam_user = await get_steamuser_from_user(self.scope["user"])
            self.steam_user_id = self.steam_user.pk
        else:
            self.steam_user = None
            self.steam_user_id = None

        # Собираем полученный от клиента json в объект
        text_data_json = json.loads(text_data)

        closed_res = await get_last_three_closed_lotteries_filtered(text_data_json['closed_filter_type'])

        # По умолчанию ставим данные как пустые
        result_list = None

        # Если данные - не пустые, то обрабатываем их
        if closed_res:
            tmp_list = closed_res
            result_list = list()

            # Обрабатываем данные в цикле
            for i in range(len(tmp_list)):
                result_list.append(await get_dict_from_closed_lottery_for_index(tmp_list[i], self.steam_user))

        # Отправляем данные
        await self.send(json.dumps({
            'message_type': 'index_private',
            'closed_filter_res': result_list
        }))

    # Метод отправки сообщений в группу главной странице (авторизованным)
    async def events_logged(self, event):

        if not self.scope["user"].is_authenticated:
            return

        message = event['message']

        # Получаем лотерею по ID
        lottery = await get_lottery_by_pk(message['lottery_id'])

        # Удаляем лишнее значение
        del message['lottery_desc_200']

        # Проверяем участвует ли пользователь в лотерее
        steam_usr = await get_steamuser_from_user(self.scope["user"])
        is_participant = await call_lottery_check_if_user_is_in_lottery_method(lottery, steam_usr)
        message['is_participant'] = is_participant

        if is_participant:
            message['lottery_ticks_for_user'] = await call_lottery_calculate_ticks_for_user_method(lottery, steam_usr)
            message['lottery_win_chance_for_user'] = await call_lottery_calculate_win_chance_for_user_method(lottery, steam_usr)
        else:
            message['lottery_ticks_for_user'] = None
            message['lottery_win_chance_for_user'] = None

        # Указываем, авторизован ли данный пользователь
        message['is_authenticated'] = True
        message = json.dumps(message)

        await self.send(text_data=message)

    # Метод отправки сообщений в группу главной странице (неавторизованным)
    async def events_unlogged(self, event):

        if self.scope["user"].is_authenticated:
            return

        message = event['message']

        # Удаляем лишнее значение
        del message['lottery_desc_480']

        # Лотереи нет у пользователя в активных, выставляем это
        message['is_participant'] = False

        # Указываем, авторизован ли данный пользователь
        message['is_authenticated'] = False
        message = json.dumps(message)

        await self.send(text_data=message)

    # Метод, вызываемый сигналом создания любого фактического розыгрыша
    @staticmethod
    @receiver(signals.post_save, sender=LotteryGame)
    def lottery_game_post_save_signal(sender, instance, created, **kwargs):

        # Если розыгрыш находится в последних 3 актуальных активных, то обновляем его на главной
        if instance in LotteryGame.objects.all().filter(lottery_state='o').order_by('-time_started')[:3]:
            layer = channels.layers.get_channel_layer()

            # Жанры
            lottery_genres = list(instance.abstract_lottery.game.genres.all())
            genres_list = list()
            for i in range(len(lottery_genres)):
                genres_list.append(lottery_genres[i].name)

            # Формируем json объект о новом розыгрыше для отправки
            message = {
                'message_type': 'index_public',
                'lottery_type': instance.abstract_lottery.lottery_type,
                'game_img': instance.abstract_lottery.game.img.url,
                'game_name': instance.abstract_lottery.game.name,
                'game_genres': genres_list,
                'lottery_id': str(instance.id),
                'lottery_link': instance.get_absolute_url(),
                'lottery_progress': instance.lottery_progress,
                'lottery_tickets_bought': instance.tickets_bought,
                'lottery_tickets_total': instance.abstract_lottery.tickets_amount,
                'lottery_desc_480': instance.abstract_lottery.game.desc[:480],
                'lottery_desc_200': instance.abstract_lottery.game.desc[:200],
                'lottery_ticket_price': instance.ticket_price
            }

            async_to_sync(layer.group_send)('ws-index-room-auth', {
                'type': 'events.logged',
                'message': message
            })

            async_to_sync(layer.group_send)('ws-index-room-no-auth', {
                'type': 'events.unlogged',
                'message': message
            })


# Функция получения steamuser'а через обычного пользователя
@sync_to_async
def get_steamuser_from_user(basic_user):
    return basic_user.steamuser


# Функция получения текущей лотереи по её ID
@sync_to_async
def get_lottery_by_pk(lottery_pk):
    return LotteryGame.objects.get(pk=lottery_pk)


# Функция вызова синхронного метода покупки билетов
@sync_to_async
def call_lottery_buy_tickets_method(lottery, steam_usr, ticks_amount):
    return lottery.buy_tickets(steam_usr, ticks_amount)


# Функция вызова синхронного метода расчета купленных билетов
@sync_to_async
def call_lottery_calculate_ticks_for_user_method(lottery, steam_usr):
    return lottery.calculate_ticks_for_user(steam_usr)


# Функция вызова синхронного метода проверки находится ли в лотерее пользователь
@sync_to_async
def call_lottery_check_if_user_is_in_lottery_method(lottery, steam_usr):
    return lottery.check_if_user_is_in_lottery(steam_usr)


# Функция вызова синхронного метода получения шанса на победу конкретного пользователя
@sync_to_async
def call_lottery_calculate_win_chance_for_user_method(lottery, steam_usr):
    return lottery.calculate_win_chance_for_user(steam_usr)


# Функция вызова синхронного метода получения URL на страницу пользователя
@sync_to_async
def call_user_get_absolute_url_method(steam_usr):
    return steam_usr.get_absolute_url()


# Функция вызова синхронного метода получения родительского розыгрыша
@sync_to_async
def get_parent_lottery_for_lottery(lottery):
    return lottery.abstract_lottery


# Функция получения правильного написания
@sync_to_async
def get_right_spelling_for_event_ticks(amount_of_ticks):
    if 10 < amount_of_ticks < 20:
        return "Билетов"
    elif amount_of_ticks % 10 == 1:
        return "Билет"
    elif 2 <= (amount_of_ticks % 10) <= 4:
        return "Билета"
    else:
        return "Билетов"


# Функция получения steam user по его ID
@sync_to_async
def get_steam_user_via_id(usr_id):
    return SteamUser.objects.get(pk=usr_id)


# Функция получения списка участников розыгрыша
@sync_to_async
def get_participants_of_lottery(lottery):
    participants_query_set = lottery.players.all()
    res_list = list()
    for i in range(len(participants_query_set)):
        res_list.append(participants_query_set[i])
    return res_list


# Функция получения победителя лотереи
@sync_to_async
def get_lottery_winner(lottery):
    return lottery.lottery_winner


# Функция получения последних 3-ех закрытых розыгрышей по фильтру
@sync_to_async
def get_last_three_closed_lotteries_filtered(type_filter):
    if type_filter == 'all':
        return list(LotteryGame.objects.all().filter(lottery_state='c').order_by('-time_finished')[:3])
    elif type_filter == 'gold':
        return list(LotteryGame.objects.all().filter(lottery_state='c').filter(abstract_lottery__lottery_type='g').order_by('-time_finished')[:3])
    elif type_filter == 'silver':
        return list(LotteryGame.objects.all().filter(lottery_state='c').filter(abstract_lottery__lottery_type='s').order_by('-time_finished')[:3])
    elif type_filter == 'bronze':
        return list(LotteryGame.objects.all().filter(lottery_state='c').filter(abstract_lottery__lottery_type='b').order_by('-time_finished')[:3])
    else:
        return None


# Функция получения словаря из закрытого розыгрыша для отправки на главную страницу
@sync_to_async
def get_dict_from_closed_lottery_for_index(lottery, steam_usr):

    result = dict()

    if lottery.lottery_winner == steam_usr:
        result['is_winner'] = True
    else:
        result['is_winner'] = False

    result['lottery_amount_of_bought_tickets_for_user'] = None

    if steam_usr:
        result['is_authenticated'] = True

        if lottery in steam_usr.lotteries_finished.all():
            result['is_participant'] = True
            result['lottery_amount_of_bought_tickets_for_user'] = lottery.calculate_ticks_for_user(steam_usr)
        else:
            result['is_participant'] = False
    else:
        result['is_authenticated'] = False
        result['is_participant'] = False

    result['lottery_type'] = lottery.abstract_lottery.lottery_type
    result['game_img'] = lottery.abstract_lottery.game.img.url
    result['game_name'] = lottery.abstract_lottery.game.name

    # Жанры
    lottery_genres = list(lottery.abstract_lottery.game.genres.all())
    genres_list = list()
    for i in range(len(lottery_genres)):
        genres_list.append(lottery_genres[i].name)
    result['game_genres'] = genres_list

    result['lottery_id'] = str(lottery.id)
    result['lottery_winner_name'] = lottery.lottery_winner.persona_name

    # Участники
    lottery_participants = list(lottery.players.all())
    participants_list = list()
    for i in range(len(lottery_participants)):
        participants_list.append({
            "avatar": lottery_participants[i].avatar_full,
            "name": lottery_participants[i].persona_name,
            "link": lottery_participants[i].get_absolute_url(),
            "chance": lottery.calculate_win_chance_for_user(lottery_participants[i])
        })
    result["lottery_participants"] = participants_list

    result["game_desc"] = lottery.abstract_lottery.game.desc[:200] + "..."
    result['lottery_ticket_price'] = lottery.ticket_price

    return result
