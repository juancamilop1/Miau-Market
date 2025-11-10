import { Component, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../auth.service';

@Component({
  standalone: true,
  selector: 'mm-cart',
  templateUrl: './cart.html',
  styleUrls: ['./cart.css']
  ,imports: [CommonModule, RouterLink]
})
export class Cart {
  auth = inject(AuthService);
  router = inject(Router);
  
  // Set para mantener los IDs de productos seleccionados
  selectedItems = signal<Set<string>>(new Set());

  cart() { return this.auth.cart(); }
  
  // Calcular total solo de items seleccionados
  cartTotal() { 
    const cart = this.cart();
    const selected = this.selectedItems();
    return cart
      .filter(item => selected.has(item.product.id))
      .reduce((sum, item) => sum + (item.product.price * item.quantity), 0);
  }
  
  // Verificar si todos están seleccionados
  allSelected = computed(() => {
    const cart = this.cart();
    const selected = this.selectedItems();
    return cart.length > 0 && cart.every(item => selected.has(item.product.id));
  });
  
  // Verificar si alguno está seleccionado
  hasSelected = computed(() => {
    return this.selectedItems().size > 0;
  });

  ngOnInit() {
    // Seleccionar todos los items por defecto
    const allIds = this.cart().map(item => item.product.id);
    this.selectedItems.set(new Set(allIds));
  }

  toggleItem(productId: string) {
    const selected = new Set(this.selectedItems());
    if (selected.has(productId)) {
      selected.delete(productId);
    } else {
      selected.add(productId);
    }
    this.selectedItems.set(selected);
  }
  
  isSelected(productId: string): boolean {
    return this.selectedItems().has(productId);
  }
  
  toggleAll() {
    const cart = this.cart();
    if (this.allSelected()) {
      // Deseleccionar todos
      this.selectedItems.set(new Set());
    } else {
      // Seleccionar todos
      const allIds = cart.map(item => item.product.id);
      this.selectedItems.set(new Set(allIds));
    }
  }

  increment(productId: string) { 
    this.auth.incrementQuantity(productId); 
  }

  decrement(productId: string) { 
    this.auth.decrementQuantity(productId); 
  }

  remove(id: string) { 
    this.auth.removeFromCart(id);
    // También remover de seleccionados
    const selected = new Set(this.selectedItems());
    selected.delete(id);
    this.selectedItems.set(selected);
  }

  clear() { 
    this.auth.clearCart();
    this.selectedItems.set(new Set());
  }
  
  // Método para obtener solo items seleccionados (usar en checkout)
  getSelectedItems() {
    const cart = this.cart();
    const selected = this.selectedItems();
    return cart.filter(item => selected.has(item.product.id));
  }
  
  proceedToCheckout(event: Event) {
    if (!this.hasSelected()) {
      event.preventDefault();
      return;
    }
    
    // Guardar IDs de items seleccionados en sessionStorage
    const selectedIds = Array.from(this.selectedItems());
    sessionStorage.setItem('selectedCartItems', JSON.stringify(selectedIds));
  }
}
