from __future__ import absolute_import

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import auth,messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.forms.models import model_to_dict

from recipes.models import Recipe, Ingredient, MethodStep
from wines.models import WineNote
from recipes.forms import RecipeForm, IngredientFormSet, MethodStepFormSet,\
                          ImportForm
from wines.forms import WineNoteForm

import urllib2
from bs4 import BeautifulSoup
import cssutils

@login_required(login_url='/accounts/login/')
def dashboard(request, template_name='dash.html'):
    recipe_form = RecipeForm()
    ingredient_formset = IngredientFormSet(instance=Recipe())
    method_formset = MethodStepFormSet(instance=Recipe())    
    import_form = ImportForm()
    wine_form = WineNoteForm()
    context = {'recipe_form': recipe_form, 'ingredient_formset':ingredient_formset,\
                'method_formset': method_formset, 'import_form':import_form,\
                'wine_form': wine_form}
    return render(request, template_name, context)

