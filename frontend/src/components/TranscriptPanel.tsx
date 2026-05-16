import { useEffect, useRef } from "react";
import type { TranscriptEntry } from "../types";
import { format } from "date-fns";

interface Props {
  transcripts: TranscriptEntry[];
}

export default function TranscriptPanel({ transcripts }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [transcripts]);

  return (
    <div className="h-64 overflow-y-auto space-y-2 pr-1">
      {transcripts.length === 0 ? (
        <p className="text-gray-600 text-sm text-center pt-8">Transkript bekleniyor…</p>
      ) : (
        transcripts.map((t, i) => (
          <div key={i} className="flex gap-3 text-sm">
            <span className="text-gray-600 text-xs font-mono shrink-0 pt-0.5">
              {format(t.timestamp, "HH:mm:ss")}
            </span>
            <div>
              <p className="text-gray-200 leading-relaxed">{t.masked || t.text}</p>
              <span className="text-xs text-gray-600">{(t.confidence * 100).toFixed(0)}% güven</span>
            </div>
          </div>
        ))
      )}
      <div ref={bottomRef} />
    </div>
  );
}
