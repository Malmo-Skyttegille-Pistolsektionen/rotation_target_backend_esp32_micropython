from microdot import Microdot
from microdot.sse import with_sse
import time
import asyncio

print("[SSE] Importing SSE routes...")

sse_part = Microdot()
connected_clients = set()


async def emit_sse_event(event, data):
    print(f"[SSE] Emitting event '{event}' to {len(connected_clients)} clients: {data}")
    for sse in list(connected_clients):
        try:
            await sse.send(data, event=event)
        except Exception as e:
            print(f"[SSE] Removing disconnected client: {e}")
            connected_clients.discard(sse)


@sse_part.route(url_pattern="/v1", methods=["GET"])
@with_sse
async def handle_sse(request, sse):
    print("[SSE] Client connected")
    connected_clients.add(sse)
    try:
        while True:
            await asyncio.sleep(60)  # Keep connection alive
    except asyncio.CancelledError:
        print("[SSE] Client disconnected (CancelledError)")
    finally:
        connected_clients.discard(sse)
        print("[SSE] Client removed from connected_clients")
