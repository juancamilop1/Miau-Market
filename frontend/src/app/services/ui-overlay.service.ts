import { Injectable, Inject, PLATFORM_ID, signal, computed } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

type OverlayEntry = { id: string; close: () => void };

@Injectable({ providedIn: 'root' })
export class UiOverlayService {
  private stack = signal<OverlayEntry[]>([]);
  readonly count = computed(() => this.stack().length);
  readonly isOpen = computed(() => this.stack().length > 0);

  constructor(@Inject(PLATFORM_ID) private platformId: object) {
    if (isPlatformBrowser(this.platformId)) {
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          this.closeTop();
        }
      });
    }
  }

  register(id: string, close: () => void): void {
    this.stack.update((items) => {
      const filtered = items.filter((i) => i.id !== id);
      return [...filtered, { id, close }];
    });
    this.syncBodyScroll();
  }

  unregister(id: string): void {
    this.stack.update((items) => items.filter((i) => i.id !== id));
    this.syncBodyScroll();
  }

  closeTop(): void {
    const items = this.stack();
    if (!items.length) return;
    const top = items[items.length - 1];
    top.close();
  }

  closeAll(): void {
    const items = [...this.stack()];
    for (let i = items.length - 1; i >= 0; i--) {
      items[i].close();
    }
  }

  private syncBodyScroll(): void {
    if (!isPlatformBrowser(this.platformId)) return;
    const doc = document.documentElement;
    const body = document.body;
    if (this.stack().length > 0) {
      doc.classList.add('mm-overlay-open');
      body.classList.add('mm-no-scroll');
    } else {
      doc.classList.remove('mm-overlay-open');
      body.classList.remove('mm-no-scroll');
    }
  }
}
