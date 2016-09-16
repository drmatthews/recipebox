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

from django.conf import settings
from django.db.models import Q

from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Recipe, Ingredient, MethodStep, ExternalRecipe
from recipebox.wines.models import WineNote
from .forms import RecipeForm, IngredientFormSet, MethodStepFormSet,\
                  UserForm, UserProfileForm, ImportForm, ExternalRecipeForm

import os  
import operator            
import urlparse    
import urllib,urllib2
from bs4 import BeautifulSoup

### user login and logout

@login_required(login_url='/accounts/login/')
def logout(request):
    auth.logout(request)
    messages.add_message(request, messages.INFO, \
                         'Successfully logged out. Login again to create recipes')
    return HttpResponseRedirect(reverse('login'))

def custom_login(request):
    response = login(request,template_name='/accounts/login/')
    if request.user.is_authenticated():
         messages.info(request, "Welcome ...")
    return response

def register(request):

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True
            return HttpResponseRedirect(reverse('recipes'))

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
            'recipes/registration.html',
            {'user_form': user_form, 'profile_form': profile_form,\
             'registered': registered})

####################################################################

###  recipes

@login_required(login_url='/accounts/login/')
def recipe_list(request, template_name='recipes/recipes.html'):
    recipes = Recipe.objects.all()    
    print settings.INSTALLED_APPS
    context = {'recipe_list': recipes}
    return render(request, template_name, context)

@login_required(login_url='/accounts/login/')
def recipe_show(request, recipe_id, template_name='recipes/show_recipe.html'):
    recipe = get_object_or_404(Recipe, pk=recipe_id)  

    ingredients = []
    for i in recipe.ingredient_set.all():
        ingredients.append(i.ingredient_name)

    steps = []
    for s in recipe.methodstep_set.all():
        steps.append(s.step)

    return render(request, template_name, {'recipe':recipe,\
                                           'ingredients': ingredients,\
                                           'steps': steps })

@login_required(login_url='/accounts/login/')
def recipe_create(request, template_name='recipes/recipe_form.html'):
    recipe = Recipe()

    if request.POST:
        recipe_form = RecipeForm(data=request.POST or None, instance=recipe)
        if recipe_form.is_valid():
            ingredient_formset = IngredientFormSet(request.POST, instance=recipe)
            method_formset = MethodStepFormSet(request.POST, instance=recipe)           
            if ingredient_formset.is_valid() and method_formset.is_valid():
                recipe.chef = request.user.get_username()
                recipe.source = request.user.get_username()
                recipe.recipe_picture_url = recipe_form.cleaned_data['recipe_picture_url']
                if request.user.is_authenticated():
                    recipe.user = request.user
                recipe.save()
                ingredient_formset.save()
                method_formset.save()
                return redirect('recipes')
    else:       
        recipe_form = RecipeForm()
        ingredient_formset = IngredientFormSet(instance=Recipe())
        method_formset = MethodStepFormSet(instance=Recipe())
        return render(request, template_name, {'recipe_form':recipe_form, \
                                               'ingredient_formset': ingredient_formset,\
                                               'method_formset': method_formset})

@login_required(login_url='/accounts/login/')
def recipe_update(request, recipe_id, template_name='recipes/recipe_form.html'):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    recipe_form = RecipeForm(request.POST or None, instance=recipe)
    ingredient_formset = IngredientFormSet(request.POST or None, instance=recipe)
    method_formset = MethodStepFormSet(request.POST or None, instance=recipe)  

    if recipe_form.is_valid():         

        if ingredient_formset.is_valid() and method_formset.is_valid():
            recipe.chef = request.user.get_username()
            recipe.source = request.user.get_username()
            recipe.recipe_picture_url = recipe_form.cleaned_data['recipe_picture_url']
            recipe.save()
            ingredient_formset.save()
            method_formset.save()
            return redirect('recipes')
    return render(request, template_name, {'recipe_id': recipe_id, 'recipe_form':recipe_form, \
                                           'ingredient_formset': ingredient_formset,\
                                           'method_formset': method_formset})

@login_required(login_url='/accounts/login/')
def recipe_delete(request, recipe_id, template_name='recipes/recipe_confirm_delete.html'):
    recipe = get_object_or_404(Recipe, pk=recipe_id)   
    if request.method=='POST':
        recipe.delete()
        return redirect('recipes')
    return render(request, template_name, {'recipe':recipe})

@login_required(login_url='/accounts/login/')
def recipe_delete_ajax(request):
    if request.is_ajax():
        recipe_id = request.POST['id']
        recipe = get_object_or_404(Recipe, pk=recipe_id)   
        recipe.delete()
        return redirect('recipes')

##################################################
### import recipe from url

@login_required(login_url='/accounts/login/')
def recipe_import(request, template_name='recipes/recipe_import.html'):

    if request.POST:
        import_form = ImportForm(request.POST)
        if import_form.is_valid():
            url = import_form.cleaned_data['url']
            source = import_form.cleaned_data['source']
            recipe = process_url(url,source)
            if request.user.is_authenticated():
                recipe.user = request.user
            recipe.save()
            return redirect('recipes')
    else:
        import_form = ImportForm()
    return render(request, template_name, {'import_form':import_form})

@login_required(login_url='/accounts/login/')
def define_external(request, template_name='recipes/external_recipe.html'):

    if request.POST:
        external_form = ExternalRecipeForm(request.POST)
        if external_form.is_valid():
            external_form.save()
            return redirect('dashboard')
    else:
        external_form = ExternalRecipeForm()
    return render(request, template_name, {'external_form':external_form}) 

