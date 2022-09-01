from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [ 'product_name','slug','detailes','stock','price','image','is_available','category']

