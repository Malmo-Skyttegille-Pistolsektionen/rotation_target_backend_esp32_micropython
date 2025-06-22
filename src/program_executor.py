from typing import Optional
from time import ticks_ms, ticks_diff, ticks_add
from common import program
from common.common import EventType, program_state
from common.programs import programs
import target
from web.sse import emit_sse_event


class ProgramExecutor:
    def __init__(self) -> None:
        print("[ProgramExecutor] Initialized")

    async def start(self) -> bool:
        print("[ProgramExecutor] Entered start()")
        if not program_state.program:
            print("[ProgramExecutor] No program loaded.")
            return False

        program_state.running_series_start = ticks_ms()
        program_state.current_series_index = 0
        program_state.current_event_index = 0

        print(f"[ProgramExecutor] Started program {program_state.program.id}")

        # Emit event: program started
        await emit_sse_event(
            EventType.PROGRAM_STARTED, {"program_id": program_state.program.id}
        )

        # Emit event: series started
        await emit_sse_event(
            EventType.SERIES_STARTED,
            {
                "program_id": program_state.program.id,
                "series_index": program_state.current_series_index,
            },
        )

        # Emit event: event started
        await emit_sse_event(
            EventType.EVENT_STARTED,
            {
                "program_id": program_state.program.id,
                "series_index": program_state.current_series_index,
                "event_index": program_state.current_event_index,
            },
        )

        return True

    async def stop(self) -> bool:
        print("[ProgramExecutor] Entered stop()")

        if not program_state.program:
            print("[ProgramExecutor] No program loaded.")
            return False

        if getattr(program_state, "running_series_start", None) is None:
            print("[ProgramExecutor] No program running.")
            return False

        program_state.running_series_start = None
        program_state.current_event_index = 0
        print("[ProgramExecutor] Program stopped and reset to the first event")

        # Emit event: series stopped
        await emit_sse_event(
            EventType.SERIES_STOPPED,
            {
                "program_id": program_state.program.id,
                "series_index": program_state.current_series_index,
            },
        )

        return True

    async def skip_to_series(self, series_index: int) -> bool:
        print(f"[ProgramExecutor] Entered skip_to_series(series_index={series_index})")

        if not program_state.program:
            print("[ProgramExecutor] No program loaded.")
            return False

        if 0 <= series_index < len(program_state.program.series):
            program_state.running_series_start = None
            program_state.current_series_index = series_index
            program_state.current_event_index = 0
            print(f"[ProgramExecutor] Skipped to series {series_index}")
            return True

        print(f"[ProgramExecutor] Invalid series index: {series_index}")
        return False

    async def load(self, program_id: int) -> bool:
        print(f"[ProgramExecutor] Entered load(program_id={program_id})")
        if not programs.get(program_id):
            print(f"[ProgramExecutor] Program {program_id} not found for loading.")
            return False

        program_state.program = programs.get(program_id)
        program_state.current_series_index = 0
        program_state.current_event_index = 0
        print(f"[ProgramExecutor] Loaded program {program_id}")
        return True


program_executor = ProgramExecutor()
