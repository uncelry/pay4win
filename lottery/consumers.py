import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .forms import BuyTicketForm
from .models import SteamUser, LotteryGame
from asgiref.sync import sync_to_async


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
            self.steam_user = await get_steam_user_via_id(self.steam_user_id)
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
                'is_user_new_in_lottery': is_user_new_in_lottery
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
