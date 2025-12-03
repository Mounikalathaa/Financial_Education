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
    if (user) {
      try {
        const result = await this.mcpService.getQuizHistory(user.user_id).toPromise();
        this.quizHistory = result?.history || [];
      } catch (error) {
        console.error('Error loading quiz history:', error);
      } finally {
        this.loading = false;
      }
    }
  }

  getScoreClass(score: number, total: number): string {
    const percentage = (score / total) * 100;
    if (percentage >= 90) return 'excellent';
    if (percentage >= 70) return 'good';
    return 'needs-improvement';
  }
}
