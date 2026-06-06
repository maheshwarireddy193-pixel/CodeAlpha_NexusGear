from store.models import Cart, Wishlist

def global_store_context(request):
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
        except Exception:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart_count = cart.total_items
        cart_items = cart.items.select_related('product').all()
        cart_subtotal = cart.subtotal
    else:
        wishlist_count = 0
        cart_count = 0
        cart_items = []
        cart_subtotal = 0
        cart = None

    return {
        'global_cart_count': cart_count,
        'global_wishlist_count': wishlist_count,
        'global_cart_items': cart_items,
        'global_cart_subtotal': cart_subtotal,
        'global_cart': cart,
	'currency_symbol': '₹',
    }
