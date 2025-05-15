#!/usr/bin/python

import logging
from evdev import UInput

import config
import device

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.info("Start joymote")

config.load_config()

devices = device.scan_devices()
ui = UInput()
device.start_key_loop(devices[0], ui)
