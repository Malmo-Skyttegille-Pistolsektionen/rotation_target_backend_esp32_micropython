import machine
import sys
import os

sys.path.insert(0, "/libs")
sys.path.insert(0, "/src")

print("main.py sys.path:", sys.path)


from src import backend


try:
    res = backend.main()
except Exception as e:
    print("Fatal error in main:")
    sys.print_exception(e)

# Following a normal Exception or main() exiting, reset the board.
# Following a non-Exception error such as KeyboardInterrupt (Ctrl-C),
# this code will drop to a REPL. Place machine.reset() in a finally
# block to always reset, instead.
machine.reset()
