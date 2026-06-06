import random
import string
import datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Avg, F
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from .models import (
    Category, Product, ProductImage, Profile, SavedAddress, 
    Cart, CartItem, Wishlist, Coupon, Order, OrderItem, Review
)

# Helper function to generate unique order ID
def generate_order_id():
    chars = string.ascii_uppercase + string.digits
    while True:
        code = 'NG-' + ''.join(random.choices(chars, k=6))
        if not Order.objects.filter(order_id=code).exists():
            return code

# --- USER AUTHENTICATION & PROFILE SYSTEM ---

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    next_url = request.GET.get('next', 'home')
    if request.method == 'POST':
        username_or_email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = None
        # Try authenticating by username first, then email
        user = authenticate(username=username_or_email, password=password)
        if not user:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
                
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0) # Browser close expiry
            messages.success(request, f"Welcome back, {user.first_name or user.username}! Login successful.")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username/email or password. Please try again.")
            
    return render(request, 'store/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Simple Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
        else:
            first_name = ''
            last_name = ''
            if full_name:
                name_parts = full_name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
            user = User.objects.create_user(
                username=username, 
                email=email, 
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            login(request, user)
            messages.success(request, f"Welcome to NexusGear, {user.first_name or user.username}! Registration successful.")
            return redirect('home')
            
    return render(request, 'store/register.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully. Have a great day!")
    return redirect('login')

@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            full_name = request.POST.get('full_name', '')
            email = request.POST.get('email', '')
            phone = request.POST.get('phone', '')
            profile_pic = request.FILES.get('profile_picture')
            
            # Email clash check
            if email and User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.error(request, "This email is already in use by another user.")
            else:
                user = request.user
                if full_name:
                    parts = full_name.split(' ', 1)
                    user.first_name = parts[0]
                    user.last_name = parts[1] if len(parts) > 1 else ''
                user.email = email
                user.save()
                
                profile.phone = phone
                if profile_pic:
                    profile.profile_picture = profile_pic
                profile.save()
                
                messages.success(request, "Profile details updated successfully!")
                return redirect('profile')
                
        elif action == 'change_password':
            old_pass = request.POST.get('old_password')
            new_pass = request.POST.get('new_password')
            confirm_new = request.POST.get('confirm_new_password')
            
            if not request.user.check_password(old_pass):
                messages.error(request, "Incorrect old password.")
            elif new_pass != confirm_new:
                messages.error(request, "New passwords do not match.")
            elif len(new_pass) < 6:
                messages.error(request, "New password must be at least 6 characters.")
            else:
                request.user.set_password(new_pass)
                request.user.save()
                update_session_auth_hash(request, request.user) # Keep user logged in
                messages.success(request, "Password changed successfully!")
                return redirect('profile')
                
    addresses = request.user.addresses.all()
    orders = request.user.orders.all()
    return render(request, 'store/profile.html', {
        'profile': profile,
        'addresses': addresses,
        'orders': orders
    })

# --- ADDRESS MANAGEMENT IN PROFILE ---

@login_required
def add_address_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address_line = request.POST.get('address_line')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        is_default = request.POST.get('is_default') == 'on'
        
        SavedAddress.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address_line=address_line,
            city=city,
            state=state,
            pincode=pincode,
            is_default=is_default
        )
        messages.success(request, "Address added successfully!")
        
        # If came from checkout page, redirect back to checkout
        next_page = request.GET.get('next')
        if next_page == 'checkout':
            return redirect('checkout')
            
    return redirect('profile')

@login_required
def edit_address_view(request, address_id):
    address = get_object_or_404(SavedAddress, id=address_id, user=request.user)
    if request.method == 'POST':
        address.full_name = request.POST.get('full_name')
        address.phone = request.POST.get('phone')
        address.address_line = request.POST.get('address_line')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.pincode = request.POST.get('pincode')
        address.is_default = request.POST.get('is_default') == 'on'
        address.save()
        
        messages.success(request, "Address updated successfully!")
        
        next_page = request.GET.get('next')
        if next_page == 'checkout':
            return redirect('checkout')
            
    return redirect('profile')

@login_required
def delete_address_view(request, address_id):
    address = get_object_or_404(SavedAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully!")
    
    next_page = request.GET.get('next')
    if next_page == 'checkout':
        return redirect('checkout')
        
    return redirect('profile')

# --- CATALOG PAGES ---

def home_view(request):
    categories = Category.objects.all()[:6]
    featured_products = Product.objects.filter(is_featured=True)[:4]
    if not featured_products.exists():
        featured_products = Product.objects.all()[:4]
        
    special_deals = Product.objects.filter(original_price__gt=F('price'))[:3]
    if not special_deals.exists():
        special_deals = Product.objects.all()[:3]
        
    return render(request, 'store/home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'special_deals': special_deals
    })

def product_list_view(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    
    # Filtering
    q = request.GET.get('q', '')
    if q:
        products = products.filter(
            Q(name__icontains=q) | 
            Q(description__icontains=q) | 
            Q(brand__icontains=q)
        )
        
    cat_id = request.GET.get('category')
    if cat_id:
        products = products.filter(category_id=cat_id)
        
    brand = request.GET.get('brand')
    if brand:
        products = products.filter(brand=brand)
        
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=Decimal(min_price))
    if max_price:
        products = products.filter(price__lte=Decimal(max_price))
        
    rating = request.GET.get('rating')
    if rating:
        products = products.filter(rating__gte=float(rating))
        
    stock = request.GET.get('stock')
    if stock == 'in_stock':
        products = products.filter(stock__gt=0)
        
    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price-low-high':
        products = products.order_by('price')
    elif sort == 'price-high-low':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.order_by('-rating')
    else: # newest
        products = products.order_by('-created_at')
        
    # Extract unique brands for filtering sidebar
    all_brands = Product.objects.values_list('brand', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(products, 8) # 8 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/product_list.html', {
        'products': page_obj,
        'categories': categories,
        'brands': all_brands,
        'selected_category': cat_id,
        'selected_brand': brand,
        'selected_sort': sort,
        'min_price': min_price,
        'max_price': max_price,
        'selected_rating': rating,
        'selected_stock': stock,
        'q': q
    })

def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.select_related('user').all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if avg_rating:
        product.rating = round(avg_rating, 1)
        product.reviews_count = reviews.count()
        product.save()
        
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    # Handle parsing of specification rows
    specs_list = []
    if product.specifications:
        for line in product.specifications.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                specs_list.append((k.strip(), v.strip()))
                
    # Check if logged in buyer has purchased this item before allowing a review
    has_purchased = False
    if request.user.is_authenticated:
        has_purchased = OrderItem.objects.filter(
            order__user=request.user, 
            product=product
        ).exists()
        
    already_reviewed = False
    if request.user.is_authenticated:
        already_reviewed = Review.objects.filter(product=product, user=request.user).exists()

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'specs_list': specs_list,
        'has_purchased': has_purchased,
        'already_reviewed': already_reviewed
    })

