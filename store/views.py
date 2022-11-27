from django.shortcuts import render, get_object_or_404

from category.models import Category
from .models import Product
from carts.views import get_cart_id
from carts.models import CartItem

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

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        cart_id = get_cart_id(request)
        in_cart = CartItem.objects.filter(
            cart__cart_id=cart_id, product=single_product).exists()
        print(f"In product detail, set in_cart={in_cart}")
    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }
    return render(request, 'store/product_detail.html', context)