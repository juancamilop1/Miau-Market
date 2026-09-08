import { Component, OnInit, signal, computed, effect, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../../auth.service';
import { ApiService } from '../../services/api.service';
import { EnvironmentService } from '../../services/environment.service';

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

interface User {
  Id_User: number;
  Username: string;
  Nombre: string;
  Apellido: string;
  Email: string;
  Telefono: string;
  Address: string;
  City: string;
  BirthDate: string;
  is_staff: boolean;
  is_superuser: boolean;
  is_active: boolean;
  FechaRegistro: string;
  Total_Pedidos: number;
  Total_Gastado: number;
}

interface UserEditForm {
  Username: string;
  Nombre: string;
  Apellido: string;
  Email: string;
  Telefono: string;
  Address: string;
  City: string;
  BirthDate: string;
  is_staff: boolean;
  is_superuser: boolean;
  is_active: boolean;
  password: string;
}

interface MiauBotAprendizaje {
  id: number;
  pregunta: string;
  respuesta: string;
  palabras_clave: string;
  animal: string;
  usuario_id: number | null;
  estado: 'pendiente' | 'aprobado' | 'rechazado';
  veces_usada: number;
  Fecha_Creacion: string;
}

@Component({
  selector: 'mm-admin',
  imports: [CommonModule, FormsModule, RouterLink],
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
  activeTab = signal<'productos' | 'pedidos' | 'usuarios' | 'miaubot'>('productos');
  orders = signal<Order[]>([]);
  loadingOrders = signal(false);

  // MiauBot aprendizaje
  aprendizajes = signal<MiauBotAprendizaje[]>([]);
  loadingAprendizaje = signal(false);
  pendientesCount = signal(0);
  filtroAprendizaje = signal<'pendiente' | 'aprobado' | 'rechazado' | 'todos'>('pendiente');
  showAprendizajeModal = signal(false);
  aprendizajeEdit = signal<MiauBotAprendizaje | null>(null);
  respuestaEditada = signal('');
  processingAprendizaje = signal<number | null>(null);

  // Usuarios
  users = signal<User[]>([]);
  loadingUsers = signal(false);
  processingUser = signal<number | null>(null);
  searchUser = signal('');
  
  // Modal de confirmación de eliminación
  showDeleteModal = signal(false);
  userToDelete = signal<User | null>(null);
  deleteConfirmationName = signal('');

  // Modal de edición de usuario
  showEditModal = signal(false);
  userToEdit = signal<User | null>(null);
  editFormData: UserEditForm = this.emptyEditForm();
  savingUser = signal(false);
  
  // Vista y selección de usuarios
  viewMode = signal<'table' | 'cards'>('table');
  selectedUsers = signal<Set<number>>(new Set());
  selectAll = signal(false);
  showBulkActions = signal(false);
  
  // Mobile
  showMobileMenu = signal(false);
  showMobileFilters = signal(false);
  isMobile = signal(false);
  
  // Paginación
  currentPage = signal(1);
  itemsPerPage = signal(10);
  
  // Usuarios filtrados por búsqueda
  filteredUsers = computed(() => {
    const search = this.searchUser().toLowerCase().trim();
    if (!search) {
      return this.users();
    }
    return this.users().filter(user =>
      user.Nombre.toLowerCase().includes(search) ||
      user.Apellido.toLowerCase().includes(search) ||
      user.Email.toLowerCase().includes(search) ||
      user.Username?.toLowerCase().includes(search) ||
      `${user.Nombre} ${user.Apellido}`.toLowerCase().includes(search)
    );
  });
  
  // Usuarios paginados
  paginatedUsers = computed(() => {
    const filtered = this.filteredUsers();
    const start = (this.currentPage() - 1) * this.itemsPerPage();
    const end = start + this.itemsPerPage();
    return filtered.slice(start, end);
  });
  
  // Total de páginas
  totalPages = computed(() => {
    return Math.ceil(this.filteredUsers().length / this.itemsPerPage());
  });
  
  // Array de números de página para navegación
  pageNumbers = computed(() => {
    const total = this.totalPages();
    const current = this.currentPage();
    const pages: number[] = [];
    
    // Lógica para mostrar páginas cercanas a la actual
    let startPage = Math.max(1, current - 2);
    let endPage = Math.min(total, current + 2);
    
    // Ajustar si estamos cerca del inicio o fin
    if (current <= 3) {
      endPage = Math.min(5, total);
    }
    if (current >= total - 2) {
      startPage = Math.max(1, total - 4);
    }
    
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    
    return pages;
  });

  // Categorías disponibles
  categorias = ['Comida de Gato', 'Comida de Perro', 'Juguetes', 'Servicios'];

  newProduct = signal<Product>({
    Titulo: '',
    Descripcion: '',
    Categoria: '',
    Precio: 0,
    Stock: 0,
    Fecha_Caducidad: ''
  });

  // Exponer Math para usar en el template
  Math = Math;

  constructor(
    @Inject(PLATFORM_ID) private platformId: Object,
    public auth: AuthService, 
    private api: ApiService,
    private env: EnvironmentService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    // Efecto para resetear la página cuando cambia la búsqueda
    effect(() => {
      this.searchUser(); // Rastrear cambios en searchUser
      this.currentPage.set(1); // Resetear a página 1
    });
    
    // Detectar si es móvil solo en el navegador
    if (isPlatformBrowser(this.platformId)) {
      this.checkIfMobile();
      window.addEventListener('resize', () => this.checkIfMobile());
    }
  }

  ngOnInit() {
    const user = this.auth.user();
    if (!user?.is_staff) {
      this.router.navigate(['/shop']);
      return;
    }

    // Forzar detección móvil después de que el componente se inicialice
    if (isPlatformBrowser(this.platformId)) {
      setTimeout(() => this.checkIfMobile(), 0);
    }

    // Verificar si viene de una notificación
    this.route.queryParams.subscribe(params => {
      if (params['tab'] === 'pedidos') {
        this.activeTab.set('pedidos');
        this.loadOrders();
      } else {
        this.loadProducts();
      }
    });
    
    // En móvil, iniciar con vista de tarjetas
    if (this.isMobile()) {
      this.viewMode.set('cards');
    }
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

  getImageUrl(imagen?: string | File | null): string {
    if (this.imagePreviewUrl()) {
      return this.imagePreviewUrl()!;
    }
    if (!imagen || imagen instanceof File) {
      return 'assets/placeholder-product.png';
    }
    return this.env.getImageUrl(imagen);
  }

  private formatApiError(error: any, fallback: string): string {
    if (error?.status === 403) {
      return 'No tienes permisos de administrador. Cierra sesión y vuelve a entrar.';
    }
    if (error?.status === 401) {
      return 'Sesión expirada. Inicia sesión nuevamente.';
    }
    const detail = error?.error?.detail || error?.error?.error;
    if (typeof detail === 'string') return detail;
    if (error?.error && typeof error.error === 'object') {
      const firstKey = Object.keys(error.error)[0];
      const firstError = error.error[firstKey];
      if (Array.isArray(firstError)) return String(firstError[0]);
      if (typeof firstError === 'string') return firstError;
    }
    return fallback;
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
          this.errorMessage.set(this.formatApiError(error, 'Error al actualizar el producto'));
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
          this.errorMessage.set(this.formatApiError(error, 'Error al crear el producto'));
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

  // ==================== MÉTODOS DE GESTIÓN DE USUARIOS ====================

  loadUsers() {
    this.loadingUsers.set(true);
    this.api.get<{usuarios: User[], total: number}>('/usuarios/gestion/usuarios/').subscribe(
      (data) => {
        this.users.set(data.usuarios || []);
        this.loadingUsers.set(false);
      },
      (error: any) => {
        console.error('Error cargando usuarios:', error);
        this.errorMessage.set('Error al cargar los usuarios');
        this.loadingUsers.set(false);
        setTimeout(() => this.errorMessage.set(''), 3000);
      }
    );
  }

  esSuperusuario(): boolean {
    return this.auth.user()?.is_superuser || false;
  }

  private emptyEditForm(): UserEditForm {
    return {
      Username: '', Nombre: '', Apellido: '', Email: '', Telefono: '',
      Address: '', City: '', BirthDate: '', is_staff: false,
      is_superuser: false, is_active: true, password: '',
    };
  }

  openEditModal(user: User) {
    this.userToEdit.set(user);
    this.editFormData = {
      Username: user.Username || '',
      Nombre: user.Nombre,
      Apellido: user.Apellido,
      Email: user.Email,
      Telefono: user.Telefono,
      Address: user.Address || '',
      City: user.City || '',
      BirthDate: user.BirthDate ? String(user.BirthDate).substring(0, 10) : '',
      is_staff: user.is_staff,
      is_superuser: user.is_superuser,
      is_active: user.is_active,
      password: '',
    };
    this.showEditModal.set(true);
  }

  closeEditModal() {
    this.showEditModal.set(false);
    this.userToEdit.set(null);
    this.editFormData = this.emptyEditForm();
  }

  saveUserEdit() {
    const user = this.userToEdit();
    if (!user) return;

    this.savingUser.set(true);
    const payload: Record<string, unknown> = { ...this.editFormData };
    if (!payload['password']) {
      delete payload['password'];
    }

    this.api.put(`/usuarios/gestion/usuarios/${user.Id_User}/`, payload).subscribe({
      next: (response: any) => {
        this.successMessage.set(response.message || 'Usuario actualizado');
        this.closeEditModal();
        this.loadUsers();
        this.savingUser.set(false);
        setTimeout(() => this.successMessage.set(''), 3000);
      },
      error: (error: any) => {
        const err = error.error?.errors || error.error?.error;
        this.errorMessage.set(typeof err === 'string' ? err : 'Error al guardar usuario');
        this.savingUser.set(false);
        setTimeout(() => this.errorMessage.set(''), 4000);
      },
    });
  }

  canEditUser(user: User): boolean {
    if (user.Id_User === this.auth.user()?.id) return true;
    if (user.is_superuser && !this.esSuperusuario()) return false;
    return true;
  }

  toggleAdmin(user: User) {
    console.log('esSuperusuario():', this.esSuperusuario());
    console.log('auth.user():', this.auth.user());
    
    if (!this.esSuperusuario()) {
      this.errorMessage.set('Solo los superusuarios pueden crear administradores');
      setTimeout(() => this.errorMessage.set(''), 3000);
      return;
    }

    const confirmMsg = user.is_staff 
      ? `¿Estás seguro de quitar privilegios de administrador a ${user.Nombre} ${user.Apellido}?`
      : `¿Estás seguro de convertir a ${user.Nombre} ${user.Apellido} en administrador?`;

    if (!confirm(confirmMsg)) {
      return;
    }

    this.processingUser.set(user.Id_User);

    this.api.post(`/usuarios/gestion/usuarios/${user.Id_User}/convertir-admin/`, {
      is_staff: !user.is_staff
    }).subscribe(
      (response: any) => {
        this.successMessage.set(response.message);
        this.loadUsers(); // Recargar lista
        this.processingUser.set(null);
        setTimeout(() => this.successMessage.set(''), 3000);
      },
      (error: any) => {
        console.error('Error cambiando rol:', error);
        this.errorMessage.set(error.error?.error || 'Error al cambiar el rol del usuario');
        this.processingUser.set(null);
        setTimeout(() => this.errorMessage.set(''), 3000);
      }
    );
  }

  openDeleteModal(user: User) {
    this.userToDelete.set(user);
    this.deleteConfirmationName.set('');
    this.showDeleteModal.set(true);
  }

  closeDeleteModal() {
    this.showDeleteModal.set(false);
    this.userToDelete.set(null);
    this.deleteConfirmationName.set('');
  }

  confirmDelete() {
    const user = this.userToDelete();
    if (!user) return;

    const expectedName = `${user.Nombre} ${user.Apellido}`.toLowerCase();
    const enteredName = this.deleteConfirmationName().toLowerCase().trim();

    if (enteredName !== expectedName) {
      this.errorMessage.set('El nombre ingresado no coincide. Por favor, verifica e intenta nuevamente.');
      setTimeout(() => this.errorMessage.set(''), 3000);
      return;
    }

    this.deleteUser(user);
    this.closeDeleteModal();
  }

  deleteUser(user: User) {
    this.processingUser.set(user.Id_User);

    this.api.delete(`/usuarios/gestion/usuarios/${user.Id_User}/eliminar/`).subscribe(
      (response: any) => {
        this.successMessage.set(response.message);
        this.loadUsers(); // Recargar lista
        this.processingUser.set(null);
        setTimeout(() => this.successMessage.set(''), 3000);
      },
      (error: any) => {
        console.error('Error eliminando usuario:', error);
        this.errorMessage.set(error.error?.error || 'Error al eliminar el usuario');
        this.processingUser.set(null);
        setTimeout(() => this.errorMessage.set(''), 3000);
      }
    );
  }

  // ==================== MÉTODOS DE PAGINACIÓN ====================

  goToPage(page: number) {
    if (page >= 1 && page <= this.totalPages()) {
      this.currentPage.set(page);
    }
  }

  nextPage() {
    if (this.currentPage() < this.totalPages()) {
      this.currentPage.set(this.currentPage() + 1);
    }
  }

  previousPage() {
    if (this.currentPage() > 1) {
      this.currentPage.set(this.currentPage() - 1);
    }
  }

  changeItemsPerPage(items: number) {
    this.itemsPerPage.set(items);
    this.currentPage.set(1); // Volver a la primera página
  }

  formatearMoneda(valor: number): string {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(valor);
  }

  formatearFecha(fecha: string): string {
    const fechaObj = new Date(fecha);
    return fechaObj.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  // ==================== VISTA Y SELECCIÓN ====================

  toggleViewMode() {
    this.viewMode.set(this.viewMode() === 'table' ? 'cards' : 'table');
  }

  toggleUserSelection(userId: number) {
    const selected = new Set(this.selectedUsers());
    if (selected.has(userId)) {
      selected.delete(userId);
    } else {
      selected.add(userId);
    }
    this.selectedUsers.set(selected);
    this.selectAll.set(selected.size === this.paginatedUsers().length);
  }

  toggleSelectAll() {
    const newSelectAll = !this.selectAll();
    this.selectAll.set(newSelectAll);
    
    if (newSelectAll) {
      const allIds = new Set(this.paginatedUsers().map(u => u.Id_User));
      this.selectedUsers.set(allIds);
    } else {
      this.selectedUsers.set(new Set());
    }
  }

  isUserSelected(userId: number): boolean {
    return this.selectedUsers().has(userId);
  }

  // ==================== ACCIONES MASIVAS ====================

  openBulkActions() {
    if (this.selectedUsers().size === 0) {
      this.errorMessage.set('Selecciona al menos un usuario para realizar acciones masivas');
      setTimeout(() => this.errorMessage.set(''), 3000);
      return;
    }
    this.showBulkActions.set(true);
  }

  closeBulkActions() {
    this.showBulkActions.set(false);
  }

  bulkDeleteUsers() {
    const count = this.selectedUsers().size;
    if (!confirm(`¿Estás seguro de eliminar ${count} usuario${count > 1 ? 's' : ''}? Esta acción no se puede deshacer.`)) {
      return;
    }

    const userIds = Array.from(this.selectedUsers());
    this.api.post('/usuarios/gestion/usuarios/bulk-delete/', { user_ids: userIds }).subscribe(
      (response: any) => {
        this.successMessage.set(response.message || `${count} usuarios eliminados correctamente`);
        this.loadUsers();
        this.selectedUsers.set(new Set());
        this.selectAll.set(false);
        this.closeBulkActions();
        setTimeout(() => this.successMessage.set(''), 3000);
      },
      (error: any) => {
        console.error('Error en eliminación masiva:', error);
        this.errorMessage.set(error.error?.error || 'Error al eliminar usuarios');
        setTimeout(() => this.errorMessage.set(''), 3000);
      }
    );
  }

  bulkMakeAdmin() {
    const count = this.selectedUsers().size;
    if (!this.esSuperusuario()) {
      this.errorMessage.set('Solo los superusuarios pueden crear administradores');
      setTimeout(() => this.errorMessage.set(''), 3000);
      return;
    }

    if (!confirm(`¿Convertir ${count} usuario${count > 1 ? 's' : ''} en administrador${count > 1 ? 'es' : ''}?`)) {
      return;
    }

    const userIds = Array.from(this.selectedUsers());
    this.api.post('/usuarios/gestion/usuarios/bulk-make-admin/', { user_ids: userIds }).subscribe(
      (response: any) => {
        this.successMessage.set(response.message || `${count} usuarios actualizados correctamente`);
        this.loadUsers();
        this.selectedUsers.set(new Set());
        this.selectAll.set(false);
        this.closeBulkActions();
        setTimeout(() => this.successMessage.set(''), 3000);
      },
      (error: any) => {
        console.error('Error en cambio masivo de rol:', error);
        this.errorMessage.set(error.error?.error || 'Error al cambiar roles');
        setTimeout(() => this.errorMessage.set(''), 3000);
      }
    );
  }

  // ==================== EXPORTACIÓN ====================

  exportUsers() {
    const users = this.filteredUsers();
    const csv = this.convertToCSV(users);
    this.downloadCSV(csv, 'usuarios.csv');
  }

  exportOrders() {
    const orders = this.orders();
    const csv = this.convertOrdersToCSV(orders);
    this.downloadCSV(csv, 'pedidos.csv');
  }

  exportSalesReport() {
    const orders = this.orders();
    const report = this.generateSalesReport(orders);
    const csv = this.convertSalesReportToCSV(report);
    this.downloadCSV(csv, 'reporte_ventas.csv');
  }

  private convertToCSV(users: User[]): string {
    const headers = ['ID', 'Nombre', 'Apellido', 'Email', 'Teléfono', 'Dirección', 'Ciudad', 'Rol', 'Pedidos', 'Total Gastado', 'Fecha Registro'];
    const rows = users.map(u => [
      u.Id_User,
      u.Nombre,
      u.Apellido,
      u.Email,
      u.Telefono,
      u.Address,
      'N/A', // Ciudad no disponible en la interfaz actual
      u.is_superuser ? 'Superusuario' : (u.is_staff ? 'Administrador' : 'Usuario'),
      u.Total_Pedidos,
      u.Total_Gastado,
      new Date(u.FechaRegistro).toLocaleDateString('es-ES')
    ]);

    return [headers, ...rows].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
  }

  private convertOrdersToCSV(orders: Order[]): string {
    const headers = ['ID Pedido', 'Cliente', 'Email', 'Fecha', 'Total', 'Estado', 'Método de Pago', 'Dirección', 'Teléfono'];
    const rows = orders.map(o => [
      o.Id_Factura,
      o.usuario_nombre || 'N/A',
      o.usuario_email || 'N/A',
      new Date(o.Fecha).toLocaleDateString('es-ES'),
      o.Total,
      o.Estado,
      o.Metodo_Pago,
      o.Direccion_Envio,
      o.Telefono_Envio
    ]);

    return [headers, ...rows].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
  }

  private generateSalesReport(orders: Order[]) {
    const report: any = {
      totalVentas: orders.reduce((sum, o) => sum + o.Total, 0),
      totalPedidos: orders.length,
      porEstado: {} as Record<string, number>,
      porMetodoPago: {} as Record<string, number>
    };

    orders.forEach(order => {
      // Por estado
      report.porEstado[order.Estado] = (report.porEstado[order.Estado] || 0) + 1;
      // Por método de pago
      report.porMetodoPago[order.Metodo_Pago] = (report.porMetodoPago[order.Metodo_Pago] || 0) + 1;
    });

    return report;
  }

  private convertSalesReportToCSV(report: any): string {
    let csv = 'REPORTE DE VENTAS\n\n';
    csv += 'Resumen General\n';
    csv += `Total Ventas,${report.totalVentas}\n`;
    csv += `Total Pedidos,${report.totalPedidos}\n`;
    csv += `Promedio por Pedido,${(report.totalVentas / report.totalPedidos).toFixed(2)}\n\n`;
    
    csv += 'Pedidos por Estado\n';
    csv += 'Estado,Cantidad\n';
    Object.entries(report.porEstado).forEach(([estado, cantidad]) => {
      csv += `${estado},${cantidad}\n`;
    });
    
    csv += '\nPedidos por Método de Pago\n';
    csv += 'Método,Cantidad\n';
    Object.entries(report.porMetodoPago).forEach(([metodo, cantidad]) => {
      csv += `${metodo},${cantidad}\n`;
    });

    return csv;
  }

  private downloadCSV(content: string, filename: string) {
    const blob = new Blob(['\ufeff' + content], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    this.successMessage.set(`Archivo ${filename} descargado correctamente`);
    setTimeout(() => this.successMessage.set(''), 3000);
  }

  // ==================== FUNCIONES MOBILE ====================

  checkIfMobile() {
    if (isPlatformBrowser(this.platformId)) {
      this.isMobile.set(window.innerWidth <= 768);
    }
  }

  toggleMobileMenu() {
    this.showMobileMenu.set(!this.showMobileMenu());
  }

  closeMobileMenu() {
    this.showMobileMenu.set(false);
  }

  toggleMobileFilters() {
    this.showMobileFilters.set(!this.showMobileFilters());
  }

  changeTab(tab: 'productos' | 'pedidos' | 'usuarios' | 'miaubot') {
    this.activeTab.set(tab);
    this.closeMobileMenu();
    
    if (tab === 'pedidos') {
      this.loadOrders();
    } else if (tab === 'usuarios') {
      this.loadUsers();
    } else if (tab === 'miaubot') {
      this.loadAprendizajes();
    }
  }

  // ==================== MIAUBOT APRENDIZAJE ====================

  loadAprendizajes() {
    this.loadingAprendizaje.set(true);
    const estado = this.filtroAprendizaje();
    this.api.get<{ items: MiauBotAprendizaje[]; pendientes: number }>(
      `/usuarios/gestion/miaubot/aprendizaje/?estado=${estado}`
    ).subscribe({
      next: (data) => {
        this.aprendizajes.set(data.items || []);
        this.pendientesCount.set(data.pendientes || 0);
        this.loadingAprendizaje.set(false);
      },
      error: (error: any) => {
        console.error('Error cargando aprendizajes:', error);
        this.errorMessage.set('Error al cargar aprendizajes de MiauBot');
        this.loadingAprendizaje.set(false);
        setTimeout(() => this.errorMessage.set(''), 3000);
      },
    });
  }

  cambiarFiltroAprendizaje(estado: 'pendiente' | 'aprobado' | 'rechazado' | 'todos') {
    this.filtroAprendizaje.set(estado);
    this.loadAprendizajes();
  }

  abrirEditarAprendizaje(item: MiauBotAprendizaje) {
    this.aprendizajeEdit.set(item);
    this.respuestaEditada.set(item.respuesta);
    this.showAprendizajeModal.set(true);
  }

  cerrarAprendizajeModal() {
    this.showAprendizajeModal.set(false);
    this.aprendizajeEdit.set(null);
    this.respuestaEditada.set('');
  }

  guardarRespuestaAprendizaje() {
    const item = this.aprendizajeEdit();
    if (!item) return;

    this.processingAprendizaje.set(item.id);
    this.api.put(`/usuarios/gestion/miaubot/aprendizaje/${item.id}/`, {
      respuesta: this.respuestaEditada(),
    }).subscribe({
      next: () => {
        this.successMessage.set('Respuesta actualizada');
        this.cerrarAprendizajeModal();
        this.loadAprendizajes();
        this.processingAprendizaje.set(null);
        setTimeout(() => this.successMessage.set(''), 3000);
      },
      error: () => {
        this.errorMessage.set('Error al guardar respuesta');
        this.processingAprendizaje.set(null);
        setTimeout(() => this.errorMessage.set(''), 3000);
      },
    });
  }

  aprobarAprendizaje(id: number) {
    this.processingAprendizaje.set(id);
    this.api.post(`/usuarios/gestion/miaubot/aprendizaje/${id}/`, { accion: 'aprobar' }).subscribe({
      next: (res: any) => {
        this.successMessage.set(res.message || 'Aprendizaje aprobado');
        this.loadAprendizajes();
        this.processingAprendizaje.set(null);
        setTimeout(() => this.successMessage.set(''), 3000);
      },
      error: () => {
        this.errorMessage.set('Error al aprobar');
        this.processingAprendizaje.set(null);
        setTimeout(() => this.errorMessage.set(''), 3000);
      },
    });
  }

  rechazarAprendizaje(id: number) {
    if (!confirm('¿Rechazar esta propuesta de aprendizaje?')) return;

    this.processingAprendizaje.set(id);
    this.api.post(`/usuarios/gestion/miaubot/aprendizaje/${id}/`, { accion: 'rechazar' }).subscribe({
      next: (res: any) => {
        this.successMessage.set(res.message || 'Aprendizaje rechazado');
        this.loadAprendizajes();
        this.processingAprendizaje.set(null);
        setTimeout(() => this.successMessage.set(''), 3000);
      },
      error: () => {
        this.errorMessage.set('Error al rechazar');
        this.processingAprendizaje.set(null);
        setTimeout(() => this.errorMessage.set(''), 3000);
      },
    });
  }

  aprobarYGuardarAprendizaje() {
    const item = this.aprendizajeEdit();
    if (!item) return;

    this.processingAprendizaje.set(item.id);
    this.api.put(`/usuarios/gestion/miaubot/aprendizaje/${item.id}/`, {
      respuesta: this.respuestaEditada(),
    }).subscribe({
      next: () => {
        this.api.post(`/usuarios/gestion/miaubot/aprendizaje/${item.id}/`, { accion: 'aprobar' }).subscribe({
          next: (res: any) => {
            this.successMessage.set(res.message || 'Aprobado con respuesta corregida');
            this.cerrarAprendizajeModal();
            this.loadAprendizajes();
            this.processingAprendizaje.set(null);
            setTimeout(() => this.successMessage.set(''), 3000);
          },
          error: () => {
            this.errorMessage.set('Error al aprobar');
            this.processingAprendizaje.set(null);
          },
        });
      },
      error: () => {
        this.errorMessage.set('Error al guardar respuesta');
        this.processingAprendizaje.set(null);
      },
    });
  }
}
