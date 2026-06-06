# Baagicha — Production eCommerce Implementation Plan

> **Date:** 2026-05-12
> **Status:** Phase 1 Complete — Authentication & Core Infrastructure ✅ | App is fully browsable without login
> **Backend:** `web_baagicha/` (Laravel 12)
> **Frontend:** `baagichaApp/` (React Native 0.85.3)

---

## Architecture Rule
All APIs live in Laravel. React Native is the pure frontend client. No backend logic in the mobile app.

---

## Phase 1: Foundation (Auth + Core Infrastructure) — CURRENT

### Backend Tasks
- [ ] Install & configure Laravel Sanctum for API token auth
- [ ] Create `AuthController` with register, login, logout, profile, refresh endpoints
- [ ] Configure CORS for mobile app access
- [ ] Update `User` model for API tokens (`HasApiTokens` trait)
- [ ] Create `PhoneVerification` model + OTP flow (optional but recommended for farmers)
- [ ] Seed product catalog migrations (products, categories, variants, attributes)
- [ ] Build `ProductController` (list, detail, filters, search)
- [ ] Build `CategoryController` (tree structure for agricultural inputs)

### Frontend Tasks
- [ ] Install Zustand + MMKV (fast encrypted storage)
- [ ] Create `authStore.ts` (login, register, logout, token persistence, user profile)
- [ ] Update `api.ts` with auth interceptor (attach Bearer token from MMKV)
- [ ] Build `LoginScreen.tsx` (phone/email + password, bilingual)
- [ ] Build `RegisterScreen.tsx` (name, phone, email, password, orchard location)
- [ ] Build `AuthStack.tsx` navigation (Login → Register)
- [ ] Update `AppNavigator.tsx` to conditionally show AuthStack or MainTabs
- [ ] Add auth gate to existing screens (redirect to login on 401)
- [ ] Build `ProductListScreen.tsx` (grid, filters, categories)
- [ ] Build `ProductDetailScreen.tsx` (gallery, price, variants, reviews, add to cart)

---

## Phase 2: Cart & Checkout Engine

### Backend
- [ ] `Cart` + `CartItem` models + migration
- [ ] `CartController` (add, update quantity, remove, get, merge on login)
- [ ] `Address` model + `AddressController` (CRUD shipping/billing)
- [ ] `Coupon` model + validation logic
- [ ] `Order` + `OrderItem` models + migration
- [ ] `OrderController` (create from cart, calculate totals)
- [ ] `InventoryService` (stock reservation on checkout, release on expiry)
- [ ] `PricingService` (subtotal, tax, discount, shipping, total)

### Frontend
- [ ] `cartStore.ts` (local + server sync)
- [ ] `CartScreen.tsx` (items, quantities, swipe delete, coupon input)
- [ ] Cart badge on Shop tab
- [ ] `AddressListScreen.tsx` + `AddAddressScreen.tsx`
- [ ] `CheckoutScreen.tsx` (address → order review → payment trigger)
- [ ] Coupon input with validation

---

## Phase 3: Payments & Order Management

### Backend
- [ ] Razorpay integration (`razorpay/razorpay` PHP SDK)
- [ ] `PaymentController` (create order, verify signature, webhook)
- [ ] `Payment` model + migration
- [ ] Order status lifecycle (pending → paid → processing → shipped → delivered → cancelled)
- [ ] `OrderStatusLog` model (audit trail)
- [ ] Order notification system (email + push via FCM)
- [ ] Admin order dashboard (Blade)

### Frontend
- [ ] Install `react-native-razorpay`
- [ ] Razorpay checkout integration
- [ ] `OrderSuccessScreen.tsx` / `OrderFailedScreen.tsx`
- [ ] `OrderListScreen.tsx` (tabs: All / Pending / Shipped / Delivered)
- [ ] `OrderDetailScreen.tsx` (timeline, tracking, reorder)
- [ ] Push notification handler for order updates

---

## Phase 4: Wishlist, Reviews & Search

### Backend
- [ ] `Wishlist` model + `WishlistController`
- [ ] `ProductReview` model + `ReviewController`
- [ ] Laravel Scout + MySQL full-text search setup
- [ ] Product recommendation engine (related by category, viewed together)

### Frontend
- [ ] `WishlistScreen.tsx`
- [ ] Heart icon on ProductCard + ProductDetail
- [ ] Review submission (star rating, title, body, photo upload)
- [ ] `ReviewCard.tsx` component
- [ ] Product search with suggestions
- [ ] Related products carousel

---

## Phase 5: Admin & Operations

### Backend
- [ ] Admin CRUD for Products, Categories, Coupons
- [ ] Inventory management (stock alerts, low stock reports)
- [ ] Order fulfillment workflow (print labels, update tracking)
- [ ] Sales analytics dashboard (revenue, top products, trends)
- [ ] Refund/return handling

### Frontend
- [ ] Profile screen expansion (addresses, orders, wishlist, reviews)
- [ ] Settings (notifications, language, logout, delete account)
- [ ] Deep linking for order sharing

---

## Core Database Schema

