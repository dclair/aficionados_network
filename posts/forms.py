from django import forms
from .models import Posts, Comment, Event, EventComment


from django import forms
from .models import Posts


class PostCreateForm(forms.ModelForm):
    # Definimos los campos que necesitan una configuración muy específica fuera del Meta
    caption = forms.CharField(
        label="Descripción",
        required=False,  # En el modelo era opcional, cámbialo a True si quieres obligar
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Cuéntanos más sobre esta publicación...",
            }
        ),
        help_text="Máximo 2000 caracteres.",
    )

    class Meta:
        model = Posts
        # Añadimos 'location' y organizamos el orden de aparición
        fields = ["title", "category", "location", "caption", "image"]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Dale un título (opcional)",
                }
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "¿Dónde se tomó esto?"}
            ),
            "image": forms.FileInput(
                attrs={
                    # Mantenemos 'form-control d-none' y AÑADIMOS 'validate-image'
                    "class": "form-control d-none validate-image",
                    "accept": "image/*",
                    "id": "id_image",
                }
            ),
        }

        error_messages = {
            "category": {
                "required": "Debes elegir una afición para clasificar tu post.",
            },
            "image": {
                "required": "Una publicación sin imagen no es un 'Click'. ¡Sube una!",
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
            "image",
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
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
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
