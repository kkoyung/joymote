#!/usr/bin/python

import argparse
import logging

import config
import engine

# Parse arguments
parser = argparse.ArgumentParser(
    description="Use Joy-Con or Pro Controller as remote control of Linux machine."
)
args = parser.parse_args()

# Set up logger
logger = logging.getLogger(__name__)

# Load configuration
conf = config.load_config()

# Start main body
devices = engine.scan_devices()
for device in devices:
    engine.start_capture(device, conf)
