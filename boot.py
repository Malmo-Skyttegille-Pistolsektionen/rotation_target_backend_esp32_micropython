import os
import network
import sys
from time import sleep

# print(os.listdir(''))

# sys_mpy = sys.implementation._mpy
# arch = [
#     None,
#     "x86",
#     "x64",
#     "armv6",
#     "armv6m",
#     "armv7m",
#     "armv7em",
#     "armv7emsp",
#     "armv7emdp",
#     "xtensa",
#     "xtensawin",
#     "rv32imc",
# ][sys_mpy >> 10]
# print("mpy version:", sys_mpy & 0xFF)
# print("mpy sub-version:", sys_mpy >> 8 & 3)
# print("mpy flags:", end="")
# if arch:
#     print(" -march=" + arch, end="")
# print()

# Wi-Fi credentials
SSID = "geniuses"
PASSWORD = "#1!#2.4Ever-"

# Connect to Wi-Fi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)  # Create a station interface
    wlan.active(True)  # Activate the interface

    print(f"Connecting to Wi-Fi network '{ssid}'...")

    if not wlan.isconnected():
        wlan.connect(ssid, password)  # Connect to the Wi-Fi network

    while not wlan.isconnected():
        sleep(1)
        print("Waiting for connection...")

    print("Connected to Wi-Fi!")
    print("Network config:", wlan.ifconfig())


connect_to_wifi(SSID, PASSWORD)
