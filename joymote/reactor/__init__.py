import subprocess

from config import AnalogInput, Config, KeyInput, MouseTarget
from evdev import InputEvent, UInput
from evdev import ecodes as e
from util import (
    CommandTarget,
    CursorDirectionTarget,
    Direction,
    KeyboardTarget,
    ScrollDirectionTarget,
)

from reactor.analog import CursorThread, ScrollThread


class Reactor:
    def __init__(self, conf: Config):
        self.conf = conf
        self.keyboard_ui = UInput()
        self.mouse_ui = UInput(
            {
                e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT],
                e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL_HI_RES, e.REL_HWHEEL_HI_RES],
            }
        )
        self.cursor_thread = CursorThread(self.mouse_ui)
        self.scroll_thread = ScrollThread(
            self.mouse_ui,
            self.conf.options["revert_scroll_x"],
            self.conf.options["revert_scroll_y"],
        )

    def push(self, event: InputEvent):
        key_input = KeyInput.from_event(event)
        analog_input = AnalogInput.from_event(event)

        if key_input is not None:
            target = self.conf.mapper.translate(key_input)
            if isinstance(target, KeyboardTarget):
                self.keyboard_ui.write(e.EV_KEY, target.ecodes, 1)
                self.keyboard_ui.write(e.EV_KEY, target.ecodes, 0)
                self.keyboard_ui.syn()
            elif isinstance(target, CommandTarget):
                subprocess.Popen(target.command, stdout=subprocess.DEVNULL, shell=True)
            elif isinstance(target, CursorDirectionTarget):
                if target.direction == Direction.UP:
                    self.mouse_ui.write(e.EV_REL, e.REL_Y, -target.pixel)
                elif target.direction == Direction.DOWN:
                    self.mouse_ui.write(e.EV_REL, e.REL_Y, target.pixel)
                elif target.direction == Direction.LEFT:
                    self.mouse_ui.write(e.EV_REL, e.REL_X, -target.pixel)
                elif target.direction == Direction.RIGHT:
                    self.mouse_ui.write(e.EV_REL, e.REL_X, target.pixel)
                self.mouse_ui.syn()
            elif isinstance(target, ScrollDirectionTarget):
                if target.direction == Direction.UP:
                    self.mouse_ui.write(e.EV_REL, e.REL_WHEEL_HI_RES, target.speed)
                elif target.direction == Direction.DOWN:
                    self.mouse_ui.write(e.EV_REL, e.REL_WHEEL_HI_RES, -target.speed)
                elif target.direction == Direction.LEFT:
                    self.mouse_ui.write(e.EV_REL, e.REL_HWHEEL_HI_RES, -target.speed)
                elif target.direction == Direction.RIGHT:
                    self.mouse_ui.write(e.EV_REL, e.REL_HWHEEL_HI_RES, target.speed)
                self.mouse_ui.syn()

        elif analog_input is not None:
            target = self.conf.mapper.translate(analog_input)
            if target == MouseTarget.CURSOR:
                self.cursor_thread.push(event)
            elif target == MouseTarget.SCROLL:
                self.scroll_thread.push(event)
