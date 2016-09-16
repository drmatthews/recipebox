import datetime
from haystack import indexes
from recipes.models import Recipe


class RecipeIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')

    def get_model(self):
        return Recipe

    def index_queryset(self, using=None):
        return self.get_model().objects.all()