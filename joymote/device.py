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


def start_key_loop(device, ui):
    for event in device.read_loop():
        if event.type == e.EV_KEY:
            if event.code == e.BTN_SOUTH:  # B Button
                ui.write(e.EV_KEY, e.KEY_SPACE, event.value)

            elif event.code == e.BTN_EAST:  # A Button
                ui.write(e.EV_KEY, e.BTN_LEFT, event.value)

            elif event.code == e.BTN_NORTH:  # X Button
                ui.write(e.EV_KEY, e.BTN_RIGHT, event.value)

            elif event.code == e.BTN_WEST:  # Y Button
                ui.write(e.EV_KEY, e.KEY_ENTER, event.value)

            elif event.code == e.BTN_TL:  # L Button
                ui.write(e.EV_KEY, e.KEY_VOLUMEDOWN, event.value)

            elif event.code == e.BTN_TR:  # R Button
                ui.write(e.EV_KEY, e.KEY_VOLUMEUP, event.value)

            elif event.code == e.BTN_TL2:  # ZL Button
                ui.write(e.EV_KEY, e.KEY_LEFT, event.value)

            elif event.code == e.BTN_TR2:  # ZR Button
                ui.write(e.EV_KEY, e.KEY_RIGHT, event.value)

            elif event.code == e.BTN_SELECT:  # - Button
                ui.write(e.EV_KEY, e.KEY_MUTE, event.value)

            elif event.code == e.BTN_START:  # + Button
                ui.write(e.EV_KEY, e.KEY_F, event.value)

            elif event.code == e.BTN_Z:  # Capture Button
                ui.write(e.EV_KEY, e.KEY_SYSRQ, event.value)

            elif event.code == e.BTN_MODE:  # HOME Button
                ui.write(e.EV_KEY, e.KEY_ESC, event.value)

            # FIXME: SYNC button

        ui.syn()
