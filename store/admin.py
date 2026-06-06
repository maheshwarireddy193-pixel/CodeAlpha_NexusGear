from django.contrib import admin
from .models import (
    Category, Product, ProductImage, Profile, SavedAddress, 
    Cart, CartItem, Wishlist, Coupon, Order, OrderItem, Review
)

# Inline models for cleaner editing experience
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_price', 'product_image', 'quantity')

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

# Customized Admin View classes
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'original_price', 'stock', 'rating', 'is_featured')
    list_filter = ('category', 'brand', 'is_featured')
    list_editable = ('price', 'stock', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'brand', 'description')
    inlines = [ProductImageInline]

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'user__email', 'phone')

@admin.register(SavedAddress)
class SavedAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'state', 'pincode', 'is_default')
    list_filter = ('city', 'state', 'is_default')
    search_fields = ('user__username', 'full_name', 'phone', 'city', 'pincode')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'total_items')
    search_fields = ('user__username',)
    inlines = [CartItemInline]

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'active')
    list_filter = ('active',)
    list_editable = ('active',)
    search_fields = ('code',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'status', 'total_amount', 'payment_method', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'created_at')
    list_editable = ('status', 'payment_status')
    search_fields = ('order_id', 'user__username', 'full_name', 'phone')
    inlines = [OrderItemInline]
    readonly_fields = ('order_id', 'created_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_verified_buyer', 'created_at')
    list_filter = ('rating', 'is_verified_buyer', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
