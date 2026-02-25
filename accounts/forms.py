from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Role


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].choices = [
            (Role.ARTISAN, Role.ARTISAN.label),
            (Role.BUYER, Role.BUYER.label),
            (Role.CONSULTANT, Role.CONSULTANT.label),
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    class Meta:
        model = User
        fields = ["email", "role", "password1", "password2"]

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")