from django import forms
from .models import Posts, Comment, Event, EventComment


class PostCreateForm(forms.ModelForm):
    caption = forms.CharField(
        label="Descripción",
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Añade una descripción a tu publicación...",
            }
        ),
        error_messages={
            "required": "El campo de descripción es obligatorio.",
        },
    )

    class Meta:
        model = Posts
        fields = ["image", "title", "caption", "category"]
        widgets = {
            "image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Título llamativo"}
            ),
            "caption": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Cuéntanos sobre esto...",
                }
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
        }
        error_messages = {
            "image": {
                "required": "Por favor, selecciona una imagen para tu publicación.",
            },
            "caption": {
                "max_length": "La descripción es demasiado larga (máximo %(limit_value)d caracteres).",
            },
            "category": {
                "required": "Por favor, selecciona una categoría para tu publicación.",
            },
        }


class ProfileFollowForm(forms.Form):
    profile_pk = forms.IntegerField(widget=forms.HiddenInput())

    def clean_profile_pk(self):
        profile_pk = self.cleaned_data.get("profile_pk")
        if not profile_pk:
            raise forms.ValidationError("El ID del perfil es requerido.")
        return profile_pk


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Añade un comentario...",
                    "required": True,
                }
            )
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "hobby",
            "location",
            "event_date",
            "max_participants",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Quedada para fotos nocturnas",
                }
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "hobby": forms.Select(attrs={"class": "form-select"}),
            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "¿Dónde nos encontramos?",
                }
            ),
            "event_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",  # Esto activa el calendario en el navegador
                }
            ),
            "max_participants": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
        }


class EventCommentForm(forms.ModelForm):
    class Meta:
        model = EventComment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Escribe un comentario o pregunta...",
                    "rows": "2",
                }
            ),
        }
