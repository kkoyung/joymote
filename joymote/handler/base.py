import logging
from abc import abstractmethod

from evdev import UInput
from evdev.events import InputEvent

logger = logging.getLogger(__name__)


class BaseHandler:
    def __init__(self, ui: UInput):
        self.ui = ui

    @abstractmethod
    def push(self, event: InputEvent):
        pass
