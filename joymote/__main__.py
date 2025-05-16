#!/usr/bin/python

import logging

import config
import device
from evdev import UInput
from evdev import ecodes as e

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logger.info("Start joymote")

conf = config.load_config()

devices = device.scan_devices()
keyboard_ui = UInput()
mouse_ui = UInput(
    {
        e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT],
        e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL_HI_RES, e.REL_HWHEEL_HI_RES],
    }
)
device.start_key_loop(devices[0], keyboard_ui, mouse_ui, conf)
