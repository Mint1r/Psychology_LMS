
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'phon_number','email')

from accounts.models import UserDocuments

class UserDocumentsForm(forms.ModelForm):
    class Meta:
        model = UserDocuments
        fields = ['diploma','passport_main','passport_registration','snils']
