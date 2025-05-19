#!/usr/bin/python

import logging

import config
import engine

# Set up logger
logger = logging.getLogger(__name__)

# Load configuration
conf = config.load_config()

# Start main body
devices = engine.scan_devices()
for device in devices:
    engine.start_capture(device, conf)
