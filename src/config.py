# GPIO pin number used to control the target device (e.g., enable/disable)
TARGET_PIN = 5

# I2S pin configuration for PCM5102A
I2S_BCK_PIN = 26  # Bit Clock
I2S_WS_PIN = 25  # Word Select (LRCK)
I2S_DATA_PIN = 22  # Data Out

# Default I2S configuration
I2S_ID = 0
I2S_SAMPLE_RATE = 8000
I2S_BITS = 16  # PCM5102A supports 16/24/32 bits, but WAV is 8-bit so we'll expand
I2S_CHANNELS = 1  # Mono

# Remove I2C config if not used for audio
