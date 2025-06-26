# from machine import DAC, Pin
import os
from typing import List
import logging
from machine import I2S, Pin
from config import (
    I2S_ID,
    I2S_BCK_PIN,
    I2S_WS_PIN,
    I2S_DATA_PIN,
    I2S_SAMPLE_RATE,
    I2S_BITS,
    I2S_CHANNELS,
)


# Use a global audio_out instance, initialize only once
audio_out = I2S(
    I2S_ID,
    sck=Pin(I2S_BCK_PIN),
    ws=Pin(I2S_WS_PIN),
    sd=Pin(I2S_DATA_PIN),
    mode=I2S.TX,
    bits=I2S_BITS,
    format=I2S.MONO if I2S_CHANNELS == 1 else I2S.STEREO,
    rate=I2S_SAMPLE_RATE,
    ibuf=2048,
)


def is_supported_wav(filename: str) -> bool:
    """Check if WAV file is 8-bit, 8kHz, mono, PCM."""
    try:
        logging.debug(f"Checking WAV file: {filename}")
        with open(filename, "rb") as f:
            header = f.read(44)
            if header[0:4] != b"RIFF" or header[8:12] != b"WAVE":
                logging.debug("Not a valid WAV file:" + filename)
                return False

            # https://docs.fileformat.com/audio/wav/
            audio_format = int.from_bytes(header[20:22], "little")
            num_channels = int.from_bytes(header[22:24], "little")
            sample_rate = int.from_bytes(header[24:28], "little")
            bits_per_sample = int.from_bytes(header[34:36], "little")
            if (
                audio_format == 1  # PCM
                and num_channels == 1
                and sample_rate == 8000
                and bits_per_sample == 8
            ):
                return True
            logging.debug(
                "Unsupported WAV format: "
                f"format={audio_format}, channels={num_channels}, "
                f"rate={sample_rate}, bits={bits_per_sample}"
            )
            return False
    except Exception as e:
        logging.debug("Error reading WAV file:", e)
        return False


def play_wav_pcm5102a(filename: str) -> None:
    """Play an 8-bit, 8kHz, mono PCM WAV file using the PCM5102A via I2S."""
    if not is_supported_wav(filename):
        logging.debug("WAV file format not supported. Must be 8-bit, 8kHz, mono, PCM.")
        return

    try:
        with open(filename, "rb") as f:
            f.read(44)  # Skip WAV header
            while True:
                data = f.read(256)
                if not data:
                    break
                # Convert 8-bit unsigned PCM to 16-bit signed PCM for I2S
                pcm16 = bytearray()
                for b in data:
                    # Convert 8-bit unsigned (0-255) to 16-bit signed (-32768 to 32767)
                    sample = (b - 128) << 8
                    pcm16 += sample.to_bytes(2, "little", signed=True)
                audio_out.write(pcm16)
    except Exception as e:
        logging.debug("Error playing WAV file:", e)
    finally:
        audio_out.deinit()


def list_wav_files(directory: str = "src/resources/audio") -> List[str]:
    wav_files = []
    for file in os.listdir(directory):
        if file.endswith(".wav"):
            wav_files.append(file)
    return wav_files
