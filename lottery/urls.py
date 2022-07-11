from . import views
from django.urls import path, re_path


urlpatterns = [

    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(r'^faq/$', views.FAQListView.as_view(), name='faq'),
    re_path(r'^contacts/$', views.contacts, name='contacts'),
    re_path(r'^manual/$', views.manual, name='manual'),
    re_path(r'^types/$', views.types, name='types'),
    re_path(r'^search/$', views.search, name='search'),
    re_path(r'^user/(?P<pk>\d+)/$', views.UserDetailView.as_view(), name='user'),
    path('game/<pk>/', views.LotteryDetailView.as_view(), name='game'),

    re_path(r'^login/$', views.steam_login, name='steam_login'),
    re_path(r'^logout/$', views.steam_logout, name='steam_logout'),
    re_path(r'^login/steam/auth/login/callback/$', views.steam_callback, name='steam_callback'),
]
