import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  template: `
    <div class="app-container" *ngIf="!isLoginPage()">
      <app-header></app-header>
      <div class="main-content">
        <app-sidebar></app-sidebar>
        <div class="content-wrapper">
          <router-outlet></router-outlet>
        </div>
      </div>
    </div>
    <router-outlet *ngIf="isLoginPage()"></router-outlet>
  `,
  styles: [`
    .app-container {
      display: flex;
      flex-direction: column;
      height: 100vh;
    }
    .main-content {
      display: flex;
      flex: 1;
      overflow: hidden;
    }
    .content-wrapper {
      flex: 1;
      padding: 20px;
      overflow-y: auto;
    }
  `]
})
export class AppComponent {
  constructor(private router: Router) {}

  isLoginPage(): boolean {
    return this.router.url === '/login' || this.router.url === '/register';
  }
}