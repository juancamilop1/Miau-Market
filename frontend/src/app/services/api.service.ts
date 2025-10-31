import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Interfaces para los datos
export interface LoginRequest {
  Email: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  user: {
    id: number;
    email: string;
    nombre: string;
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

  constructor(private http: HttpClient) { }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.baseUrl}/usuarios/login/`, credentials);
  }

  register(userData: RegisterRequest): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(`${this.baseUrl}/usuarios/registro/`, userData);
  }
}
