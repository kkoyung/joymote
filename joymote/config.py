import logging
import os
import tomllib

from evdev import ecodes as e
from util import (
    AnalogInput,
    CommandTarget,
    KeyboardTarget,
    KeyInput,
    Mapper,
    MouseTarget,
)

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        # FIXME: default value, loading order
        home_directory = os.getenv("HOME", "")
        config_path = home_directory + "/.config/joymote/config.toml"

        with open(config_path, "rb") as f:
            self.data = tomllib.load(f)

        # Default configuration
        self.mapper = Mapper()
        self.options = {
            "revert_scroll_x": False,
            "revert_scroll_y": False,
        }

        # Start parsing
        self.parse_general()
        self.parse_keys()
        self.parse_analog()
        self.parse_options()

    def parse_general(self):
        if "general" not in self.data:
            return
        general = self.data["general"]

        # Log level
        log_level = general.get("log", "INFO").upper()
        log_level = os.environ.get("JOYMOTE_LOG", log_level).upper()
        logging.basicConfig(level=log_level)

    def parse_keys(self):
        if "key" in self.data:
            for input_str, target_str in self.data["key"].items():
                if input_str == "":
                    continue

                input = KeyInput.from_string(input_str)
                if input is None:
                    logger.warning("Unknown input '%s'", input_str)
                    continue

                target_split = target_str.split(":", 1)
                if len(target_split) < 2:
                    logger.warning("Unknown target '%s'", target_str)
                    continue
                target_type = target_split[0].strip()
                target_content = target_split[1].strip()

                if target_type.lower() == "key" and target_content in e.ecodes.keys():
                    self.mapper.insert(input, KeyboardTarget(e.ecodes[target_content]))
                elif target_type.lower() == "command":
                    self.mapper.insert(input, CommandTarget(target_content))
                else:
                    logger.warning("Unknown target '%s'", target_str)

    def parse_analog(self):
        if "analog" in self.data:
            for input_str, target_str in self.data["analog"].items():
                if input_str == "":
                    continue

                input = AnalogInput.from_string(input_str)
                if input is None:
                    logger.warning("Unknown input '%s'", input_str)
                    continue

                if target_str == "cursor":
                    self.mapper.insert(input, MouseTarget.CURSOR)
                elif target_str == "wheel":
                    self.mapper.insert(input, MouseTarget.WHEEL)
                else:
                    logger.warning("Unknown target '%s'", target_str)

    def parse_options(self):
        if "options" in self.data:
            for key, value in self.data["options"].items():
                if key == "revert_scroll_x":
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
