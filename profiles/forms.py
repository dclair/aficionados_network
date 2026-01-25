from django import forms
from .models import Review


# formulario para valorar un perfil
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{i} Estrellas") for i in range(5, 0, -1)],
                attrs={"class": "form-select"},
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "¿Qué tal estuvo el plan?",
                }
            ),
        }
