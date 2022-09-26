from django import forms
from .models import Product,Variation



class ProductForm(forms.ModelForm):
  
  class Meta:
     model = Product
     fields = ['product_name','slug','detailes','stock','price','image','is_available','category']
  
  def __init__(self, *args, **kwargs):
    super(ProductForm, self).__init__(*args, **kwargs)
    
    for field in self.fields:
      self.fields[field].widget.attrs['class'] = 'form-control'
    
    self.fields['is_available'].widget.attrs['class'] = 'ml-2 mt-1 form-check-input'




class VariationForm(forms.ModelForm):
  
  class Meta:
    model = Variation
    fields = ['product', 'variation_category', 'variation_value', 'is_active']
  
  def __init__(self, *args, **kwargs):
    super(VariationForm, self).__init__(*args, **kwargs)
    
    for field in self.fields:
      self.fields[field].widget.attrs['class'] = 'form-control'
      
    self.fields['is_active'].widget.attrs['class'] = 'ml-2 mt-1 form-check-input'