import logging

import evdev
from evdev import UInput, ecodes as e
from mushroom import BaseThread, MouseThread, ScrollThread
from config import Conf

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
    left_analog_handler: BaseThread | None = None
    right_analog_handler: BaseThread | None = None
    if "left" in conf.analog_mapping:
        if conf.analog_mapping["left"] == "mouse":
            left_analog_handler = MouseThread(mouse_ui)
        elif conf.analog_mapping["left"] == "scroll":
            left_analog_handler = ScrollThread(mouse_ui)
    if "right" in conf.analog_mapping:
        if conf.analog_mapping["right"] == "mouse":
            right_analog_handler = MouseThread(mouse_ui)
        elif conf.analog_mapping["right"] == "scroll":
            right_analog_handler = ScrollThread(mouse_ui)

    logger.info("Start capturing device: %s, %s", device.path, device.name)

    for event in device.read_loop():
        if event.type == e.EV_KEY:
            # Key stroke
            if event.code in conf.keys_mapping:
                keyboard_ui.write(e.EV_KEY, conf.keys_mapping[event.code], event.value)
                keyboard_ui.syn()
        elif event.type == e.EV_ABS:
            # Left analog
            if event.code == e.ABS_X:
                if left_analog_handler is not None:
                    left_analog_handler.push(event.value, left_analog_handler.y)
            elif event.code == e.ABS_Y:
                if left_analog_handler is not None:
                    left_analog_handler.push(left_analog_handler.x, event.value)
            # Right analog
            elif event.code == e.ABS_RX:
                if right_analog_handler is not None:
                    right_analog_handler.push(event.value, right_analog_handler.y)
            elif event.code == e.ABS_RY:
                if right_analog_handler is not None:
                    right_analog_handler.push(right_analog_handler.x, event.value)
