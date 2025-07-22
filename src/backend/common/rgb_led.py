import machine
import neopixel
from typing import Tuple, Optional
from backend.config import RGG_LED_PIN

NUM_LEDS = 1


class RGBLed:
    GREEN: Tuple[int, int, int] = (0, 10, 0)
    RED: Tuple[int, int, int] = (100, 0, 0)
    OFF: Tuple[int, int, int] = (0, 0, 0)

    def __init__(self, pin: int = RGG_LED_PIN, num_leds: int = NUM_LEDS) -> None:
        self.np: neopixel.NeoPixel = neopixel.NeoPixel(machine.Pin(pin), num_leds)
        self.set_color(*self.OFF)

    def set_color(self, r: int, g: int, b: int) -> None:
        self.np[0] = (r, g, b)
        self.np.write()

    def set_green(self) -> None:
        self.set_color(*self.GREEN)

    def set_red(self) -> None:
        self.set_color(*self.RED)

    def turn_off(self) -> None:
        self.set_color(*self.OFF)


rgb_led = RGBLed()
