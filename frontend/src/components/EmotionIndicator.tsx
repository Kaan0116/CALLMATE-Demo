const EMOTION_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  happy: { label: "Mutlu", color: "text-green-400", bg: "bg-green-900/40" },
  angry: { label: "Öfkeli", color: "text-red-400", bg: "bg-red-900/40" },
  stressed: { label: "Stresli", color: "text-orange-400", bg: "bg-orange-900/40" },
  neutral: { label: "Nötr", color: "text-gray-400", bg: "bg-gray-800" },
  sad: { label: "Üzgün", color: "text-blue-400", bg: "bg-blue-900/40" },
  excited: { label: "Heyecanlı", color: "text-yellow-400", bg: "bg-yellow-900/40" },
};

interface Props {
  emotion: string;
  confidence: number;
}

export default function EmotionIndicator({ emotion, confidence }: Props) {
  const cfg = EMOTION_CONFIG[emotion] ?? EMOTION_CONFIG.neutral;
  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${cfg.bg}`}>
      <span className={`text-sm font-medium ${cfg.color}`}>{cfg.label}</span>
      <span className="text-xs text-gray-500">{(confidence * 100).toFixed(0)}%</span>
    </div>
  );
}
