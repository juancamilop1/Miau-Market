import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../../auth.service';
import { ApiService } from '../../services/api.service';

interface Product {
  Id_Products?: number;
  Titulo: string;
  Descripcion: string;
  Categoria: string;
  Precio: number;
  Stock: number;
  Fecha_Caducidad: string;  // Campo obligatorio para fecha de caducidad (formato YYYY-MM-DD)
  Imagen?: File | string | null;
}

interface Order {
  Id_Factura: number;
  Id_User: number;
  Fecha: string;
  Total: number;
  Metodo_Pago: string;
  Estado: string;
  Direccion_Envio: string;
  Telefono_Envio: string;
  usuario_nombre?: string;
  usuario_email?: string;
  productos?: OrderProduct[];
}

interface OrderProduct {
  Id_Products: number;
  Cantidad: number;
  Precio_Unitario: number;
  Subtotal: number;
  Titulo: string;
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
  
  // Pedidos
  activeTab = signal<'productos' | 'pedidos'>('productos');
  orders = signal<Order[]>([]);
  loadingOrders = signal(false);

  // Categorías disponibles
  categorias = ['Comida', 'Juguetes', 'Servicios'];

  newProduct = signal<Product>({
    Titulo: '',
    Descripcion: '',
    Categoria: '',
    Precio: 0,
    Stock: 0,
    Fecha_Caducidad: ''
  });

  constructor(
    public auth: AuthService, 
    private api: ApiService,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    // Verificar si viene de una notificación
    this.route.queryParams.subscribe(params => {
      if (params['tab'] === 'pedidos') {
        this.activeTab.set('pedidos');
        this.loadOrders();
      } else {
        this.loadProducts();
      }
    });
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
        Stock: 0,
        Fecha_Caducidad: ''
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
    
    if (!product.Titulo || !product.Categoria || product.Precio <= 0 || !product.Fecha_Caducidad) {
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
    formData.append('Fecha_Caducidad', product.Fecha_Caducidad);
    
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

  // Métodos para gestión de pedidos
  loadOrders() {
    this.loadingOrders.set(true);
    this.api.get<Order[]>('/usuarios/pedidos/').subscribe(
      (data: Order[]) => {
        this.orders.set(data || []);
        this.loadingOrders.set(false);
      },
      (error: any) => {
        console.error('Error cargando pedidos:', error);
        this.errorMessage.set('Error al cargar los pedidos');
        this.loadingOrders.set(false);
      }
    );
  }

  updateOrderStatus(orderId: number, newStatus: string) {
    this.api.put(`/usuarios/pedidos/${orderId}/`, { Estado: newStatus }).subscribe(
      () => {
        this.successMessage.set(`Pedido #${orderId} actualizado a ${newStatus}`);
        this.loadOrders(); // Recargar lista de pedidos
        setTimeout(() => this.successMessage.set(''), 3000);
      },
      (error: any) => {
        console.error('Error actualizando pedido:', error);
        this.errorMessage.set('Error al actualizar el estado del pedido');
        setTimeout(() => this.errorMessage.set(''), 3000);
      }
    );
  }
}
