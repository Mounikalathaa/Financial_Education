import { Component, OnInit } from '@angular/core';
import { McpService } from '../../services/mcp.service';
import { QuizHistory } from '../../models';

@Component({
  selector: 'app-evidence-board',
  templateUrl: './evidence-board.component.html',
  styleUrls: ['./evidence-board.component.css']
})
export class EvidenceBoardComponent implements OnInit {
  quizHistory: QuizHistory[] = [];
  loading = true;

  constructor(private mcpService: McpService) {}

  async ngOnInit() {
    const user = this.mcpService.getCurrentUser();
    console.log('🔍 Evidence Board - Current user:', user);
    
    if (user) {
      try {
        console.log('📡 Fetching quiz history for user:', user.user_id);
        const result = await this.mcpService.getQuizHistory(user.user_id).toPromise();
        console.log('📊 Quiz history API response:', result);
        this.quizHistory = result?.history || [];
        console.log('✅ Quiz history loaded:', this.quizHistory);
      } catch (error) {
        console.error('❌ Error loading quiz history:', error);
      } finally {
        this.loading = false;
      }
    } else {
      console.warn('⚠️ No user found in evidence board');
      this.loading = false;
    }
  }

  getScoreClass(score: number, total: number): string {
    const percentage = (score / total) * 100;
    if (percentage >= 90) return 'excellent';
    if (percentage >= 70) return 'good';
    return 'needs-improvement';
  }
}
