import logging

import evdev

from .config import Config
from .reactor import Reactor
from .util import BluetoothName

logger = logging.getLogger(__name__)


def scan_devices():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    devices = list(
        filter(
            lambda device: device.name == BluetoothName.JOY_CON_LEFT
            or device.name == BluetoothName.JOY_CON_RIGHT
            or device.name == BluetoothName.PRO_CONTOLLER,
            devices,
        )
    )
    for device in devices:
        logger.info("Detected device: %s, %s", device.path, device.name)

    return devices


def start_capture(device, conf: Config):
    if device.name == BluetoothName.JOY_CON_LEFT:
        reactor = Reactor(conf.joy_con_left)
    elif device.name == BluetoothName.JOY_CON_RIGHT:
        reactor = Reactor(conf.joy_con_right)
    elif device.name == BluetoothName.PRO_CONTOLLER:
        reactor = Reactor(conf.pro_contoller)
    else:
        raise Exception("Try to capture wrong device")

    logger.info("Start capturing device: %s, %s", device.path, device.name)
    try:
        for event in device.read_loop():
            reactor.push(event)
    except KeyboardInterrupt:
        logger.info("Stop capturing device: %s, %s", device.path, device.name)
        device.close()
