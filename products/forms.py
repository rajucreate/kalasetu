from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    name = forms.CharField(required=True)
    description = forms.CharField(required=True, widget=forms.Textarea)
    price = forms.DecimalField(required=True, min_value=0)
    image = forms.ImageField(required=True)

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "image",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Product name"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Product description"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Price in ₹"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }