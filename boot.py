import network
import sys

from time import sleep

from wifi_credentials import NETWORKS

sys.path.insert(0, "/libs")
sys.path.insert(0, "/src")

from backend.common.rgb_led import rgb_led

# BAUDRATE = 921600
# machine.UART(0, baudrate=BAUDRATE)


# Connect to Wi-Fi
def connect_to_wifi(ssid, password, max_attempts=3):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm=wlan.PM_PERFORMANCE)
    print(f"Connecting to Wi-Fi network '{ssid}'...")

    for attempt in range(1, max_attempts + 1):
        if not wlan.isconnected():
            wlan.connect(ssid, password)
        tries = 0
        while not wlan.isconnected() and tries < 5:
            rgb_led.set_red()
            sleep(1)
            print(f"Waiting for connection... (attempt {attempt}, try {tries+1})")
            rgb_led.set_color(0, 0, 0)
            tries += 1
        if wlan.isconnected():
            rgb_led.set_yellow()
            print("Connected to Wi-Fi!")
            print("Network config:", wlan.ifconfig())
            return True
        else:
            print(f"Failed to connect to '{ssid}' on attempt {attempt}.")
    return False


# Try each network in round robin fashion, 3 attempts per network
for ssid, password in NETWORKS:
    print(f"Trying network: {ssid}")
    if connect_to_wifi(ssid, password, max_attempts=3):
        break
else:
    print("Could not connect to any Wi-Fi network.")
    rgb_led.set_red()
