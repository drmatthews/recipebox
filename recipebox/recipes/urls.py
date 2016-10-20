from __future__ import absolute_import

from django.conf.urls import url
from django.contrib.auth.views import login, logout

from . import views

urlpatterns = [
#    url(r'^$', views.index, name='recipes'),
    url(r'^$', views.recipe_list, name='recipes'),
    # url(r'^$', views.RecipeList.as_view(), name='recipes'),
    url(r'^login/$',  views.custom_login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^registration', views.register, name='registration'),
    #url(r'^new/$', views.recipe_form, name='new_recipe'),
    url(r'^new/$', views.recipe_create, name='new_recipe'),
    url(r'^import/$', views.import_from_url, name='import_recipe'),
    url(r'^importfile/$', views.import_from_file, name='import_recipe_file'),
    url(r'^define/$', views.define_external, name='define_external'),
    url(r'^external/(?P<external_id>[0-9]+)/$', views.show_external, name='show_external'),    
    #url(r'^edit/(?P<recipe_id>[0-9]+)/$', views.recipe_form, name='edit_recipe'),
    url(r'^edit/(?P<recipe_id>[0-9]+)/$', views.recipe_update, name='edit_recipe'),
    url(r'^delete/(?P<recipe_id>[0-9]+)/$', views.recipe_delete, name='delete_recipe'),
    url(r'^delete/$', views.recipe_delete_ajax, name='delete_recipe_ajax'),    
    url(r'^(?P<recipe_id>[0-9]+)/$', views.recipe_show, name='show_recipe'),
    # url(r'^search/$', views.RecipeSearchListView.as_view(), name='recipe_search'), 
    url(r'^search/$', views.recipe_search, name='recipe_search'),           
    url(r'^inspiration/$', views.recipe_inspiration, name='inspiration'),       
    url(r'^food2fork/$', views.get_from_food2fork, name='get_from_food2fork'),
    url(r'^importfood2fork/$', views.import_from_food2fork, name='import_from_food2fork'),
]

