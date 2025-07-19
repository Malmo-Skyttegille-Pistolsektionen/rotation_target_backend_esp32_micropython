# https://awesome-micropython.com/
# import os
# logging.debug(os.listdir(''))


import asyncio
from common.audios import audios
from common.audio import is_supported_wav, play_wav_asyncio
import network
import time

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

    logging.info("[Backend] Loaded programs:")
    for program in programs.get_all().values():
        logging.info(f"  id={program.id}, title={program.title}")

    audios.load_all()
    logging.info("[Backend] Loaded audios:")
    for audio in audios.get_all().values():
        logging.info(f"  id={audio.id}, title={audio.title}")

    app = create_app()
    # start the server in a background task
    port = 8080
    server = asyncio.create_task(app.start_server(port=port, debug=True))
    ip_address = network.WLAN(network.STA_IF).ifconfig()[0]
    logging.info(f"Server started on {ip_address}:{port}")

    await server


# WAV_FILENAME = "src/resources/audio/1.wav"

# logging.debug("Checking audio files support...")
# logging.debug(
#     f"{WAV_FILENAME} is supported wav: {
#     is_supported_wav(WAV_FILENAME)}"
# )

# logging.info("Starting playback using play_wav_asyncio...")

# start_time = time.ticks_ms()

# asyncio.create_task(play_wav_asyncio(WAV_FILENAME))

# end_time = time.ticks_ms()
# elapsed = time.ticks_diff(end_time, start_time)
# logging.info(f"play_wav executed in {elapsed} ms")

asyncio.run(main())
