from microdot import Microdot
from microdot.sse import with_sse
import asyncio
import logging

logging.debug("[SSE] Importing SSE routes...")

sse_part = Microdot()
connected_clients = set()


async def emit_sse_event(event, data):
    logging.debug(
        f"[SSE] Emitting event '{event}' to {len(connected_clients)} clients: {data}"
    )
    for sse in list(connected_clients):
        try:
            await sse.send(data, event=event)
        except Exception as e:
            logging.debug(f"[SSE] Removing disconnected client: {e}")
            connected_clients.discard(sse)


@sse_part.get(url_pattern="")
@with_sse
async def handle_sse(request, sse):
    host, port = request.client_addr
    logging.info(
        f"[SSE] Client connected from {host}:{port} ({len(connected_clients)} clients)"
    )
    connected_clients.add(sse)
    try:
        while True:
            await asyncio.sleep(60)  # Keep connection alive
    except asyncio.CancelledError:
        logging.debug("[SSE] Client disconnected (CancelledError)")
    finally:
        connected_clients.discard(sse)
        logging.debug("[SSE] Client removed from connected_clients")
