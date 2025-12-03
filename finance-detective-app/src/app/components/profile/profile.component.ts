import { Component, OnInit } from '@angular/core';
import { McpService } from '../../services/mcp.service';
import { UserProfile, GamificationData } from '../../models';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  user: UserProfile | null = null;
  gamification: GamificationData | null = null;

  constructor(private mcpService: McpService) {}

  ngOnInit() {
    this.user = this.mcpService.getCurrentUser();
    this.gamification = this.mcpService.getCurrentGamification();
  }
}
