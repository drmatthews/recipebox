from __future__ import absolute_import

from django.forms import ModelForm, CharField, PasswordInput, Form, ChoiceField,\
                         TextInput, Textarea
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import WineNote

class WineNoteForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(WineNoteForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
        })

    class Meta:
        model = WineNote
        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 2}),
        }        
        fields = '__all__'
        exclude = ['user']