```sql
-- Products
products (id, category_id, name, name_hi, slug, sku, description, description_hi,
  price, compare_price, cost_price, stock_quantity, track_inventory, weight_g,
  status ENUM('active','draft','out_of_stock'), featured, avg_rating, review_count,
  meta_title, meta_description, created_at, updated_at, deleted_at)

product_categories (id, parent_id, name, name_hi, slug, description, image,
  sort_order, is_active, created_at, updated_at)

product_variants (id, product_id, sku, price, stock_quantity, weight_g,
  attribute_values JSON, created_at, updated_at)

product_attributes (id, name, name_hi, sort_order, created_at, updated_at)
product_attribute_values (id, attribute_id, value, value_hi, created_at, updated_at)

-- Cart
carts (id, user_id, session_id, coupon_code, subtotal, discount, shipping, tax, total,
  created_at, updated_at)
cart_items (id, cart_id, product_id, variant_id, quantity, unit_price, total_price,
  created_at, updated_at)

-- Orders
orders (id, user_id, order_number, status, payment_status, payment_method,
  shipping_address JSON, billing_address JSON, subtotal, tax, discount, shipping, total,
  notes, tracking_number, shipped_at, delivered_at, created_at, updated_at)

order_items (id, order_id, product_id, variant_id, product_name, product_sku,
  quantity, unit_price, total_price, created_at)

order_status_logs (id, order_id, status, note, created_by, created_at)

-- Addresses
addresses (id, user_id, type ENUM('shipping','billing'), label, name, phone,
  address_line_1, address_line_2, city, state, pincode, landmark, is_default,
  created_at, updated_at)

-- Payments
payments (id, order_id, gateway, transaction_id, amount, currency, status,
  payload JSON, paid_at, created_at, updated_at)

-- Reviews
product_reviews (id, product_id, user_id, order_id, rating, title, body,
  is_verified_purchase, helpful_count, is_approved, created_at, updated_at)

-- Wishlist
wishlists (id, user_id, product_id, created_at)

-- Coupons
coupons (id, code, type ENUM('fixed','percentage'), value, min_order_amount,
  max_discount, usage_limit, usage_count, valid_from, valid_until, is_active,
  created_at, updated_at)

-- Phone Verification (for OTP)
phone_verifications (id, phone, otp, expires_at, verified_at, created_at)
```

---

## Technology Stack Decisions

| Layer | Choice | Reason |
|-------|--------|--------|
| API Auth | Laravel Sanctum | Best for React Native, simple tokens |
| Mobile Storage | MMKV | Encrypted, synchronous, ~10x faster than AsyncStorage |
| State Management | Zustand | Minimal boilerplate, TypeScript-friendly, persists with MMKV |
| Payments | Razorpay | India-native, UPI support, strong RN SDK |
| Search | Laravel Scout + MySQL | Start with MySQL full-text, upgrade to Meilisearch if needed |
| Images | Spatie Media Library | Already installed, handles conversions & responsive images |
| Notifications | Firebase Cloud Messaging | Free, reliable for order status push |

---

## API Endpoints (Mobile API)

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
GET    /api/v1/auth/profile
PUT    /api/v1/auth/profile

GET    /api/v1/products
GET    /api/v1/products/{slug}
GET    /api/v1/categories
GET    /api/v1/categories/{slug}/products
GET    /api/v1/products/search?q={query}

GET    /api/v1/cart
POST   /api/v1/cart/items
PUT    /api/v1/cart/items/{id}
DELETE /api/v1/cart/items/{id}
POST   /api/v1/cart/merge

GET    /api/v1/addresses
POST   /api/v1/addresses
PUT    /api/v1/addresses/{id}
DELETE /api/v1/addresses/{id}
POST   /api/v1/addresses/{id}/default

POST   /api/v1/orders              (create from cart)
GET    /api/v1/orders
GET    /api/v1/orders/{id}
POST   /api/v1/orders/{id}/cancel

POST   /api/v1/payments/razorpay/order
POST   /api/v1/payments/razorpay/verify

GET    /api/v1/wishlist
POST   /api/v1/wishlist
DELETE /api/v1/wishlist/{product_id}

GET    /api/v1/products/{slug}/reviews
POST   /api/v1/products/{slug}/reviews
POST   /api/v1/reviews/{id}/helpful

POST   /api/v1/coupons/validate
```

---

## Product Categories (Agricultural Inputs for Himalayan Apple Belt)

1. **Fertilizers & Nutrients** (organic, NPK, micronutrients, foliar feeds)
2. **Pesticides & Fungicides** (insecticides, fungicides, herbicides, organic options)
3. **Growth Regulators & Hormones** (rooting powder, fruit setting sprays)
4. **Tools & Equipment** (pruning shears, sprayers, grafting tools, harvesting bags)
5. **Grafting Material** (rootstocks, scion wood, grafting tape)
6. **Protective Gear** (gloves, masks, goggles, aprons)
7. **Irrigation** (drip lines, emitters, filters)
8. **Soil & Mulch** (coco peat, vermicompost, mulch sheets)

---

## Notes
- All prices in INR (₹)
- Bilingual support (English + Hindi) for all product names and descriptions
- Offline-first cart: store cart items locally, sync when online
- Target regions: HP, Uttarakhand, J&K (Himalayan apple belt)
