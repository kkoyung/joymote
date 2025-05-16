import logging

import evdev
from evdev import ecodes as e
from mushroom import MouseThread, ScrollThread

logger = logging.getLogger(__name__)


def scan_devices():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    # FIXME: What is "Pro Controller (IMU)"?
    devices = list(filter(lambda device: device.name == "Pro Controller", devices))
    for device in devices:
        logger.info("Detected device: %s, %s", device.path, device.name)

    return devices


def start_key_loop(device, keyboard_ui, mouse_ui, conf):
    mouse_thread = MouseThread(mouse_ui)
    scroll_thread = ScrollThread(mouse_ui)

    for event in device.read_loop():
        if event.type == e.EV_KEY:
            # Key stroke
            if event.code in conf.keys_mapping:
                keyboard_ui.write(e.EV_KEY, conf.keys_mapping[event.code], event.value)
                keyboard_ui.syn()
        elif event.type == e.EV_ABS:
            # Left analog
            if event.code == e.ABS_X:
                mouse_thread.push(event.value, mouse_thread.y)
            elif event.code == e.ABS_Y:
                mouse_thread.push(mouse_thread.x, event.value)
            # Right analog
            elif event.code == e.ABS_RX:
                scroll_thread.push(event.value, scroll_thread.y)
            elif event.code == e.ABS_RY:
                scroll_thread.push(scroll_thread.x, event.value)
