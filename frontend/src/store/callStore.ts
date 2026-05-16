import { create } from "zustand";
import type { CallSession, TranscriptEntry, EmotionEvent, CoachingSuggestion } from "../types";

interface CallStore {
  activeCall: CallSession | null;
  transcripts: TranscriptEntry[];
  emotions: EmotionEvent[];
  coaching: CoachingSuggestion[];
  isRecording: boolean;
  setActiveCall: (call: CallSession | null) => void;
  addTranscript: (t: TranscriptEntry) => void;
  addEmotion: (e: EmotionEvent) => void;
  addCoaching: (c: CoachingSuggestion) => void;
  clearCall: () => void;
  setRecording: (v: boolean) => void;
}

export const useCallStore = create<CallStore>((set) => ({
  activeCall: null,
  transcripts: [],
  emotions: [],
  coaching: [],
  isRecording: false,
  setActiveCall: (call) => set({ activeCall: call }),
  addTranscript: (t) => set((s) => ({ transcripts: [...s.transcripts.slice(-200), t] })),
  addEmotion: (e) => set((s) => ({ emotions: [...s.emotions.slice(-100), e] })),
  addCoaching: (c) => set((s) => ({ coaching: [c, ...s.coaching.slice(0, 49)] })),
  clearCall: () => set({ activeCall: null, transcripts: [], emotions: [], coaching: [], isRecording: false }),
  setRecording: (v) => set({ isRecording: v }),
}));
