import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
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

  cart() { return this.auth.cart(); }
  
  cartTotal() { return this.auth.cartTotal(); }

  increment(productId: string) { 
    this.auth.incrementQuantity(productId); 
  }

  decrement(productId: string) { 
    this.auth.decrementQuantity(productId); 
  }

  remove(id: string) { 
    this.auth.removeFromCart(id); 
  }

  clear() { 
    this.auth.clearCart(); 
  }
}
