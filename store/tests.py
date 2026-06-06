from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from store.models import Category, Product, Cart, CartItem, Coupon, Order, OrderItem, Review

class NexusGearStoreTests(TestCase):

    def setUp(self):
        # Create standard category and products
        self.category = Category.objects.create(name="Mouse", slug="mouse")
        
        self.product = Product.objects.create(
            name="Viper Esports Mouse",
            slug="viper-esports-mouse",
            category=self.category,
            brand="Nexus",
            price=Decimal("80.00"),
            original_price=Decimal("100.00"),
            stock=10,
            description="Premium test mouse description.",
            specifications="Sensor: Focus Pro\nWeight: 58g",
            image_url="https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&q=80&w=600"
        )
        
        # Seed Coupons
        self.coupon10 = Coupon.objects.create(code="NEXUS10", discount_percent=10, active=True)
        
        # User details
        self.username = "testoperator"
        self.email = "test@nexusgear.demo"
        self.password = "access123"
        
        # Client setup
        self.client = Client()

    def test_user_registration_and_auto_login(self):
        """Verify registering a new user creates profile, cart, and logs them in."""
        response = self.client.post(reverse('register'), {
            'full_name': 'Test Operator',
            'username': 'newoperator',
            'email': 'new@nexusgear.demo',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to NexusGear, Test!")
        
        # Verify user database entries
        user = User.objects.get(username='newoperator')
        self.assertEqual(user.email, 'new@nexusgear.demo')
        
        # Verify profile and cart signal auto-creation
        self.assertTrue(hasattr(user, 'profile'))
        self.assertTrue(hasattr(user, 'cart'))

    def test_persistent_cart_operations(self):
        """Verify cart items persist, increment, and sum up correctly for authenticated user."""
        self.client.login(username=self.username, password=self.password)
        
        # Create user
        user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.client.login(username=self.username, password=self.password)
        
        # Call API add to cart
        response = self.client.get(reverse('api_add_to_cart'), {'product_id': self.product.id, 'qty': 2})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_count'], 2)
        self.assertEqual(data['cart_subtotal'], 160.0)
        
        # Verify DB Cart contains the items
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items[0].product, self.product)
        self.assertEqual(cart_items[0].quantity, 2)

    def test_coupon_discount_calculation(self):
        """Verify NEXUS10 coupon code subtracts 10% off the subtotal accurately."""
        subtotal = Decimal("160.00")
        
        # Trigger AJAX apply coupon
        user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.client.login(username=self.username, password=self.password)
        
        response = self.client.get(reverse('api_apply_coupon'), {
            'coupon_code': 'NEXUS10',
            'subtotal': subtotal
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        # 10% of 160 = 16.00
        self.assertEqual(data['discount'], 16.0)
        self.assertEqual(data['total'], 144.0)

    def test_verified_buyer_reviews_restriction(self):
        """Verify only buyers who ordered can review products."""
        user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.client.login(username=self.username, password=self.password)
        
        # Attempt to post a review BEFORE purchasing
        response = self.client.post(reverse('add_review', kwargs={'slug': self.product.slug}), {
            'rating': 5,
            'comment': 'Awesome cyber mouse!'
        }, follow=True)
        
        # Verify blocked with error message
        self.assertContains(response, "Only verified buyers who purchased this product can leave reviews.")
        self.assertEqual(Review.objects.filter(product=self.product, user=user).count(), 0)
        
        # Simulate purchase by adding Order and OrderItem
        import datetime
        order = Order.objects.create(
            user=user,
            order_id="NG-999999",
            status="Delivered",
            full_name="Test Operator",
            phone="000-111-222",
            address_line="Flat 404, Sector 7",
            city="Neo Tokyo",
            state="Tokyo",
            pincode="100001",
            subtotal=Decimal("80.00"),
            total_amount=Decimal("80.00"),
            expected_delivery=datetime.date.today()
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            product_price=self.product.price,
            product_image=self.product.image_url,
            quantity=1
        )
        
        # Attempt to post a review AFTER purchasing
        response = self.client.post(reverse('add_review', kwargs={'slug': self.product.slug}), {
            'rating': 5,
            'comment': 'Awesome cyber mouse!'
        }, follow=True)
        
        # Verify review is created successfully
        self.assertContains(response, "Review posted successfully!")
        self.assertEqual(Review.objects.filter(product=self.product, user=user).count(), 1)
        self.assertEqual(Review.objects.get(product=self.product, user=user).comment, "Awesome cyber mouse!")
