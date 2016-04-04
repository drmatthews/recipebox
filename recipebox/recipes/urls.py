from django.conf.urls import url
from django.contrib.auth.views import login, logout

from . import views

urlpatterns = [
#    url(r'^$', views.index, name='recipes'),
    url(r'^$', views.recipe_list, name='recipes'),
    url(r'^wines/$', views.wine_list, name='wines'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^login/$',  views.custom_login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^registration', views.register, name='registration'),
    #url(r'^new/$', views.recipe_form, name='new_recipe'),
    url(r'^new/$', views.recipe_create, name='new_recipe'),
    url(r'^import/$', views.recipe_import, name='import_recipe'),
    #url(r'^edit/(?P<recipe_id>[0-9]+)/$', views.recipe_form, name='edit_recipe'),
    url(r'^edit/(?P<recipe_id>[0-9]+)/$', views.recipe_update, name='edit_recipe'),
    url(r'^delete/(?P<recipe_id>[0-9]+)/$', views.recipe_delete, name='delete_recipe'),
    url(r'^(?P<recipe_id>[0-9]+)/$', views.recipe_show, name='show_recipe'),

    url(r'^new-note/$', views.wine_create, name='new_wine'),
    url(r'^edit-note/(?P<wine_id>[0-9]+)/$', views.wine_update, name='edit_wine'),
    url(r'^delete-delete/(?P<wine_id>[0-9]+)/$', views.wine_delete, name='delete_wine'),
    url(r'^note/(?P<wine_id>[0-9]+)/$', views.wine_show, name='show_wine'),    
]

