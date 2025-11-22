import { Component, NgZone, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { EnvironmentService } from '../../services/environment.service';

interface ChatMessage {
  type: 'user' | 'bot';
  text: string;
  timestamp: Date;
}

@Component({
  standalone: true,
  selector: 'mm-chatbot',
  templateUrl: './chatbot.html',
  styleUrls: ['./chatbot.css'],
  imports: [CommonModule, FormsModule]
})
export class Chatbot {
  private envService = inject(EnvironmentService);
  
  open = false;
  currentMessage = '';
  isLoading = signal(false);
  messages = signal<ChatMessage[]>([]);
  
  private apiUrl = this.envService.getChatbotUrl();

  constructor(private ngZone: NgZone) {
    // Agregar mensaje de bienvenida inicial
    this.addBotMessage('¡Hola! 🐾 Bienvenido a MiauMarket.\nSoy tu asistente para todo lo que tu perro necesita 🐕\n\nPuedo ayudarte con:\n• Productos recomendados\n• Cuidado y alimentación\n• Comportamiento y razas\n\n¡Cuéntame sobre tu mascota y empecemos! 🦴');
  }

  toggle() { 
    this.open = !this.open; 
  }

  sendMessage() {
    if (!this.currentMessage.trim() || this.isLoading()) return;

    // Agregar mensaje del usuario
    this.addUserMessage(this.currentMessage);
    
    const messageToSend = this.currentMessage;
    this.currentMessage = '';
    this.isLoading.set(true);

    // Enviar a la API usando fetch
    this.callChatbotAPI(messageToSend);
  }

  private async callChatbotAPI(message: string) {
    const payload = {
      message: message
    };

    try {
      console.log('📤 Enviando mensaje al chatbot:', payload);
      
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      console.log('📥 Response status:', response.status);
      console.log('📥 Response ok:', response.ok);

      const data = await response.json();
      console.log('✅ Datos recibidos:', data);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (data.success) {
        // La API puede devolver 'response' o 'recommendations'
        const botMessage = data.response || data.recommendations || 'Lo siento, no pude generar una respuesta.';
        console.log('🤖 Mensaje del bot:', botMessage);
        this.addBotMessage(botMessage);
      } else {
        const errorMsg = `Error: ${data.error || 'No se pudo procesar tu mensaje'}`;
        console.error('❌ Error del servidor:', errorMsg);
        this.addBotMessage(errorMsg);
      }
      
      this.isLoading.set(false);
    } catch (error) {
      this.isLoading.set(false);
      console.error('❌ Error calling chatbot API:', error);
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        this.addBotMessage('❌ Error de conexión. Asegúrate de que el servidor esté ejecutándose en https://adaptable-exploration-production-77dc.up.railway.app');
      } else {
        this.addBotMessage('❌ Error del servidor. Por favor intenta de nuevo.');
      }
    }
  }

  private addUserMessage(text: string) {
    const currentMessages = this.messages();
    this.messages.set([...currentMessages, {
      type: 'user',
      text: text,
      timestamp: new Date()
    }]);
    this.scrollToBottom();
  }

  private addBotMessage(text: string) {
    const currentMessages = this.messages();
    this.messages.set([...currentMessages, {
      type: 'bot',
      text: text,
      timestamp: new Date()
    }]);
    this.scrollToBottom();
  }

  private scrollToBottom() {
    // Hacer scroll hacia abajo después de agregar mensaje
    setTimeout(() => {
      const container = document.querySelector('.messages-container');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }, 100);
  }
}