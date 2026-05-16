import { useEffect, useState } from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Phone, TrendingUp, Clock, Star } from "lucide-react";

const DEMO_REPORT = {
  total_calls: 147,
  avg_duration_seconds: 342,
  avg_quality_score: 0.84,
  avg_sentiment_score: 0.71,
  top_emotions: { neutral: 58, happy: 42, stressed: 27, angry: 12, sad: 8 },
};

const DEMO_CALLS = [
  { id: "a1b2c3d4-0001", status: "completed", started_at: new Date(Date.now() - 3600000).toISOString(), duration_seconds: 284, quality_score: 0.88 },
  { id: "a1b2c3d4-0002", status: "completed", started_at: new Date(Date.now() - 7200000).toISOString(), duration_seconds: 412, quality_score: 0.76 },
  { id: "a1b2c3d4-0003", status: "completed", started_at: new Date(Date.now() - 10800000).toISOString(), duration_seconds: 198, quality_score: 0.91 },
  { id: "a1b2c3d4-0004", status: "completed", started_at: new Date(Date.now() - 14400000).toISOString(), duration_seconds: 567, quality_score: 0.65 },
  { id: "a1b2c3d4-0005", status: "active",    started_at: new Date(Date.now() - 900000).toISOString(),   duration_seconds: null, quality_score: null },
];

export default function DashboardPage() {
  const [report] = useState(DEMO_REPORT);
  const [calls] = useState(DEMO_CALLS);

  const stats = [
    { label: "Bugünkü Çağrılar", value: report.total_calls, icon: Phone, color: "text-blue-400" },
    { label: "Ort. Süre (dk)", value: Math.round(report.avg_duration_seconds / 60), icon: Clock, color: "text-purple-400" },
    { label: "Kalite Skoru", value: `${(report.avg_quality_score * 100).toFixed(0)}%`, icon: Star, color: "text-yellow-400" },
    { label: "Duygu Skoru", value: `${(report.avg_sentiment_score * 100).toFixed(0)}%`, icon: TrendingUp, color: "text-green-400" },
  ];

  const emotionData = Object.entries(report.top_emotions).map(([emotion, count]) => ({ emotion, count }));

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-100">Dashboard</h2>
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

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 className="text-lg font-semibold text-gray-100 mb-4">Son Çağrılar</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-400 text-left border-b border-gray-800">
              <th className="pb-2">ID</th><th className="pb-2">Durum</th>
              <th className="pb-2">Başlangıç</th><th className="pb-2">Süre</th><th className="pb-2">Kalite</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {calls.map((call) => (
              <tr key={call.id} className="text-gray-300">
                <td className="py-2 font-mono text-xs">{call.id.substring(0, 12)}…</td>
                <td className="py-2">
                  <span className={`px-2 py-0.5 rounded-full text-xs ${call.status === "completed" ? "bg-green-900 text-green-300" : "bg-blue-900 text-blue-300"}`}>
                    {call.status}
                  </span>
                </td>
                <td className="py-2">{new Date(call.started_at).toLocaleString("tr-TR")}</td>
                <td className="py-2">{call.duration_seconds != null ? `${Math.round(call.duration_seconds / 60)}dk` : "—"}</td>
                <td className="py-2">{call.quality_score != null ? `${(call.quality_score * 100).toFixed(0)}%` : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
