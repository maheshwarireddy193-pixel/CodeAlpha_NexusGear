from django.core.management.base import BaseCommand
from store.models import Category, Product, ProductImage, Coupon

class Command(BaseCommand):
    help = 'Seeds database with categories, gaming products, images, and coupons'

    def handle(self, *args, **options):
        self.stdout.write('Seeding categories...')
        Category.objects.all().delete()
        Product.objects.all().delete()
        Coupon.objects.all().delete()

        categories_data = [
            {'name': 'Mouse', 'image_url': 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&q=80&w=400'},
            {'name': 'Keyboard', 'image_url': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&q=80&w=400'},
            {'name': 'Headset', 'image_url': 'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&q=80&w=400'},
            {'name': 'Monitor', 'image_url': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&q=80&w=400'},
            {'name': 'Controller', 'image_url': 'https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?auto=format&fit=crop&q=80&w=400'},
            {'name': 'Chair', 'image_url': 'https://images.unsplash.com/photo-1598550476439-6847785fce6e?auto=format&fit=crop&q=80&w=400'},
        ]

        categories = {}
        for c_data in categories_data:
            cat = Category.objects.create(name=c_data['name'], image_url=c_data['image_url'])
            categories[c_data['name']] = cat

        self.stdout.write('Seeding products...')

        products_data = [
            # MICE
            {
                'name': 'Nexus Viper Mini Wireless',
                'category': categories['Mouse'],
                'brand': 'Nexus',
                'price': 79.99,
                'original_price': 99.99,
                'rating': 4.8,
                'reviews_count': 124,
                'stock': 25,
                'is_featured': True,
                'description': 'A high-performance lightweight gaming mouse with zero-latency wireless connection and optical switches. Experience lightning-fast responses and absolute tracking accuracy with a 30,000 DPI sensor. Built for esports professionals who demand the absolute best in reliability and featherlight control.',
                'specifications': 'Sensor: Focus Pro 30K Optical\nWeight: 58 grams\nBattery Life: Up to 80 Hours\nConnectivity: HyperSpeed Wireless (2.4GHz), Wired USB-C\nButtons: 6 Programmable Buttons\nPolling Rate: 4000Hz compatible',
                'image_url': 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&q=80&w=600',
                'extra_images': [
                    'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1625842268584-8f329045567f?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1625842268396-857c7d9bb6cf?auto=format&fit=crop&q=80&w=600'
                ]
            },
            {
                'name': 'AeroBlade Cyber Mouse',
                'category': categories['Mouse'],
                'brand': 'Aero',
                'price': 49.99,
                'original_price': 59.99,
                'rating': 4.5,
                'reviews_count': 82,
                'stock': 40,
                'is_featured': False,
                'description': 'Sleek honeycomb shell gaming mouse featuring ultra-flexible paracord cable and customizable 16.8 million color RGB effects. Weighing only 65g, it slides effortlessly on any surface with virgin-grade PTFE mouse feet.',
                'specifications': 'Sensor: PixArt PMW3389 Optical\nWeight: 65 grams\nDPI: Up to 16,000 DPI\nConnectivity: Wired Paracord USB\nButtons: 5 Programmable Buttons\nRGB: Full RGB under-glow',
                'image_url': 'https://images.unsplash.com/photo-1625842268584-8f329045567f?auto=format&fit=crop&q=80&w=600',
                'extra_images': [
                    'https://images.unsplash.com/photo-1625842268584-8f329045567f?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1625842268396-857c7d9bb6cf?auto=format&fit=crop&q=80&w=600'
                ]
            },
            # KEYBOARDS
            {
                'name': 'Nexus Spectre Mechanical Keyboard',
                'category': categories['Keyboard'],
                'brand': 'Nexus',
                'price': 129.99,
                'original_price': 149.99,
                'rating': 4.9,
                'reviews_count': 230,
                'stock': 15,
                'is_featured': True,
                'description': 'Premium 75% mechanical gaming keyboard with hot-swappable yellow linear switches and glowing neon cyan backlighting. The layout is optimized to save desk space while keeping core arrow keys, and the dynamic stabilizers are pre-lubricated for an incredibly smooth, satisfying typing sound.',
                'specifications': 'Layout: 75% Space-Saving\nSwitches: Pre-lubed Nexus Yellow Linear (Hot-Swappable)\nKeycaps: Double-shot PBT Cherry Profile\nConnectivity: Tri-Mode (Wired USB-C, 2.4GHz Wireless, Bluetooth 5.0)\nBattery: 4000mAh Rechargeable\nStabilizers: Screw-in PCB Stabilizers',
                'image_url': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&q=80&w=600',
                'extra_images': [
                    'https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1601445638532-3c6f6c3aa1d6?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&q=80&w=600'
                ]
            },
            {
                'name': 'Apex Pro RGB Keyboard',
                'category': categories['Keyboard'],
                'brand': 'Apex',
                'price': 89.99,
                'original_price': 109.99,
                'rating': 4.6,
                'reviews_count': 94,
                'stock': 18,
                'is_featured': False,
                'description': 'Full-size mechanical keyboard featuring tactile brown switches set into an elegant aircraft-grade aluminum top plate. Highly versatile, with dedicated media rollers, a magnetic soft-touch wrist rest, and fully customizable per-key RGB backlighting.',
                'specifications': 'Layout: Full Size (104 keys)\nSwitches: Tactile Brown Switches\nFrame: Aircraft-Grade Aluminum\nRGB: Per-key customizable with software\nWrist Rest: Ergonomic Magnetic Detachable\nConnectivity: Pass-through USB Wired',
                'image_url': 'https://images.unsplash.com/photo-1601445638532-3c6f6c3aa1d6?auto=format&fit=crop&q=80&w=600',
                'extra_images': [
                    'https://images.unsplash.com/photo-1601445638532-3c6f6c3aa1d6?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&q=80&w=600'
                ]
            },
            # HEADSETS
            {
                'name': 'Nexus Void Pro Wireless Headset',
                'category': categories['Headset'],
                'brand': 'Nexus',
                'price': 99.99,
                'original_price': 129.99,
                'rating': 4.7,
                'reviews_count': 148,
                'stock': 12,
                'is_featured': True,
                'description': 'Step into the center of the action with the Nexus Void Pro. Equipped with spatial audio and a premium broadcast-grade microphone, you can communicate with teammate perfection. Outfitted with deep, breathable memory foam earcups to deliver long-lasting comfort across continuous combat matches.',
                'specifications': 'Drivers: 50mm Custom Neodymium\nSpatial Audio: DTS Headphone:X 2.0 (7.1 Surround)\nFrequency Response: 20Hz - 20,000Hz\nBattery Life: Up to 30 Hours\nMicrophone: Detachable Noise-Cancelling with mute LED\nConnection: 2.4GHz Wireless / 3.5mm Aux',
                'image_url': 'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&q=80&w=600',
                'extra_images': [
                    'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&q=80&w=600'
                ]
            },
            {
                'name': 'EchoStrike Wired Headset',
                'category': categories['Headset'],
                'brand': 'Echo',
                'price': 59.99,
                'original_price': 69.99,
                'rating': 4.4,
                'reviews_count': 56,
                'stock': 30,
                'is_featured': False,
                'description': 'Dynamic stereo wired gaming headset providing crisp audio and deep bass. Ideal for consoles and PCs, with inline volume controller, folding mic arm, and premium noise isolation.',
                'specifications': 'Drivers: 40mm Dynamic\nSound Type: Closed-back Stereo\nConnector: 3.5mm Gold-Plated (Y-Splitter included)\nMic: Retractable Omnidirectional\nCable Length: 2.2 meters\nCompatibility: PC, PS5, Xbox Series X/S, Switch',
                'image_url': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&q=80&w=600',
                'extra_images': [
                    'https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&q=80&w=600'
                ]
            },
            # MONITORS
            {
                'name': 'Nexus Horizon 27" Curved Monitor',
                'category': categories['Monitor'],
                'brand': 'Nexus',
                'price': 299.99,
                'original_price': 349.99,
                'rating': 4.8,
                'reviews_count': 74,
                'stock': 8,
                'is_featured': True,
                'description': 'Experience zero screen tearing and buttery fluid visuals with this 27-inch curved display. Equipped with a blazing 240Hz refresh rate and crystal QHD resolution, this Fast-IPS display provides stunning HDR colors and incredibly immersive curved viewing angles.',
                'specifications': 'Display Size: 27 inch Curved (1500R)\nResolution: 2560 x 1440 (QHD 2K)\nRefresh Rate: 240Hz\nPanel Type: Fast IPS Panel\nResponse Time: 1ms (Grey-to-Grey)\nSync Technology: FreeSync Premium & G-Sync Compatible\nHDR: VESA DisplayHDR 400',
                'image_url': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&q=80&w=600',
                'extra_images': [
                    'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1547082299-de196ea013d6?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1593305841991-05c297ba4575?auto=format&fit=crop&q=80&w=600'
                ]
            },
            {
                'name': 'UltraSync 24" Gaming Monitor',
                'category': categories['Monitor'],
                'brand': 'UltraSync',
                'price': 149.99,
                'original_price': 179.99,
                'rating': 4.3,
                'reviews_count': 61,
                'stock': 14,
                'is_featured': False,
                'description': 'The ultimate entry-level esports monitor. Packed with a 165Hz panel, Full HD resolution, and AMD FreeSync, this VA screen guarantees competitive response times and deep dark-room contrast ratios.',
                'specifications': 'Display Size: 24 inch Flat\nResolution: 1920 x 1080 (FHD 1080p)\nRefresh Rate: 165Hz\nPanel Type: High-contrast VA Panel\nResponse Time: 1ms (MPRT)\nSync Technology: AMD FreeSync\nPorts: 1x DisplayPort, 2x HDMI',
                'image_url': 'https://images.unsplash.com/photo-1547082299-de196ea013d6?auto=format&fit=crop&q=80&w=600',
                'extra_images': [
                    'https://images.unsplash.com/photo-1547082299-de196ea013d6?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1593305841991-05c297ba4575?auto=format&fit=crop&q=80&w=600'
                ]
            },
            # CONTROLLERS
            {
                'name': 'Nexus Catalyst Pro Controller',
                'category': categories['Controller'],
                'brand': 'Nexus',
                'price': 69.99,
                'original_price': 79.99,
                'rating': 4.6,
                'reviews_count': 118,
                'stock': 20,
                'is_featured': False,
                'description': 'Elevate your gaming with the Nexus Catalyst. Engineered with tactile mechanical face buttons, 4 remappable rear paddles, and adjustable hair-trigger locks. Non-slip textured grips ensure perfect control through sweaty competitive matches.',
                'specifications': 'Layout: Xbox Ergonomic Layout\nRear Paddles: 4 Removable and Remappable paddles\nTriggers: Adjustable Hair-Trigger stops\nConnectivity: Wired USB-C / Low Latency Bluetooth\nCompatibility: PC, Xbox, Switch, Android, iOS\nWeight: 285g',
                'image_url': 'https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?auto=format&fit=crop&q=80&w=600',
                'extra_images': [
                    'https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1592840496694-26d035b52b48?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&q=80&w=600'
                ]
            },
            {
                'name': 'ShadowGlide Wireless Gamepad',
                'category': categories['Controller'],
                'brand': 'ShadowGlide',
                'price': 39.99,
                'original_price': 49.99,
                'rating': 4.2,
                'reviews_count': 42,
                'stock': 0, # OUT OF STOCK for demo
                'is_featured': False,
                'description': 'An affordable, versatile multi-platform wireless gamepad. Packed with dual haptic vibration motors, precise analog sticks, and quick-access macro keys. Features broad out-of-the-box compatibility.',
                'specifications': 'Layout: Dual-Shock Layout\nBattery capacity: 600mAh (Up to 12 Hours battery)\nConnectivity: 2.4GHz Wireless Dongle, Bluetooth, Wired\nCompatibility: PC (X-input), Nintendo Switch, Android, iOS\nVibration: Dual rumble motors\nWeight: 210g',
                'image_url': 'https://images.unsplash.com/photo-1592840496694-26d035b52b48?auto=format&fit=crop&q=80&w=600',
                'extra_images': [
                    'https://images.unsplash.com/photo-1592840496694-26d035b52b48?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&q=80&w=600'
                ]
            },
            # CHAIRS
            {
                'name': 'Nexus Throne Ergonomic Chair',
                'category': categories['Chair'],
                'brand': 'Nexus',
                'price': 249.99,
                'original_price': 299.99,
                'rating': 4.9,
                'reviews_count': 86,
                'stock': 5,
                'is_featured': True,
                'description': 'Achieve perfect posture and legendary comfort. The Nexus Throne is constructed from cold-cured foam, premium breathable faux leather, and a solid steel frame. It offers 4D micro-adjustable armrests, a heavy-duty Class-4 gas piston, and a full 165-degree tilt recline to support healthy gaming sessions.',
                'specifications': 'Covering Material: Premium PU Breathable Faux Leather\nInternal Frame: 2.0mm Heavy-Duty Reinforced Steel\nArmrests: 4D Multi-adjustable (Height, angle, slide, rotation)\nGas Lift Class: Certified Class 4 Hydraulic piston\nRecline capacity: 90° to 165° lockable recline\nWeight Support: Supports up to 330 lbs (150 kg)',
                'image_url': 'https://images.unsplash.com/photo-1598550476439-6847785fce6e?auto=format&fit=crop&q=80&w=600',
                'extra_images': [
                    'https://images.unsplash.com/photo-1598550476439-6847785fce6e?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1684369175833-3d0774697bd9?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1505797149-43b0069ec26b?auto=format&fit=crop&q=80&w=600'
                ]
            },
            {
                'name': 'Stamina Esports Gaming Chair',
                'category': categories['Chair'],
                'brand': 'Stamina',
                'price': 179.99,
                'original_price': 199.99,
                'rating': 4.4,
                'reviews_count': 39,
                'stock': 10,
                'is_featured': False,
                'description': 'Keep cool under pressure. Designed with advanced, high-tension breathable mesh back, a dense memory-foam neck pillow, and robust lumbar support. Built to keep you supported and sweat-free during high-intensity gaming.',
                'specifications': 'Covering Material: High-Tension Mesh and durable synthetic leather\nGas Lift: Class 3 Hydraulic cylinder\nRecline Capacity: 90° to 135° recline\nBase Material: Durable Heavy-Duty Nylon Star-base\nWeight Support: Supports up to 260 lbs (120 kg)\nLumbar Support: Integrated adjustable lumbar pad',
                'image_url': 'https://images.unsplash.com/photo-1684369175833-3d0774697bd9?auto=format&fit=crop&q=80&w=600',
                'extra_images': [
                    'https://images.unsplash.com/photo-1684369175833-3d0774697bd9?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1598550476439-6847785fce6e?auto=format&fit=crop&q=80&w=600',
                    'https://images.unsplash.com/photo-1505797149-43b0069ec26b?auto=format&fit=crop&q=80&w=600'
                ]
            }
        ]

        for p_data in products_data:
            extra_imgs = p_data.pop('extra_images')
            prod = Product.objects.create(**p_data)
            for img_url in extra_imgs:
                ProductImage.objects.create(product=prod, image_url=img_url)

        self.stdout.write('Seeding coupons...')
        Coupon.objects.create(code='NEXUS10', discount_percent=10, active=True)
        Coupon.objects.create(code='NEXUS20', discount_percent=20, active=True)

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with 6 categories, 12 products, and 2 coupons!'))
