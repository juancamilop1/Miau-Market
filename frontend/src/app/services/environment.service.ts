import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class EnvironmentService {
  private backendUrl: string;

  constructor() {
    this.backendUrl = this.getBackendUrl();
  }

  /**
   * Prioridad: environment.apiUrl (prod) → meta miau-api → LAN → localhost
   */
  private getBackendUrl(): string {
    const fromBuild = (environment.apiUrl || '').trim().replace(/\/$/, '');
    if (fromBuild) {
      return fromBuild;
    }

    if (typeof document !== 'undefined') {
      const meta = document.querySelector('meta[name="miau-api"]');
      const content = (meta?.getAttribute('content') || '').trim().replace(/\/$/, '');
      if (content) {
        return content;
      }
    }

    if (typeof window !== 'undefined') {
      const currentHost = window.location.hostname;
      if (currentHost !== 'localhost' && currentHost !== '127.0.0.1') {
        return `http://${currentHost}:8000`;
      }
    }
    return 'http://localhost:8000';
  }

  /**
   * Obtiene la URL base del backend
   */
  getBackend(): string {
    return this.backendUrl;
  }

  /**
   * Obtiene la URL de la API
   */
  getApiUrl(): string {
    return `${this.backendUrl}/api`;
  }

  /**
   * Obtiene la URL completa para una imagen del backend
   */
  getImageUrl(imagen: string | null | undefined): string {
    if (!imagen) return 'assets/placeholder-product.png';
    if (imagen.startsWith('http')) return imagen;
    
    // Si la imagen ya tiene /media/, solo agregar el backend
    if (imagen.startsWith('/media/')) {
      return `${this.backendUrl}${imagen}`;
    }
    
    // Si no, agregar /media/ también
    return `${this.backendUrl}/media/${imagen}`;
  }

  /**
   * Obtiene la URL del chatbot
   */
  getChatbotUrl(): string {
    return `${this.backendUrl}/api/usuarios/chatbot/`;
  }

  getChatbotConfigUrl(): string {
    return `${this.backendUrl}/api/usuarios/chatbot/config/`;
  }
}
