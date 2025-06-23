from microdot import Microdot
from microdot.sse import with_sse
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


@sse_part.get(url_pattern="")
@with_sse
async def handle_sse(request, sse):
    host, port = request.client_addr
    print(f"[SSE] Client connected from {host}:{port}")
    connected_clients.add(sse)
    try:
        while True:
            await asyncio.sleep(60)  # Keep connection alive
    except asyncio.CancelledError:
        print("[SSE] Client disconnected (CancelledError)")
    finally:
        connected_clients.discard(sse)
        print("[SSE] Client removed from connected_clients")


# event: program_added
# data: {"program_id":1}

# event: program_deleted
# data: {"program_id":1}

# event: program_started
# data: {"program_id":0}

# event: program_completed
# data: {"program_id":0}

# event: series_started
# data: {"program_id":0, "series_index":0}

# event: series_stopped
# data: {"program_id":0, "series_index":0, "event_index":1}

# event: event_started
# data: {"program_id":0, "series_index":0, "event_index":1}

# event: series_completed
# data: {"program_id":0, "series_index":0}

# event: series_next
# data: {"program_id":0, "series_index":0}

# event: target_status
# data: {"status":"shown"} # shown, hidden

# event: audio_added
# data: {"audio_id":1}

# event: audio_deleted
# data: {"audio_id":1}

# event: chrono
# data: {elapsed: 123, remaining: 456, total: 579}
