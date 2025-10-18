import { Injectable, computed, signal } from '@angular/core';

export interface Product {
  id: string;
  name: string;
  price: number;
  description?: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  // Simulación de sesión
  private _user = signal<null | { id: string; name: string }>(null);
  user = this._user;
  isLogged = computed(() => !!this._user());

  // Carrito en memoria
  private _cart = signal<Product[]>([]);
  cart = this._cart;

  // Buscador compartido entre header y tienda
  search = signal('');

  login(name = 'Usuario') {
    // Simulación de autenticación
    this._user.set({ id: 'u_1', name });
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
