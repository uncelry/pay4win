from django.shortcuts import render
from django.urls import reverse
from allauth.socialaccount.providers.openid.views import OpenIDCallbackView, OpenIDLoginView
from allauth.socialaccount.providers.steam.provider import SteamOpenIDProvider
from django.views import View
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.views import generic
from .models import FAQ


STEAM_OPENID_URL = "https://steamcommunity.com/openid"


# Login view
class SteamOpenIDLoginView(OpenIDLoginView):
    provider = SteamOpenIDProvider

    def get_form(self):

        items = dict(list(self.request.GET.items()) + list(self.request.POST.items()))
        items["openid"] = STEAM_OPENID_URL
        return self.form_class(items)

    def get_callback_url(self):
        return reverse(steam_callback)


class SteamOpenIDCallbackView(OpenIDCallbackView):
    provider = SteamOpenIDProvider


steam_login = SteamOpenIDLoginView.as_view()
steam_callback = SteamOpenIDCallbackView.as_view()


# Logout view
def steam_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


# FAQ view
class FAQListView(generic.ListView):
    model = FAQ
