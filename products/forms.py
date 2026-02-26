from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "image",
            "region",
            "cultural_story",
            "craft_process",
            "impact_score"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Product name"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Product description"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Price in ₹"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "region": forms.TextInput(attrs={"class": "form-control", "placeholder": "Region or origin (e.g., 'Jaipur, Rajasthan')"}),
            "cultural_story": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Tell the story of this product and its cultural significance"}),
            "craft_process": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Describe the step-by-step process of how this product is made"}),
            "impact_score": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100, "placeholder": "Artisan empowerment score (0-100)"}),
        }