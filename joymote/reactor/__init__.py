from config import Config, Input, MouseTargetValue
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
        input = Input.from_event(event)
        if input is None:
            return

        target = self.conf.mapper.translate(input)
        if target is None:
            return

        if input not in [Input.LEFT_ANALOG, Input.RIGHT_ANALOG]:
            self.keyboard_ui.write(e.EV_KEY, target.value, 1)
            self.keyboard_ui.write(e.EV_KEY, target.value, 0)
            self.keyboard_ui.syn()
        else:
            if target.value == MouseTargetValue.CURSOR:
                self.cursor_thread.push(event)
            elif target.value == MouseTargetValue.WHEEL:
                self.wheel_thread.push(event)
            else:
                return
