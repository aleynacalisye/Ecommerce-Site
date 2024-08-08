from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import LoginForm
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hoş geldiniz, {username}! Hesabınız başarıyla oluşturuldu.')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

 # LoginForm'ın doğru şekilde import edildiğinden emin olun

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login Succes")
                return redirect('/')
            else:
             messages.error(request, "İnvalid Credentails")
    else:
        form = LoginForm()
    return render(request, 'home.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def user_orders(request):
    # Kullanıcının siparişlerini getir
    orders = request.user.orders.all()  # Örnek bir sipariş sorgusu
    return render(request, 'user_orders.html', {'orders': orders})


