import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../auth.service';
import { ApiService } from '../../services/api.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-login',
  imports: [RouterLink, CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  private router = inject(Router);
  private auth = inject(AuthService);
  private api = inject(ApiService);

  email = '';
  password = '';
  errorMessage = signal<string | null>(null);
  isLoading = signal(false);

  submit(ev: Event) {
    ev.preventDefault();
    
    // Validación básica
    if (!this.email || !this.password) {
      this.errorMessage.set('Por favor completa todos los campos');
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);

    // Llamada real a la API
    this.api.login({ Email: this.email, password: this.password }).subscribe({
      next: (response) => {
        if (response.success) {
          // Guardar token
          if (response.token) {
            this.auth.setToken(response.token);
          }
          
          // Login exitoso
          this.auth.login({
            id: response.user.id,
            name: response.user.nombre,
            email: response.user.email,
            is_staff: response.user.is_staff
          });
          this.router.navigate(['/shop']);
        }
      },
      error: (error) => {
        this.isLoading.set(false);
        if (error.status === 401) {
          this.errorMessage.set('Email o contraseña incorrectos');
        } else if (error.error?.error) {
          this.errorMessage.set(error.error.error);
        } else {
          this.errorMessage.set('Error al iniciar sesión. Por favor intenta de nuevo.');
        }
        console.error('Error de login:', error);
      },
      complete: () => {
        this.isLoading.set(false);
      }
    });
  }
}
