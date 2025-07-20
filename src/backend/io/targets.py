from backend.repositories import program_state
from time import ticks_ms, ticks_diff
from machine import Pin
from backend.config import TARGET_PIN


targets = Pin(TARGET_PIN, Pin.OUT)

last_target_action_time = None


def _update_last_action_time():
    global last_target_action_time
    now = ticks_ms()
    if last_target_action_time is not None:
        elapsed = ticks_diff(now, last_target_action_time)
        print(f"############ Time since last target action: {elapsed} ms")
    last_target_action_time = now


def show():
    program_state.target_status_shown = True
    _update_last_action_time()
    target.value(0)  # Set pin low to open the connection (deactivate relay/MOSFET)


def hide():
    program_state.target_status_shown = False
    _update_last_action_time()
    target.value(1)  # Set pin high to close the connection (activate relay/MOSFET)
