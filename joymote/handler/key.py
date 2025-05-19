import logging

from handler.base import BaseHandler
from evdev import UInput
from evdev import ecodes as e
from evdev.events import InputEvent

logger = logging.getLogger(__name__)


class KeyHandler(BaseHandler):
    def __init__(self, ui: UInput, keys_mapping):
        super().__init__(ui)
        self.keys_mapping = keys_mapping

    def push(self, event: InputEvent):
        if event.type == e.EV_KEY:
            if event.code in self.keys_mapping:
                logger.debug(
                    "KeyHandler maps %s to %s",
                    e.bytype[e.EV_KEY][event.code],
                    e.bytype[e.EV_KEY][self.keys_mapping[event.code]],
                )
                self.ui.write(e.EV_KEY, self.keys_mapping[event.code], event.value)
                self.ui.syn()
        else:
            logger.error("Pushed non-KeyEvent to KeyHandler")
