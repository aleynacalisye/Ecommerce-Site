from django.contrib.auth.views import LoginView
from django.urls import path
from . import views
from django.contrib.auth import views as auth_view

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('user/orders/', views.user_orders, name='user_orders'),
    path('login/', LoginView.as_view(template_name='login_form.html', success_url='home.html'), name='login'),
    path('logout/', auth_view.LogoutView.as_view(template_name='logout.html'), name="logout"),
   
]