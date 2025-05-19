import logging

import evdev
from evdev import UInput
from evdev import ecodes as e

from config import Conf
from handler import KeyHandler, MouseHandler, ScrollHandler
from handler.analog import AnalogHandler

logger = logging.getLogger(__name__)


def scan_devices():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    # FIXME: What is "Pro Controller (IMU)"?
    devices = list(filter(lambda device: device.name == "Pro Controller", devices))
    for device in devices:
        logger.info("Detected device: %s, %s", device.path, device.name)

    return devices


def start_capture(device, conf: Conf):
    keyboard_ui = UInput()
    mouse_ui = UInput(
        {
            e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT],
            e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL_HI_RES, e.REL_HWHEEL_HI_RES],
        }
    )

    key_handler = KeyHandler(keyboard_ui, conf.keys_mapping)
    left_handler = None
    if "left" in conf.analog_mapping:
        if conf.analog_mapping["left"] == "mouse":
            left_handler = MouseHandler(mouse_ui)
        elif conf.analog_mapping["left"] == "scroll":
            left_handler = ScrollHandler(mouse_ui)
    right_handler = None
    if "right" in conf.analog_mapping:
        if conf.analog_mapping["right"] == "mouse":
            right_handler = MouseHandler(mouse_ui)
        elif conf.analog_mapping["right"] == "scroll":
            right_handler = ScrollHandler(mouse_ui)

    logger.info("Start capturing device: %s, %s", device.path, device.name)

    for event in device.read_loop():
        if event.type == e.EV_KEY:
            key_handler.push(event)
        elif event.type == e.EV_ABS:
            # Left analog
            if event.code == e.ABS_X:
                if left_handler is not None:
                    left_handler.push(event)
            elif event.code == e.ABS_Y:
                if left_handler is not None:
                    left_handler.push(event)
            # Right analog
            elif event.code == e.ABS_RX:
                if right_handler is not None:
                    right_handler.push(event)
            elif event.code == e.ABS_RY:
                if right_handler is not None:
                    right_handler.push(event)
