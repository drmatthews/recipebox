from __future__ import absolute_import

from django.conf.urls import url
from django.contrib.auth.views import login, logout

from . import views

urlpatterns = [
    url(r'^$', views.wine_list, name='wines'),
    url(r'^new-note/$', views.wine_create, name='new_wine'),
    url(r'^edit-note/(?P<wine_id>[0-9]+)/$', views.wine_update, name='edit_wine'),
    url(r'^delete-note/(?P<wine_id>[0-9]+)/$', views.wine_delete, name='delete_wine'),
    url(r'^delete-note/$', views.wine_delete_ajax, name='delete_wine_ajax'),    
    url(r'^(?P<wine_id>[0-9]+)/$', views.wine_show, name='show_wine'), 
    url(r'^search/$', views.wine_search, name='wine_search'),        
]

