import { Component, inject, signal, OnInit, PLATFORM_ID, effect } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../auth.service';
import { ApiService } from '../../services/api.service';
import { EnvironmentService } from '../../services/environment.service';
import { UiOverlayService } from '../../services/ui-overlay.service';
import { UiToastService } from '../../services/ui-toast.service';

interface OrderData {
  Total: number;
  Metodo_Pago: string;
  productos: {
    Id_Products: number;
    Cantidad: number;
    Precio_Unitario: number;
  }[];
  direccion_envio: string;
  telefono_envio: string;
}

@Component({
  standalone: true,
  selector: 'mm-checkout',
  templateUrl: './checkout.html',
  styleUrls: ['./checkout.css'],
  imports: [CommonModule, FormsModule, RouterLink]
})
export class Checkout implements OnInit {
  auth = inject(AuthService);
  private api = inject(ApiService);
  private router = inject(Router);
  private env = inject(EnvironmentService);
  private platformId = inject(PLATFORM_ID);
  private overlays = inject(UiOverlayService);
  private toasts = inject(UiToastService);

  loading = signal(false);
  errorMessage = signal('');
  successMessage = signal('');
  confirmando = signal(false); // Evitar confirmaciones múltiples

  // Datos del usuario para confirmación
  direccion = '';
  telefono = '';
  email = signal('');
  
  // Items seleccionados del carrito
  selectedCartItems = signal<any[]>([]);

  constructor() {
    effect(() => {
      const busy = this.loading() || this.confirmando();
      if (busy) {
        this.overlays.register('checkout-processing', () => {});
      } else {
        this.overlays.unregister('checkout-processing');
      }
    });
  }

  ngOnInit() {
    let selectedIds: string[] = [];
    if (isPlatformBrowser(this.platformId)) {
      const selectedIdsJson = sessionStorage.getItem('selectedCartItems');
      selectedIds = selectedIdsJson ? JSON.parse(selectedIdsJson) : [];
    }
    
    // Filtrar el carrito para obtener solo items seleccionados
    const allCartItems = this.auth.cart();
    const selectedItems = selectedIds.length > 0 
      ? allCartItems.filter((item: any) => selectedIds.includes(item.product.id))
      : allCartItems;
    
    this.selectedCartItems.set(selectedItems);
    
    // Verificar que hay productos seleccionados
    if (selectedItems.length === 0) {
      this.router.navigate(['/cart']);
      return;
    }

    const user = this.auth.user();
    if (!user) {
      this.router.navigate(['/login']);
      return;
    }

    this.email.set(user.email);
    if (user.Address) {
      this.direccion = user.Address;
    }
    if (user.Telefono) {
      this.telefono = user.Telefono;
    }
  }

  getImageUrl(imagen?: string): string {
    return this.env.getImageUrl(imagen);
  }

  cart() {
    return this.selectedCartItems();
  }

  cartTotal() {
    return this.selectedCartItems().reduce((sum, item) => 
      sum + (item.product.price * item.quantity), 0
    );
  }

  confirmarPedido() {
    // Evitar confirmaciones múltiples
    if (this.confirmando()) {
      return;
    }

    
    // Validar datos
    if (!this.direccion || !this.telefono) {
      const msg = 'Por favor completa la dirección y el teléfono';
      this.errorMessage.set(msg);
      this.toasts.error(msg);
      return;
    }

    const user = this.auth.user();
    if (!user) {
      this.errorMessage.set('Debes iniciar sesión para realizar un pedido');
      return;
    }


    // Marcar como confirmando para bloquear múltiples clics
    this.confirmando.set(true);
    this.loading.set(true);
    this.errorMessage.set('');

    // Preparar datos del pedido
    const orderData: OrderData = {
      Total: this.cartTotal(),
      Metodo_Pago: 'Contra Entrega',
      productos: this.cart().map(item => ({
        Id_Products: parseInt(item.product.id.replace('db_', '')),
        Cantidad: item.quantity,
        Precio_Unitario: item.product.price
      })),
      direccion_envio: this.direccion,
      telefono_envio: this.telefono
    };


    // Enviar pedido al backend
    this.api.post('/usuarios/pedidos/', orderData).subscribe(
      (response: any) => {
        const okMsg = '¡Pedido confirmado! Te redirigimos a Mis Pedidos.';
        this.successMessage.set(okMsg);
        this.toasts.success(okMsg);
        this.loading.set(false);
        
        if (isPlatformBrowser(this.platformId)) {
          sessionStorage.removeItem('selectedCartItems');
        }
        
        // Remover solo los items seleccionados del carrito
        const selectedIds = this.selectedCartItems().map(item => item.product.id);
        selectedIds.forEach(id => this.auth.removeFromCart(id));
        
        // Redirigir a Mis Pedidos después de 2 segundos
        setTimeout(() => {
          this.router.navigate(['/my-orders']);
        }, 2000);
      },
      (error: any) => {
        const backendError = error?.error?.error || error?.error?.message;
        const msg = backendError || 'Error al procesar el pedido. Intenta nuevamente.';
        this.errorMessage.set(msg);
        this.toasts.error(msg);
        this.loading.set(false);
        this.confirmando.set(false);
      }
    );
  }
}
