import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import type { EmotionEvent } from "../types";
import { format } from "date-fns";

interface Props {
  emotions: EmotionEvent[];
}

export default function EmotionChart({ emotions }: Props) {
  if (emotions.length === 0) {
    return <div className="h-40 flex items-center justify-center text-gray-600 text-sm">Duygu verisi bekleniyor…</div>;
  }

  const data = emotions.map((e) => ({
    time: format(e.timestamp, "HH:mm:ss"),
    valence: parseFloat((e.valence * 100).toFixed(1)),
    arousal: parseFloat((e.arousal * 100).toFixed(1)),
    confidence: parseFloat((e.confidence * 100).toFixed(1)),
  }));

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="time" stroke="#6b7280" tick={{ fontSize: 11 }} />
        <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} domain={[-100, 100]} />
        <Tooltip contentStyle={{ background: "#111827", border: "1px solid #374151", fontSize: 12 }} />
        <Legend />
        <Line type="monotone" dataKey="valence" name="Valence" stroke="#3b82f6" dot={false} strokeWidth={2} />
        <Line type="monotone" dataKey="arousal" name="Arousal" stroke="#f59e0b" dot={false} strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
