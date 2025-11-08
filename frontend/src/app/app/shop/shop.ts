import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService, Product } from '../../auth.service';
import { ApiService } from '../../services/api.service';

interface ProductFromDB {
  Id_Products: number;
  Titulo: string;
  Descripcion: string;
  Categoria: string;
  Precio: number;
  Stock: number;
  Imagen?: string;
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
}

@Component({
  standalone: true,
  selector: 'mm-shop',
  templateUrl: './shop.html',
  styleUrls: ['./shop.css']
  ,imports: [CommonModule]
})
export class Shop implements OnInit {
  auth = inject(AuthService);
  private api = inject(ApiService);

  // Todos los productos
  allProducts = signal<ProductDisplay[]>([]);
  loading = signal(false);

  // Carruseles por categoría
  highlighted = signal<ProductDisplay[]>([]);
  highlightedIndex = signal(0);

  comida = signal<ProductDisplay[]>([]);
  comidaIndex = signal(0);

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
            categoria: p.Categoria
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
    this.comida.set(products.filter(p => p.categoria === 'Comida'));
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
      description: product.description
    } as Product);
  }

  // Métodos para controlar carruseles
  nextSlide(category: 'highlighted' | 'comida' | 'juguetes' | 'servicios') {
    let items: ProductDisplay[];
    let currentIndex: number;
    let setter: (index: number) => void;

    switch(category) {
      case 'highlighted':
        items = this.highlighted();
        currentIndex = this.highlightedIndex();
        setter = (i) => this.highlightedIndex.set(i);
        break;
      case 'comida':
        items = this.comida();
        currentIndex = this.comidaIndex();
        setter = (i) => this.comidaIndex.set(i);
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

  prevSlide(category: 'highlighted' | 'comida' | 'juguetes' | 'servicios') {
    let items: ProductDisplay[];
    let currentIndex: number;
    let setter: (index: number) => void;

    switch(category) {
      case 'highlighted':
        items = this.highlighted();
        currentIndex = this.highlightedIndex();
        setter = (i) => this.highlightedIndex.set(i);
        break;
      case 'comida':
        items = this.comida();
        currentIndex = this.comidaIndex();
        setter = (i) => this.comidaIndex.set(i);
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
}

