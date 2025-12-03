import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { McpService } from '../../services/mcp.service';

@Component({
  selector: 'app-quiz',
  templateUrl: './quiz.component.html',
  styleUrls: ['./quiz.component.css']
})
export class QuizComponent implements OnInit {
  concept: string = '';
  caseTitle: string = '';
  quiz: any = null;
  currentQuestionIndex: number = 0;
  selectedAnswers: { [key: string]: string } = {};
  loading: boolean = true;
  evaluating: boolean = false;
  showResults: boolean = false;
  results: any = null;
  error: string | null = null;
  currentQuestionHint: string = '';
  loadingHint: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private mcpService: McpService
  ) {}

  async ngOnInit() {
    this.concept = this.route.snapshot.paramMap.get('concept') || '';
    this.caseTitle = this.route.snapshot.queryParamMap.get('title') || '';
    
    const user = this.mcpService.getCurrentUser();
    if (!user) {
      this.router.navigate(['/login']);
      return;
    }

    await this.loadQuiz(user.user_id);
  }

  onImageError(event: any) {
    // Hide image if it fails to load
    event.target.style.display = 'none';
    console.warn('Failed to load case image');
  }

  async loadQuiz(userId: string) {
    try {
      this.loading = true;
      this.error = null;
      
      const response = await this.mcpService.generateQuiz(
        userId,
        this.concept,
        'beginner',
        this.caseTitle
      ).toPromise();

      this.quiz = response;
      this.loading = false;
    } catch (error: any) {
      this.error = error.error?.detail || 'Failed to generate quiz. Please try again.';
      this.loading = false;
    }
  }

  get currentQuestion() {
    return this.quiz?.questions[this.currentQuestionIndex];
  }

  get progress() {
    if (!this.quiz) return 0;
    return ((this.currentQuestionIndex + 1) / this.quiz.questions.length) * 100;
  }

  selectAnswer(option: string) {
    const questionId = this.currentQuestion?.question_id;
    if (questionId) {
      this.selectedAnswers[questionId] = option;
    }
  }

  isAnswerSelected(option: string): boolean {
    const questionId = this.currentQuestion?.question_id;
    return questionId ? this.selectedAnswers[questionId] === option : false;
  }

  nextQuestion() {
    if (this.currentQuestionIndex < this.quiz.questions.length - 1) {
      this.currentQuestionIndex++;
      this.currentQuestionHint = '';
    }
  }

  previousQuestion() {
    if (this.currentQuestionIndex > 0) {
      this.currentQuestionIndex--;
      this.currentQuestionHint = '';
    }
  }

  async getAIHint() {
    const question = this.quiz.questions[this.currentQuestionIndex];
    const user = this.mcpService.getCurrentUser();
    
    if (!user || !question) return;

    try {
      this.loadingHint = true;
      const response = await this.mcpService.getAIHint(
        user.user_id,
        question.question_text || question.question,
        this.quiz.concept || this.concept
      ).toPromise();

      this.currentQuestionHint = response.hint;
      this.loadingHint = false;
    } catch (error) {
      console.error('Failed to get hint:', error);
      this.currentQuestionHint = '💡 Try thinking about the clues in the case brief!';
      this.loadingHint = false;
    }
  }

  async submitQuiz() {
    const user = this.mcpService.getCurrentUser();
    if (!user) return;

    try {
      this.evaluating = true;
      
      // Convert answers array to dictionary format: {question_id: selected_answer}
      const answersDict: Record<string, string> = {};
      this.quiz.questions.forEach((q: any) => {
        answersDict[q.question_id] = this.selectedAnswers[q.question_id] || '';
      });

      const response = await this.mcpService.evaluateQuiz(
        this.quiz,
        {
          quiz_id: this.quiz.quiz_id,
          user_id: user.user_id,
          answers: answersDict
        }
      ).toPromise();

      this.results = response;
      this.showResults = true;
      this.evaluating = false;
      
      // Refresh gamification data so dashboard updates
      await this.mcpService.getGamificationData(user.user_id).toPromise();
    } catch (error: any) {
      this.error = error.error?.detail || 'Failed to evaluate quiz. Please try again.';
      this.evaluating = false;
    }
  }

  retryQuiz() {
    this.currentQuestionIndex = 0;
    this.selectedAnswers = {};
    this.showResults = false;
    this.results = null;
    this.currentQuestionHint = '';
  }

  backToDashboard() {
    this.router.navigate(['/dashboard']);
  }

  canGoNext(): boolean {
    const questionId = this.currentQuestion?.question_id;
    return questionId ? !!this.selectedAnswers[questionId] : false;
  }

  getScoreClass(): string {
    if (!this.results) return '';
    const percentage = this.results.percentage;
    if (percentage >= 80) return 'score-excellent';
    if (percentage >= 60) return 'score-good';
    if (percentage >= 40) return 'score-fair';
    return 'score-needs-improvement';
  }

  getScorePercentage(): number {
    if (!this.results) return 0;
    return this.results.percentage || 0;
  }

  retakeQuiz() {
    this.retryQuiz();
  }
}
