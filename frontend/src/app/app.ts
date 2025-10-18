import { Component, Inject, PLATFORM_ID, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { Chatbot } from './app/chatbot/chatbot';
import { CommonModule } from '@angular/common';
import { AuthService } from './auth.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, Chatbot, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('frontend');
  constructor(@Inject(PLATFORM_ID) private platformId: Object, public auth: AuthService) {
    // Aplicar tema guardado al iniciar en el navegador
    if (isPlatformBrowser(this.platformId)) {
      const saved = localStorage.getItem('mm-theme');
      if (saved === 'dark') {
        document.documentElement.classList.add('theme-dark');
        document.documentElement.setAttribute('data-mm-theme', 'dark');
        console.log('MiauMarket: aplicando tema dark desde localStorage');
        this.applyBrandAssets('dark');
      }
    }
  }


  toggleTheme() {
    if (!isPlatformBrowser(this.platformId)) return;
    const root = document.documentElement;
    const dark = root.classList.toggle('theme-dark');
    // Also set an attribute so styles or other scripts can detect theme reliably
    root.setAttribute('data-mm-theme', dark ? 'dark' : 'light');
    console.log('MiauMarket: toggleTheme ->', dark ? 'dark' : 'light');
    localStorage.setItem('mm-theme', dark ? 'dark' : 'light');
    this.applyBrandAssets(dark ? 'dark' : 'light');
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
}
