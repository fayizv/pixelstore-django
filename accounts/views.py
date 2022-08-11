
from email import message
from django.shortcuts import redirect, render
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout, authenticate


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
            messages.success(request, "Registration Successful.")
            return redirect('login')
    else:
        form = RegistrationForm()       
    
    context = {
        'form' : form,
    }
    return render(request, 'accounts/register.html',context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            # message.success(request,"You are now Logged in.")
            return redirect('home')
        else:
            messages.error(request, "Invalid login Credentials.")   
            return redirect('login') 
    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged Out')
    return redirect('login')

