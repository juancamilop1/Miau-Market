import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService, Product } from '../../auth.service';
import { ApiService } from '../../services/api.service';
import { EnvironmentService } from '../../services/environment.service';

interface WishlistItem {
  id: number;
  Id_Products: number;
  Titulo: string;
  Precio: number;
  Stock: number;
  Categoria: string;
  Imagen?: string | null;
}

@Component({
  standalone: true,
  selector: 'mm-wishlist',
  templateUrl: './wishlist.html',
  styleUrls: ['./wishlist.css'],
  imports: [CommonModule, RouterLink]
})
export class Wishlist implements OnInit {
  private auth = inject(AuthService);
  private api = inject(ApiService);
  private env = inject(EnvironmentService);

  items = signal<WishlistItem[]>([]);
  loading = signal(true);
  error = signal('');
  mensaje = signal('');

  ngOnInit() {
    this.cargar();
  }

  cargar() {
    this.loading.set(true);
    this.error.set('');
    this.api.get<{ items: WishlistItem[] }>('/usuarios/wishlist/').subscribe({
      next: (r) => {
        this.items.set(r.items || []);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se pudo cargar tu lista de deseos');
        this.loading.set(false);
      }
    });
  }

  imagen(item: WishlistItem): string {
    return this.env.getImageUrl(item.Imagen);
  }

  quitar(item: WishlistItem) {
    this.api.delete(`/usuarios/wishlist/?Id_Products=${item.Id_Products}`).subscribe({
      next: () => this.items.update(list => list.filter(i => i.Id_Products !== item.Id_Products)),
      error: () => this.error.set('No se pudo quitar el producto')
    });
  }

  agregarAlCarrito(item: WishlistItem) {
    this.error.set('');
    this.mensaje.set('');
    const id = `db_${item.Id_Products}`;
    const enCarrito = this.auth.cart().find(i => i.product.id === id)?.quantity ?? 0;

    if (item.Stock <= 0) {
      this.error.set(`"${item.Titulo}" no tiene stock`);
      return;
    }
    if (enCarrito >= item.Stock) {
      this.error.set(`Ya tienes en el carrito todo el stock de "${item.Titulo}"`);
      return;
    }

    const product: Product = {
      id,
      name: item.Titulo,
      price: item.Precio,
      imagen: item.Imagen ? this.env.getImageUrl(item.Imagen) : undefined,
      stock: item.Stock
    };
    this.auth.addToCart(product);
    this.mensaje.set(`"${item.Titulo}" agregado al carrito`);
  }
}
