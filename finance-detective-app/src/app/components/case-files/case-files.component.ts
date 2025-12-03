import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { McpService } from '../../services/mcp.service';
import { UserProfile } from '../../models';

@Component({
  selector: 'app-case-files',
  templateUrl: './case-files.component.html',
  styleUrls: ['./case-files.component.css']
})
export class CaseFilesComponent implements OnInit {
  searchTerm: string = '';
  selectedDifficulty: string = 'all';
  allCases: any[] = [];
  loading = true;
  user: UserProfile | null = null;

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
    private router: Router,
    private mcpService: McpService
  ) {}

  async ngOnInit() {
    this.user = this.mcpService.getCurrentUser();
    
    if (!this.user) {
      this.router.navigate(['/login']);
      return;
    }

    try {
      this.loading = true;
      
      // Load all age-appropriate topics from knowledge base
      console.log('Loading all case files for user:', this.user.user_id);
      const topicsResponse = await this.mcpService.getAvailableTopics(this.user.user_id).toPromise();
      console.log(`Loaded ${topicsResponse.total} case files`);
      
      this.allCases = topicsResponse.topics.map((topic: any) => ({
        ...topic,
        icon: this.getTopicIcon(topic.concept)
      }));
      
    } catch (error) {
      console.error('Error loading case files:', error);
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

  get filteredCases() {
    return this.allCases.filter(caseFile => {
      const matchesSearch = caseFile.title.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                           caseFile.concept.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                           caseFile.description.toLowerCase().includes(this.searchTerm.toLowerCase());
      
      const matchesDifficulty = this.selectedDifficulty === 'all' || 
                               caseFile.difficulty === this.selectedDifficulty;
      
      return matchesSearch && matchesDifficulty;
    });
  }

  startCase(caseId: string) {
    // Find the case to get its title
    const caseData = this.allCases.find(c => c.id === caseId);
    const title = caseData?.title || `The Case of ${caseId}`;
    
    // Navigate with both concept ID and title as query params
    this.router.navigate(['/quiz', caseId], {
      queryParams: { title: title }
    });
  }

  getDifficultyClass(difficulty: string): string {
    return `difficulty-${difficulty}`;
  }
}
