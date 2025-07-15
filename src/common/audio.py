# from machine import DAC, Pin
import os
from typing import Dict, List
import logging

from machine import I2S, Pin
import sys

from config import (
    I2S_ID,
    I2S_BCK_PIN,
    I2S_LCK_PIN,
    I2S_DIN_PIN,
)


# Use a global audio_out instance, initialize only once
audio_out = None  # global, but not initialized yet


def is_supported_wav(filename: str) -> Dict | None:
    """Check if WAV file is PCM, 16-bit, mono or stereo, any sample rate.
    Returns a dict with audio properties if supported, else None.
    """
    try:
        logging.debug(f"Checking WAV file: {filename}")
        with open(filename, "rb") as f:
            header = f.read(44)
            if header[0:4] != b"RIFF" or header[8:12] != b"WAVE":
                logging.debug("Not a valid WAV file:" + filename)
                return None

            audio_format = int.from_bytes(header[20:22], "little")
            num_channels = int.from_bytes(header[22:24], "little")
            sample_rate = int.from_bytes(header[24:28], "little")
            bits_per_sample = int.from_bytes(header[34:36], "little")
            if (
                audio_format == 1  # PCM
                and num_channels in (1, 2)
                and bits_per_sample == 16
            ):
                return {
                    "audio_format": audio_format,
                    "num_channels": num_channels,
                    "sample_rate": sample_rate,
                    "bits_per_sample": bits_per_sample,
                }
            logging.info(
                "Unsupported WAV format: "
                f"format={audio_format}, channels={num_channels}, bits={bits_per_sample}, sample_rate={sample_rate} "
            )
            return None
    except Exception as e:
        logging.debug(f"Error reading WAV file: {e}")
        return None


def play_wav_pcm5102a(filename: str, volume: float = 1.0) -> None:
    """
    Play a WAV file using PCM5102A via I2S.
    :param filename: Path to WAV file.
    :param volume: Volume multiplier (0.0 to 1.0). Default is 1.0 (no change).
    """
    logging.debug(f"play_wav_pcm5102a called with filename={filename}, volume={volume}")
    wav_info: Dict[str, int] | None = is_supported_wav(filename)
    if not wav_info:
        return

    logging.debug(
        f"format={wav_info['audio_format']}, channels={wav_info['num_channels']}, bits={wav_info['bits_per_sample']}, sample_rate={wav_info['sample_rate']}"
    )

    try:
        with open(filename, "rb") as f:
            f.read(44)  # Skip header, already parsed

            audio_out = I2S(
                I2S_ID,
                sck=Pin(I2S_BCK_PIN),
                ws=Pin(I2S_LCK_PIN),
                sd=Pin(I2S_DIN_PIN),
                mode=I2S.TX,
                bits=wav_info["bits_per_sample"],
                format=I2S.STEREO,  # always stereo for both channels, as each mono sample is duplicated to both left and right channels before writing to I2S
                rate=wav_info["sample_rate"],
                ibuf=2048,
            )
            logging.debug("I2S initialized for this playback")

            while True:
                data = f.read(512)
                if not data:
                    logging.debug("End of WAV file reached.")
                    break
                if wav_info["num_channels"] == 2:
                    # Write stereo data directly
                    audio_out.write(data)
                else:
                    # For 16-bit mono to stereo
                    stereo_data = bytearray()
                    for i in range(0, len(data) - 1, 2):
                        sample = data[i : i + 2]
                        stereo_data += sample  # Left
                        stereo_data += sample  # Right
                    audio_out.write(stereo_data)
            logging.debug("Finished playing WAV file.")
            audio_out.deinit()
    except Exception as e:
        logging.debug(f"Error playing WAV file: {e}")
        sys.print_exception(e)


# async def play_wav_asyncio(filename):
#     with open(filename, "rb") as f:
#         header = f.read(44)
#         num_channels = int.from_bytes(header[22:24], "little")
#         swriter = asyncio.StreamWriter(audio_out)
#         while True:
#             data = f.read(512)
#             if not data:
#                 break
#             if num_channels == 2:
#                 pcm16 = bytearray()
#                 for i in range(0, len(data) - 3, 4):
#                     left = int.from_bytes(data[i : i + 2], "little")
#                     right = int.from_bytes(data[i + 2 : i + 4], "little")
#                     mono = (left + right) // 2
#                     pcm16 += mono.to_bytes(2, "little")
#             else:
#                 pcm16 = data
#             swriter.write(pcm16)
#             await swriter.drain()


def list_wav_files(directory: str = "src/resources/audio") -> List[str]:
    wav_files = []
    for file in os.listdir(directory):
        if file.endswith(".wav"):
            wav_files.append(file)
    return wav_files
