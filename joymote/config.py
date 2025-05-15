import logging
import os
import tomllib

logger = logging.getLogger(__name__)


def load_config():
    # FIXME: default value, loading order
    home_directory = os.getenv("HOME", "")
    config_path = home_directory + "/.config/joymote/config.toml"

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    logger.info("Loaded config: %s", config_path)
    logger.debug("Config: %s", data)
