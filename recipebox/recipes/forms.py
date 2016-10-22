from __future__ import absolute_import

from django.forms import ModelForm, CharField, PasswordInput, Form, ChoiceField,\
                         TextInput, Textarea, ModelChoiceField, FileField
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import Recipe, Ingredient, MethodStep, UserProfile, ExternalRecipe
from recipebox.wines.models import WineNote

INITIAL_INGREDIENTS = 1
INITIAL_STEPS = 1

def get_wines():
    wines = WineNote.objects.all()
    wine_names = [("","")]
    for w in wines:
        wine_names.append((w.id,w.title)) 
    return wine_names

class WineNoteModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.title  

class ExternalSourceChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.source           

class RecipeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RecipeForm, self).__init__(*args, **kwargs)

        self.fields['matched_wine'] = WineNoteModelChoiceField(
            queryset=WineNote.objects.all(),
            required=False, empty_label="No matching wine" )

        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': field
        })          

    class Meta:
        model = Recipe
        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 2}),
        }        
        fields = '__all__'
        exclude = ['user']

class ExternalRecipeForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ExternalRecipeForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
        }) 

    class Meta:
        model = ExternalRecipe
        fields = '__all__'        

class IngredientForm(ModelForm):
    class Meta:
        model = Ingredient
        fields = '__all__'

class MethodStepForm(ModelForm):
    class Meta:
        model = MethodStep
        fields = '__all__'

class UserForm(ModelForm):
    password = CharField(widget=PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['picture']

class ImportForm(Form):
    def __init__(self, *args, **kwargs):
        super(ImportForm, self).__init__(*args, **kwargs)

        self.fields['source'] = ExternalSourceChoiceField(
            queryset=ExternalRecipe.objects.all(),
            required=False, empty_label="No external sources defined" )

        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
        })    

    url = CharField(max_length=200)

class ImportFileForm(Form):
    def __init__(self, *args, **kwargs):
        super(ImportFileForm, self).__init__(*args, **kwargs)

        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
        })     
            
    file = FileField(label="",required=True)

MethodStepFormSet = inlineformset_factory(Recipe,
    MethodStep,
    can_delete=True,
    extra=INITIAL_STEPS,
    fields=('step',),
    widgets={'step': Textarea(attrs={'cols': 80, 'rows': 2, 'class': 'form-control',
             'placeholder': 'method step ...'})})

IngredientFormSet = inlineformset_factory(Recipe,
    Ingredient,
    can_delete=True,
    extra=INITIAL_INGREDIENTS,
    fields=('ingredient_name',),
    widgets={'ingredient_name': TextInput(attrs={'class': 'form-control',
              'placeholder': 'ingredient ...'})})

