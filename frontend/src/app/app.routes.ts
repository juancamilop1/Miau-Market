import { Routes } from '@angular/router';
import { Login } from './app/login/login';
import { Register } from './app/register/register';
import { Shop } from './app/shop/shop';
import { Cart } from './app/cart/cart';
import { Admin } from './app/admin/admin';
import { Checkout } from './app/checkout/checkout';
import { MyOrders } from './app/my-orders/my-orders';
import { Profile } from './app/profile/profile';
import { Dashboard } from './app/dashboard/dashboard';
import { ProductDetail } from './app/product-detail/product-detail';
import { Wishlist } from './app/wishlist/wishlist';
import { authGuard } from './guards/auth.guard';
import { adminGuard } from './guards/admin.guard';

export const routes: Routes = [
	{ path: '', pathMatch: 'full', redirectTo: 'shop' },
	{ path: 'shop', component: Shop, title: 'MiauMarket | Tienda' },
	{ path: 'product/:id', component: ProductDetail, title: 'MiauMarket | Producto' },
	{ path: 'cart', component: Cart, canActivate: [authGuard], title: 'MiauMarket | Carrito' },
	{ path: 'checkout', component: Checkout, canActivate: [authGuard], title: 'MiauMarket | Confirmar Pedido' },
	{ path: 'my-orders', component: MyOrders, canActivate: [authGuard], title: 'MiauMarket | Mis Pedidos' },
	{ path: 'profile', component: Profile, canActivate: [authGuard], title: 'MiauMarket | Mi Perfil' },
	{ path: 'wishlist', component: Wishlist, canActivate: [authGuard], title: 'MiauMarket | Favoritos' },
	{ path: 'admin', component: Admin, canActivate: [adminGuard], title: 'MiauMarket | Administración' },
	{ path: 'dashboard', component: Dashboard, canActivate: [adminGuard], title: 'MiauMarket | Dashboard' },
	{ path: 'login', component: Login, title: 'MiauMarket | Iniciar sesión' },
	{ path: 'register', component: Register, title: 'MiauMarket | Crear cuenta' },
	{ path: '**', redirectTo: 'shop' },
];
