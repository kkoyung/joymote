#!/usr/bin/python

import logging
from evdev import UInput

import config
import device

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logger.info("Start joymote")

conf = config.load_config()

devices = device.scan_devices()
ui = UInput()
device.start_key_loop(devices[0], ui, conf)
