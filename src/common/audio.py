# from machine import DAC, Pin
import os
from typing import List


DEFAULT_DAC_PIN: int = 25


def is_supported_wav(filename: str) -> bool:
    """Check if WAV file is 8-bit, 8kHz, mono, PCM."""
    try:
        print(f"Checking WAV file: {filename}")
        with open(filename, "rb") as f:
            header = f.read(44)
            if header[0:4] != b"RIFF" or header[8:12] != b"WAVE":
                print("Not a valid WAV file:" + filename)
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
            print(
                "Unsupported WAV format: "
                f"format={audio_format}, channels={num_channels}, "
                f"rate={sample_rate}, bits={bits_per_sample}"
            )
            return False
    except Exception as e:
        print("Error reading WAV file:", e)
        return False


# def play_wav(filename: str, pin: int = DEFAULT_DAC_PIN) -> None:
#     """Play an 8-bit, 8kHz, mono PCM WAV file using the ESP32 DAC."""
#     if not is_supported_wav(filename):
#         print("WAV file format not supported. Must be 8-bit, 8kHz, mono, PCM.")
#         return
#     dac = DAC(Pin(pin))
#     with open(filename, "rb") as f:
#         f.read(44)  # Skip WAV header
#         while True:
#             data = f.read(1024)
#             if not data:
#                 break
#             for b in data:
#                 dac.write(b)


def list_wav_files(directory: str = "src/resources/audio") -> List[str]:
    wav_files = []
    for file in os.listdir(directory):
        if file.endswith(".wav"):
            wav_files.append(file)
    return wav_files
