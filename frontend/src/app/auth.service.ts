import { Injectable, computed, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { PLATFORM_ID, inject } from '@angular/core';

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
  is_staff?: boolean;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private platformId = inject(PLATFORM_ID);

  // Sesión del usuario autenticado
  private _user = signal<null | User>(null);
  user = this._user;
  isLogged = computed(() => !!this._user());

  // Carrito en memoria
  private _cart = signal<Product[]>([]);
  cart = this._cart;

  // Buscador compartido entre header y tienda
  search = signal('');

  constructor() {
    // Cargar usuario del localStorage si existe (solo en navegador)
    if (isPlatformBrowser(this.platformId)) {
      const savedUser = localStorage.getItem('user');
      if (savedUser) {
        try {
          this._user.set(JSON.parse(savedUser));
        } catch (e) {
          console.error('Error al cargar usuario guardado:', e);
        }
      }
    }
  }

  // Método actualizado para recibir datos del backend
  login(userData: User) {
    this._user.set(userData);
    // Guardar en localStorage (solo en navegador)
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('user', JSON.stringify(userData));
    }
  }

  logout() {
    this._user.set(null);
    this._cart.set([]);
    // Limpiar localStorage (solo en navegador)
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('user');
      localStorage.removeItem('token');
    }
  }

  setToken(token: string) {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('token', token);
    }
  }

  getToken(): string | null {
    if (isPlatformBrowser(this.platformId)) {
      return localStorage.getItem('token');
    }
    return null;
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
