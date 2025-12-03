import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-case-files',
  templateUrl: './case-files.component.html',
  styleUrls: ['./case-files.component.css']
})
export class CaseFilesComponent {
  searchTerm: string = '';
  selectedDifficulty: string = 'all';

  allCases = [
    {
      id: 'budgeting',
      title: 'The Mystery of the Missing Allowance',
      concept: 'Budgeting',
      difficulty: 'beginner',
      icon: '💰',
      description: 'Help solve where all the money went! Learn how to track expenses and create a budget.',
      points: 100,
      skills: ['Expense Tracking', 'Budget Planning', 'Money Management'],
      estimatedTime: '10-15 min'
    },
    {
      id: 'saving',
      title: 'The Case of the Growing Piggy Bank',
      concept: 'Saving',
      difficulty: 'beginner',
      icon: '🏦',
      description: 'Uncover the secrets of growing wealth through smart saving strategies.',
      points: 120,
      skills: ['Savings Goals', 'Interest', 'Emergency Fund'],
      estimatedTime: '10-15 min'
    },
    {
      id: 'investing',
      title: 'The Investment Enigma',
      concept: 'Investing',
      difficulty: 'intermediate',
      icon: '📈',
      description: 'Crack the code of making money grow through investments.',
      points: 150,
      skills: ['Stocks', 'Bonds', 'Risk Management'],
      estimatedTime: '15-20 min'
    },
    {
      id: 'credit',
      title: 'The Credit Card Caper',
      concept: 'Credit',
      difficulty: 'intermediate',
      icon: '💳',
      description: 'Investigate the world of borrowed money and credit scores.',
      points: 140,
      skills: ['Credit Score', 'Interest Rates', 'Responsible Borrowing'],
      estimatedTime: '15-20 min'
    },
    {
      id: 'taxes',
      title: 'The Tax Mystery',
      concept: 'Taxes',
      difficulty: 'advanced',
      icon: '📋',
      description: 'Decode where tax money goes and how taxes work.',
      points: 180,
      skills: ['Income Tax', 'Deductions', 'Public Services'],
      estimatedTime: '20-25 min'
    },
    {
      id: 'entrepreneurship',
      title: 'The Business Blueprint',
      concept: 'Entrepreneurship',
      difficulty: 'advanced',
      icon: '🚀',
      description: 'Solve the startup success puzzle and learn business basics.',
      points: 200,
      skills: ['Business Planning', 'Revenue', 'Profit & Loss'],
      estimatedTime: '20-25 min'
    },
    {
      id: 'insurance',
      title: 'The Protection Protocol',
      concept: 'Insurance',
      difficulty: 'intermediate',
      icon: '🛡️',
      description: 'Investigate how insurance protects against financial risks.',
      points: 145,
      skills: ['Risk Protection', 'Premiums', 'Coverage'],
      estimatedTime: '15-20 min'
    },
    {
      id: 'compound-interest',
      title: 'The Compound Conundrum',
      concept: 'Compound Interest',
      difficulty: 'intermediate',
      icon: '📊',
      description: 'Unravel the mystery of money multiplying over time.',
      points: 155,
      skills: ['Interest Calculation', 'Time Value', 'Growth'],
      estimatedTime: '15-20 min'
    }
  ];

  constructor(private router: Router) {}

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
    this.router.navigate(['/quiz', caseId]);
  }

  getDifficultyClass(difficulty: string): string {
    return `difficulty-${difficulty}`;
  }
}
