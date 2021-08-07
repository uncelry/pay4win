from django.shortcuts import render
from django.urls import reverse
from allauth.socialaccount.providers.openid.views import OpenIDCallbackView, OpenIDLoginView
from allauth.socialaccount.providers.steam.provider import SteamOpenIDProvider
from django.views import View
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, request
from django.views import generic
from .models import FAQ, LotteryGame, Genre, SteamUser


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


# Search view
def search(request):

    context = dict()

    context['genre_list'] = Genre.objects.all()

    if LotteryGame.objects.count() > 0:
        context['min_ticket_price'] = LotteryGame.objects.filter(lottery_state='o').order_by('ticket_price')[0].ticket_price
        context['max_ticket_price'] = LotteryGame.objects.filter(lottery_state='o').order_by('-ticket_price')[0].ticket_price
    else:
        context['min_ticket_price'] = 0
        context['max_ticket_price'] = 0

    lotterygame_list = list()

    if request.GET:
        # Если GET не пустой (с фильтром)

        lotterygame_list = LotteryGame.objects.filter(lottery_state='o')


        # Фильтр по названию игры
        if 'search_game_name' in request.GET:
            if request.GET['search_game_name']:
                lotterygame_list = lotterygame_list.filter(lottery_state='o').filter(lottery_game_name__contains=request.GET['search_game_name'])




        # Фильтр по жанру
        if 'search_genre' in request.GET:
            if request.GET['search_genre']:
                filtred_genre = Genre.objects.filter(pk=request.GET['search_genre'])[0]
                lotterygame_list = lotterygame_list.filter(lottery_genres=filtred_genre)

                context['current_genre'] = filtred_genre


        # Фильтр по типу
        if 'search_type' in request.GET:
            if request.GET['search_type']:

                game_type = None
                if request.GET['search_type'] == 'Gold':
                    game_type = 'g'
                elif request.GET['search_type'] == 'Silver':
                    game_type = 's'
                else:
                    game_type = 'b'

                lotterygame_list = lotterygame_list.filter(lottery_type=game_type)

                context['current_type'] = game_type


        # Фильтр по скрытию пустых
        if 'search_hide_empty' in request.GET:
            lotterygame_list = lotterygame_list.filter(tickets_bought__gt=0)


        # Фильтр по цене
        if 'rangePrimary' in request.GET:
            if request.GET['rangePrimary']:
                min_max_price_range = request.GET['rangePrimary'].split(';')

                lotterygame_list = lotterygame_list.filter(ticket_price__gte=min_max_price_range[0])
                lotterygame_list = lotterygame_list.filter(ticket_price__lte=min_max_price_range[1])

                context['price_range_min'] = min_max_price_range[0]
                context['price_range_max'] = min_max_price_range[1]


        # Сортировка
        context['current_sort'] = 'new-to-old'
        if 'search_sort_by' in request.GET:
            if request.GET['search_sort_by']:

                sort_type = request.GET['search_sort_by']

                if sort_type == 'new-to-old':
                    lotterygame_list = lotterygame_list.order_by('-time_started')
                    context['current_sort'] = 'new-to-old'
                elif sort_type == 'old-to-new':
                    lotterygame_list = lotterygame_list.order_by('time_started')
                    context['current_sort'] = 'old-to-new'
                elif sort_type == 'exp-to-cheap':
                    lotterygame_list = lotterygame_list.order_by('-ticket_price')
                    context['current_sort'] = 'exp-to-cheap'
                elif sort_type == 'cheap-to-exp':
                    lotterygame_list = lotterygame_list.order_by('ticket_price')
                    context['current_sort'] = 'cheap-to-exp'
                elif sort_type == 'empty-to-full':
                    lotterygame_list = lotterygame_list.order_by('lottery_progress')
                    context['current_sort'] = 'empty-to-full'
                elif sort_type == 'full-to-empty':
                    lotterygame_list = lotterygame_list.order_by('-lottery_progress')
                    context['current_sort'] = 'full-to-empty'

            else:
                lotterygame_list = lotterygame_list.order_by('-time_started')
        else:
            lotterygame_list = lotterygame_list.order_by('-time_started')


        context['lotterygame_list'] = lotterygame_list


    else:
        # Если GET пустой (без фильтра)
        context['lotterygame_list'] = LotteryGame.objects.order_by('-time_started')

    context['check_for_games'] = LotteryGame.objects.count()

    return render(request, 'lottery/search.html', context=context)


class UserDetailView(generic.DetailView):
    model = SteamUser

    template_name = 'lottery/user.html'
