from microdot import Microdot
from microdot.sse import with_sse
import time
import asyncio

sse_md = Microdot

# SSE Handler
@sse_md.route("/events", methods=["GET"])
@with_sse
async def handle_sse(request, sse):
    print("Client connected")
    try:
        while True:
            # Example: Send a timestamp every second
            await asyncio.sleep(1)
            await sse.send({"timestamp": time.time()})
    except asyncio.CancelledError:
        pass
    print("Client disconnected")