import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService, Product } from '../../auth.service';
import { ApiService } from '../../services/api.service';
import { StarRating } from '../star-rating/star-rating';

interface ProductFromDB {
  Id_Products: number;
  Titulo: string;
  Descripcion: string;
  Categoria: string;
  Precio: number;
  Stock: number;
  Imagen?: string;
  Fecha_Caducidad?: string;
}

interface ProductDisplay {
  id: string;
  name: string;
  price: number;
  description: string;
  imagen?: string;
  stock: number;
  dbId: number;
  categoria: string;
  fechaCaducidad?: string;
}

interface Review {
  Id_Review: number;
  Id_Products: number;
  Id_User: number;
  Nombre: string;
  Apellido: string;
  Rating: number;
  Comentario: string;
  Fecha: string;
}

interface ProductRating {
  Id_Products: number;
  Titulo: string;
  Total_Reviews: number;
  Rating_Promedio: number;
  Reviews_5_Estrellas: number;
  Reviews_4_Estrellas: number;
  Reviews_3_Estrellas: number;
  Reviews_2_Estrellas: number;
  Reviews_1_Estrella: number;
}

@Component({
  standalone: true,
  selector: 'mm-shop',
  templateUrl: './shop.html',
  styleUrls: ['./shop.css'],
  imports: [CommonModule, FormsModule, StarRating, RouterLink]
})
export class Shop implements OnInit {
  auth = inject(AuthService);
  private api = inject(ApiService);

  // Todos los productos
  allProducts = signal<ProductDisplay[]>([]);
  loading = signal(false);

  // Modal de detalles del producto
  mostrarModal = signal(false);
  productoSeleccionado = signal<ProductDisplay | null>(null);
  
  // Reseñas del producto seleccionado
  reviews = signal<Review[]>([]);
  productRating = signal<ProductRating | null>(null);
  loadingReviews = signal(false);
  
  // Nueva reseña
  nuevaCalificacion = signal<number>(0);
  nuevoComentario = '';  // Variable normal para ngModel
  enviandoReview = signal(false);
  
  // Reseña del usuario
  miReview = signal<Review | null>(null);
  editandoReview = signal(false);

  // Carruseles por categoría
  highlighted = signal<ProductDisplay[]>([]);
  highlightedIndex = signal(0);

  comidaGato = signal<ProductDisplay[]>([]);
  comidaGatoIndex = signal(0);

  comidaPerro = signal<ProductDisplay[]>([]);
  comidaPerroIndex = signal(0);

  juguetes = signal<ProductDisplay[]>([]);
  juguetesIndex = signal(0);

  servicios = signal<ProductDisplay[]>([]);
  serviciosIndex = signal(0);

  itemsPerCarousel = 4;

  ngOnInit() {
    this.loadProductsFromDB();
  }

  loadProductsFromDB() {
    this.loading.set(true);
    this.api.get<ProductFromDB[]>('/usuarios/productos/').subscribe(
      (data: ProductFromDB[]) => {
        if (data && data.length > 0) {
          // Convertir productos
          const products = data.map(p => ({
            id: `db_${p.Id_Products}`,
            name: p.Titulo,
            price: p.Precio,
            description: p.Descripcion,
            imagen: p.Imagen,
            stock: p.Stock,
            dbId: p.Id_Products,
            categoria: p.Categoria,
            fechaCaducidad: p.Fecha_Caducidad
          }));

          this.allProducts.set(products);
          this.organizarPorCategoria(products);
        } else {
          this.allProducts.set([]);
        }
        this.loading.set(false);
      },
      (error: any) => {
        console.error('Error cargando productos:', error);
        this.allProducts.set([]);
        this.loading.set(false);
      }
    );
  }

  organizarPorCategoria(products: ProductDisplay[]) {
    // Productos destacados: los 4 con más stock
    const highlighted = [...products]
      .sort((a, b) => b.stock - a.stock)
      .slice(0, 4);
    this.highlighted.set(highlighted);

    // Organizar por categoría
    this.comidaGato.set(products.filter(p => p.categoria === 'Comida de Gato'));
    this.comidaPerro.set(products.filter(p => p.categoria === 'Comida de Perro'));
    this.juguetes.set(products.filter(p => p.categoria === 'Juguetes'));
    this.servicios.set(products.filter(p => p.categoria === 'Servicios'));
  }

  filtered() {
    const q = this.auth.search()?.toLowerCase().trim();
    if (!q) return this.allProducts();
    return this.allProducts().filter(p => 
      p.name.toLowerCase().includes(q) || 
      p.description.toLowerCase().includes(q)
    );
  }

  add(product: ProductDisplay) {
    this.auth.addToCart({
      id: product.id,
      name: product.name,
      price: product.price,
      description: product.description,
      imagen: product.imagen
    } as Product);
  }

