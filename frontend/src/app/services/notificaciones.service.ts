import { Injectable, inject, signal, effect } from '@angular/core';
import { ApiService } from './api.service';
import { AuthService } from '../auth.service';
import { interval } from 'rxjs';
import { switchMap, catchError, filter } from 'rxjs/operators';

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
  private auth = inject(AuthService);
  
  notificaciones = signal<Notificacion[]>([]);
  noLeidas = signal<number>(0);
  
  constructor() {
    effect(() => {
      if (this.auth.isLogged()) {
        this.cargarNotificaciones();
      } else {
        this.notificaciones.set([]);
        this.noLeidas.set(0);
      }
    });

    interval(30000).pipe(
      filter(() => this.auth.isLogged()),
      switchMap(() => this.api.post('/usuarios/notificaciones/verificar-caducados/', {})),
      switchMap(() => this.api.get<Notificacion[]>('/usuarios/notificaciones/')),
      catchError(() => this.api.get<Notificacion[]>('/usuarios/notificaciones/'))
    ).subscribe({
      next: (data: Notificacion[]) => {
        this.notificaciones.set(data);
        this.noLeidas.set(data.filter((n: Notificacion) => !n.Leida).length);
      },
      error: (error) => console.error('Error actualizando notificaciones:', error)
    });
  }
  
  cargarNotificaciones() {
    if (!this.auth.isLogged()) return;

    this.api.post('/usuarios/notificaciones/verificar-caducados/', {}).subscribe({
      next: () => this.obtenerNotificaciones(),
      error: () => this.obtenerNotificaciones()
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
