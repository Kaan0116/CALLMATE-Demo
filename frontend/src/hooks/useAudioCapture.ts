import { useRef, useState, useCallback } from "react";

const SAMPLE_RATE = 16000;
const CHUNK_SECONDS = 3;

export function useAudioCapture(onChunk: (data: Float32Array, index: number) => void) {
  const [isCapturing, setIsCapturing] = useState(false);
  const streamRef = useRef<MediaStream | null>(null);
  const contextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const chunkIndexRef = useRef(0);
  const bufferRef = useRef<Float32Array[]>([]);
  const samplesCollected = useRef(0);
  const targetSamples = SAMPLE_RATE * CHUNK_SECONDS;

  const start = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: { sampleRate: SAMPLE_RATE, channelCount: 1 } });
    streamRef.current = stream;
    const ctx = new AudioContext({ sampleRate: SAMPLE_RATE });
    contextRef.current = ctx;
    const source = ctx.createMediaStreamSource(stream);
    const processor = ctx.createScriptProcessor(4096, 1, 1);
    processorRef.current = processor;

    processor.onaudioprocess = (e) => {
      const data = e.inputBuffer.getChannelData(0).slice();
      bufferRef.current.push(data);
      samplesCollected.current += data.length;
      if (samplesCollected.current >= targetSamples) {
        const total = bufferRef.current.reduce((a, b) => a + b.length, 0);
        const merged = new Float32Array(total);
        let offset = 0;
        for (const chunk of bufferRef.current) { merged.set(chunk, offset); offset += chunk.length; }
        onChunk(merged, chunkIndexRef.current++);
        bufferRef.current = [];
        samplesCollected.current = 0;
      }
    };

    source.connect(processor);
    processor.connect(ctx.destination);
    setIsCapturing(true);
  }, [onChunk, targetSamples]);

  const stop = useCallback(() => {
    processorRef.current?.disconnect();
    contextRef.current?.close();
    streamRef.current?.getTracks().forEach((t) => t.stop());
    setIsCapturing(false);
    chunkIndexRef.current = 0;
    bufferRef.current = [];
    samplesCollected.current = 0;
  }, []);

  return { start, stop, isCapturing };
}