  // Métodos para el modal
  verDetalles(product: ProductDisplay) {
    this.productoSeleccionado.set(product);
    this.mostrarModal.set(true);
    this.cargarReviewsDelProducto(product.dbId);
  }

  cerrarModal() {
    this.mostrarModal.set(false);
    setTimeout(() => {
      this.productoSeleccionado.set(null);
      this.reviews.set([]);
      this.productRating.set(null);
      this.miReview.set(null);
      this.nuevaCalificacion.set(0);
      this.nuevoComentario = '';
      this.editandoReview.set(false);
    }, 300); // Esperar a que termine la animación
  }

  agregarDesdeModal() {
    const producto = this.productoSeleccionado();
    if (producto) {
      this.add(producto);
      this.cerrarModal();
    }
  }

  formatearFecha(fecha?: string): string {
    if (!fecha) return 'No especificada';
    const fechaObj = new Date(fecha);
    const opciones: Intl.DateTimeFormatOptions = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    };
    return fechaObj.toLocaleDateString('es-ES', opciones);
  }

  // Métodos para controlar carruseles
  nextSlide(category: 'highlighted' | 'comidaGato' | 'comidaPerro' | 'juguetes' | 'servicios') {
    let items: ProductDisplay[];
    let currentIndex: number;
    let setter: (index: number) => void;

    switch(category) {
      case 'highlighted':
        items = this.highlighted();
        currentIndex = this.highlightedIndex();
        setter = (i) => this.highlightedIndex.set(i);
        break;
      case 'comidaGato':
        items = this.comidaGato();
        currentIndex = this.comidaGatoIndex();
        setter = (i) => this.comidaGatoIndex.set(i);
        break;
      case 'comidaPerro':
        items = this.comidaPerro();
        currentIndex = this.comidaPerroIndex();
        setter = (i) => this.comidaPerroIndex.set(i);
        break;
      case 'juguetes':
        items = this.juguetes();
        currentIndex = this.juguetesIndex();
        setter = (i) => this.juguetesIndex.set(i);
        break;
      case 'servicios':
        items = this.servicios();
        currentIndex = this.serviciosIndex();
        setter = (i) => this.serviciosIndex.set(i);
        break;
    }

    const nextIndex = (currentIndex + this.itemsPerCarousel) % items.length;
    setter(nextIndex);
  }

  prevSlide(category: 'highlighted' | 'comidaGato' | 'comidaPerro' | 'juguetes' | 'servicios') {
    let items: ProductDisplay[];
    let currentIndex: number;
    let setter: (index: number) => void;

    switch(category) {
      case 'highlighted':
        items = this.highlighted();
        currentIndex = this.highlightedIndex();
        setter = (i) => this.highlightedIndex.set(i);
        break;
      case 'comidaGato':
        items = this.comidaGato();
        currentIndex = this.comidaGatoIndex();
        setter = (i) => this.comidaGatoIndex.set(i);
        break;
      case 'comidaPerro':
        items = this.comidaPerro();
        currentIndex = this.comidaPerroIndex();
        setter = (i) => this.comidaPerroIndex.set(i);
        break;
      case 'juguetes':
        items = this.juguetes();
        currentIndex = this.juguetesIndex();
        setter = (i) => this.juguetesIndex.set(i);
        break;
      case 'servicios':
        items = this.servicios();
        currentIndex = this.serviciosIndex();
        setter = (i) => this.serviciosIndex.set(i);
        break;
    }

    const prevIndex = currentIndex === 0 ? Math.max(0, items.length - this.itemsPerCarousel) : currentIndex - this.itemsPerCarousel;
    setter(prevIndex);
  }

  getVisibleProducts(products: ProductDisplay[], startIndex: number): ProductDisplay[] {
    return products.slice(startIndex, startIndex + this.itemsPerCarousel);
  }

  // Método para determinar si un producto de comida está caducado
  getEstadoFrescura(product: ProductDisplay): string | null {
    // Solo mostrar para productos de categoría Comida de Gato o Comida de Perro
    if ((product.categoria !== 'Comida de Gato' && product.categoria !== 'Comida de Perro') || !product.fechaCaducidad) {
      return null;
    }

    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0); // Resetear horas para comparar solo fechas
    
    const fechaCaducidad = new Date(product.fechaCaducidad);
    fechaCaducidad.setHours(0, 0, 0, 0);

    return fechaCaducidad >= hoy ? 'Fresco' : 'Caducado';
  }

  // Método para obtener la clase CSS según el estado
  getEstadoClass(product: ProductDisplay): string {
    const estado = this.getEstadoFrescura(product);
    if (estado === 'Fresco') return 'estado-fresco';
    if (estado === 'Caducado') return 'estado-caducado';
    return '';
  }

  // ==================== MÉTODOS DE RESEÑAS ====================
  
  cargarReviewsDelProducto(productId: number): void {
    this.loadingReviews.set(true);
    
    // Cargar reseñas del producto
    this.api.get(`/usuarios/productos/${productId}/reviews/`).subscribe({
      next: (response: any) => {
        this.reviews.set(response.reviews || []);
      },
      error: (error) => {
        console.error('Error al cargar reseñas:', error);
        this.reviews.set([]);
      }
    });
    
    // Cargar rating agregado
    this.api.get(`/usuarios/productos/${productId}/rating/`).subscribe({
      next: (response: any) => {
        this.productRating.set(response.rating || null);
      },
      error: (error) => {
        console.error('Error al cargar rating:', error);
        this.productRating.set(null);
      }
    });
    
    // Si el usuario está autenticado, cargar su reseña
    if (this.auth.isLogged()) {
      this.api.get(`/usuarios/productos/${productId}/my-review/`).subscribe({
        next: (response: any) => {
          this.miReview.set(response.review || null);
          if (response.review) {
            this.nuevaCalificacion.set(response.review.Rating);
            this.nuevoComentario = response.review.Comentario || '';
          }
          this.loadingReviews.set(false);
        },
        error: (error) => {
          console.error('Error al cargar mi reseña:', error);
          this.miReview.set(null);
          this.loadingReviews.set(false);
        }
      });
    } else {
      this.loadingReviews.set(false);
    }
  }
  
  onRatingChange(rating: number): void {
    this.nuevaCalificacion.set(rating);
  }
  
  enviarReview(): void {
    const producto = this.productoSeleccionado();
    if (!producto || this.nuevaCalificacion() === 0) {
      alert('Por favor selecciona una calificación');
      return;
    }
    
    if (!this.auth.isLogged()) {
      alert('Debes iniciar sesión para dejar una reseña');
      return;
    }
    
    this.enviandoReview.set(true);
    
    const reviewData = {
      Rating: this.nuevaCalificacion(),
      Comentario: this.nuevoComentario
    };
    
    const miReviewActual = this.miReview();
    
    if (miReviewActual) {
      // Actualizar reseña existente
      this.api.put(`/usuarios/productos/${producto.dbId}/my-review/`, reviewData).subscribe({
        next: () => {
          this.enviandoReview.set(false);
          this.editandoReview.set(false);
          this.cargarReviewsDelProducto(producto.dbId);
          alert('Reseña actualizada exitosamente');
        },
        error: (error) => {
          console.error('Error al actualizar reseña:', error);
          this.enviandoReview.set(false);
          alert('Error al actualizar la reseña');
        }
      });
    } else {
      // Crear nueva reseña
      this.api.post(`/usuarios/productos/${producto.dbId}/reviews/`, reviewData).subscribe({
        next: () => {
          this.enviandoReview.set(false);
          this.cargarReviewsDelProducto(producto.dbId);
          this.nuevaCalificacion.set(0);
          this.nuevoComentario = '';
          alert('Reseña enviada exitosamente');
        },
        error: (error) => {
          console.error('Error al enviar reseña:', error);
          this.enviandoReview.set(false);
          alert(error.error?.error || 'Error al enviar la reseña');
        }
      });
    }
  }
  
  editarMiReview(): void {
    this.editandoReview.set(true);
  }
  
  cancelarEdicion(): void {
    const miReviewActual = this.miReview();
    if (miReviewActual) {
      this.nuevaCalificacion.set(miReviewActual.Rating);
      this.nuevoComentario = miReviewActual.Comentario || '';
    }
    this.editandoReview.set(false);
  }
  
  eliminarMiReview(): void {
    const producto = this.productoSeleccionado();
    if (!producto) return;
    
    if (!confirm('¿Estás seguro de que deseas eliminar tu reseña?')) {
      return;
    }
    
    this.api.delete(`/usuarios/productos/${producto.dbId}/my-review/`).subscribe({
      next: () => {
        this.miReview.set(null);
        this.nuevaCalificacion.set(0);
        this.nuevoComentario = '';
        this.editandoReview.set(false);
        this.cargarReviewsDelProducto(producto.dbId);
        alert('Reseña eliminada exitosamente');
      },
      error: (error) => {
        console.error('Error al eliminar reseña:', error);
        alert('Error al eliminar la reseña');
      }
    });
  }
  
  formatearFechaReview(fecha: string): string {
    const fechaObj = new Date(fecha);
    const opciones: Intl.DateTimeFormatOptions = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    };
    return fechaObj.toLocaleDateString('es-ES', opciones);
  }
  
  getPercentaje(cantidad: number, total: number): number {
    return total > 0 ? (cantidad / total) * 100 : 0;
  }
}

