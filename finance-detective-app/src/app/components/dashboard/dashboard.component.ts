import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { McpService } from '../../services/mcp.service';
import { UserProfile, GamificationData, DetectiveRank } from '../../models';
import { Subscription, filter } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit, OnDestroy {
  user: UserProfile | null = null;
  gamification: GamificationData | null = null;
  loading = true;
  detectiveRank: string = DetectiveRank.ROOKIE;
  private routerSubscription?: Subscription;
  cases: any[] = [];
  
  // Icon mapping for different topics
  private topicIcons: { [key: string]: string } = {
    'money': '💰', 'budget': '💰', 'saving': '🏦', 'bank': '🏦',
    'invest': '📈', 'stock': '📈', 'share': '📈',
    'credit': '💳', 'card': '💳', 'loan': '💳',
    'tax': '📋', 'gst': '📋',
    'insurance': '🛡️', 'trade': '🔄', 'barter': '🔄',
    'business': '🚀', 'entrepreneur': '🚀', 'commerce': '🛒',
    'rbi': '🏛️', 'pan': '🆔', 'aadhaar': '🆔',
    'cheque': '💵', 'draft': '💵', 'default': '🔍'
  };

  constructor(
    private mcpService: McpService,
    private router: Router
  ) {}

  async ngOnInit() {
    await this.loadDashboardData();
    
    // Subscribe to navigation events to reload data when returning to dashboard
    this.routerSubscription = this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(async (event: any) => {
      if (event.url === '/dashboard' || event.url === '/') {
        await this.loadDashboardData();
      }
    });
  }

  ngOnDestroy() {
    if (this.routerSubscription) {
      this.routerSubscription.unsubscribe();
    }
  }

  async loadDashboardData() {
    this.user = this.mcpService.getCurrentUser();
    
    if (!this.user) {
      this.router.navigate(['/login']);
      return;
    }

    try {
      this.loading = true;
      
      // Load gamification data
      this.gamification = await this.mcpService.getGamificationData(this.user.user_id).toPromise() || null;
      this.detectiveRank = this.calculateRank(this.gamification?.total_points || 0);
      
      // Load quiz history to determine completed cases
      const historyResponse = await this.mcpService.getQuizHistory(this.user.user_id).toPromise();
      const quizHistory = historyResponse?.history || [];
      console.log('📊 Quiz History:', quizHistory);
      
      const completedConcepts = new Set(
        quizHistory
          .filter((quiz: any) => {
            const isComplete = quiz.percentage === 100;
            console.log(`  ${quiz.concept}: ${quiz.percentage}% - ${isComplete ? '✅ SOLVED' : '❌ NOT SOLVED'}`);
            return isComplete;
          })
          .map((quiz: any) => quiz.concept.toLowerCase())
      );
      
      console.log('✅ Completed concepts:', Array.from(completedConcepts));
      
      // Load age-appropriate topics from knowledge base (filtered by personalization agent)
      console.log('Loading topics for user:', this.user.user_id);
      const topicsResponse = await this.mcpService.getAvailableTopics(this.user.user_id).toPromise();
      console.log(`Loaded ${topicsResponse.total} topics:`, topicsResponse.topics.slice(0, 3).map((t: any) => `${t.concept} (Class ${t.class})`));
      
      // Filter to show only unsolved cases in dashboard (Active Cases)
      const allTopics = topicsResponse.topics;
      console.log('🔍 Filtering topics...');
      this.cases = allTopics
        .filter((topic: any) => {
          const conceptLower = topic.concept.toLowerCase();
          const isCompleted = completedConcepts.has(conceptLower);
          console.log(`  ${topic.concept}: ${isCompleted ? '❌ FILTERED OUT (completed)' : '✅ ACTIVE (not completed)'}`);
          return !isCompleted;
        })
        .map((topic: any) => ({
          ...topic,
          icon: this.getTopicIcon(topic.concept)
        }));
      
      console.log(`📋 Active (unsolved) cases: ${this.cases.length}, Completed: ${completedConcepts.size}, Total available: ${allTopics.length}`);
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      this.loading = false;
    }
  }
  
  getTopicIcon(concept: string): string {
    const lowerConcept = concept.toLowerCase();
    for (const [key, icon] of Object.entries(this.topicIcons)) {
      if (lowerConcept.includes(key)) {
        return icon;
      }
    }
    return this.topicIcons['default'];
  }

  calculateRank(points: number): string {
    if (points >= 1000) return DetectiveRank.LEGEND;
    if (points >= 750) return DetectiveRank.CHIEF;
    if (points >= 500) return DetectiveRank.SENIOR;
    if (points >= 250) return DetectiveRank.DETECTIVE;
    if (points >= 100) return DetectiveRank.JUNIOR;
    return DetectiveRank.ROOKIE;
  }

  startCase(caseId: string) {
    this.router.navigate(['/quiz', caseId]);
  }

  getDifficultyClass(difficulty: string): string {
    return `difficulty-${difficulty}`;
  }
}
