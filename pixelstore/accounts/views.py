from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from carts.models import Cart,CartItem
from orders.models import Order, OrderProduct
from category.models import category
from store.models import Product,Variation
from store.forms import ProductForm,VariationForm

from django.views.decorators.cache import never_cache
from carts.views import _cart_id
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.hashers import make_password,check_password

# verifiacation email 
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode
import requests

from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # user activation 

            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            # messages.success(request, "Registration Successful.")
            return redirect('/accounts/login/?comment=verfication&email='+email)
    else:
        form = RegistrationForm()       
    
    context = {
        'form' : form,
    }
    return render(request, 'accounts/register.html',context)

### Sign in Function
@csrf_exempt
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting the product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    # product_variation = [1, 2, 3, 4, 6]
                    # ex_var_list = [4, 6, 3, 5]

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                if (request.user.is_superadmin):
                  return redirect('admin_dashboard')
                else:
                  return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')



@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged Out')
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')

@never_cache
@login_required(login_url='login')
def admin_dashboard(request):
    if request.user.is_superadmin:

        user_count = Account.objects.filter(is_superadmin=False).count()
        product_count = Product.objects.all().count()
        order_count = Order.objects.filter(is_ordered=True).count()
        category_count = category.objects.all().count()
        variation_count = Variation.objects.all().count()
        admin_order_count = Order.objects.filter(user__is_superadmin=True).count()
        

        context = {
            'user_count': user_count,
            'product_count': product_count,
            'order_count' : order_count,
            'category_count' : category_count,
            'variation_count' : variation_count,
            'admin_order_count' : admin_order_count
        }

        return render(request,'accounts/admin_dashboard/admin_dashboard.html',context)
    else:
        return redirect('home')

@never_cache
@login_required(login_url='login')
def user_management(request):
    if request.method == "POST":
      key = request.POST['key']
      users = Account.objects.filter(Q(first_name__startswith=key) | Q(last_name__startswith=key) | Q(username__startswith=key) | Q(email__startswith=key)).order_by('id')
    else:
      users = Account.objects.filter(is_superadmin=False).order_by('id')

    paginator = Paginator(users,10)
    page = request.GET.get('page')
    paged_users = paginator.get_page(page)
    context = {
        'users' : paged_users
    }
    return render(request, 'accounts/admin_dashboard/user_management.html',context)
def user_ban(request, user_id):
    user = Account.objects.get(id=user_id)
    user.is_active = False
    user.save()
    return redirect('user_management')

def user_unban(request, user_id):
    user = Account.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return redirect('user_management')




@never_cache
@login_required(login_url='login')
def product_management(request):
  if request.method == "POST":
    key = request.POST['key']
    products = Product.objects.filter(Q(product_name__startswith=key) | Q(slug__startswith=key) | Q(category__category_name__startswith=key)).order_by('id')
  else:
    products = Product.objects.all().order_by('id')

  paginator = Paginator(products, 10)
  page = request.GET.get('page')
  paged_products = paginator.get_page(page)
  
  context = {
    'products': paged_products
  }
  return render(request, 'accounts/admin_dashboard/product_management.html', context)

# Add Product
@never_cache
@login_required(login_url='login')
def add_product(request):
  if request.method == 'POST':
    form = ProductForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()

        return redirect('product_management')
    
    return HttpResponse('Form is invalid')
  else:
    form = ProductForm()
    context = {
      'form': form
    }
    return render(request, 'accounts/admin_dashboard/add_product.html', context)

# Edit Product
@never_cache
@login_required(login_url='manager_login')
def edit_product(request, product_id):
  product = Product.objects.get(id=product_id)
  form = ProductForm(instance=product)
  
  if request.method == 'POST':
    try:
      form = ProductForm(request.POST, request.FILES, instance=product)
      if form.is_valid():
        form.save()
        
        return redirect('product_management')
    
    except Exception as e:
      raise e

  context = {
    'product': product,
    'form': form
  }
  return render(request, 'accounts/admin_dashboard/edit_product.html', context)

# Delete Product
@never_cache
@login_required(login_url='manager_login')
def delete_product(request, product_id):
  product = Product.objects.get(id=product_id)
  product.delete()
  return redirect('product_management')


