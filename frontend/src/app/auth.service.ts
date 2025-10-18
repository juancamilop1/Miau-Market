import { Injectable, computed, signal } from '@angular/core';

export interface Product {
  id: string;
  name: string;
  price: number;
  description?: string;
}

export interface User {
  id: number;
  name: string;
  email: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  // Sesión del usuario autenticado
  private _user = signal<null | User>(null);
  user = this._user;
  isLogged = computed(() => !!this._user());

  // Carrito en memoria
  private _cart = signal<Product[]>([]);
  cart = this._cart;

  // Buscador compartido entre header y tienda
  search = signal('');

  // Método actualizado para recibir datos del backend
  login(userData: User) {
    this._user.set(userData);
  }

  logout() {
    this._user.set(null);
    this._cart.set([]);
  }

  addToCart(product: Product) {
    const current = this._cart();
    this._cart.set([...current, product]);
  }

  removeFromCart(productId: string) {
    this._cart.set(this._cart().filter(p => p.id !== productId));
  }

  clearCart() {
    this._cart.set([]);
  }
}
