import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { isPlatformBrowser } from '@angular/common';
import { PLATFORM_ID, inject } from '@angular/core';

// Interfaces para los datos
export interface LoginRequest {
  Email: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  token?: string;
  user: {
    id: number;
    email: string;
    name?: string; // Nuevo formato
    nombre?: string; // Formato antiguo (compatibilidad)
    is_staff?: boolean;
    Address?: string;
    Telefono?: string;
    Ciudad?: string;
    Edad?: number;
    Apellido?: string;
  };
}

export interface RegisterRequest {
  Nombre: string;
  Apellido: string;
  Email: string;
  password: string;
  password2: string;
  Telefono?: string;
  Address?: string;
  City?: string;
  BirthDate?: string;
}

export interface RegisterResponse {
  id: number;
  Nombre: string;
  Apellido: string;
  Email: string;
  Telefono?: string;
  Address?: string;
  City?: string;
  BirthDate?: string;
  FechaRegistro: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000/api';
  private platformId = inject(PLATFORM_ID);

  constructor(private http: HttpClient) { }

  // Método privado para obtener headers con token
  private getHeaders(): HttpHeaders {
    let headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    
    if (isPlatformBrowser(this.platformId)) {
      const token = localStorage.getItem('token');
      if (token) {
        headers = headers.set('Authorization', `Token ${token}`);
      }
    }
    
    return headers;
  }

  // Método privado para obtener token
  private getToken(): string | null {
    if (isPlatformBrowser(this.platformId)) {
      return localStorage.getItem('token');
    }
    return null;
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.baseUrl}/usuarios/login/`, credentials);
  }

  register(userData: RegisterRequest): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(`${this.baseUrl}/usuarios/registro/`, userData);
  }

  // Métodos genéricos CRUD
  get<T>(endpoint: string): Observable<T> {
    return this.http.get<T>(`${this.baseUrl}${endpoint}`, {
      headers: this.getHeaders()
    });
  }

  post<T>(endpoint: string, data: any): Observable<T> {
    // Si es FormData, no agregar Content-Type (el navegador lo hará)
    if (data instanceof FormData) {
      const token = this.getToken();
      let headers = new HttpHeaders();
      if (token) {
        headers = headers.set('Authorization', `Token ${token}`);
      }
      return this.http.post<T>(`${this.baseUrl}${endpoint}`, data, { headers });
    }
    return this.http.post<T>(`${this.baseUrl}${endpoint}`, data, {
      headers: this.getHeaders()
    });
  }

  put<T>(endpoint: string, data: any): Observable<T> {
    // Si es FormData, no agregar Content-Type
    if (data instanceof FormData) {
      const token = this.getToken();
      let headers = new HttpHeaders();
      if (token) {
        headers = headers.set('Authorization', `Token ${token}`);
      }
      return this.http.put<T>(`${this.baseUrl}${endpoint}`, data, { headers });
    }
    return this.http.put<T>(`${this.baseUrl}${endpoint}`, data, {
      headers: this.getHeaders()
    });
  }

  delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(`${this.baseUrl}${endpoint}`, {
      headers: this.getHeaders()
    });
  }
}
