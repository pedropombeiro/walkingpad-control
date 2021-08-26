#!/usr/bin/env python3

"""
Control the Kingsmith Walkingpad A1 Pro
"""

import argparse, sys
import asyncio
import logging

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

COMMAND_CHARACTERISTIC = "0000FE02-0000-1000-8000-00805F9B34FB"

parser = argparse.ArgumentParser(description='A utility to control the Kingsmith Walkingpad A1 Pro')
parser.add_argument("-a", "--address", help="Bluetooth address of the Walkingpad (e.g. 9F905A19-4F80-49A6-B1D5-3F79B6A5C76F for macOS or 57:4C:4E:2D:1A:3A otherwise)", type=str, required=True)
parser.add_argument("-d", "--debug", help="Enable debug output", required=False, action="store_true")

subparsers = parser.add_subparsers(help='Commands')
parser_mode = subparsers.add_parser('mode', help='Set the device mode')
parser_mode.add_argument('mode', help='Set the Walkingpad mode', choices=['sleep', 'manual', 'auto'])

parser_set = subparsers.add_parser('set', help='Set device values')
parser_set.add_argument("--speed", help="Set the Walkingpad speed (e.g. 20 for 2 km/h)", default=argparse.SUPPRESS, type=int)
parser_set.add_argument("--initial-speed", help="Set the Walkingpad initial speed (e.g. 20 for 2 km/h)", default=argparse.SUPPRESS, type=int)

parser_start = subparsers.add_parser('toggle-start', help='Start/stop the Walkingpad')
parser_start.add_argument("--start-speed", help="Start the Walkingpad at specified speed (e.g. 20 for 2 km/h)", default=0, type=int)

p = parser.parse_args()

log = logging.getLogger(__name__)
if p.debug:
    import sys

    log.setLevel(logging.DEBUG)
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(logging.DEBUG)
    log.addHandler(h)

async def run(ble_address: str):
    client = BleakClient(ble_address)

    async def set_speed(s):
        await client.write_gatt_char(COMMAND_CHARACTERISTIC, bytearray([0xf7, 0xa2, 0x01, s, s + 0xa3, 0xfd]))

    async def set_init_speed(s):
        await client.write_gatt_char(COMMAND_CHARACTERISTIC, bytearray([0xf7, 0xa6, 0x04, 0x00, 0x00, 0x00, s, s + 0xaa, 0xfd]))

    log.info("Connecting to %s..." % ble_address)
    await client.connect()

    log.debug(f"Connected: {client.is_connected}")

    if hasattr(p, 'initial_speed'):
        log.info("Setting initial speed to %f km/h..." % (p.initial_speed / 10.0))
        await set_init_speed(p.initial_speed)
        await asyncio.sleep(0.1)

    if hasattr(p, 'speed') or (hasattr(p, 'start_speed') and p.start_speed > 0):
        if (hasattr(p, 'start_speed') and p.start_speed > 0):
            speed = p.start_speed
        else:
            speed = p.speed
        log.info("Setting speed to %f km/h..." % (speed / 10.0))
        await set_speed(speed)
        await asyncio.sleep(0.1)

    if hasattr(p, 'mode'):
        if p.mode == 'sleep':
            log.info("Setting walkingpad to sleep...")
            await client.write_gatt_char(COMMAND_CHARACTERISTIC, bytes.fromhex("f7a20202a6fd"))
        elif p.mode == 'manual':
            log.info("Setting walkingpad mode to manual mode...")
            await client.write_gatt_char(COMMAND_CHARACTERISTIC, bytes.fromhex("f7a20201a5fd"))
        elif p.mode == 'auto':
            log.info("Setting walkingpad mode to automatic mode...")
            await client.write_gatt_char(COMMAND_CHARACTERISTIC, bytes.fromhex("f7a20200a4fd"))

    if hasattr(p, 'start_speed'):
        log.info("Starting walkingpad in 3 seconds...")
        await client.write_gatt_char(COMMAND_CHARACTERISTIC, bytes.fromhex("f7a20401a7fd"))

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

if __name__ == "__main__":
    sys.stdout = Unbuffered(sys.stdout)

    loop = asyncio.get_event_loop()
    loop.set_debug(p.debug)
    loop.run_until_complete(run(p.address))
