import { Component, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../auth.service';

@Component({
  selector: 'app-register',
  imports: [RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class Register {
  private router = inject(Router);
  private auth = inject(AuthService);

  submit(ev: Event) {
    ev.preventDefault();
    // Simulación de registro: autologin
    this.auth.login('Nuevo usuario');
    this.router.navigate(['/shop']);
  }

}
