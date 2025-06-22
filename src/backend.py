# https://awesome-micropython.com/
# import os
# print(os.listdir(''))


import asyncio
import network

from microdot import Microdot, Response
from microdot.cors import CORS
from microdot.microdot import MUTED_SOCKET_ERRORS
from web.api import api_part
from web.sse import sse_part
from web.static import static_part
from common.programs import programs


# Initialize Microdot app
def create_app():
    app = Microdot()
    CORS(app, allowed_origins="*")  # Allow all origins

    MUTED_SOCKET_ERRORS.append(113)  # ECONNABORTED errorimport asyncio
    Response.default_content_type = "application/json"
    app.mount(api_part, url_prefix="/api/v1")
    app.mount(sse_part, url_prefix="/sse")
    app.mount(static_part, url_prefix="/")

    return app


async def main():
    programs.load_all_from_dir()  # Load all programs at startup

    print("[Backend] Loaded programs:")
    for program in programs.list():
        print(f"  id={program['id']}, title={program['title']}")

    app = create_app()
    # start the server in a background task
    server = asyncio.create_task(app.start_server(port=8080, debug=True))
    ip_address = network.WLAN(network.STA_IF).ifconfig()[0]
    print(f"Server started on {ip_address}:8080")

    # ... do other asynchronous work here ...

    # cleanup before ending the application
    await server


asyncio.run(main())
