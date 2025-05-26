from config import AnalogInput, Config, KeyInput, MouseTarget
from evdev import InputEvent, UInput
from evdev import ecodes as e

from reactor.analog import CursorThread, WheelThread


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
        self.wheel_thread = WheelThread(
            self.mouse_ui,
            self.conf.options["revert_scroll_x"],
            self.conf.options["revert_scroll_y"],
        )

    def push(self, event: InputEvent):
        key_input = KeyInput.from_event(event)
        analog_input = AnalogInput.from_event(event)

        if key_input is not None:
            target = self.conf.mapper.translate(key_input)
            if target is None:
                return

            self.keyboard_ui.write(e.EV_KEY, target, 1)
            self.keyboard_ui.write(e.EV_KEY, target, 0)
            self.keyboard_ui.syn()
        elif analog_input is not None:
            target = self.conf.mapper.translate(analog_input)
            if target is None:
                return

            if target == MouseTarget.CURSOR:
                self.cursor_thread.push(event)
            elif target == MouseTarget.WHEEL:
                self.wheel_thread.push(event)
            else:
                return
