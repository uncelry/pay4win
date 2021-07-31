from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from allauth.socialaccount.models import SocialAccount
from django.utils.timezone import now


# Жанр
class Genre(models.Model):
    """
    Модель, отвечающая за жанр игр (Например: Экшн, Шутер, Хоррор и т.п.)
    """

    name = models.CharField(max_length=200, help_text='Введите название жанра (Например: Экшн, Шутер, Хоррор и т.п.)')

    def __str__(self):
        return self.name


# Вопрос-ответ
class FAQ(models.Model):
    """
    Модель, отвечающая за Частые Вопросы и Ответы на них
    """

    question = models.CharField(max_length=200, help_text='Введите частый вопрос')
    answer = models.TextField(max_length=3000, help_text='Введите краткий и понятный ответ на вопрос')

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'


# Пользователь
class SteamUser(models.Model):
    """
    Модель, отвечающая за Пользователя (в структурированом виде)
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
                                                related_name="users_finished_lottery")
    lotteries_ongoing = models.ManyToManyField('LotteryGame', verbose_name="Игры, в которых участвует пользователь",
                                               related_name="users_ongoing_lottery")
    money_current = models.IntegerField(default=0, verbose_name="Текущий баланс")

    # def __str__(self):
    #     return '{0}, {1}, {2}'.format(self.persona_name, self.user, self.steam_id)

    # def get_absolute_url(self):
    #     return reverse('user_detail', args=[str(self.pk)])


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
    lottery_game = models.CharField(max_length=300, verbose_name="Ссылка на игру")
    game_price = models.IntegerField(verbose_name="Цена игры Steam в рублях")
    tickets_amount = models.IntegerField(verbose_name="Кол-во билетов в розыгрыше")
    commission_num = models.IntegerField(verbose_name="Комиссия с розыгрыша в рублях")
    lotteries_amount = models.IntegerField(verbose_name="Кол-во розыгрышей такого вида")
    lottery_active = models.BooleanField(default=True, verbose_name="Активен ли такой вид розыгрышей?",
                                         help_text="Если хотите выключить такие розыгрыши, снимите галочку, вместо"
                                                   "удаления записи")
    lottery_genres = models.ManyToManyField(Genre, verbose_name="Жанры игры из стим")


# Розыгрыш (фактический - в котором могут участвовать люди)
class LotteryGame(models.Model):
    """
    Модель, отвечающая за фактический розыгрыш, в котором могут участваовать люди
    """

    LOTTERY_TYPE_LIST = (
        ('g', 'Золото'),
        ('s', 'Серебро'),
        ('b', 'Бронза'),
    )
    LOTTERY_STATE_LIST = (
        ('o', 'Идет'),
        ('p', 'Выбор победителя'),
        ('c', 'Окончена'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Уникальный ID этого розыгрыша', verbose_name="UUID розыгрыша")
    lottery_type = models.CharField(max_length=1, choices=LOTTERY_TYPE_LIST, default='g', help_text='Тип розыгрыша:\n'
                                                                                               'Золото - 5 билетов\n'
                                                                                               'Серебро - 10 билетов\n'
                                                                                               'Бронза - 20 билетов',
                                    verbose_name='Тип розыгрыша')
    lottery_game = models.CharField(max_length=300, verbose_name="Ссылка на игру")
    lottery_game_img = models.CharField(max_length=500, verbose_name="Ссылка на картинку игры steam")
    time_started = models.DateTimeField(default=now, verbose_name="Дата и время старта розыгрыша")
    time_finished = models.DateTimeField(null=True, blank=True, verbose_name="Дата и время окончания розыгрыша")
    tickets_amount = models.IntegerField(verbose_name="Кол-во билетов в розыгрыше")
    ticket_price = models.IntegerField(verbose_name="Цена билета в розыгрыше")
    game_price = models.IntegerField(verbose_name="Цена игры Steam в рублях")
    commission_num = models.IntegerField(verbose_name="Комиссия с розыгрыша в рублях")
    players_amount = models.IntegerField(default=0, verbose_name="Кол-во текущих игроков")
    players = models.ManyToManyField(SteamUser, blank=True, verbose_name="Кол-во текущих игроков")
    lottery_genres = models.ManyToManyField(Genre, verbose_name="Жанры игры из стим")
    abstract_lottery = models.ForeignKey(AbstractLottery, on_delete=models.SET_NULL, null=True,
                                         verbose_name='Родительский розыгрыш')
    lottery_state = models.CharField(max_length=1, choices=LOTTERY_STATE_LIST, default='o',
                                     verbose_name='Текущее состояние лотереи',
                                     help_text='Идет/Выбор победителя/Окончена')
    tickets_bought = models.IntegerField(default=0, verbose_name="Куплено билетов")
    tickets_left = models.IntegerField(verbose_name="Билетов осталось")


# Билет (привязан к игроку и розыгрышу)
class Ticket(models.Model):
    """
    Модель, отвечающая за билет
    """

    owner = models.ForeignKey(SteamUser, on_delete=models.SET_NULL, null=True, verbose_name='Владелец билета')
    lottery = models.ForeignKey(LotteryGame, on_delete=models.CASCADE, null=True,
                                verbose_name='Розыгрыш, которому принадлежит билет')
