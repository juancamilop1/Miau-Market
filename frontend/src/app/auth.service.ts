import { Injectable, computed, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { PLATFORM_ID, inject } from '@angular/core';

export interface Product {
  id: string;
  name: string;
  price: number;
  description?: string;
  imagen?: string;
}

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface User {
  id: number;
  name: string;
  email: string;
  is_staff?: boolean;
  is_superuser?: boolean;
  Address?: string;
  Telefono?: string;
  Ciudad?: string;
  Edad?: number;
  Apellido?: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private platformId = inject(PLATFORM_ID);

  // Sesión del usuario autenticado
  private _user = signal<null | User>(null);
  user = this._user;
  isLogged = computed(() => !!this._user());

  // Carrito en memoria - ahora usa CartItem con cantidad
  private _cart = signal<CartItem[]>([]);
  cart = this._cart;

  // Computed: cantidad de productos ÚNICOS en el carrito
  cartCount = computed(() => {
    return this._cart().length;
  });

  // Computed: total de items en el carrito (suma de cantidades)
  cartTotalItems = computed(() => {
    return this._cart().reduce((sum, item) => sum + item.quantity, 0);
  });

  // Computed: total en dinero
  cartTotal = computed(() => {
    return this._cart().reduce((sum, item) => sum + (item.product.price * item.quantity), 0);
  });

  // Buscador compartido entre header y tienda
  search = signal('');

  constructor() {
    // Cargar usuario del localStorage si existe (solo en navegador)
    if (isPlatformBrowser(this.platformId)) {
      const savedUser = localStorage.getItem('user');
      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser);
          this._user.set(userData);
          
          // Cargar el carrito específico de este usuario
          const userCartKey = `cart_${userData.id}`;
          const savedCart = localStorage.getItem(userCartKey);
          if (savedCart) {
            try {
              this._cart.set(JSON.parse(savedCart));
            } catch (e) {
              console.error('Error al cargar carrito del usuario:', e);
            }
          }
        } catch (e) {
          console.error('Error al cargar usuario guardado:', e);
        }
      } else {
        // Usuario no logueado: cargar carrito anónimo
        const anonCart = localStorage.getItem('cart_anon');
        if (anonCart) {
          try {
            this._cart.set(JSON.parse(anonCart));
          } catch (e) {
            console.error('Error al cargar carrito anónimo:', e);
          }
        }
      }
    }
  }

  // Método actualizado para recibir datos del backend
  login(userData: User) {
    // Guardar el carrito anónimo antes de hacer login
    const anonCart = isPlatformBrowser(this.platformId) 
      ? this._cart() 
      : [];
    
    this._user.set(userData);
    
    // Guardar en localStorage (solo en navegador)
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Cargar el carrito específico de este usuario
      const userCartKey = `cart_${userData.id}`;
      const savedCart = localStorage.getItem(userCartKey);
      let userCart: CartItem[] = [];
      
      if (savedCart) {
        try {
          userCart = JSON.parse(savedCart);
        } catch (e) {
          console.error('Error al cargar carrito del usuario:', e);
        }
      }
      
      // Fusionar carrito anónimo con carrito del usuario
      if (anonCart.length > 0) {
        const mergedCart = this.mergeCart(userCart, anonCart);
        this._cart.set(mergedCart);
        localStorage.setItem(userCartKey, JSON.stringify(mergedCart));
        // Limpiar carrito anónimo
        localStorage.removeItem('cart_anon');
      } else {
        this._cart.set(userCart);
      }
    }
  }
  
  // Método auxiliar para fusionar carritos
  private mergeCart(userCart: CartItem[], anonCart: CartItem[]): CartItem[] {
    const merged = [...userCart];
    
    // Para cada item del carrito anónimo
    for (const anonItem of anonCart) {
      const existingIndex = merged.findIndex(item => item.product.id === anonItem.product.id);
      
      if (existingIndex >= 0) {
        // Si ya existe, sumar las cantidades
        merged[existingIndex] = {
          ...merged[existingIndex],
          quantity: merged[existingIndex].quantity + anonItem.quantity
        };
      } else {
        // Si no existe, agregarlo
        merged.push(anonItem);
      }
    }
    
    return merged;
  }

  logout() {
    // Guardar el carrito del usuario actual antes de cerrar sesión
    const currentUser = this._user();
    const currentCart = this._cart();
    
    if (currentUser && isPlatformBrowser(this.platformId)) {
      const userCartKey = `cart_${currentUser.id}`;
      localStorage.setItem(userCartKey, JSON.stringify(currentCart));
    }
    
    this._user.set(null);
    
    // Mantener el carrito pero cambiarlo a anónimo
    if (isPlatformBrowser(this.platformId) && currentCart.length > 0) {
      localStorage.setItem('cart_anon', JSON.stringify(currentCart));
    }
    
    // Limpiar localStorage de usuario (solo en navegador)
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
    const existingItemIndex = current.findIndex(item => item.product.id === product.id);
    
    let updatedCart: CartItem[];
    if (existingItemIndex >= 0) {
      // Si el producto ya existe, incrementar cantidad
      updatedCart = [...current];
      updatedCart[existingItemIndex] = {
        ...updatedCart[existingItemIndex],
        quantity: updatedCart[existingItemIndex].quantity + 1
      };
    } else {
      // Si es nuevo, agregarlo con cantidad 1
      updatedCart = [...current, { product, quantity: 1 }];
    }
    
    this._cart.set(updatedCart);
    
    // Guardar en localStorage (solo en navegador)
    if (isPlatformBrowser(this.platformId)) {
      const user = this._user();
      if (user) {
        const userCartKey = `cart_${user.id}`;
        localStorage.setItem(userCartKey, JSON.stringify(updatedCart));
      }
      localStorage.setItem('cart', JSON.stringify(updatedCart));
    }
  }

  // Incrementar cantidad de un producto
  incrementQuantity(productId: string) {
    const current = this._cart();
    const updatedCart = current.map(item => 
      item.product.id === productId 
        ? { ...item, quantity: item.quantity + 1 }
        : item
    );
    this._cart.set(updatedCart);
    this.saveCart(updatedCart);
  }

  // Decrementar cantidad de un producto
  decrementQuantity(productId: string) {
    const current = this._cart();
    const item = current.find(item => item.product.id === productId);
    
    if (item && item.quantity > 1) {
      // Si hay más de 1, decrementar
      const updatedCart = current.map(item => 
        item.product.id === productId 
          ? { ...item, quantity: item.quantity - 1 }
          : item
      );
      this._cart.set(updatedCart);
      this.saveCart(updatedCart);
    } else {
      // Si solo hay 1, eliminar el producto
      this.removeFromCart(productId);
    }
  }

  removeFromCart(productId: string) {
    const updatedCart = this._cart().filter(item => item.product.id !== productId);
    this._cart.set(updatedCart);
    this.saveCart(updatedCart);
  }

  clearCart() {
    this._cart.set([]);
    
    // Limpiar del localStorage (solo en navegador)
    if (isPlatformBrowser(this.platformId)) {
      const user = this._user();
      if (user) {
        const userCartKey = `cart_${user.id}`;
        localStorage.removeItem(userCartKey);
      }
      localStorage.removeItem('cart');
    }
  }

  // Método auxiliar para guardar carrito
  private saveCart(cart: CartItem[]) {
    if (isPlatformBrowser(this.platformId)) {
      const user = this._user();
      if (user) {
        // Usuario logueado: guardar en su carrito específico
        const userCartKey = `cart_${user.id}`;
        localStorage.setItem(userCartKey, JSON.stringify(cart));
      } else {
        // Usuario anónimo: guardar en carrito anónimo
        localStorage.setItem('cart_anon', JSON.stringify(cart));
      }
      // Mantener también en 'cart' para compatibilidad
      localStorage.setItem('cart', JSON.stringify(cart));
    }
  }
}
