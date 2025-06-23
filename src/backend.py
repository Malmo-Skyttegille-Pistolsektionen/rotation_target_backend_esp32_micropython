# https://awesome-micropython.com/
# import os
# logging.debug(os.listdir(''))


import asyncio
from common.audios import audios
from common.audio import is_supported_wav
from common.utils import dir_exists, file_exists
import network

from microdot import Microdot, Response, Request
from microdot.cors import CORS
from microdot.microdot import MUTED_SOCKET_ERRORS
from web.api import api_part
from web.sse import sse_part
from web.static import static_part
from common.programs import programs
import logging


# Initialize Microdot app
def create_app():
    app = Microdot()
    CORS(app, allowed_origins="*")  # Allow all origins

    MUTED_SOCKET_ERRORS.append(113)  # ECONNABORTED error
    Response.default_content_type = "application/json"
    Request.max_content_length = 1024 * 1024  # 1 MB max request size

    app.mount(api_part, url_prefix="/api/v1")
    app.mount(sse_part, url_prefix="/sse/v1")
    app.mount(static_part, url_prefix="/")

    return app


async def main():
    programs.load_all()  # Load all programs at startup

    logging.debug("[Backend] Loaded programs:")
    for program in programs.get_all().values():
        logging.debug(f"  id={program.id}, title={program.title}")

    audios.load_all()
    logging.debug("[Backend] Loaded audios:")
    for audio in audios.get_all().values():
        logging.debug(f"  id={audio.id}, title={audio.title}")

    app = create_app()
    # start the server in a background task
    port = 8080
    server = asyncio.create_task(app.start_server(port=port, debug=True))
    ip_address = network.WLAN(network.STA_IF).ifconfig()[0]
    logging.debug(f"Server started on {ip_address}:{port}")

    await server


logging.debug(
    f"8bit_8khz_mono.wav is supported wav: {
    is_supported_wav("src/resources/audio/8bit_8khz_mono.wav")}"
)


asyncio.run(main())
