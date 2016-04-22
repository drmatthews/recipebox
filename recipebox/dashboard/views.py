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

from recipebox.recipes.models import Recipe, Ingredient, MethodStep
from recipebox.wines.models import WineNote
from recipebox.recipes.forms import RecipeForm, IngredientFormSet, MethodStepFormSet,\
                          ImportForm
from recipebox.wines.forms import WineNoteForm

import os
import time
import hmac
from hashlib import sha1
import json
import urllib, base64
import urllib2
from bs4 import BeautifulSoup

@login_required(login_url='/accounts/login/')
def dashboard(request, template_name='dash.html'):

    wines = WineNote.objects.all()
    wine_names = [("","")]
    for w in wines:
        wine_names.append((w.title,w.title))

    recipe_form = RecipeForm(wines=wine_names)
    ingredient_formset = IngredientFormSet(instance=Recipe())
    method_formset = MethodStepFormSet(instance=Recipe())    
    import_form = ImportForm()
    wine_form = WineNoteForm()
    context = {'recipe_form': recipe_form, 'ingredient_formset':ingredient_formset,\
                'method_formset': method_formset, 'import_form':import_form,\
                'wine_form': wine_form}
    return render(request, template_name, context)

@login_required(login_url='/accounts/login/')
def sign_s3(request):

    AWS_ACCESS_KEY = os.environ.get('DJANGO_AWS_ACCESS_KEY_ID')
    AWS_SECRET_KEY = os.environ.get('DJANGO_AWS_SECRET_ACCESS_KEY')
    S3_BUCKET = os.environ.get('DJANGO_AWS_STORAGE_BUCKET_NAME')
    object_name = urllib.quote_plus(request.GET['file_name'])
    mime_type = request.GET['file_type']
    expires = int(time.time()+60*60*24)
    amz_headers = "x-amz-acl:public-read"

    string_to_sign = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (mime_type, expires, amz_headers, S3_BUCKET, object_name)

    signature = base64.encodestring(hmac.new(AWS_SECRET_KEY.encode(), string_to_sign.encode('utf8'), sha1).digest())
    signature = urllib.quote_plus(signature.strip())

    url = 'https://s3.amazonaws.com/%s/%s' % (S3_BUCKET, object_name)

    content = json.dumps({
        'signed_request': '%s?AWSAccessKeyId=%s&Expires=%s&Signature=%s' % (url, AWS_ACCESS_KEY, expires, signature),
        'url': url,
    })
    return HttpResponse(content)    