@login_required
def add_review_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    # Check verification
    has_purchased = OrderItem.objects.filter(
        order__user=request.user, 
        product=product
    ).exists()
    
    if not has_purchased:
        messages.error(request, "Only verified buyers who purchased this product can leave reviews.")
        return redirect('product_detail', slug=slug)
        
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not rating or not comment:
            messages.error(request, "Rating and comments are required.")
            return redirect('product_detail', slug=slug)
            
        review, created = Review.objects.update_or_create(
            product=product, 
            user=request.user,
            defaults={
                'rating': int(rating),
                'comment': comment,
                'is_verified_buyer': True
            }
        )
        
        # Re-calc average rating
        reviews = product.reviews.all()
        avg = reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0
        product.rating = round(avg, 1)
        product.reviews_count = reviews.count()
        product.save()
        
        if created:
            messages.success(request, "Review posted successfully! Thank you.")
        else:
            messages.success(request, "Your review has been updated.")
            
    return redirect('product_detail', slug=slug)

# --- WISHLIST VIEW ---

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {
        'wishlist_items': wishlist_items
    })

# --- CART VIEW ---

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product').all()
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'subtotal': cart.subtotal
    })

# --- BUY NOW DIRECT BYPASS ---

@login_required
def buy_now_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.stock <= 0:
        messages.error(request, "Sorry, this product is currently out of stock.")
        return redirect('product_detail', slug=product.slug)
    # Bypasses the cart by packing product parameters in a checkout session
    return redirect(f"/checkout/?buy_now={product.id}&qty=1")

# --- CHECKOUT & ORDER FLOW ---

