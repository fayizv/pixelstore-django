from django.http import HttpResponse
from django.shortcuts import redirect, render
from carts.models import Cart,CartItem

from django.views.decorators.cache import never_cache
from carts.views import _cart_id
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required

# verifiacation email 
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode
import requests

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
@never_cache
def login(request):
  if request.user.is_authenticated:
    return redirect('home')
  else:
    if request.method == 'POST':
      email = request.POST['email']
      password = request.POST['password']
      
      user = auth.authenticate(request, username=email, password=password)
      if user is not None:
        if user.is_authenticated:
          
          try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) 
            is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
            if is_cart_item_exists:
              cart_item = CartItem.objects.filter(cart=cart)
              
              # Get product variation by cart id
              product_variation = []
              for item in cart_item:
                variation = item.variations.all()
                product_variation.append(list(variation))
              
              # Get cart item from user to access product variation
              cart_item = CartItem.objects.filter(user=user)
              existing_variations_list = []
              id = []
              for item in cart_item:
                existing_variations = item.variations.all()
                existing_variations_list.append(list(existing_variations))
                id.append(item.id)
              
              for variation in product_variation:
                if variation in existing_variations_list:
                  index = existing_variations_list.index(variation)
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
          url = request.META.get('HTTP_REFERER')
          
          try:
            query = request.utils.urlparse(url).query
            params = dict(x.split('=') for x in query.split('&'))
            if 'next' in params:
              next_page = params['next']
              return redirect(next_page)
            
          except:
            return redirect('home')
    
        else:
          messages.warning(request, 'Account is not activated, Please activate your account to login')
      
      else:
        messages.error(request, 'Email or Password is incorrect')
      
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

@login_required(login_url = 'login')
def dashboard(request):
    return render(request, 'accounts/dashboard/admin_dashboard.html')