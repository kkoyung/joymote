import evdev
from evdev import ecodes as e
import logging

logger = logging.getLogger(__name__)


def scan_devices():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    # FIXME: What is "Pro Controller (IMU)"?
    devices = list(filter(lambda device: device.name == "Pro Controller", devices))
    for device in devices:
        logger.info("Detected device: %s, %s", device.path, device.name)

    return devices


def start_key_loop(device, ui, conf):
    for event in device.read_loop():
        if event.type == e.EV_KEY:
            if event.code in conf.keys_mapping:
                ui.write(e.EV_KEY, conf.keys_mapping[event.code], event.value)
                ui.syn()
