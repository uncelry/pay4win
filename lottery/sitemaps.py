from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from .models import SteamUser, LotteryGame


class StaticViewSitemap(Sitemap):

    changefreq = 'always'

    def items(self):
        return [
            'faq',
            'contacts',
            'manual',
            'types',
            'search',
        ]

    def location(self, item):
        return reverse(item)


class SteamUserSitemap(Sitemap):

    changefreq = 'always'

    def items(self):
        return SteamUser.objects.all()


class LotteryGameSitemap(Sitemap):

    changefreq = 'always'

    def items(self):
        return LotteryGame.objects.all()
