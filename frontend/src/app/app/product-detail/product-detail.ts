import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService, Product } from '../../auth.service';
import { ApiService } from '../../services/api.service';
import { EnvironmentService } from '../../services/environment.service';
import { StarRating } from '../star-rating/star-rating';

interface ProductDetailData {
  Id_Products: number;
  Titulo: string;
  Descripcion: string;
  Categoria: string;
  Precio: number;
  Stock: number;
  Imagen?: string | null;
  Fecha_Caducidad?: string;
}

interface Review {
  Id_Review: number;
  Nombre: string;
  Apellido: string;
  Rating: number;
  Comentario: string;
  Fecha: string;
}

interface ProductRating {
  Total_Reviews: number;
  Rating_Promedio: number;
}

@Component({
  standalone: true,
  selector: 'mm-product-detail',
  templateUrl: './product-detail.html',
  styleUrls: ['./product-detail.css'],
  imports: [CommonModule, FormsModule, RouterLink, StarRating]
})
export class ProductDetail implements OnInit {
  auth = inject(AuthService);
  private api = inject(ApiService);
  private env = inject(EnvironmentService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  producto = signal<ProductDetailData | null>(null);
  reviews = signal<Review[]>([]);
  rating = signal<ProductRating | null>(null);
  loading = signal(true);
  error = signal('');
  mensaje = signal('');
  enWishlist = signal(false);
  cantidad = 1;

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const id = Number(params.get('id'));
      if (!id) {
        this.router.navigate(['/shop']);
        return;
      }
      this.cargar(id);
    });
  }

  private cargar(id: number) {
    this.loading.set(true);
    this.error.set('');
    this.mensaje.set('');
    this.cantidad = 1;

    this.api.get<ProductDetailData>(`/usuarios/productos/${id}/`).subscribe({
      next: (p) => {
        this.producto.set(p);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.status === 404 ? 'Producto no encontrado' : 'No se pudo cargar el producto');
        this.loading.set(false);
      }
    });

    this.api.get<{ reviews: Review[] }>(`/usuarios/productos/${id}/reviews/`).subscribe({
      next: (r) => this.reviews.set(r.reviews || []),
      error: () => this.reviews.set([])
    });

    this.api.get<{ rating: ProductRating | null }>(`/usuarios/productos/${id}/rating/`).subscribe({
      next: (r) => this.rating.set(r.rating || null),
      error: () => this.rating.set(null)
    });

    if (this.auth.isLogged()) {
      this.api.get<{ items: { Id_Products: number }[] }>('/usuarios/wishlist/').subscribe({
        next: (r) => this.enWishlist.set((r.items || []).some(i => i.Id_Products === id)),
        error: () => this.enWishlist.set(false)
      });
    }
  }

  imagen(p: ProductDetailData): string {
    return this.env.getImageUrl(p.Imagen);
  }

  formatearFecha(fecha: string): string {
    return new Date(fecha).toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' });
  }

  enCarrito(p: ProductDetailData): number {
    return this.auth.cart().find(i => i.product.id === `db_${p.Id_Products}`)?.quantity ?? 0;
  }

  agregarAlCarrito() {
    const p = this.producto();
    if (!p) return;
    this.mensaje.set('');
    this.error.set('');

    const qty = Math.floor(Number(this.cantidad));
    if (p.Stock <= 0) {
      this.error.set('Producto sin stock');
      return;
    }
    if (!qty || qty < 1) {
      this.error.set('Cantidad invalida');
      return;
    }
    const disponible = p.Stock - this.enCarrito(p);
    if (qty > disponible) {
      this.error.set(
        disponible <= 0
          ? 'Ya tienes en el carrito todo el stock disponible'
          : `Solo puedes agregar ${disponible} unidad(es) mas`
      );
      return;
    }

    const item: Product = {
      id: `db_${p.Id_Products}`,
      name: p.Titulo,
      price: p.Precio,
      description: p.Descripcion,
      imagen: p.Imagen ? this.env.getImageUrl(p.Imagen) : undefined,
      stock: p.Stock
    };
    for (let i = 0; i < qty; i++) {
      this.auth.addToCart(item);
    }
    this.mensaje.set(`${qty} unidad(es) agregada(s) al carrito`);
  }

  toggleWishlist() {
    const p = this.producto();
    if (!p) return;
    const request$ = this.enWishlist()
      ? this.api.delete(`/usuarios/wishlist/?Id_Products=${p.Id_Products}`)
      : this.api.post('/usuarios/wishlist/', { Id_Products: p.Id_Products });
    request$.subscribe({
      next: () => this.enWishlist.update(v => !v),
      error: () => this.error.set('No se pudo actualizar tu lista de deseos')
    });
  }
}
