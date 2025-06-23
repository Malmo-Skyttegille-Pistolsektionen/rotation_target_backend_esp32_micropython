from typing import Optional
from time import ticks_ms, ticks_diff
from common.program import Program, Event, Series
from common.common import EventType, program_state
from common.programs import programs
import common.target as target
from web.sse import emit_sse_event
import asyncio
import logging


class ProgramExecutor:
    def __init__(self) -> None:
        logging.debug("[ProgramExecutor] Initialized")

    async def start(self) -> bool:
        logging.debug("[ProgramExecutor] Entered start()")
        if program_state.program is None:
            logging.debug("[ProgramExecutor] No program loaded.")
            return False

        if program_state.running_series_start:
            logging.debug("[ProgramExecutor] Series is already running.")
            return False

        asyncio.create_task(self.run_series())
        return True

    async def run_series(self) -> None:
        logging.debug("[ProgramExecutor] Entered run_series()")
        program = program_state.program
        series_index = program_state.current_series_index
        event_index = program_state.current_event_index

        if program is None:
            logging.debug("[ProgramExecutor] No program loaded in run_series.")
            return

        if not (0 <= series_index < len(program.series)):
            logging.debug("[ProgramExecutor] Invalid series index in run_series.")
            return

        series = program.series[series_index]
        # All durations in ms
        event_durations_ms = [e.duration * 1000 for e in series.events]
        total_time_ms = sum(event_durations_ms)
        logging.debug(
            f"[ProgramExecutor] Running series {series_index} with total time {total_time_ms} ms"
        )
        await emit_sse_event(
            EventType.SERIES_STARTED,
            {
                "program_id": program.id,
                "series_index": series_index,
            },
        )

        program_state.running_series_start = ticks_ms()
        chrono_task = asyncio.create_task(
            self._emit_series_chrono(program_state.running_series_start, total_time_ms)
        )

        for idx in range(event_index, len(series.events)):
            event = series.events[idx]
            program_state.current_event_index = idx
            await emit_sse_event(
                EventType.EVENT_STARTED,
                {
                    "program_id": program.id,
                    "series_index": series_index,
                    "event_index": idx,
                },
            )

            if event.command:
                await emit_sse_event(
                    EventType.TARGET_STATUS,
                    {"status": "shown" if event.command == "show" else "hidden"},
                )
                if event.command == "show":
                    target.show()
                elif event.command == "hide":
                    target.hide()

            # Wait for this event's duration (in ms), but check for external stop frequently
            event_start = ticks_ms()
            event_duration_ms = event.duration * 1000
            while True:
                elapsed_ms = ticks_diff(ticks_ms(), event_start)
                if elapsed_ms >= event_duration_ms:
                    break
                # Check for external stop every 200ms
                for _ in range(5):
                    if program_state.running_series_start is None:
                        logging.debug(
                            "[ProgramExecutor] Series stopped externally during event."
                        )
                        chrono_task.cancel()
                        return
                    await asyncio.sleep(0.2)

            if program_state.running_series_start is None:
                logging.debug("[ProgramExecutor] Series stopped externally.")
                chrono_task.cancel()
                return

        chrono_task.cancel()
        await emit_sse_event(
            EventType.SERIES_COMPLETED,
            {
                "program_id": program.id,
                "series_index": series_index,
            },
        )
        logging.debug("[ProgramExecutor] Series finished.")

        if series_index + 1 < len(program.series):
            program_state.current_series_index = series_index + 1
            program_state.current_event_index = 0
            program_state.running_series_start = None
            await emit_sse_event(
                EventType.SERIES_NEXT,
                {
                    "program_id": program.id,
                    "series_index": program_state.current_series_index,
                },
            )
        else:
            await emit_sse_event(
                EventType.PROGRAM_COMPLETED,
                {
                    "program_id": program.id,
                },
            )
            program_state.running_series_start = None
            program_state.current_series_index = 0
            program_state.current_event_index = 0

    async def _emit_series_chrono(self, start_time_ms, total_time_ms):
        while True:
            if program_state.running_series_start is None:
                logging.debug(
                    "[ProgramExecutor] _emit_series_chrono detected external stop."
                )
                break
            elapsed_ms = ticks_diff(ticks_ms(), start_time_ms)
            remaining_ms = max(0, total_time_ms - elapsed_ms)
            await emit_sse_event(
                EventType.CHRONO,
                {
                    "elapsed": elapsed_ms,
                    "remaining": remaining_ms,
                    "total": total_time_ms,
                },
            )
            if elapsed_ms >= total_time_ms:
                break
            await asyncio.sleep(1)

    async def stop(self) -> bool:
        logging.debug("[ProgramExecutor] Entered stop()")
        if program_state.program is None:
            logging.debug("[ProgramExecutor] No program loaded.")
            return False

        if program_state.running_series_start is None:
            logging.debug("[ProgramExecutor] No program running.")
            return False

        program_state.running_series_start = None
        program_state.current_event_index = 0
        logging.debug("[ProgramExecutor] Program stopped and reset to the first event")

        await emit_sse_event(
            EventType.SERIES_STOPPED,
            {
                "program_id": program_state.program.id,
                "series_index": program_state.current_series_index,
            },
        )

        return True

    async def skip_to_series(self, series_index: int) -> bool:
        logging.debug(
            f"[ProgramExecutor] Entered skip_to_series(series_index={series_index})"
        )

        if program_state.program is None:
            logging.debug("[ProgramExecutor] No program loaded.")
            return False

        if 0 <= series_index < len(program_state.program.series):
            program_state.running_series_start = None
            program_state.current_series_index = series_index
            program_state.current_event_index = 0
            logging.debug(f"[ProgramExecutor] Skipped to series {series_index}")
            return True

        logging.debug(f"[ProgramExecutor] Invalid series index: {series_index}")
        return False

    async def load(self, program_id: int) -> bool:
        logging.debug(f"[ProgramExecutor] Entered load(program_id={program_id})")
        program = programs.get(program_id)
        if not program:
            logging.debug(
                f"[ProgramExecutor] Program {program_id} not found for loading."
            )
            return False

        program_state.program = program
        program_state.current_series_index = 0
        program_state.current_event_index = 0
        logging.debug(f"[ProgramExecutor] Loaded program {program_id}")
        return True


program_executor = ProgramExecutor()
