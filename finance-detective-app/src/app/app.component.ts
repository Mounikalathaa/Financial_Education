import { Component } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { McpService } from './services/mcp.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'Finance Detective';
  showNav = false;
  currentUser$ = this.mcpService.currentUser$;
  isDarkMode = true;

  constructor(
    private router: Router,
    private mcpService: McpService
  ) {
    // Hide nav on login page
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.showNav = !event.url.includes('/login');
      }
    });
    
    // Load theme preference
    const savedTheme = localStorage.getItem('theme');
    this.isDarkMode = savedTheme !== 'bright';
    this.applyTheme();
  }

  toggleTheme() {
    this.isDarkMode = !this.isDarkMode;
    this.applyTheme();
    localStorage.setItem('theme', this.isDarkMode ? 'dark' : 'bright');
  }

  private applyTheme() {
    if (this.isDarkMode) {
      document.body.classList.remove('bright-mode');
    } else {
      document.body.classList.add('bright-mode');
    }
  }

  logout() {
    this.mcpService.clearSession();
    this.router.navigate(['/login']);
  }
}
