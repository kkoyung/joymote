#!/usr/bin/python

import argparse
import logging

import config
import engine
import version

# Parse arguments
parser = argparse.ArgumentParser(
    description="Use Joy-Con or Pro Controller as remote control of Linux machine.",
    add_help=False,
)
parser.add_argument(
    "-h", "--help", help="Show this help message and exit.", action="help"
)
parser.add_argument(
    "-v",
    "--version",
    help="Print version information.",
    action="version",
    version=version.get_version(),
)
args = parser.parse_args()

# Set up logger
logger = logging.getLogger(__name__)

# Load configuration
conf = config.load_config()

# Start main body
devices = engine.scan_devices()
if len(devices) == 0:
    logger.warning("Not detected device")
    exit()
for device in devices:
    engine.start_capture(device, conf)
