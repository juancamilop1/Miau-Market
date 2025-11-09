import { Injectable, inject, signal } from '@angular/core';
import { ApiService } from './api.service';
import { interval } from 'rxjs';
import { switchMap, catchError } from 'rxjs/operators';
import { of } from 'rxjs';

export interface Notificacion {
  id: number;
  Id_User: number;
  Titulo: string;
  Mensaje: string;
  Tipo: string;
  Leida: boolean;
  Fecha_Creacion: string;
  Id_Factura?: number;
}

@Injectable({
  providedIn: 'root'
})
export class NotificacionesService {
  private api = inject(ApiService);
  
  notificaciones = signal<Notificacion[]>([]);
  noLeidas = signal<number>(0);
  
  constructor() {
    // Actualizar notificaciones cada 30 segundos
    interval(30000).pipe(
      switchMap(() => {
        // Verificar productos caducados antes de obtener notificaciones
        return this.api.post('/usuarios/notificaciones/verificar-caducados/', {}).pipe(
          switchMap(() => this.api.get<Notificacion[]>('/usuarios/notificaciones/')),
          // Si falla la verificación, continuar con las notificaciones
          catchError(() => this.api.get<Notificacion[]>('/usuarios/notificaciones/'))
        );
      })
    ).subscribe({
      next: (data: Notificacion[]) => {
        this.notificaciones.set(data);
        this.noLeidas.set(data.filter((n: Notificacion) => !n.Leida).length);
      },
      error: (error) => console.error('Error actualizando notificaciones:', error)
    });
  }
  
  cargarNotificaciones() {
    // Primero verificar productos caducados (solo para admins)
    this.api.post('/usuarios/notificaciones/verificar-caducados/', {}).subscribe({
      next: () => {
        // Después cargar notificaciones
        this.obtenerNotificaciones();
      },
      error: () => {
        // Si falla la verificación, igual cargar notificaciones
        this.obtenerNotificaciones();
      }
    });
  }
  
  private obtenerNotificaciones() {
    this.api.get<Notificacion[]>('/usuarios/notificaciones/').subscribe({
      next: (data) => {
        this.notificaciones.set(data);
        this.noLeidas.set(data.filter(n => !n.Leida).length);
      },
      error: (error) => console.error('Error cargando notificaciones:', error)
    });
  }
  
  marcarComoLeida(id: number) {
    this.api.put(`/usuarios/notificaciones/${id}/leer/`, {}).subscribe({
      next: () => {
        const notifs = this.notificaciones();
        const index = notifs.findIndex(n => n.id === id);
        if (index !== -1) {
          notifs[index].Leida = true;
          this.notificaciones.set([...notifs]);
          this.noLeidas.set(notifs.filter(n => !n.Leida).length);
        }
      },
      error: (error) => console.error('Error marcando como leída:', error)
    });
  }
  
  marcarTodasComoLeidas() {
    this.api.put('/usuarios/notificaciones/leer-todas/', {}).subscribe({
      next: () => {
        const notifs = this.notificaciones().map(n => ({ ...n, Leida: true }));
        this.notificaciones.set(notifs);
        this.noLeidas.set(0);
      },
      error: (error) => console.error('Error marcando todas como leídas:', error)
    });
  }
}
