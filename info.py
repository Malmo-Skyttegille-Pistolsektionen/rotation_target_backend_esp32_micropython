import os
import gc
import machine
import esp
import network
import esp32

from micropython import mem_info


def print_system_info():
    print("=== MicroPython System Info ===")
    sys_info = os.uname()
    print(f"System:     {sys_info.sysname}")
    print(f"Node name:  {sys_info.nodename}")
    print(f"Release:    {sys_info.release}")
    print(f"Version:    {sys_info.version}")
    print(f"Machine:    {sys_info.machine}")
    print()


def print_memory_info():
    print("=== Memory Info ===")
    print(f"Mem free:  {gc.mem_free()} bytes")
    print(f"Mem allocated:  {gc.mem_alloc()} bytes")
    # PSRAM status
    try:
        psram_status = "Available" if esp32.ULP() is not None else "Not available"
    except:
        psram_status = "Not detected"
    print(f"PSRAM: {psram_status}")

    # print(f"Mem info: {mem_info(False)}")
    print()


def print_cpu_info():
    print("=== CPU & Flash Info ===")
    print(f"CPU freq:   {machine.freq()} Hz")
    print(f"Flash size: {esp.flash_size()} bytes")
    print()


def print_network_info():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        ip_info = wlan.ifconfig()
        mac = ":".join("{:02x}".format(b) for b in wlan.config("mac"))
        ssid = wlan.config("essid")
        print("=== Network Info ===")
        print(f"Hostname:   {network.hostname()}")
        print(f"SSID:       {ssid}")
        print(f"MAC addr:   {mac}")
        print(f"IP address: {ip_info[0]}")
        print(f"Netmask:    {ip_info[1]}")
        print(f"Gateway:    {ip_info[2]}")
        print(f"DNS:        {ip_info[3]}")
        print()
    else:
        print("=== Network Info ===\nWi-Fi not connected.\n")


def main():
    print_system_info()
    print_memory_info()
    print_cpu_info()
    print_network_info()
