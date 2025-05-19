import logging
import os
from collections import namedtuple

import tomllib
from evdev import ecodes as e

logger = logging.getLogger(__name__)

Conf = namedtuple("Conf", ["keys_mapping", "analog_mapping", "analog_options"])


def load_config():
    # FIXME: default value, loading order
    home_directory = os.getenv("HOME", "")
    config_path = home_directory + "/.config/joymote/config.toml"

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    parse_general(data)
    keys_mapping = parse_keys(data)
    analog_mapping, analog_options = parse_analog(data)

    return Conf(keys_mapping, analog_mapping, analog_options)


def parse_general(data):
    if "general" not in data:
        return
    general = data["general"]

    # Log level
    log_level = general.get("log", "INFO").upper()
    log_level = os.environ.get("JOYMOTE_LOG", log_level).upper()
    logging.basicConfig(level=log_level)


def parse_keys(data):
    # from: ecodes of input
    # to: ecodes of target
    mapping = {}

    # from: common name of input
    # to: ecodes of input
    input_common_to_ecodes = {
        "a": e.BTN_EAST,
        "b": e.BTN_SOUTH,
        "x": e.BTN_NORTH,
        "y": e.BTN_WEST,
        "l": e.BTN_TL,
        "r": e.BTN_TR,
        "zl": e.BTN_TL2,
        "zr": e.BTN_TR2,
        "plus": e.BTN_START,
        "minus": e.BTN_SELECT,
        "capture": e.BTN_Z,
        "home": e.BTN_MODE,
    }
    # FIXME: SYNC button

    if "keys" in data:
        for input_common, target_name in data["keys"].items():
            if input_common not in input_common_to_ecodes.keys():
                logger.warning("Unknown input key '%s'", input_common)
                continue

            if target_name not in e.ecodes.keys():
                logger.warning("Unknown target name '%s'", target_name)
                continue

            mapping[input_common_to_ecodes[input_common]] = e.ecodes[target_name]
            logger.debug(
                "Mapped '%s' to '%s'",
                input_common,
                target_name,
            )

    return mapping


def parse_analog(data):
    available_input = ["left", "right"]
    available_target = ["mouse", "scroll"]
    mapping = {}
    options = {
        "revert_scroll_x": False,
        "revert_scroll_y": False,
    }

    if "analog" not in data:
        return mapping, options

    for key, value in data["analog"].items():
        if key in available_input and value in available_target:
            mapping[key] = value
            continue

        if key == "revert_scroll_x" and type(value) is bool:
            options["revert_scroll_x"] = value
            continue

        if key == "revert_scroll_y" and type(value) is bool:
            options["revert_scroll_y"] = value
            continue

        logger.warning("Unknown key-value pair '%s: %s'", key, value)

    return mapping, options
