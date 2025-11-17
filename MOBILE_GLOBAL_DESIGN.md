# 📱 Diseño Mobile-First Global - MiauMarket

## 🎯 Resumen Ejecutivo

MiauMarket ha sido completamente rediseñado con un enfoque **mobile-first** para toda la aplicación. Este documento describe la implementación completa del diseño responsive optimizado para dispositivos móviles, tablets y desktop.

### 🌐 Alcance Global

- ✅ **Header Principal**: Menú hamburguesa, navegación optimizada
- ✅ **Todas las Páginas**: Shop, Cart, Checkout, Login, Register, Profile, My Orders
- ✅ **Panel Administrativo**: Gestión completa mobile-first
- ✅ **Componentes Globales**: Botones, formularios, cards, modales

## 📐 Sistema de Breakpoints

```css
/* Mobile First Approach */
Base (0px)       → Estilos móviles por defecto
600px  (tablet)  → Grid 2 columnas, espaciado medio
768px  (tablet)  → Ocultar desktop, mostrar mobile menu
1024px (desktop) → Layout sidebar, grid 3+ columnas
1200px (large)   → Grid 4 columnas, max-width containers
```

## 🎨 Header Principal - Navegación Global

### Mobile Header (≤768px)

**Estructura:**
```
[☰ Menu] [Logo] [🛒 Carrito] [🔔 Notificaciones]
```

**Características:**
- **Altura**: 64px (var(--header-h))
- **Sticky**: Siempre visible al hacer scroll
- **Hamburger Menu**: Slide-in desde la izquierda (280px)
- **Cart Badge**: Contador de productos visible
- **Notifications Bell**: Campana de notificaciones integrada

**Implementación:**
```html
<!-- app.html -->
<div class="mobile-header" *ngIf="isMobile() && auth.isLogged()">
  <button class="mobile-menu-btn" (click)="toggleMobileMenu()">
    <span class="hamburger-icon">☰</span>
  </button>
  <div class="brand">
    <img src="/miauMarket.png" alt="Logo" class="brand-logo" />
  </div>
  <div class="mobile-header-actions">
    <a class="cart-link-mobile" routerLink="/cart">
      🛒
      <span class="cart-badge-mobile" *ngIf="auth.cartCount() > 0">
        {{ auth.cartCount() }}
      </span>
    </a>
    <app-notifications-bell></app-notifications-bell>
  </div>
</div>
```

### Mobile Menu Overlay

**Características:**
- **Width**: 280px (max 85vw)
- **Animation**: slideInLeft 0.3s ease
- **Backdrop**: rgba(0,0,0,0.5) con blur
- **Contenido**:
  1. User Info Card (avatar, nombre, email)
  2. Navigation Items (iconos + texto)
  3. Theme Toggle
  4. Logout Button

**Secciones del menú:**
```
┌─────────────────────────┐
│ Menú              [✕]   │ ← Header
├─────────────────────────┤
│ [AA] Usuario Name       │ ← User Info
│      user@email.com     │
├─────────────────────────┤
│ 🏪 Tienda              │
│ 🛒 Carrito        [3]  │ ← Badge contador
│ 📦 Mis Pedidos         │
│ 👤 Mi Perfil           │
│ ⚙️ Administración      │ ← Solo admins
├─────────────────────────┤
│ 🌓 Cambiar Tema        │
│ 🚪 Cerrar Sesión       │ ← Logout
└─────────────────────────┘
```

### Desktop Header (>768px)

**Estructura clásica:**
```
[Logo] [Usuario] [Cerrar Sesión] | [Búsqueda] | [Tienda] [Pedidos] [Carrito] [🔔] [Admin] [🌓]
```

## 🛍️ Página Shop - Tienda

### Mobile Optimizations

**Hero Section:**
```css
/* Mobile */
padding: 1rem;
text-align: center;
h1: 1.5rem
p: 0.9rem
```

