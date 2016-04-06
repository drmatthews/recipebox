from __future__ import absolute_import

from django.conf.urls import url
from django.contrib.auth.views import login, logout

from . import views

urlpatterns = [

    url(r'^$', views.dashboard, name='dashboard'),  
]

