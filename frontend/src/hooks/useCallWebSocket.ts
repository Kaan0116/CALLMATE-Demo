import { useEffect, useRef, useCallback } from "react";
import { useCallStore } from "../store/callStore";
import type { WSMessage } from "../types";

export function useCallWebSocket(callId: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const coachingWsRef = useRef<WebSocket | null>(null);
  const { addTranscript, addEmotion, addCoaching } = useCallStore();

  const handleMessage = useCallback((msg: WSMessage) => {
    const now = new Date();
    switch (msg.type) {
      case "transcript":
        addTranscript({
          text: msg.text as string,
          masked: msg.masked as string,
          confidence: msg.confidence as number,
          chunk_index: msg.chunk_index as number,
          processing_ms: msg.processing_ms as number,
          timestamp: now,
        });
        break;
      case "emotion":
        addEmotion({
          emotion: msg.emotion as any,
          confidence: msg.confidence as number,
          valence: msg.valence as number,
          arousal: msg.arousal as number,
          pitch_hz: msg.pitch_hz as number | null,
          energy_db: msg.energy_db as number,
          speech_rate_wpm: msg.speech_rate_wpm as number | null,
          timestamp: now,
        });
        break;
      case "coaching":
        addCoaching({
          coaching_type: msg.coaching_type as string,
          message: msg.message as string,
          suggested_phrase: msg.suggested_phrase as string | null,
          urgency: msg.urgency as any,
          timestamp: now,
        });
        break;
    }
  }, [addTranscript, addEmotion, addCoaching]);

  useEffect(() => {
    if (!callId) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const base = `${protocol}//${window.location.host}`;

    wsRef.current = new WebSocket(`${base}/ws/call/${callId}`);
    coachingWsRef.current = new WebSocket(`${base}/ws/coaching/${callId}`);

    wsRef.current.onmessage = (e) => handleMessage(JSON.parse(e.data));
    coachingWsRef.current.onmessage = (e) => handleMessage(JSON.parse(e.data));

    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) wsRef.current.send(JSON.stringify({ type: "ping" }));
      if (coachingWsRef.current?.readyState === WebSocket.OPEN) coachingWsRef.current.send("ping");
    }, 30000);

    return () => {
      clearInterval(pingInterval);
      wsRef.current?.close();
      coachingWsRef.current?.close();
    };
  }, [callId, handleMessage]);

  const sendAudioChunk = useCallback((audioData: Float32Array, chunkIndex: number) => {
    if (wsRef.current?.readyState !== WebSocket.OPEN) return;
    const bytes = new Uint8Array(audioData.buffer);
    const base64 = btoa(String.fromCharCode(...bytes));
    wsRef.current.send(JSON.stringify({
      type: "audio_chunk",
      data: base64,
      sample_rate: 16000,
      chunk_index: chunkIndex,
    }));
  }, []);

  return { sendAudioChunk };
}
