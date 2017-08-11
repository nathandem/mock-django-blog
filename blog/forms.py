# we connect css to form widget

from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta():
        model = Post
        fields = ("author","title","text")

        # we set up widgets right in the form Meta class with the widget dict
        # widgets enable us to change default input tag Django chooses to render the form fields
        # doc for more: https://docs.djangoproject.com/en/1.11/ref/forms/widgets/#built-in-widgets
        widgets = {
            'title':forms.TextInput(attrs={'class':'textinputclass'}),
            'text':forms.Textarea(attrs={'class':'editable medium-editor-textarea postcontent'}),
            # attrs arg contains a dict of html attributes for the input tag which correspond to the widget (form field)
            # textinputclass is a class we define (but don't use later in blog.css) vs editable is from the medium style editor
        }

class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment
        fields = ('author','text')

        widgets = {
            'author':forms.TextInput(attrs={'class':'textinputclass'}),
            'text':forms.Textarea(attrs={'class':'editable medium-editor-textarea'}),
        }

# check the view of this SimpleForm

BIRTH_YEAR_CHOICES = ('1980', '1981', '1982')
FAVORITE_COLORS_CHOICES = (
    ('blue', 'Blue'),
    ('green', 'Green'),
    ('black', 'Black'),
)

class PersonalityForm(forms.Form):
    birth_year = forms.DateField(widget=forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES))
    favorite_colors = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=FAVORITE_COLORS_CHOICES,
    )
    file_user = forms.FileField() # some constraints possible, e.g. on the name of the file (like for Webperf!!! :D)
    image_user = forms.ImageField()