@login_required
def checkout_view(request):
    # Determine if this is a Buy Now flow or Cart checkout
    buy_now_id = request.GET.get('buy_now')
    qty = int(request.GET.get('qty', 1))
    
    product_buy_now = None
    cart_items = []
    
    if buy_now_id:
        product_buy_now = get_object_or_404(Product, id=buy_now_id)
        subtotal = product_buy_now.price * qty
        items_summary = [{
            'product': product_buy_now,
            'quantity': qty,
            'total_price': subtotal
        }]
    else:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.select_related('product').all()
        if not cart_items:
            messages.error(request, "Your cart is empty. Add products to proceed.")
            return redirect('product_list')
        subtotal = cart.subtotal
        items_summary = cart_items

    # Coupon Processing via Session
    coupon_code = request.session.get('coupon_code', None)
    discount_amount = Decimal(0.00)
    coupon_obj = None
    if coupon_code:
        try:
            coupon_obj = Coupon.objects.get(code=coupon_code, active=True)
            discount_amount = (subtotal * Decimal(coupon_obj.discount_percent)) / Decimal(100)
            discount_amount = round(discount_amount, 2)
        except Coupon.DoesNotExist:
            pass

    total_amount = subtotal - discount_amount
    
    # Save addresses list for address selectors
    saved_addresses = request.user.addresses.all()
    
    if request.method == 'POST':
        # Collect shipping variables
        address_selection = request.POST.get('address_selection')
        
        full_name = ""
        phone = ""
        address_line = ""
        city = ""
        state = ""
        pincode = ""
        
        if address_selection and address_selection != 'new':
            address_obj = get_object_or_404(SavedAddress, id=address_selection, user=request.user)
            full_name = address_obj.full_name
            phone = address_obj.phone
            address_line = address_obj.address_line
            city = address_obj.city
            state = address_obj.state
            pincode = address_obj.pincode
        else:
            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            address_line = request.POST.get('address_line')
            city = request.POST.get('city')
            state = request.POST.get('state')
            pincode = request.POST.get('pincode')
            
            # Option to save the address for later
            save_address_checked = request.POST.get('save_address') == 'on'
            if save_address_checked and full_name and address_line:
                SavedAddress.objects.create(
                    user=request.user,
                    full_name=full_name,
                    phone=phone,
                    address_line=address_line,
                    city=city,
                    state=state,
                    pincode=pincode,
                    is_default=(not saved_addresses.exists()) # default if first
                )
                
        payment_method = request.POST.get('payment_method')
        
        # Validations
        if not full_name or not phone or not address_line or not city or not state or not pincode:
            messages.error(request, "Please complete all shipping address fields.")
            return render(request, 'store/checkout.html', {
                'items': items_summary, 'subtotal': subtotal,
                'discount_amount': discount_amount, 'total_amount': total_amount,
                'saved_addresses': saved_addresses, 'coupon': coupon_obj
            })
            
        # Verify Stock availability first
        for item in items_summary:
            prod = item['product'] if buy_now_id else item.product
            q = qty if buy_now_id else item.quantity
            if prod.stock < q:
                messages.error(request, f"Sorry, the item '{prod.name}' does not have enough stock. (Available: {prod.stock})")
                return redirect('cart')

        # Create Order
        new_order_id = generate_order_id()
        expected_del = datetime.date.today() + datetime.timedelta(days=5)
        
        order = Order.objects.create(
            user=request.user,
            order_id=new_order_id,
            full_name=full_name,
            phone=phone,
            address_line=address_line,
            city=city,
            state=state,
            pincode=pincode,
            subtotal=subtotal,
            coupon=coupon_obj,
            discount_amount=discount_amount,
            total_amount=total_amount,
            payment_method=payment_method,
            payment_status='Paid' if payment_method != 'COD' else 'Pending',
            expected_delivery=expected_del
        )
        
        # Generate OrderItems & Subtract inventory stock
        for item in items_summary:
            prod = item['product'] if buy_now_id else item.product
            q = qty if buy_now_id else item.quantity
            
            OrderItem.objects.create(
                order=order,
                product=prod,
                product_name=prod.name,
                product_price=prod.price,
                product_image=prod.image_url,
                quantity=q
            )
            
            # Deduct inventory stock
            prod.stock -= q
            prod.save()
            
        # Clean Cart if order came from cart
        if not buy_now_id:
            cart = request.user.cart
            cart.items.all().delete()
            
        # Clean Coupon Session state
        if 'coupon_code' in request.session:
            del request.session['coupon_code']
            
        messages.success(request, "Order placed successfully! Thank you for shopping with us.")
        return redirect('order_success', order_id=order.order_id)
        
    return render(request, 'store/checkout.html', {
        'items': items_summary,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'total_amount': total_amount,
        'saved_addresses': saved_addresses,
        'coupon': coupon_obj,
        'buy_now_id': buy_now_id,
        'buy_now_qty': qty
    })

@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {
        'order': order
    })

def order_tracking_view(request):
    order_id = request.GET.get('order_id', '').strip()
    order = None
    stages = ['Placed', 'Confirmed', 'Packed', 'Shipped', 'Delivered']
    current_index = -1
    
    if order_id:
        try:
            # If authenticated, restrict to user. Else allow open lookup (demo convenience)
            if request.user.is_authenticated:
                order = Order.objects.get(order_id=order_id, user=request.user)
            else:
                order = Order.objects.get(order_id=order_id)
            current_index = stages.index(order.status)
        except Order.DoesNotExist:
            messages.error(request, "Order not found. Please double-check your Order ID.")
            
    return render(request, 'store/order_tracking.html', {
        'order': order,
        'order_id': order_id,
        'stages': stages,
        'current_index': current_index
    })

