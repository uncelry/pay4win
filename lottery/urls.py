from . import views
from django.conf.urls import url
from django.urls import path


urlpatterns = [

    #url(r'^$', views.index, name='index'),
    url(r'^faq/$', views.FAQListView.as_view(), name='faq'),
    url(r'^contacts/$', views.contacts, name='contacts'),
    url(r'^manual/$', views.manual, name='manual'),
    url(r'^types/$', views.types, name='types'),
    url(r'^search/$', views.search, name='search'),
    url(r'^user/(?P<pk>\d+)/$', views.UserDetailView.as_view(), name='user'),
    path('game/<pk>/', views.LotteryDetailView.as_view(), name='game'),

    url(r'^login/$', views.steam_login, name='steam_login'),
    url(r'^logout/$', views.steam_logout, name='steam_logout'),
    url(r'^login/steam/auth/login/callback/$', views.steam_callback, name='steam_callback'),
]
