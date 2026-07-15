"""Forms for signup and login.

We use email as the login identifier, so Django's default
AuthenticationForm/UserCreationForm (username-based) are subclassed rather
than reused as-is.
"""

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm

from apps.core.forms import StyledModelForm, TailwindStyledFormMixin

from .models import User


class SignUpForm(StyledModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, min_length=8)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]
        widgets = {
            "email": forms.EmailInput(attrs={"autofocus": True}),
        }

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean() or {}
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(TailwindStyledFormMixin, AuthenticationForm):
    """Login form using 'email' as the field name shown to the user."""

    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data
