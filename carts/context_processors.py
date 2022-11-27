from .models import Cart, CartItem
from carts.views import get_cart_id

def get_cart_item_count(request) -> dict:
    if 'admin' in request.path:
        return {}

    try:    
        cart = Cart.objects.filter(cart_id=get_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart[:1])
        if not cart_items:
            return dict(cart_item_count=0)

        item_count = 0
        for cart_item in cart_items:
            item_count += cart_item.quantity
    except Cart.DoesNotExist:
        item_count = 0

    return dict(cart_item_count=item_count)