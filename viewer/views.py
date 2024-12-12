from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def products(request):
    return render(request, 'products.html')

def services(request):
    return render(request, 'services.html')

def trainers(request):
    return render(request, 'trainers.html')

def menu_view(request):
    categories = Category.objects.prefetch_related('subcategories').all()
    return render(request, 'base.html', {'categories': categories})