def process_url(url,site):
    source = site.source.lower()
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    if "bbc" in source:
        ingredients = get_ingredients_from_bbc(soup)
    elif "taste" in source:
        ingredients = get_ingredients_from_taste(soup)

    steps = get_method(soup, site)
    description = get_description(soup, site)
    chef = get_chef(soup, site)
    title = get_title(soup, site)
    
    recipe = create_recipe(source,title,chef,description,ingredients,steps)
    return recipe   

def create_recipe(source,title,chef,description,ingredients,steps):
    recipe = Recipe()
    recipe.title = title
    recipe.source = source
    recipe.chef = chef
    recipe.description = description
    recipe.save()
    for ingredient in ingredients:
        recipe.ingredient_set.create(ingredient_name=ingredient)    
    
    for step in steps:
        # if len(step) > 200:
        #     step_reduced = step[:200]
        # else:
        #     step_reduced = step

        recipe.methodstep_set.create(step=step) 
    return recipe  

###########################################################################
### ajax recipe filtering
def recipe_search(request):
    result = Recipe.objects.all()
    query = request.GET.get('q')
    if query:
        query_list = query.split()
        result = result.filter(
            reduce(operator.and_,
                   (Q(title__icontains=q) for q in query_list)) |
            reduce(operator.and_,
                   (Q(description__icontains=q) for q in query_list))
        )
        ids = ['recipe_'+str(r.id) for r in result]
    else:
        ids = []
        
    data = {'id_list': ids}        
    return JsonResponse(data)  

###########################################################################
### food2fork api searching
@login_required(login_url='/accounts/login/')
def recipe_inspiration(request,template_name='recipes/inspiration.html'):
    return render(request, template_name)


###########################################################################
### utility functions which work on external recipe model instance

### site specfic - need a way of generalising

def get_ingredients_from_taste(soup):
    section = soup.find('ul','ingredient-table').find_all('li')
    inner_list = []
    for li in section:
        inner_list.append(li.find('label').contents[0])
    return inner_list

def get_ingredients_from_bbc(soup): #this is the same as ingredients_from_taste except for label - no cb's
    try:
        sections = soup.find_all('ul','recipe-ingredients__list')
        inner_list = []
        for s,section in enumerate(sections):
            section_li = section.find_all('li')
            for li in section_li:
                li_contents = li.contents
                li_text = []
                for li_c in li_contents:
                    a_text = ""
                    if li_c.find('a') is None:
                        a_text = li_c.contents[0]
                    else:
                        li_text.append(li_c)
                    li_text.append(a_text)
                inner_list.append("".join(li_text))        
    except Exception, e:
        inner_list = ["could not find ingredients on page"]
    return inner_list

### generalised functions

def get_chef(soup, site):
    try:
        chef = soup.find('a',{'class':site.chef_class}).contents[0]
    except Exception, e:
        chef = "could not find chef on page"

    return chef    
  

def get_description(soup, site):
    try:
        description = get_text_from_div(soup,site.description_class,'p')
    except Exception, e:
        description = "could not find description on page" 

    return description  

def get_title(soup, site):
    try:
        title = get_text_from_div(soup,site.title_class,'h1')
    except Exception, e:
        title = "could not find title on page"   

    return title            

def get_method(soup, site):
    try:
        method = get_li_group(soup, site.method_class)
    except Exception, e:
        method = ["could not find method on page"]

    return method

### utilities
def get_text_from_div(soup, div_class, el_type):
    return soup.find('div',div_class).find(el_type).contents[0]

def get_li_group(soup, div_class):
    section = soup.find('div',div_class).find('ol').find_all('li')
    inner_list = []
    for li in section:
        inner_list.append(li.find('p').contents[0])
    return inner_list    
###############################################################



############################################
##      recipes - class based views
############################################

class RecipeList(LoginRequiredMixin,ListView):
    model = Recipe
    context_object_name = 'recipe_list'
    template_name = 'recipes/recipes.html'

class RecipeDetail(LoginRequiredMixin,DetailView):
    model = Recipe
    context_object_name = 'recipe'
    template_name = 'recipes/show_recipe.html'    

###############################################
## search
###############################################
# class JSONResponseMixin(object):
#     """
#     A mixin that can be used to render a JSON response.
#     """
#     def render_to_json_response(self, context, **response_kwargs):
#         """
#         Returns a JSON response, transforming 'context' to make the payload.
#         """
#         return JsonResponse(
#             self.get_data(context),
#             **response_kwargs
#         )

#     def get_data(self, context):
#         """
#         Returns an object that will be serialized as JSON by json.dumps().
#         """
#         # Note: This is *EXTREMELY* naive; in reality, you'll need
#         # to do much more complex handling to ensure that arbitrary
#         # objects -- such as Django model instances or querysets
#         # -- can be serialized as JSON.
#         return context

# class RecipeSearchListView(JSONResponseMixin,TemplateView):
#     model = Recipe

#     def get_queryset(self):
#         result = super(RecipeSearchListView, self).get_queryset()
#         query = self.request.GET.get('q')
#         if query:
#             query_list = query.split()
#             result = result.filter(
#                 reduce(operator.and_,
#                        (Q(title__icontains=q) for q in query_list)) |
#                 reduce(operator.and_,
#                        (Q(description__icontains=q) for q in query_list))
#             )
#             ids = ['recipe_'+str(r.id) for r in result]
#         else:
#             ids = []
            
#         self.data = {'id_list': ids} 

#     def get_context_data(self, **kwargs):
#         context = super(RecipeSearchListView, self).get_context_data(**kwargs)
#         context['id_list'] = self.data['id_list']
#         return context        

#     def render_to_response(self, context, **response_kwargs):
#         return self.render_to_json_response(context, **response_kwargs)
