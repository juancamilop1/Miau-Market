import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../auth.service';

@Component({
  standalone: true,
  selector: 'mm-cart',
  templateUrl: './cart.html',
  styleUrls: ['./cart.css']
  ,imports: [CommonModule]
})
export class Cart {
  private auth = inject(AuthService);

  cart() { return this.auth.cart(); }

  remove(id: string) { this.auth.removeFromCart(id); }

  clear() { this.auth.clearCart(); }
}
