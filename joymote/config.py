import logging
import os
import tomllib

from evdev import ecodes as e

from .util import (
    AnalogInput,
    CommandTarget,
    ControllerType,
    CursorDirectionTarget,
    Direction,
    KeyboardTarget,
    KeyInput,
    Mapper,
    MouseTarget,
    ScrollDirectionTarget,
)

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, config_path: str):
        try:
            config_file = open(config_path, "rb")
            data = tomllib.load(config_file)
        except Exception:
            logger.error(f"Cannot open config file: {config_path}")
            exit()

        if "general" in data:
            # Log level
            log_level = data["general"].get("log", "INFO").upper()
            log_level = os.environ.get("JOYMOTE_LOG", log_level).upper()
            logging.basicConfig(level=log_level)

        self.pro_contoller = ControllerConfig(
            data.get("pro_controller", {}), ControllerType.PRO_CONTOLLER
        )
        self.joy_con_left = ControllerConfig(
            data.get("joy_con_left", {}), ControllerType.JOY_CON_LEFT
        )
        self.joy_con_right = ControllerConfig(
            data.get("joy_con_right", {}), ControllerType.JOY_CON_RIGHT
        )


class ControllerConfig:
    def __init__(self, data: dict, controller_type: ControllerType):
        self.controller_type = controller_type

        # Default configuration
        self.mapper = Mapper()
        self.options = {
            "revert_scroll_x": False,
            "revert_scroll_y": False,
            "cursor_speed": 1.0,
            "scroll_speed": 1.0,
            "left_analog_idle_range": 1.0,
            "right_analog_idle_range": 1.0,
        }

        # Start parsing
        self.parse_keys(data)
        self.parse_analog(data)
        self.parse_options(data)

    def parse_keys(self, data: dict):
        if "key" in data:
            for input_str, target_str in data["key"].items():
                if input_str == "":
                    continue

                input = KeyInput.from_string(input_str, self.controller_type)
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
                elif target_type.lower() == "cursor_up":
                    try:
                        target_content = int(target_content)
                        if target_content < 0:
                            raise Exception("Negative value")
                        self.mapper.insert(
                            input, CursorDirectionTarget(Direction.UP, target_content)
                        )
                    except Exception:
                        logger.warning("Unknown target '%s'", target_str)
                elif target_type.lower() == "cursor_down":
                    try:
                        target_content = int(target_content)
                        if target_content < 0:
                            raise Exception("Negative value")
                        self.mapper.insert(
                            input, CursorDirectionTarget(Direction.DOWN, target_content)
                        )
                    except Exception:
                        logger.warning("Unknown target '%s'", target_str)
                elif target_type.lower() == "cursor_left":
                    try:
                        target_content = int(target_content)
                        if target_content < 0:
                            raise Exception("Negative value")
                        self.mapper.insert(
                            input, CursorDirectionTarget(Direction.LEFT, target_content)
                        )
                    except Exception:
                        logger.warning("Unknown target '%s'", target_str)
                elif target_type.lower() == "cursor_right":
                    try:
                        target_content = int(target_content)
                        if target_content < 0:
                            raise Exception("Negative value")
                        self.mapper.insert(
                            input,
                            CursorDirectionTarget(Direction.RIGHT, target_content),
                        )
                    except Exception:
                        logger.warning("Unknown target '%s'", target_str)
                elif target_type.lower() == "scroll_up":
                    try:
                        target_content = int(target_content)
                        if target_content < 0:
                            raise Exception("Negative value")
                        self.mapper.insert(
                            input, ScrollDirectionTarget(Direction.UP, target_content)
                        )
                    except Exception:
                        logger.warning("Unknown target '%s'", target_str)
                elif target_type.lower() == "scroll_down":
                    try:
                        target_content = int(target_content)
                        if target_content < 0:
                            raise Exception("Negative value")
                        self.mapper.insert(
                            input, ScrollDirectionTarget(Direction.DOWN, target_content)
                        )
                    except Exception:
                        logger.warning("Unknown target '%s'", target_str)
                elif target_type.lower() == "scroll_left":
                    try:
                        target_content = int(target_content)
                        if target_content < 0:
                            raise Exception("Negative value")
                        self.mapper.insert(
                            input, ScrollDirectionTarget(Direction.LEFT, target_content)
                        )
                    except Exception:
                        logger.warning("Unknown target '%s'", target_str)
                elif target_type.lower() == "scroll_right":
                    try:
                        target_content = int(target_content)
                        if target_content < 0:
                            raise Exception("Negative value")
                        self.mapper.insert(
                            input,
                            ScrollDirectionTarget(Direction.RIGHT, target_content),
                        )
                    except Exception:
                        logger.warning("Unknown target '%s'", target_str)
                else:
                    logger.warning("Unknown target '%s'", target_str)

    def parse_analog(self, data: dict):
        if "analog" in data:
            for input_str, target_str in data["analog"].items():
                if input_str == "":
                    continue

                input = AnalogInput.from_string(input_str, self.controller_type)
                if input is None:
                    logger.warning("Unknown input '%s'", input_str)
                    continue

                if target_str == "cursor":
                    self.mapper.insert(input, MouseTarget.CURSOR)
                elif target_str == "scroll":
                    self.mapper.insert(input, MouseTarget.SCROLL)
                else:
                    logger.warning("Unknown target '%s'", target_str)

    def parse_options(self, data: dict):
        if "options" in data:
            for key, value in data["options"].items():
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
                elif key == "cursor_speed":
                    try:
                        speed = float(value)
                        if speed < 0:
                            raise ValueError("Negative value")
                        self.options["cursor_speed"] = speed
                    except ValueError:
                        logger.warning("Unknown value '%s'", value)
                elif key == "scroll_speed":
                    try:
                        speed = float(value)
                        if speed < 0:
                            raise ValueError("Negative value")
                        self.options["scroll_speed"] = speed
                    except ValueError:
                        logger.warning("Unknown value '%s'", value)
                elif (
                    key == "left_analog_idle_range"
                    and self.controller_type == ControllerType.PRO_CONTOLLER
                ):
                    try:
                        idle_range = float(value)
                        if idle_range < 0:
                            raise ValueError("Negative value")
                        self.options["left_analog_idle_range"] = idle_range
                    except ValueError:
                        logger.warning("Unknown value '%s'", value)
                elif (
                    key == "right_analog_idle_range"
                    and self.controller_type == ControllerType.PRO_CONTOLLER
                ):
                    try:
                        idle_range = float(value)
                        if idle_range < 0:
                            raise ValueError("Negative value")
                        self.options["right_analog_idle_range"] = idle_range
                    except ValueError:
                        logger.warning("Unknown value '%s'", value)
                elif key == "analog_idle_range" and (
                    self.controller_type == ControllerType.JOY_CON_LEFT
                    or self.controller_type == ControllerType.JOY_CON_RIGHT
                ):
                    try:
                        idle_range = float(value)
                        if idle_range < 0:
                            raise ValueError("Negative value")
                        self.options["analog_idle_range"] = idle_range
                    except ValueError:
                        logger.warning("Unknown value '%s'", value)
                else:
                    logger.warning("Unknown key '%s'", key)
