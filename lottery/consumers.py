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

    # Текущая лотерея
    current_lottery = None

    # Метод при подключении нового сокета
    async def connect(self):
        # Берем id текущей лотереи
        self.lottery_id = self.scope['url_route']['kwargs']['game_pk']
        # Создаем id группы из id лотереи
        self.lottery_group_id = 'chat_%s' % self.lottery_id

        # Если пользователь авторизован, то получаем его объект
        if self.scope["user"].is_authenticated:
            self.steam_user = await get_steamuser_from_user(self.scope["user"])

        # Получаем объект текущей лотереи
        self.current_lottery = await get_lottery_by_pk(self.lottery_id)

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
        # Собираем полученный от клиента json в объект
        text_data_json = json.loads(text_data)

        # Создаем объект форму, и загружаем туда данные от клиента
        form = BuyTicketForm(text_data_json)

        # Проверяем правильность заполнения формы
        if form.is_valid():
            if (0 < form.cleaned_data['amount'] <= self.current_lottery.tickets_left) and ((form.cleaned_data['amount'] * self.current_lottery.ticket_price) <= self.steam_user.money_current) and self.current_lottery.lottery_state == 'o':
                res = await call_lottery_buy_tickets_method(self.current_lottery, self.steam_user, form.cleaned_data['amount'])
                if res:
                    result_code = 'res_success'
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

        # Генерируем сообщение в ответ клиенту
        message = json.dumps({
            'result_code': result_code,
            'is_lottery_finished': lottery_finished,
            'tickets_left': self.current_lottery.tickets_left,
            'total_bought_for_user': await call_lottery_calculate_ticks_for_user_mehtod(self.current_lottery, self.steam_user),
            'is_user_in_lottery': self.current_lottery.check_if_user_is_in_lottery(self.steam_user),  # ПОПРАВИТЬ=================================
            'steam_user_new_balance': self.steam_user.money_current,
            'user_win_chance': self.current_lottery.calculate_win_chance_for_user(self.steam_user)  # ПОПРАВИТЬ===================================
        })

        # Посылаем сообщение в группу розыгрыша
        await self.channel_layer.group_send(
            self.lottery_group_id,
            {
                'type': 'lottery_response',
                'message': message
            }
        )

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
def call_lottery_calculate_ticks_for_user_mehtod(lottery, steam_usr):
    return lottery.calculate_ticks_for_user(steam_usr)
