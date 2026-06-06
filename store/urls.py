from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.product_list_view, name='product_list'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('product/<slug:slug>/review/', views.add_review_view, name='add_review'),
    
    # Cart & Buy Now Flow
    path('cart/', views.cart_view, name='cart'),
    path('buy-now/<int:product_id>/', views.buy_now_view, name='buy_now'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-success/<str:order_id>/', views.order_success_view, name='order_success'),
    path('track/', views.order_tracking_view, name='order_tracking'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile & Address management
    path('profile/', views.profile_view, name='profile'),
    path('profile/address/add/', views.add_address_view, name='add_address'),
    path('profile/address/edit/<int:address_id>/', views.edit_address_view, name='edit_address'),
    path('profile/address/delete/<int:address_id>/', views.delete_address_view, name='delete_address'),
    
    # API / AJAX Endpoints
    path('api/search/', views.api_live_search, name='api_live_search'),
    path('api/cart/add/', views.api_add_to_cart, name='api_add_to_cart'),
    path('api/cart/update/', views.api_update_cart_qty, name='api_update_cart_qty'),
    path('api/cart/remove/', views.api_remove_from_cart, name='api_remove_from_cart'),
    path('api/cart/coupon/', views.api_apply_coupon, name='api_apply_coupon'),
    path('api/wishlist/toggle/', views.api_toggle_wishlist, name='api_toggle_wishlist'),
]
