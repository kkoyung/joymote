import logging
import os
import tomllib
from enum import Enum

from evdev import InputEvent
from evdev import ecodes as e

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        # FIXME: default value, loading order
        home_directory = os.getenv("HOME", "")
        config_path = home_directory + "/.config/joymote/config.toml"

        with open(config_path, "rb") as f:
            self.data = tomllib.load(f)

        self.mapper = Mapper()
        self.options = {
            "revert_scroll_x": False,
            "revert_scroll_y": False,
        }
        self.parse_general()
        self.parse_keys()
        self.parse_analog()

    def parse_general(self):
        if "general" not in self.data:
            return
        general = self.data["general"]

        # Log level
        log_level = general.get("log", "INFO").upper()
        log_level = os.environ.get("JOYMOTE_LOG", log_level).upper()
        logging.basicConfig(level=log_level)

    def parse_keys(self):
        if "keys" in self.data:
            for input_str, target_str in self.data["keys"].items():
                input = Input.from_string(input_str)
                if input is None or input in [
                    Input.LEFT_ANALOG,
                    Input.LEFT_ANALOG_PRESS,
                    Input.RIGHT_ANALOG,
                    Input.RIGHT_ANALOG_PRESS,
                ]:
                    logger.warning("Unknown input '%s'", input_str)
                    continue

                if target_str not in e.ecodes.keys():
                    logger.warning("Unknown target '%s'", input_str)
                    continue

                self.mapper.insert(
                    input, Target(type=TargetType.KEYBOARD, value=e.ecodes[target_str])
                )

    def parse_analog(self):
        if "analog" in self.data:
            for key, value in self.data["analog"].items():
                input = Input.from_string(key)
                if input is not None and input in [
                    Input.LEFT_ANALOG_PRESS,
                    Input.RIGHT_ANALOG_PRESS,
                ]:
                    if value in e.ecodes.keys():
                        self.mapper.insert(
                            input,
                            Target(type=TargetType.KEYBOARD, value=e.ecodes[value]),
                        )
                    else:
                        logger.warning("Unknown value '%s'", key)

                elif input is not None and input in [
                    Input.LEFT_ANALOG,
                    Input.RIGHT_ANALOG,
                ]:
                    if value == "cursor":
                        self.mapper.insert(
                            input,
                            Target(type=TargetType.MOUSE, value=MouseTarget.CURSOR),
                        )
                    elif value == "wheel":
                        self.mapper.insert(
                            input,
                            Target(type=TargetType.MOUSE, value=MouseTarget.WHEEL),
                        )
                    else:
                        logger.warning("Unknown value '%s'", value)
                elif key == "revert_scroll_x":
                    if type(value) is bool:
                        self.options["revert_scroll_x"] = value
                    else:
                        logger.warning("Unknown value '%s'", value)
                elif key == "revert_scroll_y":
                    if type(value) is bool:
                        self.options["revert_scroll_y"] = value
                    else:
                        logger.warning("Unknown value '%s'", value)
                else:
                    logger.warning("Unknown key '%s'", key)


class Input(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    A = 5
    B = 6
    X = 7
    Y = 8
    L = 9
    R = 10
    ZL = 11
    ZR = 12
    PLUS = 13
    MINUS = 14
    CAPTURE = 15
    HOME = 16
    LEFT_ANALOG = 17
    LEFT_ANALOG_PRESS = 18
    RIGHT_ANALOG = 19
    RIGHT_ANALOG_PRESS = 20

    @staticmethod
    def from_string(string: str):
        all_names = [i.name for i in list(Input)]
        if string.upper() in all_names:
            return Input[string.upper()]
        else:
            return None

    @staticmethod
    def from_event(event: InputEvent):
        if event.type == e.EV_KEY:
            if event.code == e.BTN_EAST and event.value == 1:
                return Input.A
            elif event.code == e.BTN_SOUTH and event.value == 1:
                return Input.B
            elif event.code == e.BTN_NORTH and event.value == 1:
                return Input.X
            elif event.code == e.BTN_WEST and event.value == 1:
                return Input.Y
            elif event.code == e.BTN_TL and event.value == 1:
                return Input.L
            elif event.code == e.BTN_TR and event.value == 1:
                return Input.R
            elif event.code == e.BTN_TL2 and event.value == 1:
                return Input.ZL
            elif event.code == e.BTN_TR2 and event.value == 1:
                return Input.ZR
            elif event.code == e.BTN_START and event.value == 1:
                return Input.PLUS
            elif event.code == e.BTN_SELECT and event.value == 1:
                return Input.MINUS
            elif event.code == e.BTN_Z and event.value == 1:
                return Input.CAPTURE
            elif event.code == e.BTN_MODE and event.value == 1:
                return Input.HOME
            else:
                return None
        elif event.type == e.EV_ABS:
            if event.code == e.ABS_X or event.code == e.ABS_Y:
                return Input.LEFT_ANALOG
            elif event.code == e.ABS_RX or event.code == e.ABS_RY:
                return Input.RIGHT_ANALOG
            elif event.code == e.ABS_HAT0Y and event.value == -1:
                return Input.UP
            elif event.code == e.ABS_HAT0Y and event.value == 1:
                return Input.DOWN
            elif event.code == e.ABS_HAT0X and event.value == -1:
                return Input.LEFT
            elif event.code == e.ABS_HAT0X and event.value == 1:
                return Input.RIGHT
            else:
                return None
        else:
            return None


class TargetType(Enum):
    KEYBOARD = 1
    MOUSE = 2
    # COMMAND = 3


type KeyboardTarget = int


class MouseTarget(Enum):
    CURSOR = 1
    WHEEL = 2


# type CommandTarget = str


class Target:
    def __init__(self, type: TargetType, value: KeyboardTarget | MouseTarget):
        self.type = type
        self.value = value


class Mapper:
    def __init__(self):
        self.mapping = {}

    def insert(self, input: Input, target: Target):
        self.mapping[input] = target

    def translate(self, input: Input) -> Target | None:
        if input in self.mapping.keys():
            return self.mapping[input]
        else:
            return None
