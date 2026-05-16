# CallMate AI

Çağrı merkezleri için yapay zeka destekli gerçek zamanlı analiz platformu.

## Özellikler
- **Gerçek Zamanlı STT**: OpenAI Whisper Large-v3 ile Türkçe ses-metin dönüşümü
- **Duygu Analizi**: BERT tabanlı NLP + akustik özellik füzyonu
- **Live Coaching**: WebSocket üzerinden operatöre anlık öneriler
- **Dinamik Kişilik Profili**: Qdrant vektör veritabanında müşteri embedding'leri
- **Multi-tenant**: Şirket bazlı veri izolasyonu
- **KVKK Uyumlu**: PII maskeleme, AES-256 şifreleme

## Hızlı Başlangıç

### Gereksinimler
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+

### Kurulum

```bash
# Tüm servisleri başlat
docker compose up --build

# VEYA manuel kurulum:
bash scripts/setup_dev.sh
```

### Erişim
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/api/docs
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9090

## Mimari

```
callmate-ai/
├── backend/               # FastAPI + AI/ML Pipeline
│   ├── app/
│   │   ├── api/routes/    # REST endpoints
│   │   ├── core/          # Config, security
│   │   ├── db/            # SQLAlchemy + Redis
│   │   ├── models/        # ORM models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/
│   │   │   ├── audio/     # STT + audio analysis
│   │   │   ├── nlp/       # Emotion + personality
│   │   │   └── coaching/  # Live coaching engine
│   │   └── websocket/     # WS connection manager
│   ├── migrations/        # Alembic migrations
│   └── tests/             # Unit + integration tests
├── frontend/              # React + TypeScript
│   └── src/
│       ├── api/           # Axios client
│       ├── components/    # UI components
│       ├── hooks/         # WS + audio hooks
│       ├── pages/         # Login, Dashboard, Call, Reports
│       ├── store/         # Zustand state
│       └── types/         # TypeScript types
├── infrastructure/
│   ├── nginx/             # Reverse proxy + WS
│   └── prometheus/        # Metrics
└── docker-compose.yml
```

## API Endpoints

| Method | Path | Açıklama |
|--------|------|----------|
| POST | /api/auth/login | Giriş |
| POST | /api/auth/refresh | Token yenileme |
| POST | /api/calls/start | Çağrı başlat |
| POST | /api/calls/end | Çağrı bitir |
| GET | /api/calls/history | Çağrı geçmişi |
| GET | /api/analysis/emotions/{id} | Duygu analizi |
| GET | /api/analysis/personality/{id} | Kişilik profili |
| GET | /api/reports/daily | Günlük rapor |
| WS | /ws/call/{id} | Gerçek zamanlı analiz |
| WS | /ws/coaching/{id} | Coaching akışı |

## WebSocket Protokolü

**Client → Server:**
```json
{ "type": "audio_chunk", "data": "<base64 PCM float32>", "sample_rate": 16000 }
```

**Server → Client:**
```json
{ "type": "transcript", "text": "...", "masked": "...", "confidence": 0.92 }
{ "type": "emotion", "emotion": "neutral", "valence": 0.1, "arousal": 0.3 }
{ "type": "coaching", "coaching_type": "sales_opportunity", "message": "..." }
```

## Test

```bash
cd backend
pytest tests/unit/ -v --cov=app
```
