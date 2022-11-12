from django.shortcuts import render, get_object_or_404

from category.models import Category
from .models import Product

# Create your views here.

def store(request, category_slug=None):
    category = None
    products = None
    
    if category_slug != None:
        print("store view for", type(category_slug), category_slug)
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()

    context = {
        'products': products,
        'products_count': product_count
    }
    return render(request, 'store/store.html', context)