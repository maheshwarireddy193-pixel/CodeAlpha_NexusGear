/* ==========================================================================
   NEXUSGEAR CLIENT SIDE CONTROLLER
   Vanilla JavaScript for complete interactive UX
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize core handlers
    initCartDrawer();
    initLiveSearch();
    initWishlistToggle();
    initBackToTop();
    initMobileHamburger();
    initProductDetailGallery();
    initProductDetailTabs();
    initCheckoutFlow();
    initCustomConfirm();
});

// ==========================================================================
// TOAST NOTIFICATIONS ENGINE
// ==========================================================================
window.showToast = function(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let iconClass = 'fa-info-circle';
    if (type === 'success') iconClass = 'fa-check-circle';
    if (type === 'error') iconClass = 'fa-exclamation-circle';

    toast.innerHTML = `
        <i class="fas ${iconClass} toast-icon"></i>
        <div class="toast-content">${message}</div>
        <i class="fas fa-times toast-close"></i>
    `;

    container.appendChild(toast);

    // Bind close click
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.style.animation = 'fadeOut 0.3s ease-out forwards';
        setTimeout(() => toast.remove(), 300);
    });

    // Auto dismiss after 4s
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = 'fadeOut 0.3s ease-out forwards';
            setTimeout(() => toast.remove(), 300);
        }
    }, 4000);
};

// ==========================================================================
// SLIDE-OUT CART DRAWER & ASYNC ADD-TO-CART
// ==========================================================================
function initCartDrawer() {
    const overlay = document.querySelector('.cart-drawer-overlay');
    const drawer = document.querySelector('.cart-drawer');
    const openBtns = document.querySelectorAll('.js-open-cart');
    const closeBtns = document.querySelectorAll('.js-close-cart');

    if (!overlay || !drawer) return;

    // Toggle Drawer Open
    openBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden'; // prevent scroll
        });
    });

    // Close Drawer
    closeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    });

    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });

    // Bind Async Add to Cart triggers
    document.body.addEventListener('click', async (e) => {
        const cartBtn = e.target.closest('.js-add-to-cart');
        if (!cartBtn) return;

        e.preventDefault();
        const productId = cartBtn.dataset.productId;
        const qtyInput = document.querySelector('.qty-input');
        const quantity = qtyInput ? parseInt(qtyInput.value) : 1;

        // Visual loading state on button
        const originalHTML = cartBtn.innerHTML;
        cartBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
        cartBtn.disabled = true;

        try {
            const response = await fetch(`/api/cart/add/?product_id=${productId}&qty=${quantity}`);
            const data = await response.json();

            if (data.success) {
                // Update badge quantities in navbar
                const badge = document.querySelector('.js-cart-badge');
                if (badge) {
                    badge.textContent = data.cart_count;
                    badge.style.display = data.cart_count > 0 ? 'flex' : 'none';
                }

                // Refresh Cart Drawer items list dynamically
                refreshDrawerItems(data.items, data.cart_subtotal);

                // Show success toast
                window.showToast(data.message, 'success');

                // Open Cart Drawer
                overlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            } else {
                // If user not authenticated, redirect to login
                if (response.status === 401 || response.url.includes('/login/')) {
                    window.location.href = `/login/?next=${window.location.pathname}`;
                } else {
                    window.showToast(data.message || 'Error adding to cart.', 'error');
                }
            }
        } catch (error) {
            console.error(error);
            window.showToast('Something went wrong. Please try again.', 'error');
        } finally {
            cartBtn.innerHTML = originalHTML;
            cartBtn.disabled = false;
        }
    });
}

function refreshDrawerItems(items, subtotal) {
    const listContainer = document.querySelector('.drawer-items-list');
    const subtotalVal = document.querySelector('.js-drawer-subtotal');
    const bodyContainer = document.querySelector('.cart-drawer-body');
    const footerContainer = document.querySelector('.cart-drawer-footer');

    if (!listContainer) return;

    if (items.length === 0) {
        bodyContainer.innerHTML = `
            <div class="drawer-empty-state">
                <i class="fas fa-shopping-bag drawer-empty-icon"></i>
                <p>Your shopping drawer is empty.</p>
            </div>
        `;
        if (footerContainer) footerContainer.style.display = 'none';
        return;
    }

    // Populate items
    let listHTML = '';
    items.forEach(item => {
        listHTML += `
            <div class="drawer-item">
                <img src="${item.image_url}" alt="${item.name}" class="drawer-item-img">
                <div class="drawer-item-info">
                    <h4 class="drawer-item-name">${item.name}</h4>
                    <p class="drawer-item-qty-price">${item.quantity} x <span>₹${item.price.toFixed(2)}</span></p>
                </div>
            </div>
        `;
    });

    listContainer.innerHTML = listHTML;
    if (subtotalVal) subtotalVal.textContent = `₹${subtotal.toFixed(2)}`;
}

// ==========================================================================
// NAVBAR LIVE SEARCH AUTO-COMPLETE
// ==========================================================================
function initLiveSearch() {
    const searchInput = document.querySelector('.js-search-input');
    const dropdown = document.querySelector('.js-search-dropdown');

    if (!searchInput || !dropdown) return;

    let debounceTimer;

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        clearTimeout(debounceTimer);
        if (query.length < 2) {
            dropdown.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(async () => {
            try {
                const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                if (data.products && data.products.length > 0) {
                    let resultsHTML = '';
                    data.products.forEach(p => {
                        resultsHTML += `
                            <a href="/product/${p.slug}/" class="search-dropdown-item">
                                <img src="${p.image_url}" alt="${p.name}" class="search-dropdown-img">
                                <div class="search-dropdown-info">
                                    <div class="search-dropdown-name">${p.name}</div>
                                    <div class="search-dropdown-price">₹${p.price.toFixed(2)}</div>
                                </div>
                            </a>
                        `;
                    });
                    dropdown.innerHTML = resultsHTML;
                    dropdown.style.display = 'block';
                } else {
                    dropdown.innerHTML = '<div style="padding: 15px 20px; color: rgba(255,255,255,0.5); font-size:14px;">No products found...</div>';
                    dropdown.style.display = 'block';
                }
            } catch (err) {
                console.error(err);
            }
        }, 300); // 300ms debounce
    });

    // Close search dropdown on click-away
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
}

// ==========================================================================
// WISHLIST TOGGLE (AJAX HANDLER)
// ==========================================================================
function initWishlistToggle() {
    document.body.addEventListener('click', async (e) => {
        const wishlistBtn = e.target.closest('.js-wishlist-toggle');
        if (!wishlistBtn) return;

        e.preventDefault();
        const productId = wishlistBtn.dataset.productId;

        try {
            const response = await fetch(`/api/wishlist/toggle/?product_id=${productId}`);
            const data = await response.json();

            if (data.success) {
                // Update badge count
                const badge = document.querySelector('.js-wishlist-badge');
                if (badge) {
                    badge.textContent = data.wishlist_count;
                    badge.style.display = data.wishlist_count > 0 ? 'flex' : 'none';
                }

                // Toggle heart visual state
                if (data.added) {
                    wishlistBtn.classList.add('wished');
                    wishlistBtn.innerHTML = '<i class="fas fa-heart" style="color:var(--color-danger)"></i>';
                    window.showToast(data.message, 'success');
                } else {
                    wishlistBtn.classList.remove('wished');
                    wishlistBtn.innerHTML = '<i class="far fa-heart"></i>';
                    window.showToast(data.message, 'success');
                    
                    // If on wishlist page, remove the card dynamically
                    const wishedCard = wishlistBtn.closest('.js-wishlist-card');
                    if (wishedCard) {
                        wishedCard.remove();
                        // Check if empty
                        const grid = document.querySelector('.js-wishlist-grid');
                        if (grid && grid.children.length === 0) {
                            window.location.reload();
                        }
                    }
                }
            } else {
                if (response.status === 401 || response.url.includes('/login/')) {
                    window.location.href = `/login/?next=${window.location.pathname}`;
                } else {
                    window.showToast(data.message || 'Error updating wishlist.', 'error');
                }
            }
        } catch (err) {
            console.error(err);
            window.showToast('Failed to toggle wishlist.', 'error');
        }
    });
}

// ==========================================================================
// BACK TO TOP UTILITY
// ==========================================================================
function initBackToTop() {
    const btn = document.querySelector('.js-back-to-top');
    if (!btn) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    btn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ==========================================================================
// MOBILE HAMBURGER MENU
// ==========================================================================
function initMobileHamburger() {
    const burger = document.querySelector('.js-mobile-hamburger');
    const menu = document.querySelector('.js-mobile-nav-menu');

    if (!burger || !menu) return;

    burger.addEventListener('click', () => {
        menu.classList.toggle('active');
        burger.classList.toggle('fa-bars');
        burger.classList.toggle('fa-times');
    });
}

// ==========================================================================
// GALLERY IMAGES & ZOOM ON HOVER
// ==========================================================================
function initProductDetailGallery() {
    const mainImg = document.querySelector('.js-gallery-main');
    const thumbs = document.querySelectorAll('.js-gallery-thumb');

    if (!mainImg || thumbs.length === 0) return;

    // Swap Image on Thumbnail click
    thumbs.forEach(thumb => {
        thumb.addEventListener('click', () => {
            thumbs.forEach(t => t.classList.remove('active'));
            thumb.classList.add('active');
            
            const targetSrc = thumb.dataset.largeImg;
            mainImg.src = targetSrc;
        });
    });

    // Zoom on Hover Physics
    const container = mainImg.parentElement;
    if (container) {
        container.addEventListener('mousemove', (e) => {
            const rect = container.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;

            mainImg.style.transformOrigin = `${x}% ${y}%`;
            mainImg.style.transform = 'scale(1.5)';
        });

        container.addEventListener('mouseleave', () => {
            mainImg.style.transform = 'scale(1)';
            mainImg.style.transformOrigin = 'center center';
        });
    }

    // Detail quantity selector hooks (+/-)
    const qtyInput = document.querySelector('.js-qty-input');
    const minusBtn = document.querySelector('.js-qty-minus');
    const plusBtn = document.querySelector('.js-qty-plus');

    if (qtyInput && minusBtn && plusBtn) {
        minusBtn.addEventListener('click', () => {
            let val = parseInt(qtyInput.value);
            if (val > 1) qtyInput.value = val - 1;
        });

        plusBtn.addEventListener('click', () => {
            let val = parseInt(qtyInput.value);
            qtyInput.value = val + 1;
        });
    }
}

// ==========================================================================
// TABS CALCULATOR
// ==========================================================================
function initProductDetailTabs() {
    const tabs = document.querySelectorAll('.js-tab-btn');
    const panes = document.querySelectorAll('.js-tab-pane');

    if (tabs.length === 0) return;

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            panes.forEach(p => p.classList.remove('active'));

            tab.classList.add('active');
            const paneId = tab.dataset.pane;
            const targetPane = document.getElementById(paneId);
            if (targetPane) targetPane.classList.add('active');
        });
    });
}

// ==========================================================================
// CHECKOUT & MOCK PAYMENT FORMS
// ==========================================================================
function initCheckoutFlow() {
    // 1. Saved Address Selection populate fields
    const addrSelect = document.querySelector('.js-address-select');
    const newAddrFields = document.querySelector('.js-new-address-fields');

    if (addrSelect && newAddrFields) {
        addrSelect.addEventListener('change', (e) => {
            if (e.target.value === 'new' || e.target.value === '') {
                newAddrFields.style.display = 'block';
                // Make new address inputs required
                toggleInputsRequired(newAddrFields, true);
            } else {
                newAddrFields.style.display = 'none';
                toggleInputsRequired(newAddrFields, false);
            }
        });
        
        // Initial setup trigger
        if (addrSelect.value !== 'new' && addrSelect.value !== '') {
            newAddrFields.style.display = 'none';
            toggleInputsRequired(newAddrFields, false);
        }
    }

    // 2. Payment Selector
    const payOptions = document.querySelectorAll('.js-payment-option');
    const cardForm = document.querySelector('.js-payment-card-form');
    const upiForm = document.querySelector('.js-payment-upi-form');

    if (payOptions.length > 0) {
        payOptions.forEach(card => {
            card.addEventListener('click', () => {
                payOptions.forEach(c => c.classList.remove('active'));
                card.classList.add('active');

                // Radio Sync
                const radio = card.querySelector('input[type="radio"]');
                if (radio) radio.checked = true;

                const method = radio.value;
                if (cardForm) cardForm.style.display = method === 'Card' ? 'block' : 'none';
                if (upiForm) upiForm.style.display = method === 'UPI' ? 'block' : 'none';
                
                // Toggle input required markers
                if (cardForm) toggleInputsRequired(cardForm, method === 'Card');
                if (upiForm) toggleInputsRequired(upiForm, method === 'UPI');
            });
        });
    }
}

function toggleInputsRequired(container, isRequired) {
    const inputs = container.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        if (isRequired) {
            input.setAttribute('required', '');
        } else {
            input.removeAttribute('required');
        }
    });
}

// ==========================================================================
// GLASSMORPHISM CUSTOM CONFIRM OVERLAY DIALOGS
// ==========================================================================
let confirmResolve = null;

function initCustomConfirm() {
    const overlay = document.querySelector('.confirm-overlay');
    const okBtn = document.querySelector('.js-confirm-ok');
    const cancelBtn = document.querySelector('.js-confirm-cancel');

    if (!overlay || !okBtn || !cancelBtn) return;

    okBtn.addEventListener('click', () => {
        overlay.classList.remove('active');
        if (confirmResolve) confirmResolve(true);
    });

    cancelBtn.addEventListener('click', () => {
        overlay.classList.remove('active');
        if (confirmResolve) confirmResolve(false);
    });
}

window.customConfirm = function(title, description) {
    const overlay = document.querySelector('.confirm-overlay');
    const titleEl = document.querySelector('.confirm-title');
    const descEl = document.querySelector('.confirm-desc');

    if (!overlay) {
        // Fallback to browser confirm if dialog HTML is missing
        return Promise.resolve(window.confirm(description));
    }

    titleEl.textContent = title;
    descEl.textContent = description;
    overlay.classList.add('active');

    return new Promise((resolve) => {
        confirmResolve = resolve;
    });
};
