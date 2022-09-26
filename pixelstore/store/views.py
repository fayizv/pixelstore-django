from django.shortcuts import render,get_object_or_404,redirect
from carts.models import CartItem
from store.models import Product
from category.models import category
from .forms import ProductForm
from carts.views import _cart_id
from django.db.models import Q
from orders.models import ProductGallery




def home(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(category,slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        product_count = products.count()

    else:
        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()

    context = {
        'products' : products,
        'product_count' : product_count,
    }
    return render(request,'home.html',context)   


def product_detail(request,category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
        
        
    except Exception as e:
        raise e

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product' : single_product,
        'in_cart'        : in_cart,
    }
    return render(request,'store/product_detail.html',context)    

# def view_product(request,slug=None):
#     categories = None
#     products = None

#     if slug != None:
#         categories = get_object_or_404(category, slug=slug)
#         products = Product.objects.filter(category=categories, is_available=True)
#     else:
#         products = Product.objects.all().filter(is_available=True).order_by("id")
#         # product_count = products.count()
#     context = {
#         "products": products,
#         #'product_count': product_count,
#     }
#     return render(request,'accounts/admin_dashboard/view_product.html',context)

# def add_product(request):
#     if request.method == 'POST':
#         product_form = ProductForm(request.POST,request.FILES)

#         if product_form.is_valid():
#             product_form.save()
#             return redirect('add_product.html')

#     else:
#         product_form = ProductForm()

#     context = {
#         'product_form' : product_form

#     }    

#     return render(request,'accounts/admin_dashboard/add_product.html',context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(detailes__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
            print('hello')
    context = {
        'products' : products,
        'product_count' : product_count,
    } 
    return render(request,'home.html',context)

