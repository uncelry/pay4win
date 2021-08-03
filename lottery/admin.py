from django.contrib import admin
from lottery.models import FAQ, SteamUser, AbstractLottery, Genre, LotteryGame


admin.site.register(SteamUser)
admin.site.register(FAQ)
admin.site.register(Genre)
admin.site.register(AbstractLottery)
admin.site.register(LotteryGame)
