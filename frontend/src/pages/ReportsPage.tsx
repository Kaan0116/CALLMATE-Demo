import { useEffect, useState } from "react";
import { reportsApi } from "../api/client";
import { format } from "date-fns";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function ReportsPage() {
  const [report, setReport] = useState<any>(null);
  const [date, setDate] = useState(format(new Date(), "yyyy-MM-dd"));

  useEffect(() => {
    reportsApi.daily(date).then((r) => setReport(r.data)).catch(() => {});
  }, [date]);

  const emotionData = Object.entries(report?.top_emotions ?? {}).map(([k, v]) => ({ name: k, value: v }));

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-100">Raporlar</h2>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-gray-100 focus:outline-none focus:border-brand-500"
        />
      </div>

      {report && (
        <>
          <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
            {[
              { label: "Toplam Çağrı", value: report.total_calls },
              { label: "Ort. Süre (dk)", value: Math.round((report.avg_duration_seconds || 0) / 60) },
              { label: "Kalite", value: `${((report.avg_quality_score || 0) * 100).toFixed(1)}%` },
              { label: "Duygu", value: `${((report.avg_sentiment_score || 0) * 100).toFixed(1)}%` },
            ].map(({ label, value }) => (
              <div key={label} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <div className="text-sm text-gray-400 mb-1">{label}</div>
                <div className="text-2xl font-bold text-gray-100">{value}</div>
              </div>
            ))}
          </div>

          {emotionData.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Duygu Dağılımı</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={emotionData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip contentStyle={{ background: "#111827", border: "1px solid #374151" }} />
                  <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}
    </div>
  );
}
