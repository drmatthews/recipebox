from __future__ import absolute_import

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from django.contrib import auth,messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.forms.models import model_to_dict
from django.db.models import Q

from .models import WineNote
from .forms import WineNoteForm

import operator
import urllib2
from bs4 import BeautifulSoup

############################################
##      CRUD
############################################

############################################
##      wines
############################################
@login_required(login_url='/accounts/login/')
def wine_list(request, template_name='wines/winenotes.html'):
    wines = WineNote.objects.all()    
    context = {'wine_list': wines}
    return render(request, template_name, context)

@login_required(login_url='/accounts/login/')
def wine_show(request, wine_id, template_name='wines/show_wine.html'):
    wine = get_object_or_404(WineNote, pk=wine_id)  
    return render(request, template_name, {'wine':wine })

@login_required(login_url='/accounts/login/')
def wine_create(request, template_name='wines/wine_form.html'):

    wine = WineNote()

    if request.POST:
        wine_form = WineNoteForm(request.POST, instance=wine)
        if wine_form.is_valid():           
            wine.wine_picture_url = wine_form.cleaned_data['wine_picture_url']
            wine.save()
            return redirect('wines')
    else:
        wine_form = WineNoteForm()
        return render(request, template_name, {'wine_form':wine_form })

@login_required(login_url='/accounts/login/')
def wine_update(request, wine_id, template_name='wines/wine_form.html'):
    wine = get_object_or_404(Recipe, pk=wine_id)
    wine_form = WineNoteForm(request.POST or None, instance=wine)

    if wine_form.is_valid():
        wine_form.save()
        return redirect('wines')
    return render(request, template_name, {'wine_form':wine_form})

@login_required(login_url='/accounts/login/')
def wine_delete(request, wine_id, template_name='wines/wine_confirm_delete.html'):
    wine = get_object_or_404(WineNote, pk=wine_id)   
    if request.method=='POST':
        wine.delete()
        return redirect('wines')
    return render(request, template_name, {'wine':wine}) 

@login_required(login_url='/accounts/login/')
def wine_delete_ajax(request):
    if request.is_ajax():
        wine_id = request.POST['id']
        wine = get_object_or_404(WineNote, pk=wine_id)   
        wine.delete()
        return redirect('wines')   

def wine_search(request):

    result = WineNote.objects.all()
    query = request.GET.get('q')
    if query:
        query_list = query.split()
        result = result.filter(
            reduce(operator.and_,
                   (Q(title__icontains=q) for q in query_list)) |
            reduce(operator.and_,
                   (Q(description__icontains=q) for q in query_list))
        )
        ids = ['wine_'+str(r.id) for r in result]
    else:
        ids = []
        
    data = {'id_list': ids}        
    return JsonResponse(data)        


