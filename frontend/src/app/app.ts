import { Component, Inject, PLATFORM_ID, signal, OnInit } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Router, RouterLink, RouterLinkActive, RouterOutlet, NavigationEnd } from '@angular/router';
import { Chatbot } from './app/chatbot/chatbot';
import { NotificationsBell } from './app/notifications-bell/notifications-bell';
import { CommonModule } from '@angular/common';
import { AuthService } from './auth.service';
import { filter } from 'rxjs';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, Chatbot, NotificationsBell, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  protected readonly title = signal('frontend');
  showSearch = signal(false);
  
  // Mobile menu state
  showMobileMenu = signal(false);
  isMobile = signal(false);
  
  // Hide chatbot in admin
  isAdminPage = signal(false);
  
  constructor(
    @Inject(PLATFORM_ID) private platformId: Object, 
    public auth: AuthService,
    private router: Router
  ) {
    // Aplicar tema guardado al iniciar en el navegador
    if (isPlatformBrowser(this.platformId)) {
      const saved = localStorage.getItem('mm-theme');
      const root = document.documentElement;
      
      if (saved === 'dark') {
        root.classList.remove('theme-light');
        root.classList.add('theme-dark');
        root.setAttribute('data-mm-theme', 'dark');
        console.log('MiauMarket: aplicando tema dark desde localStorage');
        this.applyBrandAssets('dark');
      } else {
        // Asegurarse de que el tema light está aplicado por defecto
        root.classList.remove('theme-dark');
        root.classList.add('theme-light');
        root.setAttribute('data-mm-theme', 'light');
        console.log('MiauMarket: aplicando tema light');
        this.applyBrandAssets('light');
      }
      
      // Detectar si es móvil
      this.checkIfMobile();
      window.addEventListener('resize', () => this.checkIfMobile());
    }

    // Verificar la URL inicial
    const currentUrl = this.router.url;
    this.showSearch.set(currentUrl === '/shop');
    this.isAdminPage.set(
      currentUrl === '/admin' || 
      currentUrl.startsWith('/admin/') || 
      currentUrl === '/dashboard' || 
      currentUrl.startsWith('/dashboard/')
    );

    // Detectar cambios de ruta para mostrar/ocultar búsqueda y chatbot
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      const url = event.urlAfterRedirects || event.url;
      // Mostrar búsqueda solo en /shop
      this.showSearch.set(url === '/shop');
      // Ocultar chatbot en /admin y /dashboard
      this.isAdminPage.set(
        url === '/admin' || 
        url.startsWith('/admin/') || 
        url === '/dashboard' || 
        url.startsWith('/dashboard/')
      );
    });
  }

  ngOnInit() {
    // Forzar detección móvil después de que el componente se inicialice
    if (isPlatformBrowser(this.platformId)) {
      setTimeout(() => this.checkIfMobile(), 0);
    }
  }


  toggleTheme() {
    if (!isPlatformBrowser(this.platformId)) return;
    const root = document.documentElement;
    const isDark = root.classList.contains('theme-dark');
    
    if (isDark) {
      // Cambiar a light
      root.classList.remove('theme-dark');
      root.classList.add('theme-light');
      root.setAttribute('data-mm-theme', 'light');
      localStorage.setItem('mm-theme', 'light');
      console.log('MiauMarket: toggleTheme -> light');
      this.applyBrandAssets('light');
    } else {
      // Cambiar a dark
      root.classList.remove('theme-light');
      root.classList.add('theme-dark');
      root.setAttribute('data-mm-theme', 'dark');
      localStorage.setItem('mm-theme', 'dark');
      console.log('MiauMarket: toggleTheme -> dark');
      this.applyBrandAssets('dark');
    }
  }

  private applyBrandAssets(mode: 'dark' | 'light') {
    if (!isPlatformBrowser(this.platformId)) return;
    const darkLogo = '/miauMarket-dark.png';
    const lightLogo = '/miauMarket.png';
    const targetLogo = mode === 'dark' ? darkLogo : lightLogo;
    const imgs = document.querySelectorAll<HTMLImageElement>('img[data-brand="logo"]');
    imgs.forEach(img => {
      // fallback si el logo dark no existe
      if (mode === 'dark') {
        this.imageExists(darkLogo).then(exists => {
          img.src = exists ? darkLogo : lightLogo;
        });
      } else {
        img.src = lightLogo;
      }
    });

    // Actualiza favicon si existe la variante oscura
    const favicon = document.getElementById('favicon') as HTMLLinkElement | null;
    if (favicon) {
      if (mode === 'dark') {
        this.imageExists(darkLogo).then(exists => {
          favicon.href = exists ? darkLogo : lightLogo;
        });
      } else {
        favicon.href = lightLogo;
      }
    }
  }

  private imageExists(url: string): Promise<boolean> {
    return new Promise(resolve => {
      const img = new Image();
      img.onload = () => resolve(true);
      img.onerror = () => resolve(false);
      img.src = url;
    });
  }

  logout() {
    this.auth.logout();
    this.router.navigate(['/login']);
  }

  // Mobile menu functions
  toggleMobileMenu() {
    this.showMobileMenu.update(val => !val);
  }

  closeMobileMenu() {
    this.showMobileMenu.set(false);
  }

  private checkIfMobile() {
    if (isPlatformBrowser(this.platformId)) {
      // Usar matchMedia para mejor detección móvil
      const isMobileDevice = window.matchMedia('(max-width: 768px)').matches;
      this.isMobile.set(isMobileDevice);
      console.log('Mobile detection:', isMobileDevice, 'Width:', window.innerWidth);
    }
  }
}
