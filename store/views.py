from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, Page
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404

from category.models import Category
from .models import Product
from carts.views import get_cart_id
from carts.models import CartItem

# Create your views here.

NUMBER_OF_PRODUCTS_PER_PAGE = 2

def store(request:HttpRequest, category_slug:str|None=None):
    category = None
    products = None
    
    if category_slug != None:
        print("store view for", type(category_slug), category_slug)
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True).order_by('product_name')
    else:
        print("store view for all products")
        products = Product.objects.all().filter(is_available=True).order_by('product_name')

    paginator = Paginator(products, NUMBER_OF_PRODUCTS_PER_PAGE)
    page_number = request.GET.get('page') # from the URL query parameter
    page_obj: Page = paginator.get_page(page_number)
    product_count = products.count()

    context = {
        'products_count': product_count,
        'page_obj': page_obj,
    }
    return render(request, 'store/store.html', context)

def product_detail(request:HttpRequest, category_slug:str|None, product_slug:str|None):
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

def search(request: HttpRequest):
    print("Started search")
    params = request.GET
    if 'keyword' in params:
        keyword_value = params['keyword']
        if keyword_value:  # if it is not empty
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword_value) | Q(product_name__icontains=keyword_value))
            product_count = products.count()

            context = {
                'products_count': product_count,
                'page_obj': products,
            }
            return render(request, 'store/store.html', context)

    return render(request, 'store/store.html')