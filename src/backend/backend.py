# https://awesome-micropython.com/
# import os
# logging.debug(os.listdir(''))


import asyncio


import network
import logging

from microdot import Microdot, Response, Request
from microdot.cors import CORS
from microdot.microdot import MUTED_SOCKET_ERRORS
from backend.apis.api import api_part
from backend.apis.sse import sse_part
from backend.apis.static import static_part
from backend.repositories.programs import programs
from backend.repositories.audios import audios
from backend.common.rgb_led import rgb_led


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

    audios.load_all()  # Load all audios at startup

    app = create_app()
    # start the server in a background task
    port = 80
    server = asyncio.create_task(app.start_server(port=port))
    ip_address = network.WLAN(network.STA_IF).ifconfig()[0]
    logging.info(f"[Backend] Server started on {ip_address}:{port}")
    rgb_led.set_green()

    await server


# WAV_FILENAME = "src/resources/audio/1.wav"

# from backend.dataclasses.audio import is_supported_wav, play_wav_asyncio
# import time


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
