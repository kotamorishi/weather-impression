"""Inky display and GPIO LED control."""

import gpiod
from gpiod.line import Direction, Value

from inky.inky_uc8159 import Inky

from .config import SATURATION

LED_PIN = 4
GPIO_CHIP = "/dev/gpiochip0"


class DisplayController:
    """Manages the Inky e-paper display and status LED."""

    def __init__(self):
        self._led_request = gpiod.request_lines(
            GPIO_CHIP,
            consumer="weather-impression",
            config={
                LED_PIN: gpiod.LineSettings(
                    direction=Direction.OUTPUT,
                    output_value=Value.INACTIVE,
                )
            },
        )
        self._inky = Inky()

    def set_busy(self, busy):
        """Turn the status LED on (busy) or off (idle)."""
        self._led_request.set_value(
            LED_PIN, Value.ACTIVE if busy else Value.INACTIVE
        )

    def show(self, image):
        """Send an image to the Inky display."""
        self._inky.set_image(image, saturation=SATURATION)
        self._inky.show()
