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
        console.log('Registro exitoso:', response);
        // Registro exitoso, ahora hacer login automático
        this.api.login({ Email: this.email, password: this.password }).subscribe({
          next: (loginResponse) => {
            console.log('Login automático exitoso:', loginResponse);
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
            console.error('Error en login automático:', error);
            // Si falla el login automático, redirigir al login manual
            this.router.navigate(['/login']);
          }
        });
      },
      error: (error) => {
        this.isLoading.set(false);
        console.error('Error completo:', error);
        console.error('Error status:', error.status);
        console.error('Error body:', error.error);
        
        // Mejor manejo de errores
        let errorMsg = 'Error al registrar. Por favor intenta de nuevo.';
        
        if (error.error) {
          if (typeof error.error === 'string') {
            errorMsg = error.error;
          } else if (error.error.password) {
            errorMsg = Array.isArray(error.error.password) ? error.error.password[0] : error.error.password;
          } else if (error.error.Email) {
            errorMsg = 'Este email ya está registrado';
          } else if (error.error.error) {
            errorMsg = error.error.error;
          } else if (error.error.detail) {
            errorMsg = error.error.detail;
          } else if (error.error.errors) {
            // Si hay un objeto errors, extraer primer error
            const errorsObj = error.error.errors;
            const firstKey = Object.keys(errorsObj)[0];
            const firstError = errorsObj[firstKey];
            errorMsg = Array.isArray(firstError) ? firstError[0] : String(firstError);
          } else if (Object.keys(error.error).length > 0) {
            // Obtener el primer error disponible
            const firstKey = Object.keys(error.error)[0];
            const firstError = error.error[firstKey];
            errorMsg = Array.isArray(firstError) ? firstError[0] : String(firstError);
          }
        } else if (error.status === 0) {
          errorMsg = 'Error de conexión. Verifica que el servidor esté ejecutándose.';
        }
        
        console.warn('Mensaje de error final:', errorMsg);
        this.errorMessage.set(errorMsg);
      }
    });
  }
}
