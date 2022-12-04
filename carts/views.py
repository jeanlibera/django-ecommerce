import traceback

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

    product_variation_list = []
    if request.method == 'POST':
        print("Handling a POST request, add_to_cart")
        input_values = ""
        for cart_item in request.POST:
            key = cart_item
            value = request.POST[key]

            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value)
                product_variation_list.append(variation)
                print(variation)
                input_values += f"{key}={value}, "
            except:
                pass

        print(f"Input values are {input_values}")
        print(f"product_variation: {product_variation_list}")

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
    
    # does the cart item exist?
    cart_items_exist: bool = CartItem.objects.filter(product=product, cart=cart).exists()
    if cart_items_exist:
        cart_item_objects = CartItem.objects.filter(product=product, cart=cart)
        # get the existing variations in the cart
        # TODO: I think you could immediately compare list(existing_variation) to product_variation_list,
        # and break out of the loop when they match. That would simplify the code below.
        existing_variation_list = []
        cart_item_id_list = []
        for cart_item in cart_item_objects:
            print("Examining cart item: ")
            print(cart_item)
            existing_variation = cart_item.variations.all()
            # convert the query set to a list, so that it can eventually be compared to product_variation_list
            existing_variation_list.append(list(existing_variation))
            cart_item_id_list.append(cart_item.id)

            print(f"Added {existing_variation} to the variation list")
        print(f"The complete variation list: {existing_variation_list}")
        
        if product_variation_list in existing_variation_list:
            print(f"Found the product {product.product_name} with variation {product_variation_list} in the existing list, and will increase the quantity")
            # increase the cart item quantity
            index = existing_variation_list.index(product_variation_list)
            item_id = cart_item_id_list[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
            
        else:
            # create a new cart item
            print("There are cart items for this product, but they do not have matching variations")
            cart_item: CartItem = CartItem.objects.create(product=product, cart=cart, quantity=1)
            # If there are product variations, add them to the cart item
            if len(product_variation_list) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation_list)
            print(f"Creating a new cart item for {product.product_name} with variation {product_variation_list}, quantity is 1")
            cart_item.save()

    else:
        print("There are no existing cart items for this product.")
        cart_item: CartItem = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1)
        # If there are product variations, add them to the cart item
        if len(product_variation_list) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation_list)
        print(f"Creating a new cart item for {product.product_name}, quantity is 1")
        cart_item.save()

    # redirect the user to the cart page
    cartUrl = reverse('cart_page')
    print("redirecting to", cartUrl)
    return redirect(cartUrl)

def decrement_item_quantity(request:HttpRequest, product_id:int, cart_item_id:int):
    print(f"Starting decrement_item_quantity for product_id={product_id}")

    try:
        # get the cart item
        product = get_object_or_404(Product, id=product_id)

        cart_id = get_cart_id(request)
        print(f"The cart id is {cart_id}")
        cart = Cart.objects.get(cart_id=cart_id)

        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        # lower the quantity, or remove it (if there are no items left)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            print(f"Reduced the number of items to {cart_item.quantity}")
        elif cart_item.quantity == 1:
            # delete the item
            print("The item quantity is 1. Deleting the item.")
            cart_item.delete()
    except Exception:
        traceback.print_exc()
        pass
    return redirect('cart_page')

def remove_cart_item(request:HttpRequest, product_id:int, cart_item_id:int):
    print(f"Starting remove_cart_item for product_id={product_id}")
    try:
        product = get_object_or_404(Product, id=product_id)

        # get the cart
        cart_id = get_cart_id(request)
        print(f"The cart id is {cart_id}")
        cart = Cart.objects.get(cart_id=cart_id)

        # get the cart item
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        # delete the item
        cart_item.delete()
    except Exception:
        traceback.print_exc()

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