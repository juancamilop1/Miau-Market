import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class EnvironmentService {
  private backendUrl: string;

  constructor() {
    this.backendUrl = this.getBackendUrl();
  }

  /**
   * Determina la URL del backend según el hostname actual
   */
  private getBackendUrl(): string {
    if (typeof window !== 'undefined') {
      const currentHost = window.location.hostname;
      // Si accedes desde la red (no localhost), usa la misma IP del frontend
      if (currentHost !== 'localhost' && currentHost !== '127.0.0.1') {
        return `http://${currentHost}:8000`;
      }
    }
    // Por defecto, usa localhost
    return 'https://adaptable-exploration-production-77dc.up.railway.app';
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
}
