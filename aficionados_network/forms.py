from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from profiles.models import UserProfile


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["first_name", "username", "email", "password1", "password2"]


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nombre de usuario"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Contraseña"}
        )
    )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["bio", "birth_date", "location", "website", "profile_picture"]
        widgets = {
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "birth_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"
            ),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "profile_picture": forms.FileInput(
                attrs={
                    "class": "form-control-file",
                    "accept": "image/*",
                    "onchange": "previewImage(this);",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurarse de que el formato de fecha sea compatible con el input type="date"
        self.fields["birth_date"].input_formats = ["%Y-%m-%d"]

        # Si ya hay una imagen de perfil, mostrarla
        if self.instance and self.instance.profile_picture:
            self.fields["profile_picture"].widget.initial_text = "Imagen actual"
            self.fields["profile_picture"].widget.template_name = (
                "django/forms/widgets/clearable_file_input.html"
            )
