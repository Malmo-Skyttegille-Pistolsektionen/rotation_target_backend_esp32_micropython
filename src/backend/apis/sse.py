from microdot import Microdot
from microdot.sse import with_sse
import asyncio
import logging

logging.debug("[SSE] Importing SSE routes...")

sse_part = Microdot()
connected_clients = set()

HEARTBEAT_INTERVAL = 15  # seconds


async def emit_sse_event(event, data):
    logging.debug(
        f"[SSE] Emitting event '{event}' to {len(connected_clients)} clients: {data}"
    )
    for sse in list(connected_clients):
        try:
            await sse.send(data, event=event)
        except Exception as e:
            logging.warning(f"[SSE] Removing disconnected client due to error: {e}")
            connected_clients.discard(sse)


@sse_part.get(url_pattern="")
@with_sse
async def handle_sse(request, sse):
    host, port = request.client_addr
    logging.info(
        f"[SSE] Client connected from {host}:{port} ({len(connected_clients)+1} clients)"
    )
    connected_clients.add(sse)
    heartbeat_id = 1
    try:
        while True:
            await sse.send(
                {"id": heartbeat_id}, event="heartbeat"
            )  # Send heartbeat event with counter
            logging.info(f"[SSE] Heartbeat id={heartbeat_id} sent to {host}:{port}")
            heartbeat_id += 1
            await asyncio.sleep(HEARTBEAT_INTERVAL)
    except asyncio.CancelledError:
        logging.info(f"[SSE] Client {host}:{port} disconnected (CancelledError)")
    finally:
        connected_clients.discard(sse)
        logging.info(
            f"[SSE] Client {host}:{port} removed from connected_clients ({len(connected_clients)} clients left)"
        )
