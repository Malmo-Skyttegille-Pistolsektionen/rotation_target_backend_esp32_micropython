import machine
import sys
import asyncio
import os


sys.path.insert(0, "/libs")
sys.path.insert(0, "/src")

import logging

logging.basicConfig(level=logging.DEBUG)

# logging.debug("main.py sys.path: %s", sys.path)
# logging.debug(f"os.uname: { os.uname()}")

logging.debug("Starting backend...")

from info import main as print_info

print_info()

from src import backend


async def run_backend():
    try:
        await backend.main()
    except Exception as e:
        print("Fatal error in main:")
        sys.print_exception(e)
    finally:
        # Following a normal Exception or main() exiting, reset the board.
        # Following a non-Exception error such as KeyboardInterrupt (Ctrl-C),
        # this code will drop to a REPL. Place machine.reset() in a finally
        # block to always reset, instead.
        machine.reset()
