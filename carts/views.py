from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from store.models import Product, Variation
from .models import Cart, CartItem

# Create your views here.

def get_cart_id(request:HttpRequest) -> str:
    # use the session id for the cart id
    cart_id = request.session.session_key
    if not cart_id:
        print(f"Creating a new cart id (really just the session key)"
               " because the cart id did not exist")
        request.session.create()
        cart_id = request.session.session_key
        print(f"In get_cart_id(), the new cart_id is {cart_id}")
    return cart_id

def add_to_cart(request:HttpRequest, product_id:int):
    print(f"Starting add_to_cart for product_id={product_id}")
    product=Product.objects.get(id=product_id)

    product_variation = []
    if request.method == 'POST':
        input_values = ""
        for item in request.POST:
            key = item
            value = request.POST[key]

            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value)
                product_variation.append(variation)
                print(variation)
                input_values += f"{key}={value}, "
            except:
                pass

        return HttpResponse(input_values)
        #color = request.POST['color']
        #size = request.POST['size']
        #print(f"Color={color}, Size={size}")
        #return HttpResponse(f"Color={color}, Size={size}")

    # get the cart
    cart_id = get_cart_id(request)
    print(f"The cart id is {cart_id}")
    try:
        cart = Cart.objects.get(cart_id=cart_id)
    except:
        # if the cart does not exist, create it
        print(f"Created a new cart because the cart did not exist")
        cart = Cart.objects.create(cart_id = cart_id)
        cart.save()
    
    # add the product to the cart
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        print(f"A cart item for {product.product_name} already existed,"
               " increased the quantity to {cart_item.quantity}")
    except:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1)
        print(f"Creating a new cart item for {product.product_name}, quantity is 1")
    cart_item.save()

    # redirect the user to the cart page
    cartUrl = reverse('cart_page')
    print("redirecting to", cartUrl)
    return redirect(cartUrl)

def decrement_item_quantity(request:HttpRequest, product_id:int):
    print(f"Starting decrement_item_quantity for product_id={product_id}")
    product = get_object_or_404(Product, id=product_id)

    # get the cart
    cart_id = get_cart_id(request)
    print(f"The cart id is {cart_id}")
    cart = Cart.objects.get(cart_id=cart_id)

    # get the cart item
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        print(f"Reduced the number of items to {cart_item.quantity}")
    elif cart_item.quantity == 1:
        # delete the item
        print("The item quantity is 1. Deleting the item.")
        cart_item.delete()
    return redirect('cart_page')

def remove_cart_item(request:HttpRequest, product_id:int):
    print(f"Starting remove_cart_item for product_id={product_id}")
    product = get_object_or_404(Product, id=product_id)

    # get the cart
    cart_id = get_cart_id(request)
    print(f"The cart id is {cart_id}")
    cart = Cart.objects.get(cart_id=cart_id)

    # get the cart item
    cart_item = CartItem.objects.get(product=product, cart=cart)

    # delete the item
    cart_item.delete()
    return redirect('cart_page')

def cart(request:HttpRequest, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=get_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        cart_item: CartItem
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = total * .02
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        "total": total,
        "tax": tax,
        "grand_total": grand_total,
        "quantity": quantity,
        "cart_items": cart_items
    }
    return render(request, 'store/cart.html', context)