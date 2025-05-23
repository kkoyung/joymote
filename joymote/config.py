import logging
import os
import tomllib

from evdev import ecodes as e
from util import Input, Mapper, MouseTargetValue, Target, TargetType

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
                            Target(
                                type=TargetType.MOUSE, value=MouseTargetValue.CURSOR
                            ),
                        )
                    elif value == "wheel":
                        self.mapper.insert(
                            input,
                            Target(type=TargetType.MOUSE, value=MouseTargetValue.WHEEL),
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
