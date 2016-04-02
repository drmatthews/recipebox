from django.forms import ModelForm, CharField, PasswordInput, Form, ChoiceField
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from models import Recipe, Ingredient, MethodStep, RecipePicture, UserProfile

MAX_INGREDIENTS = 5
MAX_STEPS = 5

class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'
        exclude = ['user']

class IngredientForm(ModelForm):
    class Meta:
        model = Ingredient
        fields = '__all__'

class MethodStepForm(ModelForm):
    class Meta:
        model = MethodStep
        fields = '__all__'

class RecipePictureForm(ModelForm):
    class Meta:
        model = RecipePicture
        fields = ['picture']

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
    url = CharField(max_length=200)
    source = ChoiceField(choices=(('bbc','BBC Food'),('taste','taste.com.au')))

MethodStepFormSet = inlineformset_factory(Recipe,\
    MethodStep,\
    can_delete=False,\
    extra=MAX_STEPS,\
    fields=('step',))

IngredientFormSet = inlineformset_factory(Recipe,\
    Ingredient,\
    can_delete=False,\
    extra=MAX_INGREDIENTS,\
    fields=('ingredient_name',))

