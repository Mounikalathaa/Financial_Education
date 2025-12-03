import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, BehaviorSubject, tap, timeout } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  UserProfile,
  GamificationData,
  QuizHistory,
  Transaction
} from '../models';

@Injectable({
  providedIn: 'root'
})
export class McpService {
  private apiUrl = environment.mcpApiUrl;
  
  // State management
  private currentUserSubject = new BehaviorSubject<UserProfile | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();
  
  private gamificationSubject = new BehaviorSubject<GamificationData | null>(null);
  public gamification$ = this.gamificationSubject.asObservable();

  constructor(private http: HttpClient) {}

  // User Profile APIs
  getUserProfile(userId: string): Observable<UserProfile> {
    const params = new HttpParams().set('user_id', userId);
    return this.http.get<UserProfile>(`${this.apiUrl}/user/profile`, { params })
      .pipe(tap(profile => this.currentUserSubject.next(profile)));
  }

  createUserProfile(profile: UserProfile): Observable<any> {
    return this.http.post(`${this.apiUrl}/user/profile`, profile)
      .pipe(tap(() => this.currentUserSubject.next(profile)));
  }

  loginUser(name: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/user/login`, { name });
  }

  // Gamification APIs
  getGamificationData(userId: string): Observable<GamificationData> {
    const params = new HttpParams().set('user_id', userId);
    return this.http.get<GamificationData>(`${this.apiUrl}/user/gamification`, { params })
      .pipe(tap(data => this.gamificationSubject.next(data)));
  }

  updateGamificationData(data: GamificationData): Observable<any> {
    return this.http.post(`${this.apiUrl}/user/gamification/update`, data)
      .pipe(tap(() => this.gamificationSubject.next(data)));
  }

  // Quiz History APIs
  getQuizHistory(userId: string): Observable<{ history: QuizHistory[] }> {
    const params = new HttpParams().set('user_id', userId);
    return this.http.get<{ history: QuizHistory[] }>(`${this.apiUrl}/user/quiz-history`, { params });
  }

  saveQuizResult(quizData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/user/quiz-history`, quizData);
  }

  // Transaction APIs
  getTransactions(userId: string, limit: number = 10): Observable<{ transactions: Transaction[] }> {
    const params = new HttpParams()
      .set('user_id', userId)
      .set('limit', limit.toString());
    return this.http.get<{ transactions: Transaction[] }>(`${this.apiUrl}/user/transactions`, { params });
  }

  // Quiz APIs
  generateQuiz(userId: string, concept: string, difficulty: string = 'beginner'): Observable<any> {
    return this.http.post(`${this.apiUrl}/quiz/generate`, {
      user_id: userId,
      concept: concept,
      difficulty: difficulty
    }).pipe(
      timeout(150000) // 150 seconds timeout for quiz generation (AI takes time)
    );
  }

  evaluateQuiz(quiz: any, response: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/quiz/evaluate`, {
      quiz: quiz,
      response: response
    });
  }

  getAIHint(userId: string, question: string, concept: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/quiz/hint`, {
      user_id: userId,
      question: question,
      concept: concept
    });
  }

  getAIExplanation(userId: string, question: string, correctAnswer: string, userAnswer: string, concept: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/quiz/explanation`, {
      user_id: userId,
      question: question,
      correct_answer: correctAnswer,
      user_answer: userAnswer,
      concept: concept
    });
  }

  generateVoiceScript(data: { text: string, context: string, user_age: number, personality?: string, difficulty?: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/voice/script`, data);
  }

  getAvailableTopics(userId?: string): Observable<any> {
    const params = userId ? new HttpParams().set('user_id', userId) : {};
    return this.http.get(`${this.apiUrl}/topics`, { params });
  }

  // Utility Methods
  getCurrentUser(): UserProfile | null {
    return this.currentUserSubject.value;
  }

  getCurrentGamification(): GamificationData | null {
    return this.gamificationSubject.value;
  }

  setCurrentUser(user: UserProfile): void {
    this.currentUserSubject.next(user);
  }

  clearSession(): void {
    this.currentUserSubject.next(null);
    this.gamificationSubject.next(null);
  }
}
