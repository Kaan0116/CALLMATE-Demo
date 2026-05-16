import { useState, useCallback } from "react";
import { Phone, PhoneOff, Mic, MicOff } from "lucide-react";
import { callsApi } from "../api/client";
import { useCallStore } from "../store/callStore";
import { useCallWebSocket } from "../hooks/useCallWebSocket";
import { useAudioCapture } from "../hooks/useAudioCapture";
import EmotionIndicator from "../components/EmotionIndicator";
import TranscriptPanel from "../components/TranscriptPanel";
import CoachingPanel from "../components/CoachingPanel";
import EmotionChart from "../components/EmotionChart";

const DEMO_TRANSCRIPTS = [
  "Merhaba, size nasıl yardımcı olabilirim?",
  "Anladım, ürününüzle ilgili bir sorun yaşıyorsunuz.",
  "Hemen çözüm üretiyorum, bir dakika bekler misiniz?",
  "Sisteme baktım, siparişiniz kargoya verilmiş görünüyor.",
  "Tahmini teslimat yarın olarak gözüküyor.",
  "Başka yardımcı olabileceğim bir konu var mı?",
];

const DEMO_EMOTIONS = ["neutral", "stressed", "happy", "neutral", "happy", "excited"] as const;
const DEMO_COACHING = [
  { type: "script_suggestion", msg: "Empati gösterin: 'Anlıyorum, bu durum can sıkıcı olmuş.'", phrase: "Anlıyorum, bu durum gerçekten can sıkıcı. Hemen çözüm üretiyorum." },
  { type: "sales_opportunity", msg: "Satış fırsatı! Ek ürün önerisi yapabilirsiniz.", phrase: "Bu ürünle birlikte genellikle X ürünümüzü de tercih ediyorlar, ister misiniz?" },
  { type: "tone_warning", msg: "Konuşma hızınızı biraz düşürün.", phrase: null },
];

let _demoInterval: ReturnType<typeof setInterval> | null = null;

export default function CallPage() {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const { activeCall, transcripts, emotions, coaching, isRecording, setActiveCall, clearCall, setRecording, addTranscript, addEmotion, addCoaching } = useCallStore();
  const { sendAudioChunk } = useCallWebSocket(activeCall?.call_id ?? null);

  const _startDemoStream = () => {
    let i = 0;
    _demoInterval = setInterval(() => {
      if (i >= DEMO_TRANSCRIPTS.length) { clearInterval(_demoInterval!); return; }
      addTranscript({ text: DEMO_TRANSCRIPTS[i], masked: DEMO_TRANSCRIPTS[i], confidence: 0.92, chunk_index: i, processing_ms: 180, timestamp: new Date() });
      addEmotion({ emotion: DEMO_EMOTIONS[i] as any, confidence: 0.85, valence: i % 2 === 0 ? 0.3 : -0.2, arousal: 0.4, pitch_hz: 180, energy_db: -25, speech_rate_wpm: 130, timestamp: new Date() });
      if (i < DEMO_COACHING.length) {
        const c = DEMO_COACHING[i];
        addCoaching({ coaching_type: c.type, message: c.msg, suggested_phrase: c.phrase, urgency: "normal", timestamp: new Date() });
      }
      i++;
    }, 3000);
  };

  const onChunk = useCallback(
    (data: Float32Array, index: number) => sendAudioChunk(data, index),
    [sendAudioChunk]
  );
  const { start: startCapture, stop: stopCapture, isCapturing } = useAudioCapture(onChunk);

  const startCall = async () => {
    setLoading(true);
    try {
      // Demo mode: mock call session (API auth yokken)
      let callData;
      try {
        const res = await callsApi.start(phoneNumber || undefined);
        callData = res.data;
      } catch {
        // Backend 401 → demo mock
        callData = {
          call_id: `demo-${Date.now()}`,
          websocket_url: `/ws/call/demo`,
          coaching_websocket_url: `/ws/coaching/demo`,
          started_at: new Date().toISOString(),
        };
      }
      setActiveCall(callData);
      // Demo modda sahte transkript ve duygu verisi üret
      _startDemoStream();
    } catch (e) {
      alert("Çağrı başlatılamadı.");
    } finally {
      setLoading(false);
    }
  };

  const endCall = async () => {
    if (!activeCall) return;
    stopCapture();
    setRecording(false);
    if (_demoInterval) { clearInterval(_demoInterval); _demoInterval = null; }
    await callsApi.end(activeCall.call_id).catch(() => {});
    clearCall();
  };

  const toggleMic = async () => {
    if (isCapturing) {
      stopCapture();
      setRecording(false);
    } else {
      await startCapture();
      setRecording(true);
    }
  };

  const lastEmotion = emotions[emotions.length - 1];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-100">Aktif Çağrı</h2>
        {activeCall && (
          <span className="flex items-center gap-2 text-sm text-green-400">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            Bağlı
          </span>
        )}
      </div>

      {/* Call Controls */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        {!activeCall ? (
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm text-gray-400 mb-2">Telefon Numarası (opsiyonel)</label>
              <input
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="0532 xxx xx xx"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-gray-100 focus:outline-none focus:border-brand-500"
              />
            </div>
            <button
              onClick={startCall}
              disabled={loading}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-semibold px-6 py-2.5 rounded-lg transition-colors"
            >
              <Phone size={18} />
              {loading ? "Bağlanıyor..." : "Çağrı Başlat"}
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-4">
            <button
              onClick={toggleMic}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium transition-colors ${isCapturing ? "bg-yellow-600 hover:bg-yellow-700 text-white" : "bg-gray-700 hover:bg-gray-600 text-gray-200"}`}
            >
              {isCapturing ? <><MicOff size={18} /> Mikrofonu Durdur</> : <><Mic size={18} /> Mikrofon Aç</>}
            </button>
            <button
              onClick={endCall}
              className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-semibold px-5 py-2.5 rounded-lg transition-colors"
            >
              <PhoneOff size={18} /> Çağrıyı Bitir
            </button>
            <span className="text-sm text-gray-500 font-mono">ID: {activeCall.call_id.substring(0, 12)}…</span>
          </div>
        )}
      </div>

      {activeCall && (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Left: Transcript + Emotion Chart */}
          <div className="xl:col-span-2 space-y-6">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-100">Transkript</h3>
                {lastEmotion && <EmotionIndicator emotion={lastEmotion.emotion} confidence={lastEmotion.confidence} />}
              </div>
              <TranscriptPanel transcripts={transcripts} />
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Duygu Grafiği</h3>
              <EmotionChart emotions={emotions} />
            </div>
          </div>

          {/* Right: Coaching */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">
              Live Coaching
              {coaching.length > 0 && (
                <span className="ml-2 bg-brand-600 text-white text-xs px-2 py-0.5 rounded-full">{coaching.length}</span>
              )}
            </h3>
            <CoachingPanel suggestions={coaching} />
          </div>
        </div>
      )}
    </div>
  );
}
