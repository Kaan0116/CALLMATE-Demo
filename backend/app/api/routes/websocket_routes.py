from fastapi import APIRouter, WebSocket, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.websocket.call_handler import CallWebSocketHandler
from app.websocket.connection_manager import coaching_manager

router = APIRouter(tags=["WebSocket"])
_handler = CallWebSocketHandler()


@router.websocket("/ws/call/{call_id}")
async def call_websocket(call_id: str, websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    await _handler.handle(call_id, websocket, db)


@router.websocket("/ws/coaching/{call_id}")
async def coaching_websocket(call_id: str, websocket: WebSocket):
    """Coaching-only stream for operator dashboard."""
    await coaching_manager.connect(call_id, websocket)
    try:
        while True:
            # Keep alive - data pushed from call_handler via coaching_manager.broadcast
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type":"pong"}')
    except Exception:
        pass
    finally:
        await coaching_manager.disconnect(call_id, websocket)
