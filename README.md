# Walkingpad Control

A multi-platform Python script to control the Kingsmith Walkingpad A1 Pro through Bluetooth

## Installation

### Prerequisites

1. Create a virtual environment named `venv_walkingpad-control`:

    ```shell
    $ python3 -m venv venv_walkingpad-control
    $ . ./venv_walkingpad-control/bin/activate
    ```

2. Install required packages (namely [Bleak](https://github.com/hbldh/bleak)):

    ```shell
    pip install -r requirements.txt
    ```

3. **MacOS Big Sur and later**: Ensure that the program invoking the script has permissions to access Bluetooth in `System Preferences/Privacy/Bluetooth`.

### Finding device ID

1. Install [Bluetility](https://github.com/jnross/Bluetility):

    ```shell
    brew install bluetility
    ```

1. Run it and let it scan for Bluetooth devices. A device named `WalkingPad` should appear.

1. Right-click the WalkingPad device and click `Copy device tooltip`. That will copy something like the following to the clipboard:

    ```text
    identifier:		9F905A19-4F80-49A6-B1D5-3F79B6A5C76F
    MAC:		57-4C-4E-2D-1A-3A
    Local Name:	WalkingPad
    ```

1. The device ID is the value of `identifier` for MacOS, or `MAC` otherwise (replacing the dashes with colons, `57:4C:4E:2D:1A:3A`).

## Running the script

```shell
# Turn the device to manual mode
$ ./walkingpad-control.py -a 9F905A19-4F80-49A6-B1D5-3F79B6A5C76F mode manual
```
