// Core Models
export interface UserProfile {
  user_id: string;
  name: string;
  age: number;
  hobbies: string[];
  interests: string[];
  learning_style?: string;
}

export interface GamificationData {
  user_id: string;
  total_points: number;
  level: string;
  badges: string[];
  streak_days: number;
  quizzes_completed: number;
  perfect_scores: number;
}

export interface QuizHistory {
  quiz_id: string;
  user_id: string;
  concept: string;
  title?: string;
  score: number;
  total_questions: number;
  completed_at: string;
}

export interface Transaction {
  transaction_id: string;
  user_id: string;
  amount: number;
  category: string;
  merchant: string;
  description: string;
  timestamp: string;
}

export interface CaseBrief {
  case_id: string;
  title: string;
  mission: string;
  clues: string[];
  scenario: string;
  concept: string;
  age_appropriate?: boolean;
  personalization_elements?: string[];
  image_url?: string;
}

export interface Quiz {
  quiz_id: string;
  user_id: string;
  concept: string;
  difficulty: string;
  case_brief?: CaseBrief;
  story?: EducationalStory;
  questions: QuizQuestion[];
}

export interface EducationalStory {
  story_id: string;
  concept: string;
  title: string;
  narrative?: string;
  content?: string;
  characters?: string[];
}

export interface QuizQuestion {
  question_id: string;
  question_text: string;
  options: string[];
  correct_answer: string;
  explanation: string;
}

export interface QuizResponse {
  quiz_id: string;
  user_id: string;
  answers: { [question_id: string]: string };
}

export interface QuizResult {
  quiz_id: string;
  user_id: string;
  score: number;
  total_questions: number;
  percentage: number;
  feedback: string;
  gamification_updates: GamificationData;
}

// Detective Ranks
export enum DetectiveRank {
  ROOKIE = 'Rookie Detective',
  JUNIOR = 'Junior Detective',
  DETECTIVE = 'Detective',
  SENIOR = 'Senior Detective',
  CHIEF = 'Chief Detective',
  LEGEND = 'Legendary Detective'
}

// Badge Types
export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}
