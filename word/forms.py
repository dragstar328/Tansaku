from django import forms

class WordForm(forms.Form):
  word = forms.CharField(max_length=1024)
  #json_field = forms.CharField(max_length=1024)

