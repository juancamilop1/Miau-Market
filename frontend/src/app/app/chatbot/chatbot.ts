import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  standalone: true,
  selector: 'mm-chatbot',
  templateUrl: './chatbot.html',
  styleUrls: ['./chatbot.css']
  ,imports: [CommonModule]
})
export class Chatbot {
  open = false;
  toggle() { this.open = !this.open; }
}