**Search Bar Móvil:**
- **Display**: Solo visible en móvil (hidden en desktop)
- **Font-size**: 16px (evita zoom en iOS)
- **Padding**: 12px 16px
- **Border-radius**: 24px (pill shape)
- **Focus**: Orange border + shadow

**Product Grid:**
```css
/* Mobile (default) */
grid-template-columns: 1fr;

/* Tablet (≥600px) */
grid-template-columns: repeat(2, 1fr);

/* Desktop (≥1024px) */
grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
```

**Product Cards:**
- **Min-height**: 360px
- **Image height**: 200px (mobile), 250px (desktop)
- **Actions**: 
  - Mobile: Stacked vertical, full-width buttons
  - Desktop: Horizontal flex, 2 buttons side-by-side

**Touch Targets:**
- Botones: **min 44px height** (48px en mobile)
- Gap entre botones: 8px (6px en mobile stacked)

## 🛒 Página Cart - Carrito

### Mobile Layout

**Hero:**
```css
padding: 1rem;
border-radius: 8px;
```

**Cart Items:**
```css
/* Desktop Grid */
grid-template-columns: 40px 100px 1fr auto auto;

/* Mobile Grid (≤768px) */
grid-template-columns: 40px 1fr;
grid-template-rows: auto auto auto auto;

Layout:
Row 1: [✓] [Image spanning full width]
Row 2: [Info spanning full width]
Row 3: [Quantity controls centered]
Row 4: [Subtotal] [🗑️ Delete]
```

**Summary Box:**
- **Desktop**: Sticky right sidebar (top: 20px)
- **Mobile**: Sticky bottom (border-radius: 12px 12px 0 0)
- **Shadow**: Elevado en mobile para destacar
- **Z-index**: 10 (sobre contenido)

**Responsive Behavior:**
```css
/* Mobile stacked */
@media (max-width: 1023px) {
  .cart-content {
    grid-template-columns: 1fr;
  }
  
  .cart-summary-box {
    position: sticky;
    bottom: 0;
    box-shadow: 0 -4px 12px rgba(0,0,0,0.1);
  }
}
```

## 📝 Formularios - Login/Register

### Mobile Optimizations

**Auth Card:**
```css
/* Mobile */
width: 100%;
padding: 1.5rem;
margin: 0;

/* Logo */
width: 56px;
height: 56px;
```

**Input Fields:**
```css
font-size: 16px;        /* Prevent iOS zoom */
padding: 10px 12px;
min-height: 44px;       /* Touch target */
border-radius: 12px;
```

**Buttons:**
```css
width: 100%;            /* Full width on mobile */
min-height: 44px;
padding: 12px 16px;
font-size: 1rem;
```

**Form Layout:**
```css
.form {
  display: grid;
  gap: 14px;
  width: 100%;
}

/* Mobile */
.field {
  width: 100%;
}
```

## ⚙️ Panel Administrativo

### Mobile Features

Ver [ADMIN_FEATURES.md](./ADMIN_FEATURES.md) y [MOBILE_DESIGN.md](./MOBILE_DESIGN.md) para detalles completos del panel administrativo móvil.

**Resumen:**
- Hamburger menu navigation
- FAB (Floating Action Buttons)
- Card/Table view toggle
- Bulk actions modal
- Export functionality
- Touch-optimized controls (44x44px minimum)

## 🎨 Componentes Globales Mobile-First

### 1. Buttons

```css
.btn {
  min-height: 44px;        /* Touch target */
  padding: 10px 14px;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.2s ease;
}

/* Mobile */
@media (max-width: 768px) {
  .btn {
    width: 100%;
    justify-content: center;
    min-height: 48px;      /* Larger on mobile */
  }
}
```

### 2. Input Fields

```css
.input {
  width: 100%;
  padding: 12px 14px;
  font-size: 16px;         /* iOS zoom prevention */
  border: 1px solid var(--border);
  border-radius: 12px;
  min-height: 44px;
}

.input:focus {
  border-color: var(--mm-orange);
  box-shadow: 0 0 0 3px rgba(255,122,0,0.25);
}
```

