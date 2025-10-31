import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../auth.service';
import { ApiService } from '../../services/api.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-register',
  imports: [RouterLink, CommonModule, FormsModule],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class Register {
  private router = inject(Router);
  private auth = inject(AuthService);
  private api = inject(ApiService);

  // Campos del formulario
  nombre = '';
  apellido = '';
  email = '';
  password = '';
  password2 = '';
  telefono = '';
  address = '';
  city = '';
  birthDate = '';

  errorMessage = signal<string | null>(null);
  isLoading = signal(false);

  submit(ev: Event) {
    ev.preventDefault();
    
    // Validación básica
    if (!this.nombre || !this.apellido || !this.email || !this.password || !this.password2) {
      this.errorMessage.set('Por favor completa todos los campos requeridos');
      return;
    }

    if (this.password !== this.password2) {
      this.errorMessage.set('Las contraseñas no coinciden');
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);

    // Llamada real a la API
    const registerData = {
      Nombre: this.nombre,
      Apellido: this.apellido,
      Email: this.email,
      password: this.password,
      password2: this.password2,
      Telefono: this.telefono || undefined,
      Address: this.address || undefined,
      City: this.city || undefined,
      BirthDate: this.birthDate || undefined
    };

    this.api.register(registerData).subscribe({
      next: (response) => {
        // Registro exitoso, ahora hacer login automático
        this.api.login({ Email: this.email, password: this.password }).subscribe({
          next: (loginResponse) => {
            if (loginResponse.success) {
              this.auth.login({
                id: loginResponse.user.id,
                name: loginResponse.user.nombre,
                email: loginResponse.user.email
              });
              this.router.navigate(['/shop']);
            }
          },
          error: (error) => {
            this.isLoading.set(false);
            // Si falla el login automático, redirigir al login manual
            this.router.navigate(['/login']);
          }
        });
      },
      error: (error) => {
        this.isLoading.set(false);
        if (error.error?.password) {
          this.errorMessage.set(error.error.password[0]);
        } else if (error.error?.Email) {
          this.errorMessage.set('Este email ya está registrado');
        } else if (error.error) {
          // Mostrar el primer error que venga del backend
          const firstError = Object.values(error.error)[0];
          this.errorMessage.set(Array.isArray(firstError) ? firstError[0] : String(firstError));
        } else {
          this.errorMessage.set('Error al registrar. Por favor intenta de nuevo.');
        }
        console.error('Error de registro:', error);
      }
    });
  }
}
