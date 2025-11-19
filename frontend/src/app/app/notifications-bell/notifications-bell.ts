import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { NotificacionesService, Notificacion } from '../../services/notificaciones.service';
import { AuthService } from '../../auth.service';

@Component({
  selector: 'app-notifications-bell',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notifications-bell.html',
  styleUrl: './notifications-bell.css'
})
export class NotificationsBell implements OnInit {
  notifService = inject(NotificacionesService);
  auth = inject(AuthService);
  router = inject(Router);
  
  showPanel = signal(false);
  
  ngOnInit() {
    // Cargar notificaciones al iniciar si el usuario está autenticado
    if (this.auth.user()) {
      this.notifService.cargarNotificaciones();
    }
  }
  
  togglePanel() {
    this.showPanel.update(val => !val);
  }
  
  clickNotificacion(notif: Notificacion, event: Event) {
    event.stopPropagation();
    
    // Marcar como leída
    if (!notif.Leida) {
      this.notifService.marcarComoLeida(notif.id);
    }
    
    // Cerrar el panel
    this.showPanel.set(false);
    
    // Redirigir según el tipo de notificación
    const user = this.auth.user();
    
    if (notif.Tipo === 'nuevo_pedido' && user?.is_staff) {
      // Admin: ir a administración de pedidos (pestaña de pedidos)
      this.router.navigate(['/admin'], { queryParams: { tab: 'pedidos' } });
    } else if (notif.Tipo === 'producto_caducado' && user?.is_staff) {
      // Admin: ir a administración de productos (pestaña de productos)
      this.router.navigate(['/admin'], { queryParams: { tab: 'productos' } });
    } else if (['pendiente', 'enviado', 'entregado', 'devuelto'].includes(notif.Tipo)) {
      // Usuario: ir a mis pedidos
      this.router.navigate(['/my-orders']);
    }
  }
  
  marcarLeida(id: number, event: Event) {
    event.stopPropagation();
    this.notifService.marcarComoLeida(id);
  }
  
  marcarTodasLeidas(event: Event) {
    event.stopPropagation();
    this.notifService.marcarTodasComoLeidas();
  }
  
  getIconoTipo(tipo: string): string {
    const iconos: { [key: string]: string } = {
      'nuevo_pedido': '🛒',
      'pendiente': '⏳',
      'enviado': '📦',
      'entregado': '✅',
      'devuelto': '↩️',
      'producto_caducado': '⚠️'
    };
    return iconos[tipo] || '🔔';
  }
  
  formatearFecha(fecha: string): string {
    const date = new Date(fecha);
    const ahora = new Date();
    const diff = ahora.getTime() - date.getTime();
    const minutos = Math.floor(diff / 60000);
    const horas = Math.floor(diff / 3600000);
    const dias = Math.floor(diff / 86400000);
    
    if (minutos < 1) return 'Ahora';
    if (minutos < 60) return `Hace ${minutos} min`;
    if (horas < 24) return `Hace ${horas}h`;
    if (dias < 7) return `Hace ${dias}d`;
    return date.toLocaleDateString();
  }
}
