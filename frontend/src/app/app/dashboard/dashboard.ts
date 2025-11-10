import { Component, OnInit, signal, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../auth.service';
import { ApiService } from '../../services/api.service';

interface Product {
  Id_Products: number;
  Titulo: string;
  Categoria: string;
  Precio: number;
  Stock: number;
  Fecha_Caducidad?: string;
}

interface Order {
  Id_Factura: number;
  Id_User: number;
  Fecha: string;
  Total: number;
  Estado: string;
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
  id: number;
  name: string;
  email: string;
}

interface EstadisticaCategoria {
  categoria: string;
  cantidad: number;
  porcentaje: number;
}

interface ProductoMasVendido {
  nombre: string;
  cantidad: number;
  ingresos: number;
}

@Component({
  selector: 'mm-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css']
})
export class Dashboard implements OnInit {
  auth = inject(AuthService);
  private api = inject(ApiService);
  private router = inject(Router);

  // Datos cargados
  products = signal<Product[]>([]);
  orders = signal<Order[]>([]);
  users = signal<User[]>([]);
  loading = signal(true);

  // Estadísticas calculadas
  totalProductos = computed(() => this.products().length);
  totalPedidos = computed(() => this.orders().length);
  totalUsuarios = computed(() => this.users().length);
  
  ingresosTotales = computed(() => {
    return this.orders().reduce((sum, order) => sum + order.Total, 0);
  });

  pedidosPendientes = computed(() => {
    return this.orders().filter(o => o.Estado === 'Pendiente').length;
  });

  pedidosEnviados = computed(() => {
    return this.orders().filter(o => o.Estado === 'Enviado').length;
  });

  pedidosEntregados = computed(() => {
    return this.orders().filter(o => o.Estado === 'Entregado').length;
  });

  ticketPromedio = computed(() => {
    const total = this.ingresosTotales();
    const cantidad = this.totalPedidos();
    return cantidad > 0 ? total / cantidad : 0;
  });

  // Productos con bajo stock (menos de 10)
  productosStockBajo = computed(() => {
    return this.products().filter(p => p.Stock < 10);
  });

  // Productos por categoría
  estadisticasCategorias = computed(() => {
    const productos = this.products();
    const total = productos.length;
    
    if (total === 0) return [];

    const categorias: { [key: string]: number } = {};
    
    productos.forEach(p => {
      categorias[p.Categoria] = (categorias[p.Categoria] || 0) + 1;
    });

    return Object.entries(categorias).map(([categoria, cantidad]) => ({
      categoria,
      cantidad,
      porcentaje: (cantidad / total) * 100
    })).sort((a, b) => b.cantidad - a.cantidad);
  });

  // Productos más vendidos
  productosMasVendidos = computed(() => {
    const ventas: { [key: string]: { cantidad: number, ingresos: number } } = {};
    
    this.orders().forEach(order => {
      if (order.productos) {
        order.productos.forEach(p => {
          if (!ventas[p.Titulo]) {
            ventas[p.Titulo] = { cantidad: 0, ingresos: 0 };
          }
          ventas[p.Titulo].cantidad += p.Cantidad;
          ventas[p.Titulo].ingresos += p.Subtotal;
        });
      }
    });

    return Object.entries(ventas)
      .map(([nombre, datos]) => ({
        nombre,
        cantidad: datos.cantidad,
        ingresos: datos.ingresos
      }))
      .sort((a, b) => b.cantidad - a.cantidad)
      .slice(0, 5); // Top 5
  });

  // Ventas por mes (últimos 6 meses)
  ventasPorMes = computed(() => {
    const meses: { [key: string]: number } = {};
    const hoy = new Date();
    
    // Inicializar últimos 6 meses
    for (let i = 5; i >= 0; i--) {
      const fecha = new Date(hoy.getFullYear(), hoy.getMonth() - i, 1);
      const key = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`;
      meses[key] = 0;
    }

    // Contar ventas
    this.orders().forEach(order => {
      const fecha = new Date(order.Fecha);
      const key = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`;
      if (meses.hasOwnProperty(key)) {
        meses[key] += order.Total;
      }
    });

    return Object.entries(meses).map(([mes, total]) => ({
      mes: this.formatearMes(mes),
      total
    }));
  });

  ngOnInit() {
    // Verificar que sea admin
    if (!this.auth.user()?.is_staff) {
      this.router.navigate(['/shop']);
      return;
    }

    this.cargarDatos();
  }

  cargarDatos() {
    this.loading.set(true);
    
    // Cargar productos
    this.api.get<Product[]>('/usuarios/productos/').subscribe(
      (data: any) => {
        this.products.set(data || []);
        this.verificarCargaCompleta();
      },
      (error: any) => {
        console.error('Error cargando productos:', error);
        this.verificarCargaCompleta();
      }
    );

    // Cargar pedidos
    this.api.get<Order[]>('/usuarios/pedidos/').subscribe(
      (data: any) => {
        this.orders.set(data || []);
        this.verificarCargaCompleta();
      },
      (error: any) => {
        console.error('Error cargando pedidos:', error);
        this.verificarCargaCompleta();
      }
    );

    // Cargar usuarios (si hay endpoint disponible)
    this.api.get<User[]>('/usuarios/usuarios/').subscribe(
      (data: any) => {
        this.users.set(data || []);
        this.verificarCargaCompleta();
      },
      (error: any) => {
        console.error('Error cargando usuarios:', error);
        // No es crítico, podemos continuar sin este dato
        this.verificarCargaCompleta();
      }
    );
  }

  private cargasCompletadas = 0;
  private verificarCargaCompleta() {
    this.cargasCompletadas++;
    if (this.cargasCompletadas >= 2) { // Productos y pedidos son críticos
      this.loading.set(false);
    }
  }

  formatearMes(mes: string): string {
    const [year, month] = mes.split('-');
    const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    return `${meses[parseInt(month) - 1]} ${year}`;
  }

  formatearMoneda(valor: number): string {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(valor);
  }

  getBarHeight(valor: number): number {
    const ventas = this.ventasPorMes();
    if (ventas.length === 0) return 0;
    
    const maxVenta = Math.max(...ventas.map(v => v.total));
    if (maxVenta === 0) return 0;
    
    return (valor / maxVenta) * 100;
  }

  volverAAdmin() {
    this.router.navigate(['/admin']);
  }
}
