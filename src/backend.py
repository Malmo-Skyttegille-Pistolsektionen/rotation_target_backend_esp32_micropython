# https://awesome-micropython.com/
# import os
# print(os.listdir(''))


import asyncio
from common.audios import audios
from common.audio import is_supported_wav
from common.utils import dir_exists, file_exists
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

    MUTED_SOCKET_ERRORS.append(113)  # ECONNABORTED error
    Response.default_content_type = "application/json"
    app.mount(api_part, url_prefix="/api/v1")
    app.mount(sse_part, url_prefix="/sse/v1")
    app.mount(static_part, url_prefix="/")

    return app


async def main():
    programs.load_all()  # Load all programs at startup

    print("[Backend] Loaded programs:")
    for program in programs.get_all().values():
        print(f"  id={program.id}, title={program.title}")

    audios.load_all()
    print("[Backend] Loaded audios:")
    for audio in audios.get_all().values():
        print(f"  id={audio.id}, title={audio.title}")

    app = create_app()
    # start the server in a background task
    server = asyncio.create_task(app.start_server(port=8080, debug=True))
    ip_address = network.WLAN(network.STA_IF).ifconfig()[0]
    print(f"Server started on {ip_address}:8080")

    await server


print(
    "8bit_8khz_mono.wav is supported wav: ",
    is_supported_wav("src/resources/audio/8bit_8khz_mono.wav"),
)


asyncio.run(main())
