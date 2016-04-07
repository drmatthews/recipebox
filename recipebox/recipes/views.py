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

from .models import Recipe, Ingredient, MethodStep
from .forms import RecipeForm, IngredientFormSet, MethodStepFormSet,\
                  UserForm, UserProfileForm, ImportForm

import urllib2
from bs4 import BeautifulSoup

############################################
##      CRUD
############################################

############################################
##      recipes
############################################

@login_required(login_url='/accounts/login/')
def recipe_list(request, template_name='recipes/recipes.html'):
    recipes = Recipe.objects.all()    
    context = {'recipe_list': recipes}
    return render(request, template_name, context)

@login_required(login_url='/accounts/login/')
def recipe_show(request, recipe_id, template_name='recipes/show_recipe.html'):
    recipe = get_object_or_404(Recipe, pk=recipe_id)  
    print "recipe", recipe._meta.get_fields()
    print RecipeForm(data=model_to_dict(Recipe.objects.get(pk=recipe_id)))
    print recipe.ingredient_set.all()[0].ingredient_name
    #ingredients = get_object_or_404(Ingredient, pk=recipe_id)
    print "ingredients", Ingredient.objects.filter(id=recipe_id).values() 
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
        recipe_form = RecipeForm(request.POST,request.FILES, instance=recipe)
        if recipe_form.is_valid():
            ingredient_formset = IngredientFormSet(request.POST, instance=recipe)
            method_formset = MethodStepFormSet(request.POST, instance=recipe)            
            if ingredient_formset.is_valid() and method_formset.is_valid():
                recipe.chef = request.user.get_username()
                recipe.source = request.user.get_username()
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

    if recipe_form.is_valid():
        recipe_form.save()
        return redirect('recipes')
    return render(request, template_name, {'recipe_form':recipe_form})#, 'picture_form':picture_form})

@login_required(login_url='/accounts/login/')
def recipe_delete(request, recipe_id, template_name='recipes/recipe_confirm_delete.html'):
    recipe = get_object_or_404(Recipe, pk=recipe_id)   
    if request.method=='POST':
        recipe.delete()
        return redirect('recipes')
    return render(request, template_name, {'recipe':recipe})

##################################################

@login_required(login_url='/accounts/login/')
def recipe_import(request, template_name='recipes/recipe_import.html'):

    if request.POST:
        import_form = ImportForm(request.POST)
        if import_form.is_valid():
            url = import_form.cleaned_data['url']
            source = import_form.cleaned_data['source']
            process_url(url,source)
            return redirect('recipes')
    else:
        import_form = ImportForm()
    return render(request, template_name, {'import_form':import_form})

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
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


def get_chef_from_taste(soup):
    #return soup.find('a',{'class':'chef__link'}).contents[0]
    return "Coles"

def get_ingredients_from_taste(soup):
    section = soup.find('ul','ingredient-table').find_all('li')
    inner_list = []
    for li in section:
        inner_list.append(li.find('label').contents[0])
    return inner_list

def get_method_from_taste(soup):
    section = soup.find('div','content-item tab-content current method-tab-content').find('ol').find_all('li')
    inner_list = []
    for li in section:
        inner_list.append(li.find('p').contents[0])
    return inner_list

def get_image_from_taste(soup):
    link = soup.find('img','print-thumb main-image')
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urllib2.urlopen(link["src"]).read())
    img_temp.flush()
    return img_temp

def get_description_from_taste(soup):
    return soup.find('div','content-item quote-left-right clearfix').find('p').contents[0]

def get_title_from_taste(soup):
    return soup.find('div','heading').find('h1').contents[0]

def get_chef_from_bbc(soup):
    return soup.find('a',{'class':'chef__link'}).contents[0]

def get_ingredients_from_bbc(soup): #this is the same as ingredients_from_taste except for label - no cb's
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
    return inner_list

def get_method_from_bbc(soup): #this is the same as method_from_taste
    section = soup.find('div','recipe-method-wrapper').find('ol').find_all('li')
    inner_list = []
    for li in section:
        inner_list.append(li.find('p').contents[0])
    return inner_list

def get_image_from_bbc(soup): #this is the same as image_from_taste except for getting div for image
    link = soup.find('div','emp-placeholder').find('img')
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urllib2.urlopen(link["src"]).read())
    img_temp.flush()
    return img_temp

def get_description_from_bbc(soup): #this is the same as description_from_taste
    return soup.find('div','recipe-description').find('p').contents[0]

def get_title_from_bbc(soup): #this is the same as title_from_taste
    return soup.find('div','recipe-title--small-spacing').find('h1').contents[0]

def create_recipe(source,title,chef,description,ingredients,steps,picture):
    recipe = Recipe()
    recipe.title = title
    recipe.source = source
    recipe.chef = chef
    recipe.description = description
    recipe.picture.save('test.jpg',File(picture))
    for ingredient in ingredients:
        recipe.ingredient_set.create(ingredient_name=ingredient)    
    
    for step in steps:
        if len(step) > 200:
            step_reduced = step[:200]
        else:
            step_reduced = step

        recipe.methodstep_set.create(step=step_reduced)         

def process_url(url,site):
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    print site
    if "bbc" in site:
        ingredients = get_ingredients_from_bbc(soup)
        steps = get_method_from_bbc(soup)
        picture = get_image_from_bbc(soup)
        description = get_description_from_bbc(soup)
        chef = get_chef_from_bbc(soup)
        title = get_title_from_bbc(soup)
        create_recipe(site,title,chef,description,ingredients,steps,picture)        
    elif "taste" in site:
        ingredients = get_ingredients_from_taste(soup)
        steps = get_method_from_taste(soup)
        picture = get_image_from_taste(soup)
        description = get_description_from_taste(soup)
        chef = get_chef_from_taste(soup)
        title = get_title_from_taste(soup)
        create_recipe(site,title,chef,description,ingredients,steps,picture)

