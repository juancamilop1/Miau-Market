import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../auth.service';
import { ApiService } from '../../services/api.service';

interface Product {
  Id_Products?: number;
  Titulo: string;
  Descripcion: string;
  Categoria: string;
  Precio: number;
  Stock: number;
  Imagen?: File | string | null;
}

@Component({
  selector: 'mm-admin',
  imports: [CommonModule, FormsModule],
  templateUrl: './admin.html',
  styleUrl: './admin.css'
})
export class Admin implements OnInit {
  products = signal<Product[]>([]);
  loading = signal(false);
  editingId = signal<number | null>(null);
  showForm = signal(false);
  successMessage = signal('');
  errorMessage = signal('');
  imagePreviewUrl = signal<string | null>(null);

  // Categorías disponibles
  categorias = ['Comida', 'Juguetes', 'Servicios'];

  newProduct = signal<Product>({
    Titulo: '',
    Descripcion: '',
    Categoria: '',
    Precio: 0,
    Stock: 0
  });

  constructor(public auth: AuthService, private api: ApiService) {}

  ngOnInit() {
    this.loadProducts();
  }

  loadProducts() {
    this.loading.set(true);
    this.api.get<Product[]>('/usuarios/productos/').subscribe(
      (data: Product[]) => {
        console.log('Productos cargados:', data);
        this.products.set(data || []);
        this.loading.set(false);
        this.errorMessage.set(''); // Limpiar error si tenía uno
      },
      (error: any) => {
        console.error('Error cargando productos:', error);
        console.error('Error details:', error.status, error.statusText, error.url);
        // No mostrar error para permitir agregar de todas formas
        this.loading.set(false);
        // Seguir permitiendo agregar productos aunque falle la carga
      }
    );
  }

  openForm(product?: Product) {
    if (product) {
      this.editingId.set(product.Id_Products || null);
      this.newProduct.set({ ...product });
    } else {
      this.editingId.set(null);
      this.newProduct.set({
        Titulo: '',
        Descripcion: '',
        Categoria: '',
        Precio: 0,
        Stock: 0
      });
    }
    this.showForm.set(true);
    this.successMessage.set('');
  }

  closeForm() {
    this.showForm.set(false);
    this.editingId.set(null);
    this.imagePreviewUrl.set(null);
  }

  saveProduct() {
    const product = this.newProduct();
    
    if (!product.Titulo || !product.Categoria || product.Precio <= 0) {
      this.errorMessage.set('Por favor completa todos los campos correctamente');
      return;
    }

    this.loading.set(true);
    const editingId = this.editingId();

    // Crear FormData para enviar archivos
    const formData = new FormData();
    formData.append('Titulo', product.Titulo);
    formData.append('Descripcion', product.Descripcion);
    formData.append('Categoria', product.Categoria);
    formData.append('Precio', Math.floor(product.Precio).toString());
    formData.append('Stock', product.Stock.toString());
    
    // Si hay una imagen tipo File, agregarla
    if (product.Imagen instanceof File) {
      formData.append('Imagen', product.Imagen);
    }

    if (editingId && editingId !== null) {
      // Actualizar producto existente
      this.api.put<Product>(`/usuarios/productos/${editingId}/`, formData).subscribe(
        () => {
          this.successMessage.set('Producto actualizado exitosamente');
          this.loading.set(false);
          this.closeForm();
          this.loadProducts();
        },
        (error: any) => {
          this.errorMessage.set('Error al actualizar el producto');
          console.error(error);
          this.loading.set(false);
        }
      );
    } else {
      // Crear nuevo producto
      this.api.post<Product>('/usuarios/productos/', formData).subscribe(
        () => {
          this.successMessage.set('Producto creado exitosamente');
          this.loading.set(false);
          this.closeForm();
          this.loadProducts();
        },
        (error: any) => {
          this.errorMessage.set('Error al crear el producto');
          console.error(error);
          this.loading.set(false);
        }
      );
    }
  }

  deleteProduct(id: number | undefined) {
    console.log('Intentando eliminar producto con ID:', id, typeof id);
    
    if (!id || id === undefined || id === null) {
      this.errorMessage.set('Error: ID de producto no válido');
      return;
    }

    if (confirm('¿Estás seguro de que quieres eliminar este producto?')) {
      this.loading.set(true);
      console.log('Enviando DELETE a:', `/usuarios/productos/${id}/`);
      this.api.delete<void>(`/usuarios/productos/${id}/`).subscribe(
        () => {
          this.successMessage.set('Producto eliminado exitosamente');
          this.loading.set(false);
          this.loadProducts();
        },
        (error: any) => {
          this.errorMessage.set('Error al eliminar el producto');
          console.error('Error de eliminación:', error);
          this.loading.set(false);
        }
      );
    }
  }

  onImageSelect(event: any) {
    const file = event.target.files[0];
    if (file) {
      // Guardar el archivo en el producto
      const product = this.newProduct();
      this.newProduct.set({ ...product, Imagen: file });
      
      // Generar URL de vista previa usando FileReader
      const reader = new FileReader();
      reader.onload = () => {
        this.imagePreviewUrl.set(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  }
}
