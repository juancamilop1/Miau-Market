import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../auth.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class Profile implements OnInit {
  auth = inject(AuthService);
  private api = inject(ApiService);
  private router = inject(Router);

  // Modo edición
  editando = signal(false);
  
  // Datos del perfil
  nombre = '';
  apellido = '';
  email = '';
  telefono = '';
  direccion = '';
  ciudad = '';
  edad = '';
  
  // Cambio de contraseña
  mostrarCambioPassword = signal(false);
  passwordActual = '';
  passwordNueva = '';
  passwordConfirmar = '';
  
  // Estados
  cargando = signal(false);
  mensaje = signal('');
  error = signal('');

  ciudadesColombia = [
    'Bogota',
    'Medellin',
    'Cali',
    'Barranquilla',
    'Cartagena',
    'Cucuta',
    'Bucaramanga',
    'Pereira',
    'Santa Marta',
    'Ibague',
    'Pasto',
    'Manizales',
    'Neiva',
    'Villavicencio',
    'Armenia',
    'Valledupar',
    'Monteria',
    'Sincelejo',
    'Popayan',
    'Tunja',
    'Florencia',
    'Riohacha',
    'Yopal',
    'Quibdo',
    'Leticia',
    'Mocoa',
    'San Andres',
    'Arauca',
    'Puerto Carreno',
    'San Jose del Guaviare',
    'Mitu',
    'Inirida',
    'Palmira'
  ];

  ngOnInit() {
    const user = this.auth.user();
    if (!user) {
      this.router.navigate(['/login']);
      return;
    }

    // Cargar datos del usuario
    console.log('Usuario completo en perfil:', user);
    console.log('Ciudad del usuario:', user.Ciudad);
    this.nombre = user.name || '';
    this.apellido = user.Apellido || '';
    this.email = user.email || '';
    this.telefono = user.Telefono || '';
    this.direccion = user.Address || '';
    this.ciudad = user.Ciudad || '';
    this.edad = user.Edad ? user.Edad.toString() : '';
    
    console.log('Ciudad asignada:', this.ciudad);
  }

  activarEdicion() {
    this.editando.set(true);
    this.mensaje.set('');
    this.error.set('');
  }

  cancelarEdicion() {
    this.editando.set(false);
    this.mostrarCambioPassword.set(false);
    // Restaurar datos originales
    const user = this.auth.user();
    if (user) {
      this.nombre = user.name || '';
      this.apellido = user.Apellido || '';
      this.telefono = user.Telefono || '';
      this.direccion = user.Address || '';
      this.ciudad = user.Ciudad || '';
      this.edad = user.Edad ? user.Edad.toString() : '';
    }
    this.passwordActual = '';
    this.passwordNueva = '';
    this.passwordConfirmar = '';
    this.mensaje.set('');
    this.error.set('');
  }

  guardarCambios() {
    this.error.set('');
    this.mensaje.set('');

    console.log('Guardando cambios...', {
      nombre: this.nombre,
      apellido: this.apellido,
      telefono: this.telefono,
      direccion: this.direccion,
      ciudad: this.ciudad,
      edad: this.edad
    });

    // Validaciones
    if (!this.nombre || !this.apellido || !this.telefono || !this.direccion || !this.ciudad || !this.edad) {
      this.error.set('Todos los campos son obligatorios');
      console.error('Validación fallida: campos vacíos');
      return;
    }

    const edadNum = parseInt(this.edad);
    if (isNaN(edadNum) || edadNum < 18 || edadNum > 120) {
      this.error.set('La edad debe ser un número entre 18 y 120');
      console.error('Validación fallida: edad inválida', this.edad);
      return;
    }

    // Validar cambio de contraseña si está activado
    if (this.mostrarCambioPassword()) {
      if (!this.passwordActual || !this.passwordNueva || !this.passwordConfirmar) {
        this.error.set('Debes completar todos los campos de contraseña');
        return;
      }
      if (this.passwordNueva !== this.passwordConfirmar) {
        this.error.set('Las contraseñas nuevas no coinciden');
        return;
      }
      if (this.passwordNueva.length < 6) {
        this.error.set('La contraseña nueva debe tener al menos 6 caracteres');
        return;
      }
    }

    this.cargando.set(true);

    const datosActualizar: any = {
      name: this.nombre,
      Apellido: this.apellido,
      Telefono: this.telefono,
      Address: this.direccion,
      Ciudad: this.ciudad,
      Edad: edadNum
    };

    // Si está cambiando la contraseña, agregarla
    if (this.mostrarCambioPassword()) {
      datosActualizar.password_actual = this.passwordActual;
      datosActualizar.password_nueva = this.passwordNueva;
    }

    console.log('Enviando datos:', datosActualizar);

    this.api.put('/usuarios/perfil/', datosActualizar).subscribe({
      next: (response: any) => {
        console.log('Respuesta exitosa:', response);
        this.mensaje.set('Perfil actualizado exitosamente');
        this.cargando.set(false);
        this.editando.set(false);
        this.mostrarCambioPassword.set(false);
        
        // Actualizar el usuario en el auth service
        const user = this.auth.user();
        if (user) {
          this.auth.user.set({
            ...user,
            name: this.nombre,
            Telefono: this.telefono,
            Address: this.direccion,
            Ciudad: this.ciudad,
            Edad: edadNum
          });
        }

        // Limpiar campos de contraseña
        this.passwordActual = '';
        this.passwordNueva = '';
        this.passwordConfirmar = '';

        // Ocultar mensaje después de 3 segundos
        setTimeout(() => {
          this.mensaje.set('');
        }, 3000);
      },
      error: (err) => {
        console.error('Error actualizando perfil:', err);
        console.error('Error status:', err.status);
        console.error('Error body:', err.error);
        if (err.status === 400 && err.error?.error) {
          this.error.set(err.error.error);
        } else {
          this.error.set('Error al actualizar el perfil. Intenta nuevamente.');
        }
        this.cargando.set(false);
      }
    });
  }

  toggleCambioPassword() {
    this.mostrarCambioPassword.set(!this.mostrarCambioPassword());
    if (!this.mostrarCambioPassword()) {
      this.passwordActual = '';
      this.passwordNueva = '';
      this.passwordConfirmar = '';
    }
  }
}
