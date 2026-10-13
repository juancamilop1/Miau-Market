import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UiToastService } from '../../services/ui-toast.service';

@Component({
  selector: 'mm-toast',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="mm-toast-host" aria-live="polite" aria-relevant="additions">
      @for (t of toast.toasts(); track t.id) {
        <div class="mm-toast mm-toast--{{ t.type }}" role="status">
          <span class="mm-toast__text">{{ t.message }}</span>
          <button type="button" class="mm-toast__close" (click)="toast.dismiss(t.id)" aria-label="Cerrar">×</button>
        </div>
      }
    </div>
  `,
  styles: `
    :host { display: contents; }
  `,
})
export class MmToast {
  toast = inject(UiToastService);
}
