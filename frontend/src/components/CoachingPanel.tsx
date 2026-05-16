import type { CoachingSuggestion } from "../types";
import { format } from "date-fns";
import { AlertTriangle, Lightbulb, TrendingUp, CheckCircle } from "lucide-react";

const TYPE_CONFIG: Record<string, { label: string; icon: any; color: string }> = {
  tone_warning: { label: "Ton Uyarısı", icon: AlertTriangle, color: "text-orange-400" },
  script_suggestion: { label: "Cümle Önerisi", icon: Lightbulb, color: "text-blue-400" },
  sales_opportunity: { label: "Satış Fırsatı", icon: TrendingUp, color: "text-green-400" },
  procedure_step: { label: "Prosedür", icon: CheckCircle, color: "text-purple-400" },
  profanity_alert: { label: "Uyarı", icon: AlertTriangle, color: "text-red-400" },
  pause_suggestion: { label: "Duraklama", icon: Lightbulb, color: "text-yellow-400" },
};

const URGENCY_BORDER: Record<string, string> = {
  high: "border-l-red-500",
  normal: "border-l-blue-500",
  low: "border-l-gray-600",
};

interface Props {
  suggestions: CoachingSuggestion[];
}

export default function CoachingPanel({ suggestions }: Props) {
  if (suggestions.length === 0) {
    return <p className="text-gray-600 text-sm text-center pt-8">Öneri bekleniyor…</p>;
  }
  return (
    <div className="space-y-3 max-h-96 overflow-y-auto">
      {suggestions.map((s, i) => {
        const cfg = TYPE_CONFIG[s.coaching_type] ?? { label: s.coaching_type, icon: Lightbulb, color: "text-gray-400" };
        const Icon = cfg.icon;
        return (
          <div key={i} className={`border-l-4 ${URGENCY_BORDER[s.urgency]} bg-gray-800/50 rounded-r-lg p-3`}>
            <div className="flex items-center gap-2 mb-1">
              <Icon size={14} className={cfg.color} />
              <span className={`text-xs font-semibold ${cfg.color}`}>{cfg.label}</span>
              <span className="text-xs text-gray-600 ml-auto">{format(s.timestamp, "HH:mm:ss")}</span>
            </div>
            <p className="text-sm text-gray-300">{s.message}</p>
            {s.suggested_phrase && (
              <div className="mt-2 bg-gray-900 rounded p-2">
                <p className="text-xs text-gray-400 mb-1">Önerilen cümle:</p>
                <p className="text-sm text-brand-400 italic">"{s.suggested_phrase}"</p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
