import time
from common import program
from common.common import EventType, program_state
from common.programs import programs
import target


class ProgramExecutor:
    def __init__(self):
        pass  # No internal state needed

    def start(self):
        program_id = getattr(program_state, "program_id", None)
        if program_id is None:
            print("[ProgramExecutor] No program loaded.")
            return False

        program = programs.get(program_id)
        if not program:
            print(f"[ProgramExecutor] Program {program_id} not found.")
            return False

        program_state.running_series_start = ticks_ms()
        program_state.current_series_index = 0
        program_state.current_event_index = 0
        print(f"[ProgramExecutor] Started program {program_id}")
        # ... (emit events, start timers, etc.)
        return True

    def stop(self):
        if getattr(program_state, "running_series_start", None) is None:
            print("[ProgramExecutor] No program running.")
            return False

        program_state.running_series_start = None
        program_state.current_event_index = 0
        print("[ProgramExecutor] Program stopped and reset to the first event")
        # ... (emit events, cleanup, etc.)
        return True

    def skip_to_series(self, series_index):
        program_id = getattr(program_state, "program_id", None)
        program = programs.get(program_id)
        if not program:
            print(f"[ProgramExecutor] Program {program_id} not found.")
            return False

        if 0 <= series_index < len(program.series):
            program_state.current_series_index = series_index
            program_state.current_event_index = 0
            print(f"[ProgramExecutor] Skipped to series {series_index}")
            return True
        print(f"[ProgramExecutor] Invalid series index: {series_index}")
        return False

    def load(self, program_id: int) -> bool:
        program = programs.get(program_id)
        if program is None:
            return False
        program_state.program_id = program_id
        program_state.current_series_index = 0
        program_state.current_event_index = 0

        return True


program_executor = ProgramExecutor()
