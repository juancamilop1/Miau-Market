import { Component, OnInit, signal, computed, inject, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../auth.service';
import { ApiService } from '../../services/api.service';
import { StarRating } from '../star-rating/star-rating';
import { Chart, ChartConfiguration, registerables } from 'chart.js';

// Registrar todos los componentes de Chart.js
Chart.register(...registerables);

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
  selector: 'mm-dashboard',
  standalone: true,
  imports: [CommonModule, StarRating],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css']
})
export class Dashboard implements OnInit, AfterViewInit {
  auth = inject(AuthService);
  private api = inject(ApiService);
  private router = inject(Router);

  // Referencias a los canvas de los gráficos
  @ViewChild('ventasChart') ventasChartRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('categoriasChart') categoriasChartRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('estadosPedidosChart') estadosPedidosChartRef!: ElementRef<HTMLCanvasElement>;

  // Instancias de los gráficos
  private ventasChart?: Chart;
  private categoriasChart?: Chart;
  private estadosPedidosChart?: Chart;

  // Datos cargados
  products = signal<Product[]>([]);
  orders = signal<Order[]>([]);
  users = signal<User[]>([]);
  ratings = signal<ProductRating[]>([]);
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

  // Estadísticas de calificaciones
  productosMejorCalificados = computed(() => {
    return this.ratings()
      .filter(r => r.Total_Reviews > 0)
      .sort((a, b) => b.Rating_Promedio - a.Rating_Promedio)
      .slice(0, 5);
  });

  totalReviews = computed(() => {
    return this.ratings().reduce((sum, r) => sum + r.Total_Reviews, 0);
  });

  promedioGeneralRating = computed(() => {
    const ratingsConReviews = this.ratings().filter(r => r.Total_Reviews > 0);
    if (ratingsConReviews.length === 0) return 0;
    
    const suma = ratingsConReviews.reduce((sum, r) => sum + r.Rating_Promedio, 0);
    return suma / ratingsConReviews.length;
  });

  ngOnInit() {
    // Verificar que sea admin
    if (!this.auth.user()?.is_staff) {
      this.router.navigate(['/shop']);
      return;
    }

    this.cargarDatos();
  }

  ngAfterViewInit() {
    // Los gráficos se crearán después de que los datos se carguen
    // en verificarCargaCompleta()
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

    // Cargar ratings de productos
    this.api.get<{ratings: ProductRating[]}>('/usuarios/ratings/').subscribe(
      (data: any) => {
        this.ratings.set(data.ratings || []);
        this.verificarCargaCompleta();
      },
      (error: any) => {
        console.error('Error cargando ratings:', error);
        this.verificarCargaCompleta();
      }
    );
  }

  private cargasCompletadas = 0;
  private verificarCargaCompleta() {
    this.cargasCompletadas++;
    if (this.cargasCompletadas >= 3) { // Productos, pedidos y ratings son críticos
      this.loading.set(false);
      // Crear gráficos después de cargar los datos
      setTimeout(() => this.crearGraficos(), 100);
    }
  }

  private crearGraficos() {
    this.crearGraficoVentas();
    this.crearGraficoCategorias();
    this.crearGraficoEstadosPedidos();
  }

  private crearGraficoVentas() {
    if (!this.ventasChartRef) return;

    const ctx = this.ventasChartRef.nativeElement.getContext('2d');
    if (!ctx) return;

    // Destruir gráfico anterior si existe
    if (this.ventasChart) {
      this.ventasChart.destroy();
    }

    const ventas = this.ventasPorMes();
    
    const config: ChartConfiguration<'line'> = {
      type: 'line',
      data: {
        labels: ventas.map(v => v.mes),
        datasets: [{
          label: 'Ingresos',
          data: ventas.map(v => v.total),
          borderColor: '#ff6f00',
          backgroundColor: 'rgba(255, 111, 0, 0.1)',
          borderWidth: 3,
          tension: 0.4,
          fill: true,
          pointBackgroundColor: '#ff6f00',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--mm-black') || '#333',
              font: {
                size: 14,
                weight: 'bold'
              }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            titleFont: {
              size: 14
            },
            bodyFont: {
              size: 13
            },
            callbacks: {
              label: (context) => {
                const value = context.parsed.y ?? 0;
                return `Ingresos: ${this.formatearMoneda(value)}`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--mm-gray-700') || '#666',
              callback: (value) => {
                return this.formatearMoneda(Number(value));
              }
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          x: {
            ticks: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--mm-gray-700') || '#666'
            },
            grid: {
              display: false
            }
          }
        }
      }
    };

    this.ventasChart = new Chart(ctx, config);
  }

  private crearGraficoCategorias() {
    if (!this.categoriasChartRef) return;

    const ctx = this.categoriasChartRef.nativeElement.getContext('2d');
    if (!ctx) return;

    if (this.categoriasChart) {
      this.categoriasChart.destroy();
    }

    const categorias = this.estadisticasCategorias();
    
    // Colores variados para las categorías
    const colores = [
      '#ff6f00',
      '#ffa726',
      '#ffb74d',
      '#ffc107',
      '#ffca28',
      '#ffd54f',
      '#ffe082',
      '#ffecb3'
    ];

    const config: ChartConfiguration<'doughnut'> = {
      type: 'doughnut',
      data: {
        labels: categorias.map(c => c.categoria),
        datasets: [{
          data: categorias.map(c => c.cantidad),
          backgroundColor: colores.slice(0, categorias.length),
          borderColor: '#fff',
          borderWidth: 2,
          hoverOffset: 10
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'right',
            labels: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--mm-black') || '#333',
              font: {
                size: 12
              },
              padding: 15,
              usePointStyle: true
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            callbacks: {
              label: (context) => {
                const label = context.label || '';
                const value = context.parsed;
                const total = categorias.reduce((sum, c) => sum + c.cantidad, 0);
                const porcentaje = ((value / total) * 100).toFixed(1);
                return `${label}: ${value} productos (${porcentaje}%)`;
              }
            }
          }
        }
      }
    };

    this.categoriasChart = new Chart(ctx, config);
  }

  private crearGraficoEstadosPedidos() {
    if (!this.estadosPedidosChartRef) return;

    const ctx = this.estadosPedidosChartRef.nativeElement.getContext('2d');
    if (!ctx) return;

    if (this.estadosPedidosChart) {
      this.estadosPedidosChart.destroy();
    }

    const config: ChartConfiguration<'bar'> = {
      type: 'bar',
      data: {
        labels: ['Pendientes', 'Enviados', 'Entregados'],
        datasets: [{
          label: 'Cantidad de Pedidos',
          data: [
            this.pedidosPendientes(),
            this.pedidosEnviados(),
            this.pedidosEntregados()
          ],
          backgroundColor: [
            'rgba(255, 193, 7, 0.7)',
            'rgba(33, 150, 243, 0.7)',
            'rgba(76, 175, 80, 0.7)'
          ],
          borderColor: [
            '#ffc107',
            '#2196f3',
            '#4caf50'
          ],
          borderWidth: 2,
          borderRadius: 8,
          barThickness: 60
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            callbacks: {
              label: (context) => {
                return `${context.parsed.y} pedido${context.parsed.y !== 1 ? 's' : ''}`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--mm-gray-700') || '#666',
              stepSize: 1
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          x: {
            ticks: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--mm-gray-700') || '#666',
              font: {
                size: 13,
                weight: 'bold'
              }
            },
            grid: {
              display: false
            }
          }
        }
      }
    };

    this.estadosPedidosChart = new Chart(ctx, config);
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
