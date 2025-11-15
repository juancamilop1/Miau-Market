import { Component, input, output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-star-rating',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './star-rating.html',
  styleUrls: ['./star-rating.css']
})
export class StarRating {
  // Inputs
  rating = input<number>(0);
  readonly = input<boolean>(false);
  size = input<'small' | 'medium' | 'large'>('medium');
  
  // Output
  ratingChange = output<number>();
  
  // Estado interno
  hoveredStar = signal<number>(0);
  
  stars = [1, 2, 3, 4, 5];
  
  onStarClick(star: number): void {
    if (!this.readonly()) {
      this.ratingChange.emit(star);
    }
  }
  
  onStarHover(star: number): void {
    if (!this.readonly()) {
      this.hoveredStar.set(star);
    }
  }
  
  onMouseLeave(): void {
    this.hoveredStar.set(0);
  }
  
  isStarFilled(star: number): boolean {
    const currentRating = this.hoveredStar() || this.rating();
    return star <= currentRating;
  }
  
  getSizeClass(): string {
    return `star-${this.size()}`;
  }
}
