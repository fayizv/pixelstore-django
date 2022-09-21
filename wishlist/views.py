from django.shortcuts import redirect, render
from .models import *
from django.core.exceptions import ObjectDoesNotExist
import requests


# Create your views here.
def wishlist(request,wishlist_items=None):
    if request.user.is_authenticated:
        try:
            wishlist_items = Wishlist.objects.all().filter(user=request.user).order_by('product')
            product = Product.objects.all()

        except ObjectDoesNotExist:  
            pass
        context = {
            'cart_items':wishlist_items,
            'all':product,
        }
        return render(request,'store/wishlist.html',context)
    else:
        return redirect('login')


def add_wishlist(request,product_id):
    product = Product.objects.get(id=product_id)
    is_wishlist_exist = Wishlist.objects.filter(user=request.user,product=product).exists()
    if is_wishlist_exist:
        pass
    else:
        wishlist = Wishlist.objects.create(
            user = request.user,
            product = product
        )
    return redirect('wishlist')


def remove_wishlist(request,product_id):
    product = Product.objects.get(id=product_id)
    wishlist_item = Wishlist.objects.get(user=request.user,product=product_id)
    wishlist_item.delete()
    return redirect('wishlist')
