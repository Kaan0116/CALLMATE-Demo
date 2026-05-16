import { useEffect, useState } from "react";
import { reportsApi, callsApi } from "../api/client";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Phone, TrendingUp, Clock, Star } from "lucide-react";

interface DailyReport {
  total_calls: number;
  avg_duration_seconds: number;
  avg_quality_score: number;
  avg_sentiment_score: number;
  top_emotions: Record<string, number>;
}

interface CallSummary {
  id: string;
  status: string;
  started_at: string;
  duration_seconds: number | null;
  quality_score: number | null;
}

export default function DashboardPage() {
  const [report, setReport] = useState<DailyReport | null>(null);
  const [calls, setCalls] = useState<CallSummary[]>([]);

  useEffect(() => {
    reportsApi.daily().then((r) => setReport(r.data)).catch(() => {});
    callsApi.history(10).then((r) => setCalls(r.data)).catch(() => {});
  }, []);

  const stats = [
    { label: "Bugünkü Çağrılar", value: report?.total_calls ?? "-", icon: Phone, color: "text-blue-400" },
    { label: "Ort. Süre (dk)", value: report ? Math.round((report.avg_duration_seconds || 0) / 60) : "-", icon: Clock, color: "text-purple-400" },
    { label: "Kalite Skoru", value: report ? `${((report.avg_quality_score || 0) * 100).toFixed(0)}%` : "-", icon: Star, color: "text-yellow-400" },
    { label: "Duygu Skoru", value: report ? `${((report.avg_sentiment_score || 0) * 100).toFixed(0)}%` : "-", icon: TrendingUp, color: "text-green-400" },
  ];

  const emotionData = Object.entries(report?.top_emotions ?? {}).map(([emotion, count]) => ({ emotion, count }));

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-100">Dashboard</h2>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-400">{label}</span>
              <Icon size={20} className={color} />
            </div>
            <div className="text-3xl font-bold text-gray-100">{value}</div>
          </div>
        ))}
      </div>

      {/* Emotion Distribution */}
      {emotionData.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Duygu Dağılımı</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={emotionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="emotion" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ background: "#111827", border: "1px solid #374151" }} />
              <Area type="monotone" dataKey="count" stroke="#3b82f6" fill="#1e3a8a" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Recent Calls */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 className="text-lg font-semibold text-gray-100 mb-4">Son Çağrılar</h3>
        {calls.length === 0 ? (
          <p className="text-gray-500 text-sm">Henüz çağrı yok.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-400 text-left border-b border-gray-800">
                <th className="pb-2">ID</th>
                <th className="pb-2">Durum</th>
                <th className="pb-2">Başlangıç</th>
                <th className="pb-2">Süre</th>
                <th className="pb-2">Kalite</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {calls.map((call) => (
                <tr key={call.id} className="text-gray-300">
                  <td className="py-2 font-mono text-xs">{call.id.substring(0, 8)}…</td>
                  <td className="py-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs ${call.status === "completed" ? "bg-green-900 text-green-300" : call.status === "active" ? "bg-blue-900 text-blue-300" : "bg-red-900 text-red-300"}`}>
                      {call.status}
                    </span>
                  </td>
                  <td className="py-2">{new Date(call.started_at).toLocaleString("tr-TR")}</td>
                  <td className="py-2">{call.duration_seconds != null ? `${Math.round(call.duration_seconds / 60)}dk` : "-"}</td>
                  <td className="py-2">{call.quality_score != null ? `${(call.quality_score * 100).toFixed(0)}%` : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