### 3. Cards

```css
.card {
  background: var(--mm-white);
  border-radius: 12px;
  box-shadow: var(--shadow-2);
  padding: 20px;
}

/* Mobile */
@media (max-width: 768px) {
  .card {
    padding: 16px;
    border-radius: 8px;
  }
}
```

### 4. Modals

```css
.modal-overlay {
  padding: 20px;
}

.modal-content {
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
}

/* Mobile */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 10px;
  }
  
  .modal-content {
    max-height: 95vh;
  }
  
  .modal-body {
    grid-template-columns: 1fr; /* Stacked layout */
    padding: 20px;
  }
}
```

## 📱 Touch Target Guidelines

### Minimum Sizes (iOS/Android Guidelines)

```css
/* Buttons, Links, Interactive Elements */
min-width: 44px;
min-height: 44px;

/* Mobile Preference */
min-height: 48px;  /* Google Material Design */

/* Small buttons (icons only) */
min-width: 40px;
min-height: 40px;
padding: 8px;
```

### Spacing

```css
/* Gap between touch targets */
gap: 8px;          /* Minimum */
gap: 12px;         /* Recommended */

/* Mobile cards/items */
gap: 16px;
```

## 🎯 Performance Optimizations

### CSS Animations

```css
/* Use transform instead of position */
/* GOOD ✅ */
@keyframes slideIn {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

/* AVOID ❌ */
@keyframes slideIn {
  from { left: -280px; }
  to { left: 0; }
}
```

### Will-change Property

```css
/* For frequently animated elements */
.mobile-menu {
  will-change: transform;
}

.cart-badge {
  will-change: contents;
}
```

### Font Loading

```css
/* iOS zoom prevention */
input, textarea, select {
  font-size: 16px;  /* Minimum to prevent zoom */
}
```

## 🌓 Dark Mode Support

### Mobile-Specific Dark Mode

```css
@media (prefers-color-scheme: dark) {
  .mobile-header {
    background: var(--mm-white);  /* Auto-adapts */
    border-bottom: 1px solid var(--border);
  }
  
  .mobile-menu {
    background: var(--mm-white);
  }
  
  .search-input-mobile {
    background: var(--mm-white);
    color: var(--mm-black);
    border-color: var(--border);
  }
}
```

## 🧪 Testing Recommendations

### Mobile Devices

**iOS:**
- iPhone SE (375px) - Smallest modern iPhone
- iPhone 12/13 (390px) - Standard size
- iPhone 14 Pro Max (428px) - Largest

**Android:**
- Samsung Galaxy S21 (360px)
- Pixel 5 (393px)
- OnePlus (412px)

### Tablets

- iPad Mini (744px × 1133px)
- iPad Air (820px × 1180px)
- iPad Pro 11" (834px × 1194px)
- iPad Pro 12.9" (1024px × 1366px)

### Chrome DevTools

```
1. F12 → Toggle Device Toolbar
2. Test responsive breakpoints: 375px, 768px, 1024px
3. Throttle to "Slow 3G" for performance testing
4. Test touch events (not just hover)
```

### Real Device Testing

```bash
# Serve on local network
ng serve --host 0.0.0.0

# Access from mobile device
http://192.168.x.x:4200
```

## 📚 CSS Classes Reference

### Visibility Utilities

```css
.mobile-only {
  display: block;
}

@media (min-width: 769px) {
  .mobile-only {
    display: none !important;
  }
}

.desktop-only {
  display: none;
}

@media (min-width: 769px) {
  .desktop-only {
    display: flex;
  }
}
```

### Mobile Header Classes

```css
.mobile-header          /* Main mobile header container */
.mobile-menu-btn        /* Hamburger button */
.hamburger-icon         /* ☰ icon */
.mobile-header-actions  /* Right side actions */
.cart-link-mobile       /* Mobile cart link */
.cart-badge-mobile      /* Cart counter badge */
```

### Mobile Menu Classes

