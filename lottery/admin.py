from django.contrib import admin
from lottery.models import FAQ, SteamUser, AbstractLottery, Genre, LotteryGame, Ticket, Game, GameSliderPicture, GameSliderVideo, EventLottery


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'pk')
    search_fields = ['name']


class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'pk')
    search_fields = ['question']


class SteamUserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'persona_name', 'time_last_logged_in', 'money_saved', 'lotteries_total_amount')
    search_fields = ['persona_name']
    list_filter = ('time_last_logged_in', 'profile_is_private')


class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'pk')
    search_fields = ['name']


class GameSliderPictureAdmin(admin.ModelAdmin):
    list_display = ('game', 'pk')
    search_fields = ['game']
    list_filter = ('game', )


class GameSliderVideoAdmin(admin.ModelAdmin):
    list_display = ('game', 'pk')
    search_fields = ['game']
    list_filter = ('game', )


class AbstractLotteryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'game', 'lottery_type', 'commission_num', 'lottery_active')
    list_filter = ('lottery_type', 'game', 'lottery_active')


class LotteryGameAdmin(admin.ModelAdmin):
    list_display = ('abstract_lottery', 'pk', 'time_started', 'lottery_progress', 'lottery_state')
    search_fields = ['pk']
    list_filter = ('lottery_state', 'time_started', 'time_finished')


class TicketAdmin(admin.ModelAdmin):
    list_display = ('owner', 'lottery')


class EventLotteryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'target_lottery', 'target_user', 'event_time')
    list_filter = ('event_time', )
    search_fields = ['pk']


admin.site.register(Genre, GenreAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(SteamUser, SteamUserAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(GameSliderPicture, GameSliderPictureAdmin)
admin.site.register(GameSliderVideo, GameSliderVideoAdmin)
admin.site.register(AbstractLottery, AbstractLotteryAdmin)
admin.site.register(LotteryGame, LotteryGameAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(EventLottery, EventLotteryAdmin)
