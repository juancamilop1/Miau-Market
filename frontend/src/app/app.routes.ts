import { Routes } from '@angular/router';
import { Login } from './app/login/login';
import { Register } from './app/register/register';

export const routes: Routes = [
	{ path: '', pathMatch: 'full', redirectTo: 'login' },
	{ path: 'login', component: Login, title: 'MiauMarket | Iniciar sesión' },
	{ path: 'register', component: Register, title: 'MiauMarket | Crear cuenta' },
	{ path: '**', redirectTo: 'login' },
];
