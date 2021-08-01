from django.shortcuts import render
from django.urls import reverse
from allauth.socialaccount.providers.openid.views import OpenIDCallbackView, OpenIDLoginView
from allauth.socialaccount.providers.steam.provider import SteamOpenIDProvider
from django.views import View
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, request
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


# Contacts view
def contacts(request):

    contact_email = 'info@pay4win.com'

    main_text = """Если у вас появились какие-либо проблемы с получением выигрыша, либо с участием в розыгрышах, то напишите нам на почту - мы ответим в ближайшее время! По вопросам сотрудничества и/или рекламы просьба писать ответственному администратору нашего паблика ВКонтакте. Все ссылки и контакты указаны ниже. Заявки в техническую поддержку принимаются в любое время суток; рассматриватся - только в рабочее время (за исключением праздников и выходных дней).
    Большая просьба не писать в техническую поддержку и/или ответственному администратору нашего паблика ВКонтакте сразу несколько писем, не дождавшись ответа на предыдущее. Если у нас будет много спама, то на ответ уйдет гораздо больше времени. 
    Благодарим за понимание!"""

    context = {
        'main_text': main_text,
        'contact_email': contact_email,
    }

    return render(request, 'lottery/contacts.html', context=context)


# Manual view
def manual(request):

    return render(request, 'lottery/manual.html')


# Types view
def types(request):

    return render(request, 'lottery/types.html')
