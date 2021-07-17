from . import views
from django.conf.urls import url

urlpatterns = [

    #url(r'^$', views.index, name='index'),
    url(r'^faq/$', views.FAQListView.as_view(), name='faq'),

    url(r'^login/$', views.steam_login, name='steam_login'),
    url(r'^logout/$', views.steam_logout, name='steam_logout'),
    url(r'^login/steam/auth/login/callback/$', views.steam_callback, name='steam_callback'),
]
