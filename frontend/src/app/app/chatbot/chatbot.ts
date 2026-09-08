import { Component, signal, inject, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { EnvironmentService } from '../../services/environment.service';
import { AuthService } from '../../auth.service';

interface ChatAction {
  label: string;
  route: string;
  style: 'primary' | 'secondary';
}

interface ChatMessage {
  type: 'user' | 'bot' | 'auth';
  text: string;
  timestamp: Date;
  actions?: ChatAction[];
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
  auth = inject(AuthService);
  private router = inject(Router);

  open = false;
  currentMessage = '';
  isLoading = signal(false);
  messages = signal<ChatMessage[]>([]);
  private hasShownGreeting = false;
  private wasLoggedIn = false;

  private apiUrl = this.envService.getChatbotUrl();

  constructor() {
    this.wasLoggedIn = this.auth.isLogged();

    effect(() => {
      const logged = this.auth.isLogged();
      if (logged && !this.wasLoggedIn) {
        this.onLogin();
      }
      if (!logged && this.wasLoggedIn) {
        this.messages.set([]);
        this.hasShownGreeting = false;
      }
      this.wasLoggedIn = logged;
    });
  }

  /** Mensajes visibles: oculta avisos de login si ya hay sesion */
  visibleMessages = () => {
    if (this.auth.isLogged()) {
      return this.messages().filter(m => m.type !== 'auth');
    }
    return this.messages();
  };

  toggle() {
    this.open = !this.open;
    if (this.open && !this.hasShownGreeting) {
      this.hasShownGreeting = true;
      if (this.auth.isLogged()) {
        this.addWelcomeMessage();
      } else {
        this.addAuthMessage();
      }
    }
  }

  sendMessage() {
    if (!this.currentMessage.trim() || this.isLoading()) return;

    if (!this.auth.isLogged()) {
      this.addUserMessage(this.currentMessage);
      this.currentMessage = '';
      this.addAuthMessage();
      return;
    }

    this.addUserMessage(this.currentMessage);
    const messageToSend = this.currentMessage;
    this.currentMessage = '';
    this.isLoading.set(true);
    this.callChatbotAPI(messageToSend);
  }

  private onLogin() {
    const hadAuthPrompt = this.messages().some(m => m.type === 'auth');
    this.messages.update(msgs => msgs.filter(m => m.type !== 'auth'));

    if (hadAuthPrompt || this.open) {
      this.hasShownGreeting = true;
      this.addWelcomeMessage(true);
    }
  }

  private addWelcomeMessage(returning = false) {
    this.fetchWelcomeFromServer();
  }

  private async fetchWelcomeFromServer() {
    try {
      const headers: Record<string, string> = {};
      const token = this.auth.getToken();
      if (token) headers['Authorization'] = `Token ${token}`;

      const res = await fetch(this.envService.getChatbotConfigUrl(), { headers });
      const data = await res.json();
      if (data.success && data.mensaje_bienvenida) {
        this.addBotMessage(data.mensaje_bienvenida);
        return;
      }
    } catch { /* fallback local */ }

    const name = this.auth.user()?.name?.trim();
    const fallback = name
      ? `Hola ${name}! Cuéntame de tu mascota y te recomiendo productos de MiauMarket.`
      : 'Hola! Cuéntame de tu mascota (gato o perro) y te ayudo con productos y consejos.';
    this.addBotMessage(fallback);
  }

  private addAuthMessage() {
    this.messages.update(msgs => [...msgs, {
      type: 'auth',
      text: 'Para usar MiauBot necesitas iniciar sesion o crear una cuenta. Asi podre darte recomendaciones personalizadas para tu gato.',
      timestamp: new Date(),
      actions: [
        { label: 'Iniciar sesion', route: '/login', style: 'primary' },
        { label: 'Registrarse', route: '/register', style: 'secondary' },
      ],
    }]);
    this.scrollToBottom();
  }

  private async callChatbotAPI(message: string) {
    const conversationHistory = this.messages()
      .filter(msg => msg.type !== 'auth')
      .map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.text,
      }));

    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    const token = this.auth.getToken();
    if (token) {
      headers['Authorization'] = `Token ${token}`;
    }

    try {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers,
        body: JSON.stringify({ message, conversation_history: conversationHistory }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (data.success) {
        const text = data.response || data.recommendations || 'No pude generar una respuesta.';
        this.addBotMessage(text);
      } else {
        this.addBotMessage(`Error: ${data.error || 'No se pudo procesar tu mensaje'}`);
      }
    } catch {
      this.addBotMessage('Error de conexion con el servidor. Verifica que el backend este activo.');
    } finally {
      this.isLoading.set(false);
    }
  }

  navigateAction(route: string) {
    this.open = false;
    this.router.navigate([route]);
  }

  private addUserMessage(text: string) {
    this.messages.update(msgs => [...msgs, { type: 'user', text, timestamp: new Date() }]);
    this.scrollToBottom();
  }

  private addBotMessage(text: string) {
    this.messages.update(msgs => [...msgs, { type: 'bot', text, timestamp: new Date() }]);
    this.scrollToBottom();
  }

  private scrollToBottom() {
    setTimeout(() => {
      const container = document.querySelector('.messages-container');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }, 100);
  }
}
