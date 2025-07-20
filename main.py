import machine
import sys
import asyncio
import os
from info import main as print_info
from micropython import alloc_emergency_exception_buf

sys.path.insert(0, "/libs")
sys.path.insert(0, "/src")

import logging

# do not change order
logging.basicConfig(level=logging.DEBUG)

from backend import backend


alloc_emergency_exception_buf(200)


if logging.getLogger().isEnabledFor(logging.DEBUG):
    print_info()


try:
    asyncio.run(backend.main())
except Exception as e:
    print("Fatal error in main:")
    sys.print_exception(e)
finally:
    # Following a normal Exception or main() exiting, reset the board.
    # Following a non-Exception error such as KeyboardInterrupt (Ctrl-C),
    # this code will drop to a REPL.dist/assets dist/assets/index-BUx743Ix.css dist/assets/index-YTchXzvl.js dist/icons dist/favicon.ico dist/index.html dist/msg_logo.png Place machine.reset() in a finally
    # block to always reset, instead.
    machine.reset()