```css
.mobile-menu-overlay    /* Backdrop overlay */
.mobile-menu            /* Slide-in menu container */
.mobile-menu-header     /* Menu header with title + close */
.close-btn              /* ✕ close button */
.mobile-user-info       /* User info card */
.user-avatar            /* Circular avatar */
.user-details           /* Name + email */
.mobile-menu-items      /* Navigation items container */
.mobile-menu-item       /* Individual menu item */
.item-icon              /* Icon (emoji/svg) */
.item-text              /* Text label */
.item-badge             /* Counter badge */
.mobile-menu-divider    /* Separator line */
```

## 🚀 Future Enhancements

### Planned Features

1. **Bottom Navigation Bar**
   - Fixed bottom navigation (Home, Shop, Cart, Profile)
   - Active state indicators
   - Badge counters

2. **Pull-to-Refresh**
   - Native-like pull gesture
   - Refresh product lists
   - Sync user data

3. **Swipe Gestures**
   - Swipe to delete cart items
   - Swipe between product categories
   - Gesture-based navigation

4. **PWA Features**
   - Add to Home Screen
   - Offline mode
   - Push notifications
   - Service worker caching

5. **Advanced Touch**
   - Long-press menus
   - Double-tap actions
   - Pinch-to-zoom in product images

## 🎓 Best Practices Summary

### ✅ DO

- Start with mobile styles, add desktop enhancements
- Use 16px minimum font-size for inputs (prevent iOS zoom)
- Ensure 44px minimum touch targets (48px recommended)
- Test on real devices, not just DevTools
- Use transform for animations (not left/top)
- Implement sticky elements for key UI (header, cart summary)
- Provide visual feedback for all touch interactions
- Optimize images for mobile bandwidth

### ❌ DON'T

- Don't use hover-only interactions (no mobile hover)
- Don't make touch targets smaller than 40px
- Don't use fixed pixel widths (use %, rem, vw)
- Don't forget focus states for accessibility
- Don't rely solely on desktop testing
- Don't use tiny font sizes (<14px for body text)
- Don't forget landscape orientation
- Don't assume fast internet (optimize assets)

## 📞 Support & Documentation

### Related Documentation

- [MOBILE_DESIGN.md](./MOBILE_DESIGN.md) - Panel administrativo móvil
- [ADMIN_FEATURES.md](./ADMIN_FEATURES.md) - Features del admin panel
- [INTEGRATION.md](./frontend/INTEGRATION.md) - Integración frontend/backend
- [README.md](./frontend/README.md) - Setup y desarrollo

### Component Files

```
frontend/src/
├── app/
│   ├── app.html                    # Header global + mobile menu
│   ├── app.css                     # Estilos de header móvil
│   ├── app.ts                      # Lógica mobile menu
│   ├── app/
│   │   ├── shop/
│   │   │   ├── shop.html           # Shop mobile-optimized
│   │   │   └── shop.css            # Grid responsive + search
│   │   ├── cart/
│   │   │   ├── cart.html           # Cart mobile layout
│   │   │   └── cart.css            # Sticky summary mobile
│   │   ├── admin/
│   │   │   ├── admin.html          # Panel admin mobile
│   │   │   └── admin.css           # Mobile-first admin
│   └── styles.css                  # Global mobile styles
```

### Variables CSS Globales

```css
:root {
  --mm-orange: #FF7A00;
  --mm-black: #0f0f10;
  --mm-white: #ffffff;
  --mm-gray-100: #f5f5f6;
  --mm-gray-400: #b7bcc0;
  --mm-gray-700: #3b3f44;
  --header-h: 64px;
  --radius: 12px;
  --border: #e6e8ea;
  --shadow-1: 0 6px 18px rgba(14,14,14,0.06);
  --shadow-2: 0 8px 24px rgba(14,14,14,0.08);
}
```

---

**Última actualización**: Noviembre 2025  
**Versión**: 2.0 - Mobile-First Global Implementation  
**Autor**: MiauMarket Development Team 🐱
