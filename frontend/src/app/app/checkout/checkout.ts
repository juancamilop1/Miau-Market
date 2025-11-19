import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../auth.service';
import { ApiService } from '../../services/api.service';

interface OrderData {
  Id_User: number;
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

  ngOnInit() {
    // Obtener items seleccionados del sessionStorage
    const selectedIdsJson = sessionStorage.getItem('selectedCartItems');
    const selectedIds = selectedIdsJson ? JSON.parse(selectedIdsJson) : [];
    
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

    // Pre-llenar datos del usuario
    const user = this.auth.user();
    if (user) {
      this.email.set(user.email);
      // Autocompletar dirección y teléfono desde los datos del usuario
      if (user.Address) {
        this.direccion = user.Address;
      }
      if (user.Telefono) {
        this.telefono = user.Telefono;
      }
    }
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
      console.log('Ya se está procesando un pedido, ignorando clic');
      return;
    }

    console.log('Botón confirmar pedido clickeado');
    console.log('Dirección:', this.direccion);
    console.log('Teléfono:', this.telefono);
    
    // Validar datos
    if (!this.direccion || !this.telefono) {
      this.errorMessage.set('Por favor completa la dirección y el teléfono');
      return;
    }

    const user = this.auth.user();
    if (!user) {
      this.errorMessage.set('Debes iniciar sesión para realizar un pedido');
      return;
    }

    console.log('Usuario:', user);
    console.log('Carrito:', this.cart());

    // Marcar como confirmando para bloquear múltiples clics
    this.confirmando.set(true);
    this.loading.set(true);
    this.errorMessage.set('');

    // Preparar datos del pedido
    const orderData: OrderData = {
      Id_User: user.id,
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

    console.log('Datos del pedido:', orderData);

    // Enviar pedido al backend
    this.api.post('/usuarios/pedidos/', orderData).subscribe(
      (response: any) => {
        console.log('Respuesta del servidor:', response);
        this.successMessage.set('¡Pedido confirmado exitosamente! Redirigiendo a tus pedidos...');
        this.loading.set(false);
        
        // Limpiar sessionStorage
        sessionStorage.removeItem('selectedCartItems');
        
        // Remover solo los items seleccionados del carrito
        const selectedIds = this.selectedCartItems().map(item => item.product.id);
        selectedIds.forEach(id => this.auth.removeFromCart(id));
        
        // Redirigir a Mis Pedidos después de 2 segundos
        setTimeout(() => {
          this.router.navigate(['/my-orders']);
        }, 2000);
      },
      (error: any) => {
        console.error('Error completo:', error);
        console.error('Error status:', error.status);
        console.error('Error message:', error.message);
        console.error('Error error:', error.error);
        this.errorMessage.set('Error al procesar el pedido. Intenta nuevamente.');
        this.loading.set(false);
        this.confirmando.set(false); // Permitir reintentar si hay error
      }
    );
  }
}
