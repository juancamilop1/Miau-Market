import { Component, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../auth.service';

@Component({
  selector: 'app-login',
  imports: [RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  private router = inject(Router);
  private auth = inject(AuthService);

  submit(ev: Event) {
    ev.preventDefault();
    // Simulación de login
    this.auth.login('Usuario');
    this.router.navigate(['/shop']);
  }

}
