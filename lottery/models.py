import math

from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from allauth.socialaccount.models import SocialAccount
from django.utils.timezone import now
from bs4 import BeautifulSoup
import requests
import random


# Жанр
class Genre(models.Model):
    """
    Модель, отвечающая за жанр игр (Например: Экшн, Шутер, Хоррор и т.п.)
    """

    name = models.CharField(max_length=200, help_text='Введите название жанра (Например: Экшн, Шутер, Хоррор и т.п.)')

    def __str__(self):
        return '{0}'.format(self.name)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


# Вопрос-ответ
class FAQ(models.Model):
    """
    Модель, отвечающая за Частые Вопросы и Ответы на них
    """

    question = models.CharField(max_length=200, help_text='Введите частый вопрос')
    answer = models.TextField(max_length=3000, help_text='Введите краткий и понятный ответ на вопрос')

    def __str__(self):
        return '{0}, {1}'.format(self.question, self.pk)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'


# Пользователь
class SteamUser(models.Model):
    """
    Модель, отвечающая за Пользователя (в структурированном виде)
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name='Пользователь')
    steam_id = models.CharField(max_length=50, verbose_name="steam_id")
    community_visibility_state = models.CharField(max_length=10, verbose_name="Видимость профиля steam")
    profile_state = models.CharField(max_length=10, verbose_name="Имеется ли профиль сообщества steam")
    persona_name = models.CharField(max_length=200, verbose_name="Отображаемое имя пользователя steam")
    profile_url = models.CharField(max_length=200, verbose_name="Ссылка на профиль steam")
    avatar = models.CharField(max_length=400, verbose_name="Автар (маленький размер)")
    avatar_medium = models.CharField(max_length=400, verbose_name="Автар (средний размер)")
    avatar_full = models.CharField(max_length=400, verbose_name="Автар (полный размер)")
    avatar_hash = models.CharField(max_length=256, verbose_name="Хэш сумма аватара")
    last_logoff = models.CharField(max_length=256, verbose_name="Дата последнего онлайна (по юникс)")
    persona_state = models.CharField(max_length=10, verbose_name="Текущий статус пользователя")
    primary_clan_id = models.CharField(max_length=100, verbose_name="ID основного клана пользователя steam")
    time_created = models.CharField(max_length=256, verbose_name="Дата регистрации аккаунта steam (по юникс)")
    persona_state_flags = models.CharField(max_length=10, verbose_name="С чего пользователь онлайн и прочее")

    time_registered = models.DateTimeField(default=now, verbose_name="Дата и время регистрации на Pay4Win")
    time_last_logged_in = models.DateTimeField(null=True, verbose_name="Последняя дата и время входа на Pay4Win")
    lotteries_total_amount = models.IntegerField(default=0, verbose_name="Всего игр сыграно")
    lotteries_gold_amount = models.IntegerField(default=0, verbose_name="Золотых игр сыграно")
    lotteries_silver_amount = models.IntegerField(default=0, verbose_name="Серебряных игр сыграно")
    lotteries_bronze_amount = models.IntegerField(default=0, verbose_name="Бронзовых игр сыграно")
    money_saved = models.IntegerField(default=0, verbose_name="Всего сэкономлено денег (в рублях)")
    lotteries_won_amount = models.IntegerField(default=0, verbose_name="Всего игр выиграно")
    lotteries_lost_amount = models.IntegerField(default=0, verbose_name="Всего игр проиграно")
    lotteries_finished = models.ManyToManyField('LotteryGame', verbose_name="Игры, в которых участвовал пользователь",
                                                related_name="users_finished_lottery", blank=True)
    lotteries_ongoing = models.ManyToManyField('LotteryGame', verbose_name="Игры, в которых участвует пользователь",
                                               related_name="users_ongoing_lottery", blank=True)
    money_current = models.IntegerField(default=0, verbose_name="Текущий баланс")
    profile_is_private = models.BooleanField(default=False, verbose_name="Приватен ли профиль на сервисе?")

    def __str__(self):
        return '{0}) {1}'.format(self.pk, self.persona_name)

    def get_absolute_url(self):
        return reverse('user', args=[str(self.pk)])

    class Meta:
        verbose_name = 'Steam пользователь'
        verbose_name_plural = 'Steam пользователи'
        ordering = ['-pk']


# Функция обновления информации пользователя
def update_user_info(user_to_update, allauth_user_instance):
    user_to_update.steam_id = allauth_user_instance.extra_data['steamid']
    user_to_update.community_visibility_state = allauth_user_instance.extra_data['communityvisibilitystate']
    user_to_update.profile_state = allauth_user_instance.extra_data['profilestate']
    user_to_update.persona_name = allauth_user_instance.extra_data['personaname']
    user_to_update.profile_url = allauth_user_instance.extra_data['profileurl']
    user_to_update.avatar = allauth_user_instance.extra_data['avatar']
    user_to_update.avatar_medium = allauth_user_instance.extra_data['avatarmedium']
    user_to_update.avatar_full = allauth_user_instance.extra_data['avatarfull']
    user_to_update.avatar_hash = allauth_user_instance.extra_data['avatarhash']
    user_to_update.last_logoff = allauth_user_instance.extra_data['lastlogoff']
    user_to_update.persona_state = allauth_user_instance.extra_data['personastate']
    user_to_update.primary_clan_id = allauth_user_instance.extra_data['primaryclanid']
    user_to_update.time_created = allauth_user_instance.extra_data['timecreated']
    user_to_update.persona_state_flags = allauth_user_instance.extra_data['personastateflags']

    user_to_update.time_last_logged_in = now()
    user_to_update.save()


@receiver(post_save, sender=SocialAccount)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        SteamUser.objects.create(user=instance.user)
        new_user = SteamUser.objects.get(user=instance.user)
        update_user_info(new_user, instance)
    else:
        updatable_user = SteamUser.objects.get(user=instance.user)
        update_user_info(updatable_user, instance)


# Игра из Steam и вся информация о ней
class Game(models.Model):
    """
    Модель, отвечающая за всю информацию об игре Steam
    """

    link = models.CharField(max_length=300, unique=True, verbose_name="Ссылка на игру")
    name = models.CharField(max_length=250, unique=True, verbose_name="Название игры steam")
    desc = models.TextField(max_length=550, verbose_name="Описание игры")
    img = models.ImageField(verbose_name="Картинка игры (230x320)")
    genres = models.ManyToManyField(Genre, verbose_name="Жанры игры из стим")
    price = models.IntegerField(verbose_name="Цена игры Steam в рублях")

    class Meta:
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'

    def __str__(self):
        return '{0}'.format(self.name)


# Фото для слайдера игр
class GameSliderPicture(models.Model):
    """
    Модель, отвечающая за фото из Steam для слайдера игр
    """

    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE, verbose_name='Игра, к которой относятся фото')
    pic_small = models.CharField(max_length=500, verbose_name="Ссылка на маленькую картинку игры")
    pic_medium = models.CharField(max_length=500, verbose_name="Ссылка на среднюю картинку игры")
    pic_large = models.CharField(max_length=500, verbose_name="Ссылка на большую картинку игры")

    class Meta:
        verbose_name = 'Картинка слайдера игр'
        verbose_name_plural = 'Картинки слайдера игр'

    def __str__(self):
        return '{0}'.format(self.game)


# Видео для слайдера игр
class GameSliderVideo(models.Model):
    """
    Модель, отвечающая за видео из Steam для слайдера игр
    """

    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE, verbose_name='Игра, к которой относится видео')
    preview = models.CharField(max_length=500, verbose_name="Ссылка на превью для видео игры")
    video = models.CharField(max_length=500, verbose_name="Ссылка на видео игры")

    class Meta:
        verbose_name = 'Видео слайдера игр'
        verbose_name_plural = 'Видео слайдера игр'

    def __str__(self):
        return '{0}'.format(self.game)


# Создание новой игры
@receiver(post_save, sender=Game)
def create_game(sender, instance, created, **kwargs):
    # Если мы именно создали новую игру (не просто сохранили)
    if created:
        resp = requests.get(instance.link)
        soup = BeautifulSoup(resp.text, 'lxml')

        # Сначала ищем ссылка на превью для видео
        img_list = soup.select("#highlight_strip .highlight_strip_movie img")
        video_posters_links_list = list(map(lambda x: x['src'], img_list))

        # Теперь ищем ссылки на сами видео
        video_list = soup.select("#highlight_player_area .highlight_movie")
        video_links_list = list(map(lambda x: x['data-webm-source'], video_list))

        # Создаем новые объекты - видео и прикрепляем их к этой игре
        for i in range(len(video_posters_links_list)):
            GameSliderVideo.objects.create(
                game=instance,
                preview=video_posters_links_list[i],
                video=video_links_list[i]
            )

        # Теперь ищем ссылки на миниатюры картинок
        img_list = soup.select("#highlight_strip .highlight_strip_screenshot img")
        img_mini_links_list = list(map(lambda x: x['src'], img_list))

        # Теперь получаем ссылки на средние картинки
        img_medium_links_list = list(map(lambda x: x.replace('116x65', '600x338'), img_mini_links_list))

        # Теперь получаем ссылки на большие картинки
        img_large_links_list = list(map(lambda x: x.replace('116x65', '1920x1080'), img_mini_links_list))

        for i in range(len(img_mini_links_list)):
            GameSliderPicture.objects.create(
                game=instance,
                pic_small=img_mini_links_list[i],
                pic_medium=img_medium_links_list[i],
                pic_large=img_large_links_list[i]
            )


# Абстрактный розыгрыш (интерфейсная модель)
class AbstractLottery(models.Model):
    """
    Модель, отвечающая за настройку активных розыгрышей на сайте (управление розыгрышами происходит через неё)
    """

    LOTTERY_TYPE_LIST = (
        ('g', 'Золото'),
        ('s', 'Серебро'),
        ('b', 'Бронза'),
    )

    lottery_type = models.CharField(max_length=1, choices=LOTTERY_TYPE_LIST, default='g', help_text='Тип розыгрыша:\n'
                                                                                               'Золото - 5 билетов\n'
                                                                                               'Серебро - 10 билетов\n'
                                                                                               'Бронза - 20 билетов',
                                    verbose_name='Тип розыгрыша')
    game = models.ForeignKey(Game, null=True, on_delete=models.PROTECT, default='', verbose_name='Разыгрываемая игра')
    tickets_amount = models.IntegerField(verbose_name="Кол-во билетов в розыгрыше")
    commission_num = models.IntegerField(verbose_name="Комиссия с розыгрыша в рублях")
    lotteries_amount = models.IntegerField(verbose_name="Кол-во розыгрышей такого вида")
    lottery_active = models.BooleanField(default=True, verbose_name="Активен ли такой вид розыгрышей?",
                                         help_text="Если хотите выключить такие розыгрыши, снимите галочку, вместо"
                                                   "удаления записи")

    class Meta:
        verbose_name = 'Розыгрыш'
        verbose_name_plural = 'Розыгрыши'

    def __str__(self):
        return '{0}'.format(self.game)


# Функция создания розыгрышей
def create_lottery_from_abstract(abstract):

    # Получаем цену билета:
    ticket_price = ((abstract.game.price + abstract.commission_num) / abstract.tickets_amount)
    ticket_price = math.ceil(ticket_price)

    # Создаем игру:
    LotteryGame.objects.create(
        time_started=now(),
        ticket_price=ticket_price,
        abstract_lottery=abstract,
        lottery_state='o',
        tickets_left=abstract.tickets_amount,
    )


@receiver(post_save, sender=AbstractLottery)
def save_abstract_lottery(sender, instance, **kwargs):
    if instance.lottery_active:

        current_lotteries_amount = LotteryGame.objects.filter(abstract_lottery=instance).count()
        current_inactive_lotteries_amount = LotteryGame.objects.filter(lottery_state='c').count()

        if (current_lotteries_amount == 0) or (current_lotteries_amount == current_inactive_lotteries_amount):
            for i in range(instance.lotteries_amount):
                create_lottery_from_abstract(instance)


# Розыгрыш (фактический - в котором могут участвовать люди)
class LotteryGame(models.Model):
    """
    Модель, отвечающая за фактический розыгрыш, в котором могут участвовать люди
    """

    LOTTERY_STATE_LIST = (
        ('o', 'Идет'),
        ('c', 'Окончена'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Уникальный ID этого розыгрыша', verbose_name="UUID розыгрыша")
    ticket_price = models.IntegerField(verbose_name="Цена билета в розыгрыше")
    tickets_bought = models.IntegerField(default=0, verbose_name="Куплено билетов")
    tickets_left = models.IntegerField(verbose_name="Билетов осталось")
    lottery_progress = models.IntegerField(default=0, verbose_name="Процент купленных билетов")
    players = models.ManyToManyField(SteamUser, blank=True, verbose_name="Текущие игроки")
    players_amount = models.IntegerField(default=0, verbose_name="Кол-во текущих игроков")
    lottery_state = models.CharField(max_length=1, choices=LOTTERY_STATE_LIST, default='o',
                                     verbose_name='Текущее состояние лотереи',
                                     help_text='Идет/Окончена')
    lottery_winner = models.ForeignKey(SteamUser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Победитель',
                                       related_name='user_lottery_winner')

    abstract_lottery = models.ForeignKey(AbstractLottery, on_delete=models.PROTECT, null=True,
                                         verbose_name='Родительский розыгрыш')
    time_started = models.DateTimeField(default=now, verbose_name="Дата и время старта розыгрыша")
    time_finished = models.DateTimeField(null=True, blank=True, verbose_name="Дата и время окончания розыгрыша")

    def calculate_ticks_for_user(self, participant):
        return participant.ticket_set.filter(lottery=self).count()

    def calculate_win_chance_for_user(self, participant):
        return round(round(participant.ticket_set.filter(lottery=self).count() / self.abstract_lottery.tickets_amount, 2) * 100)

    def check_if_user_is_in_lottery(self, steam_user):
        if steam_user.ticket_set.filter(lottery=self).count() > 0:
            return True
        return False

    def buy_tickets(self, steam_user, ticket_amount):
        # Проверяем достаточно ли у пользователя средств / билетов в розыгрыше / открыт ли розыгрыш
        if (steam_user.money_current < ticket_amount * self.ticket_price) or (self.tickets_left < ticket_amount) or (self.lottery_state != 'o'):
            return False

        # Если всё хорошо, то начинаем обновлять данные. Если пользователь новый
        if not self.check_if_user_is_in_lottery(steam_user):
            self.players.add(steam_user)
            self.players_amount += 1

        # Создаем билеты
        for i in range(ticket_amount):
            Ticket.objects.create(
                owner=steam_user,
                lottery=self
            )

        # Уменьшаем деньги пользователя
        steam_user.money_current -= ticket_amount * self.ticket_price

        # Добавляем розыгрыш к пользователю в активные
        steam_user.lotteries_ongoing.add(self)

        # Обновляем информацию розыгрыша
        self.tickets_bought += ticket_amount
        self.tickets_left -= ticket_amount
        new_progress = math.floor((self.tickets_bought / (self.tickets_bought + self.tickets_left)) * 100)
        self.lottery_progress = new_progress

        # Создаем новое событие
        win_chance_for_event = round(round(ticket_amount / self.abstract_lottery.tickets_amount, 2) * 100)
        EventLottery.objects.create(
            target_user=steam_user,
            target_lottery=self,
            tickets_amount=ticket_amount,
            win_chance=win_chance_for_event
        )

        # Сохраняем всё
        steam_user.save()
        self.save()

        return True

    def finish_lottery(self):
        # Определяем победителя
        winner = self.pick_winner()

        # Обновляем статистику всех участников (и победителя в том числе)
        participants_list = self.players.all()

        for i in range(len(participants_list)):

            # Увеличиваем на 1 кол-во завершенных лотерей
            participants_list[i].lotteries_total_amount += 1

            # Увеличиваем на 1 кол-во завершенных лотерей по типу
            if self.abstract_lottery.lottery_type == 'g':
                participants_list[i].lotteries_gold_amount += 1
            elif self.abstract_lottery.lottery_type == 's':
                participants_list[i].lotteries_silver_amount += 1
            elif self.abstract_lottery.lottery_type == 'b':
                participants_list[i].lotteries_bronze_amount += 1

            # Добавляем лотерею в список завершенных у пользователей
            participants_list[i].lotteries_finished.add(self)

            # Убираем лотерею из списка текущих у пользователя
            participants_list[i].lotteries_ongoing.remove(self)

            # Если победитель
            if participants_list[i] == winner:
                money_spent = self.calculate_ticks_for_user(participants_list[i]) * self.ticket_price
                if money_spent <= self.abstract_lottery.game.price:
                    participants_list[i].money_saved += (self.abstract_lottery.game.price - money_spent)
                participants_list[i].lotteries_won_amount += 1
            # Если не победитель
            else:
                participants_list[i].lotteries_lost_amount += 1

            # Сохраняем изменения у пользователя
            participants_list[i].save()

        # Обновляем информацию лотереи (закрываем её)
        self.lottery_state = 'c'
        self.lottery_winner = winner
        self.time_finished = now()
        self.save()

        # И в самом конце решаем нужно ли создавать следующую(-ие) лотерею(-и)
        self.decide_generate_new_lotteries_or_not()

    def pick_winner(self):
        # Получаем список всех участников
        participants_list = self.players.all()

        # Создаем список
        participants_percentage = list()

        # Заполняем словарь (id_пользователя: список процентов)
        percent_cnt = 1
        for i in range(len(participants_list)):
            participants_percentage.append(list(range(percent_cnt, percent_cnt + self.calculate_win_chance_for_user(participants_list[i]))))
            percent_cnt = percent_cnt + self.calculate_win_chance_for_user(participants_list[i])

        # Генерируем случайное число от 1 до 100 (percent_cnt - 1)
        win_num = random.randint(1, percent_cnt - 1)

        # Узнаем какому участнику оно соответствует
        for i in range(len(participants_list)):
            if win_num in participants_percentage[i]:
                return participants_list[i]

    def decide_generate_new_lotteries_or_not(self):
        # Если у родительского розыгрыша стоит галочка, то проверяем дальше
        if self.abstract_lottery.lottery_active:

            # Если сейчас меньше активных дочерних розыгрышей, чем указано у родителя, то создаем разницу (по кол-ву)
            current_active_lotteries = self.abstract_lottery.lotterygame_set.filter(lottery_state='o').count()
            if current_active_lotteries < self.abstract_lottery.lotteries_amount:
                amount_to_create = self.abstract_lottery.lotteries_amount - current_active_lotteries
                for i in range(amount_to_create):
                    create_lottery_from_abstract(self.abstract_lottery)

    class Meta:
        verbose_name = 'Розыгрыш (фактический - не менять)'
        verbose_name_plural = 'Розыгрыши (фактические - не менять)'
        ordering = ['-pk']

    def __str__(self):
        return '{0}'.format(self.pk)

    def get_absolute_url(self):
        return reverse('game', args=[str(self.pk)])


@receiver(post_save, sender=LotteryGame)
def save_lottery_game(sender, instance, created, **kwargs):

    # Если в лотерее уже есть купленные билеты и она ещё не закончилась
    if not created and instance.tickets_bought != 0 and instance.lottery_state != 'c':
        if instance.tickets_left == 0:
            instance.finish_lottery()


# Билет (привязан к игроку и розыгрышу)
class Ticket(models.Model):
    """
    Модель, отвечающая за билет
    """

    owner = models.ForeignKey(SteamUser, on_delete=models.SET_NULL, null=True, verbose_name='Владелец билета')
    lottery = models.ForeignKey(LotteryGame, on_delete=models.CASCADE, null=True,
                                verbose_name='Розыгрыш, которому принадлежит билет')

    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'

    def __str__(self):
        return '{0}, {1}'.format(self.owner, self.lottery)


# Событие в розыгрыше (привязано к розыгрышу и игроку)
class EventLottery(models.Model):
    """
    Модель, отвечающая за событие в розыгрыше
    """

    target_user = models.ForeignKey(SteamUser, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь события')
    target_lottery = models.ForeignKey(LotteryGame, on_delete=models.CASCADE, null=True,
                                verbose_name='Розыгрыш события')
    tickets_amount = models.IntegerField(verbose_name="Кол-во билетов, купленных в событии")
    win_chance = models.IntegerField(verbose_name="Шанс выигрыша по билетам в событии")
    event_time = models.DateTimeField(default=now, verbose_name="Дата и время события")

    class Meta:
        verbose_name = 'Игровое событие'
        verbose_name_plural = 'Игровые события'
        ordering = ['-pk']

    def __str__(self):
        return '{0}: {1} - {2}'.format(self.pk, self.target_lottery, self.target_user)
