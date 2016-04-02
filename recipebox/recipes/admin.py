from django.contrib import admin

from .models import Recipe,Ingredient,MethodStep

class IngredientInline(admin.StackedInline):
    model = Ingredient

class MethodStepInline(admin.StackedInline):
    model = MethodStep

class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline,MethodStepInline]

admin.site.register(Recipe, RecipeAdmin)
