export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "admin" | "supervisor" | "operator";
  company_id: string;
}

export interface AuthState {
  user: User | null;
  access_token: string | null;
  isAuthenticated: boolean;
}

export interface CallSession {
  call_id: string;
  websocket_url: string;
  coaching_websocket_url: string;
  started_at: string;
}

export interface TranscriptEntry {
  text: string;
  masked: string;
  confidence: number;
  chunk_index: number;
  processing_ms: number;
  timestamp: Date;
}

export interface EmotionEvent {
  emotion: "happy" | "angry" | "stressed" | "neutral" | "sad" | "excited";
  confidence: number;
  valence: number;
  arousal: number;
  pitch_hz: number | null;
  energy_db: number;
  speech_rate_wpm: number | null;
  timestamp: Date;
}

export interface CoachingSuggestion {
  coaching_type: string;
  message: string;
  suggested_phrase: string | null;
  urgency: "low" | "normal" | "high";
  timestamp: Date;
}

export interface WSMessage {
  type: "transcript" | "emotion" | "coaching" | "error" | "pong";
  [key: string]: unknown;
}
