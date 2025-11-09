import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../auth.service';

interface Producto {
  Id_Products: number;
  Cantidad: number;
  Precio_Unitario: number;
  Titulo: string;
  Imagen: string | null;
}

interface Pedido {
  Id_Factura: number;
  Total: number;
  Fecha_Compra: string;
  Estado: string;
  Direccion_Envio: string;
  Telefono_Envio: string;
  productos: Producto[];
}

@Component({
  selector: 'app-my-orders',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './my-orders.html',
  styleUrl: './my-orders.css'
})
export class MyOrders implements OnInit {
  private api = inject(ApiService);
  private auth = inject(AuthService);
  private router = inject(Router);
  
  pedidos = signal<Pedido[]>([]);
  cargando = signal(true);
  error = signal('');
  
  ngOnInit() {
    if (!this.auth.user()) {
      this.router.navigate(['/login']);
      return;
    }
    
    this.cargarPedidos();
  }
  
  cargarPedidos() {
    this.cargando.set(true);
    this.error.set('');
    
    this.api.get<Pedido[]>('/usuarios/mis-pedidos/').subscribe({
      next: (data) => {
        this.pedidos.set(data);
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('Error cargando pedidos:', err);
        this.error.set('Error al cargar tus pedidos. Por favor intenta de nuevo.');
        this.cargando.set(false);
      }
    });
  }
  
  getEstadoClase(estado: string): string {
    const clases: { [key: string]: string } = {
      'Pendiente': 'estado-pendiente',
      'Enviado': 'estado-enviado',
      'Entregado': 'estado-entregado',
      'Devuelto': 'estado-devuelto'
    };
    return clases[estado] || 'estado-pendiente';
  }
  
  getEstadoIcono(estado: string): string {
    const iconos: { [key: string]: string } = {
      'Pendiente': '⏳',
      'Enviado': '📦',
      'Entregado': '✅',
      'Devuelto': '↩️'
    };
    return iconos[estado] || '📋';
  }
  
  formatearFecha(fecha: string): string {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  getImagenUrl(imagen: string | null): string {
    if (!imagen) return 'assets/placeholder-product.png';
    if (imagen.startsWith('http')) return imagen;
    // Si no empieza con /media/, agregarlo
    if (!imagen.startsWith('/media/')) {
      return `http://localhost:8000/media/${imagen}`;
    }
    return `http://localhost:8000${imagen}`;
  }
  
  volverATienda() {
    this.router.navigate(['/shop']);
  }
}