# --- AJAX / REST API GATEWAYS ---

@csrf_exempt
def api_live_search(request):
    q = request.GET.get('q', '').strip()
    results = []
    if len(q) >= 2:
        products = Product.objects.filter(
            Q(name__icontains=q) | 
            Q(brand__icontains=q) |
            Q(category__name__icontains=q)
        )[:5]
        for p in products:
            results.append({
                'id': p.id,
                'name': p.name,
                'price': float(p.price),
                'slug': p.slug,
                'image_url': p.image_url
            })
    return JsonResponse({'products': results})

@login_required
def api_add_to_cart(request):
    product_id = request.GET.get('product_id')
    qty = int(request.GET.get('qty', 1))
    
    product = get_object_or_404(Product, id=product_id)
    if product.stock <= 0:
        return JsonResponse({'success': False, 'message': 'Product is currently out of stock.'})
        
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        if cart_item.quantity + qty > product.stock:
            return JsonResponse({'success': False, 'message': f'Cannot add more. Only {product.stock} items in stock.'})
        cart_item.quantity += qty
    else:
        if qty > product.stock:
             return JsonResponse({'success': False, 'message': f'Cannot add. Only {product.stock} items in stock.'})
        cart_item.quantity = qty
        
    cart_item.save()
    
    # Reload items to return updated html snippets
    items = []
    for item in cart.items.all():
        items.append({
            'name': item.product.name,
            'quantity': item.quantity,
            'price': float(item.product.price),
            'image_url': item.product.image_url
        })
        
    return JsonResponse({
        'success': True,
        'message': f"Added '{product.name}' to your cart!",
        'cart_count': cart.total_items,
        'cart_subtotal': float(cart.subtotal),
        'items': items
    })

@login_required
def api_update_cart_qty(request):
    item_id = request.GET.get('item_id')
    action = request.GET.get('action') # 'increase' or 'decrease'
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if action == 'increase':
        if cart_item.quantity + 1 > cart_item.product.stock:
            return JsonResponse({'success': False, 'message': f'Cannot increase. Only {cart_item.product.stock} in stock.'})
        cart_item.quantity += 1
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            return JsonResponse({'success': False, 'message': 'Quantity cannot be less than 1. Remove the item instead.'})
            
    cart_item.save()
    cart = request.user.cart
    
    return JsonResponse({
        'success': True,
        'item_qty': cart_item.quantity,
        'item_total': float(cart_item.total_price),
        'cart_count': cart.total_items,
        'cart_subtotal': float(cart.subtotal)
    })

@login_required
def api_remove_from_cart(request):
    item_id = request.GET.get('item_id')
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    p_name = cart_item.product.name
    cart_item.delete()
    
    cart = request.user.cart
    return JsonResponse({
        'success': True,
        'message': f"Removed '{p_name}' from your cart.",
        'cart_count': cart.total_items,
        'cart_subtotal': float(cart.subtotal)
    })

@login_required
def api_apply_coupon(request):
    code = request.GET.get('coupon_code', '').strip().upper()
    subtotal = Decimal(request.GET.get('subtotal', 0.0))
    
    if not code:
        if 'coupon_code' in request.session:
            del request.session['coupon_code']
        return JsonResponse({'success': True, 'discount': 0.0, 'total': float(subtotal), 'message': 'Coupon cleared.'})
        
    try:
        coupon = Coupon.objects.get(code=code, active=True)
        # Set coupon in session
        request.session['coupon_code'] = coupon.code
        
        discount = (subtotal * Decimal(coupon.discount_percent)) / Decimal(100)
        discount = round(discount, 2)
        total = subtotal - discount
        
        return JsonResponse({
            'success': True,
            'discount': float(discount),
            'total': float(total),
            'message': f"Coupon '{coupon.code}' applied! You saved {coupon.discount_percent}%."
        })
    except Coupon.DoesNotExist:
        if 'coupon_code' in request.session:
            del request.session['coupon_code']
        return JsonResponse({
            'success': False,
            'message': 'Invalid or expired coupon code.'
        })

@login_required
def api_toggle_wishlist(request):
    product_id = request.GET.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)
    
    if wishlist_item.exists():
        wishlist_item.delete()
        added = False
        message = f"Removed '{product.name}' from your wishlist."
    else:
        Wishlist.objects.create(user=request.user, product=product)
        added = True
        message = f"Added '{product.name}' to your wishlist!"
        
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return JsonResponse({
        'success': True,
        'added': added,
        'message': message,
        'wishlist_count': wishlist_count
    })
