import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService, Product } from '../../auth.service';

@Component({
  standalone: true,
  selector: 'mm-shop',
  templateUrl: './shop.html',
  styleUrls: ['./shop.css']
  ,imports: [CommonModule]
})
export class Shop {
  private auth = inject(AuthService);
  products = [
    { id: 'p_1', name: 'Rascador para gatos', price: 30000, description: 'Rascador resistente con plataforma y juguete colgante.' },
    { id: 'p_2', name: 'Comida premium 1kg', price: 40000, description: 'Alimento balanceado de alta calidad para gatos adultos.' },
    { id: 'p_3', name: 'Cama acolchada', price: 50000, description: 'Cama ergonómica y lavable para el descanso de tu gato.' },
    { id: 'p_4', name: 'Juguete interactivo', price: 20000, description: 'Juguete con movimiento para estimular el instinto de caza.' }
  ];
  filtered() {
    const q = this.auth.search()?.toLowerCase().trim();
    if (!q) return this.products;
    return this.products.filter(p => p.name.toLowerCase().includes(q) || p.description.toLowerCase().includes(q));
  }

  add(i: number) {
    const p = this.products[i - 1];
    if (p) this.auth.addToCart(p as Product);
  }
}
