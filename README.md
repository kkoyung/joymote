# Joymote

Use Joy-Con or Pro Controller as remote control of Linux machine.

## Development environment

1. Install [joycond](https://github.com/DanielOgorchock/joycond). Start and enable it by:

    ```bash
    sudo systemctl start joycond
    sudo systemctl enable joycond
    ```

    Follow the instruction [here](https://github.com/DanielOgorchock/joycond?tab=readme-ov-file#usage) to pair the controller(s).

2. Check whether the `uinput` module is loaded, by running:

    ```bash
    lsmod | grep uinput
    ```

    If it is loaded, you will see a line like:

    ```plaintext
    uinput                 20480  0
    ```

    You can manually load the module by running:

    ```bash
    sudo modprobe uinput
    ```

    Or permanently load the module by running:

    ```bash
    sudo bash -c "cat uinput > /etc/modules-load.d/uinput.conf"
    ```

3. Set up the environment.

    ```bash
    git clone
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

4. Run the code.

    ```bash
    python joymote
    ```
    ```

## Disclaimer

Nintendo®, Nintendo Switch®, Joy-Con®, and Pro Controller® are registered trademarks of Nintendo of America Inc. This project is an independent work and is not affiliated with, endorsed by, or sponsored by Nintendo. All trademarks are the property of their respective owners.
