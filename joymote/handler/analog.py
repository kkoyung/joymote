import logging
import threading
from abc import abstractmethod
from math import atan, cos, sin
from time import sleep

from evdev import InputEvent, UInput
from evdev import ecodes as e

from handler.base import BaseHandler

logger = logging.getLogger(__name__)


class AnalogHandler(BaseHandler, threading.Thread):
    def __init__(self, ui: UInput):
        BaseHandler.__init__(self, ui)
        threading.Thread.__init__(self, daemon=True)

        self.step_time = 0.02
        self.step_factor = 1000
        self.center_threshold = 3000
        self.stopping_event = threading.Event()
        self.x = 0
        self.y = 0

    def run(self):
        while True:
            self.step()
            sleep(self.step_time)

            if self.stopping_event.is_set():
                break

    def step(self):
        logger.debug("AnalogHandler make a step: x=%d, y=%d", self.x, self.y)

    def push(self, event: InputEvent):
        if event.type == e.EV_ABS:
            if event.code == e.ABS_X or event.code == e.ABS_RX:
                self.x = event.value
            elif event.code == e.ABS_Y or event.code == e.ABS_RY:
                self.y = event.value
        else:
            logger.error("Pushed non-AbsEvent to AnalogHandler")
            return

        if self.x**2 + self.y**2 > self.center_threshold**2:
            # Restart the thread if it has stopped
            if not self.is_alive():
                self.__init__(self.ui)
                self.stopping_event.clear()
                self.start()
        else:
            # Stop the thread
            self.stopping_event.set()


class MouseHandler(AnalogHandler):
    def step(self):
        logger.debug("MouseHandler make a step: x=%d, y=%d", self.x, self.y)

        if self.x == 0:
            self.x = 1  # set to 1 to avoid division of zero

        rel_x = int(
            (self.x - self.center_threshold * cos(atan(self.y / self.x)))
            / self.step_factor
        )
        rel_y = int(
            (self.y - self.center_threshold * sin(atan(self.y / self.x)))
            / self.step_factor
        )
        self.ui.write(e.EV_REL, e.REL_X, rel_x)
        self.ui.write(e.EV_REL, e.REL_Y, rel_y)
        self.ui.syn()


class ScrollHandler(AnalogHandler):
    def step(self):
        logger.debug("ScrollHandler make a step: x=%d, y=%d", self.x, self.y)

        if self.x == 0:
            self.x = 1  # set to 1 to avoid division of zero

        rel_x = int(
            (self.x - self.center_threshold * cos(atan(self.y / self.x)))
            / self.step_factor
        )
        rel_y = int(
            (self.y - self.center_threshold * sin(atan(self.y / self.x)))
            / self.step_factor
        )

        self.ui.write(e.EV_REL, e.REL_HWHEEL_HI_RES, rel_x)
        self.ui.write(e.EV_REL, e.REL_WHEEL_HI_RES, rel_y)
        self.ui.syn()
