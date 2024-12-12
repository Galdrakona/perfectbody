"""
URL configuration for perfectbody project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from accounts.views import register, login_view, logout_view, edit_profile, profile_view, change_password, \
    trainer_register
from viewer.views import home, products, services, trainers, view_cart, add_to_cart, remove_from_cart, update_cart, \
    user_profile_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('products/', products, name='products'),
    path('services/', services, name='services'),
    path('trainers/', trainers, name='trainers'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('cart/', view_cart, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('card/update/<int:product_id>/', update_cart, name='update_cart'),
    path('change_password/', change_password, name='change_password'),
    path('trainer_register', trainer_register, name='trainer_register'),
    path('user/<str:username>/', user_profile_view, name='user_profile'),
]
