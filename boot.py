import os
import machine
import network

import sys
from time import sleep

from wifi_credentials import PASSWORD, SSID

# BAUDRATE = 921600
# machine.UART(0, baudrate=BAUDRATE)


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
