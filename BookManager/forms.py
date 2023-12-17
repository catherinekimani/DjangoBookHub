from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper

class SignUpForm(UserCreationForm):
    name = forms.CharField(required=True)
    email = forms.CharField(required=True)

    class Meta:
        model = User

        fields = [
			'name',
            'email',
            'username',
            'password1',
            'password2'
		]

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.first_name = self.changed_data=['name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user