import { Injectable, signal } from '@angular/core';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastItem {
  id: string;
  message: string;
  type: ToastType;
}

@Injectable({ providedIn: 'root' })
export class UiToastService {
  readonly toasts = signal<ToastItem[]>([]);

  show(message: string, type: ToastType = 'info', durationMs = 4200): void {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
    this.toasts.update((items) => [...items, { id, message, type }]);
    if (durationMs > 0) {
      setTimeout(() => this.dismiss(id), durationMs);
    }
  }

  success(message: string, durationMs = 4200): void {
    this.show(message, 'success', durationMs);
  }

  error(message: string, durationMs = 5200): void {
    this.show(message, 'error', durationMs);
  }

  dismiss(id: string): void {
    this.toasts.update((items) => items.filter((t) => t.id !== id));
  }
}
