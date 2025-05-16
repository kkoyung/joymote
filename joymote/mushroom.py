import logging
import threading
from math import atan, cos, sin
from time import sleep

from evdev import ecodes as e

logger = logging.getLogger(__name__)


class BaseThread(threading.Thread):
    def __init__(self, ui, *args, **kwargs):
        super(BaseThread, self).__init__(daemon=True, *args, **kwargs)

        self.ui = ui
        self.step_time = 0.02
        self.step_factor = 1000
        self.center_threshold = 3000
        self.stopping_event = threading.Event()
        self.x = 0
        self.y = 0

    def run(self):
        while True:
            self.move()
            sleep(self.step_time)

            if self.stopping_event.is_set():
                break

    def move(self):
        logger.debug("BaseThread: x=%d, y=%d", self.x, self.y)

    def push(self, x, y):
        self.x = x
        self.y = y

        if x**2 + y**2 > self.center_threshold**2:
            # Restart the thread if it has stopped
            if not self.is_alive():
                self.__init__(self.ui)
                self.stopping_event.clear()
                self.start()
        else:
            # Stop the thread
            self.stopping_event.set()


class MouseThread(BaseThread):
    def __init__(self, ui):
        super(MouseThread, self).__init__(ui)

    def move(self):
        logger.debug("MouseThread: x=%d, y=%d", self.x, self.y)

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


class ScrollThread(BaseThread):
    def __init__(self, ui):
        super(ScrollThread, self).__init__(ui)

    def move(self):
        logger.debug("ScrollThread: x=%d, y=%d", self.x, self.y)

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