# Admin change password
@never_cache
@login_required(login_url='login')
def admin_change_password(request):
  if request.method == 'POST':
    current_user = request.user
    current_password = request.POST['current_password']
    password = request.POST['password']
    confirm_password = request.POST['confirm_password']
    
    if password == confirm_password:
      if check_password(current_password, current_user.password):
        if check_password(password, current_user.password):
          messages.warning(request, 'Current password and new password is same')
        else:
          hashed_password = make_password(password)
          current_user.password = hashed_password
          current_user.save()
          messages.success(request, 'Password changed successfully')
      else:
        messages.error(request, 'Wrong password')
    else:
      messages.error(request, 'Passwords does not match')
  
  return render(request, 'accounts/admin_dashboard/admin_password.html')

# Manage Order
@never_cache
@login_required(login_url='login')
def order_management(request):
  if request.method =="POST":
    key = request.POST['key']
    orders = Order.objects.filter(Q(is_ordered=True), Q(order_number_startswith=key) | Q(useremailstartswith=key) | Q(first_name_startswith=key)).order_by('id')
  else:
    orders = Order.objects.filter(is_ordered=True).order_by('id')
    

  context = {
    'orders': orders
  }
  return render(request, 'accounts/admin_dashboard/order_management.html', context)



# Cancel Order
@never_cache
@login_required(login_url='login')
def admin_cancel_order(request, order_number):
  order = Order.objects.get(order_number=order_number)
  order.status = 'Cancelled'
  order.save()
  
  return redirect('order_management')
  

# Accept Order
@never_cache
@login_required(login_url='login')
def accept_order(request, order_number):
  order = Order.objects.get(order_number=order_number)
  order.status = 'Shipped'
  order.save()
  
  return redirect('order_management')

# Complete Order
@never_cache
@login_required(login_url='login')
def complete_order(request, order_number):
  order = Order.objects.get(order_number=order_number)
  order.status = 'Delivered'
  order.save()
  
  return redirect('order_management')


def category_management(request):
    categories = category.objects.all().order_by('id')

    context = {
        'categories' :categories
    }

    return render(request, 'accounts/admin_dashboard/category_management.html',context)


def add_category(request):
    if request.method == 'POST':
        try:
            category_name = request.POST['category_name']
            category_slug = request.POST['category_slug']
            category_description = request.POST['category_description']
            
            categories = category(
                category_name = category_name,
                slug = category_slug,
                description = category_description
            )
            
            categories.save()
            return redirect('category_management')
        except Exception as e:
            raise e
    return render(request, 'accounts/admin_dashboard/add_category.html')

# Update Category
@never_cache
@login_required(login_url='login')
def update_category(request, category_id):
  try:
    categories = category.objects.get(id=category_id)
    
    if request.method == 'POST':
      category_name = request.POST['category_name']
      category_slug = request.POST['category_slug']
      
      
      categories.category_name = category_name
      categories.slug = category_slug
      
      categories.save()
      
      return redirect('category_management')
    
    context = {
      'category': categories
    }
    return render(request, 'accounts/admin_dashboard/update_category.html', context)
    
  except Exception as e:
    raise e
    
       

@never_cache
@login_required(login_url='login')
def delete_category(request,category_id):
    categories = category.objects.get(id=category_id)
    categories.delete()

    return redirect('category_management')



# My orders
@login_required(login_url='login')
def admin_order(request):
  current_user = request.user
  
  if request.method == 'POST':
    keyword = request.POST['keyword']
    orders = Order.objects.filter(Q(user=current_user), Q(is_ordered=True), Q(order_number_startswith=keyword) | Q(useremailstartswith=keyword) | Q(first_namestartswith=keyword) | Q(last_namestartswith=keyword) | Q(phone_startswith=keyword)).order_by('-created_at')
    
  else:
    orders = Order.objects.all().order_by('-created_at')
  
  paginator = Paginator(orders, 10)
  page = request.GET.get('page')
  paged_orders = paginator.get_page(page)
  context = {
    'orders': paged_orders,
  }
  return render(request, 'accounts/admin_dashboard/admin_orders.html', context)

# Cancel Order
@never_cache
@login_required(login_url='login')
def cancel_order(request, order_number):
  order = Order.objects.get(order_number=order_number)
  order.status = 'Cancelled'
  order.save()
  
  return redirect('order_management')

# User Dashboard
@login_required(login_url = 'login')
def user_dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/user_dashboard/user_dashboard.html', context)

def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/user_dashboard/my_orders.html', context)



@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
                                    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/user_dashboard/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/user_dashboard/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/user_dashboard/order_detail.html', context)