import { Routes } from '@angular/router';
import { Login } from './app/login/login';
import { Register } from './app/register/register';
import { Shop } from './app/shop/shop';
import { Cart } from './app/cart/cart';
import { Admin } from './app/admin/admin';
import { Checkout } from './app/checkout/checkout';
import { MyOrders } from './app/my-orders/my-orders';

export const routes: Routes = [
	{ path: '', pathMatch: 'full', redirectTo: 'shop' },
	{ path: 'shop', component: Shop, title: 'MiauMarket | Tienda' },
	{ path: 'cart', component: Cart, title: 'MiauMarket | Carrito' },
	{ path: 'checkout', component: Checkout, title: 'MiauMarket | Confirmar Pedido' },
	{ path: 'my-orders', component: MyOrders, title: 'MiauMarket | Mis Pedidos' },
	{ path: 'admin', component: Admin, title: 'MiauMarket | Administración' },
	{ path: 'login', component: Login, title: 'MiauMarket | Iniciar sesión' },
	{ path: 'register', component: Register, title: 'MiauMarket | Crear cuenta' },
	{ path: '**', redirectTo: 'shop' },
];
