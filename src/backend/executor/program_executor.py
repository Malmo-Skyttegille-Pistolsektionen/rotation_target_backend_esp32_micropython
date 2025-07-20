from typing import Optional
import asyncio
import logging
from time import ticks_ms, ticks_diff
from backend.common.event_type import EventType
from backend.dataclasses.program import Program, Series, Event
from backend.io.audio import play_wav_asyncio
import backend.io.targets as targets
from backend.repositories.audios import audios
from backend.repositories.programs import programs
from backend.repositories.program_state import program_state
from backend.apis.sse import emit_sse_event


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
        logging.info("[ProgramExecutor] Entered run_series()")
        program: Optional[Program] = program_state.program
        series_index: int = program_state.current_series_index
        event_index: int = program_state.current_event_index

        if program is None:
            logging.debug("[ProgramExecutor] No program loaded in run_series.")
            return

        if not (0 <= series_index < len(program.series)):
            logging.debug("[ProgramExecutor] Invalid series index in run_series.")
            return

        series: Series = program.series[series_index]
        event_durations_ms: list[int] = [e.duration for e in series.events]
        total_time_ms: int = sum(event_durations_ms)
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

        series_start = ticks_ms()
        program_state.running_series_start = series_start
        chrono_task: asyncio.Task = asyncio.create_task(
            self._emit_series_chrono(series_start, total_time_ms)
        )

        # Calculate absolute start time for each event
        event_absolute_times = []
        t = series_start
        for dur in event_durations_ms:
            event_absolute_times.append(t)
            t += dur

        for idx in range(event_index, len(series.events)):
            event: Event = series.events[idx]
            program_state.current_event_index = idx
            await emit_sse_event(
                EventType.EVENT_STARTED,
                {
                    "program_id": program.id,
                    "series_index": series_index,
                    "event_index": idx,
                },
            )

            # Start audio playback as a background task (sequential playback per event)
            audio_task = None
            if hasattr(event, "audio_ids") and event.audio_ids:

                async def play_all_audios(audio_ids):
                    for audio_id in audio_ids:
                        audio = audios.get(audio_id)
                        if audio:
                            await play_wav_asyncio(audio.filename)
                        else:
                            logging.debug(
                                f"[ProgramExecutor] Audio ID {audio_id} not found for event {idx}"
                            )

                audio_task = asyncio.create_task(play_all_audios(event.audio_ids))

            if event.command:
                await emit_sse_event(
                    EventType.TARGET_STATUS,
                    {"status": "shown" if event.command == "show" else "hidden"},
                )
                if event.command == "show":
                    targets.show()
                elif event.command == "hide":
                    targets.hide()

            # Wait until the absolute end time for this event
            event_end_time = event_absolute_times[idx] + event_durations_ms[idx]
            while True:
                now = ticks_ms()
                remaining = ticks_diff(event_end_time, now)
                if remaining <= 0:
                    break
                # Sleep for the smaller of 200ms or the remaining time
                await asyncio.sleep(min(0.2, remaining / 1000))

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
        logging.info("[ProgramExecutor] Series finished.")

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

    async def _emit_series_chrono(self, start_time_ms: int, total_time_ms: int) -> None:
        while True:
            if program_state.running_series_start is None:
                logging.debug(
                    "[ProgramExecutor] _emit_series_chrono detected external stop."
                )
                break
            elapsed_ms: int = ticks_diff(ticks_ms(), start_time_ms)
            remaining_ms: int = max(0, total_time_ms - elapsed_ms)
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

        if series_index < 0 or series_index >= len(program_state.program.series):
            logging.debug(f"[ProgramExecutor] Invalid series index: {series_index}")
            return False

        program_state.running_series_start = None
        program_state.current_series_index = series_index
        program_state.current_event_index = 0
        logging.debug(f"[ProgramExecutor] Skipped to series {series_index}")

        await emit_sse_event(
            EventType.SERIES_NEXT,
            {
                "program_id": program_state.program.id,
                "series_index": program_state.current_series_index,
            },
        )

        return True

    async def load(self, program_id: int) -> bool:
        logging.debug(f"[ProgramExecutor] Entered load(program_id={program_id})")
        program: Optional[Program] = programs.get(program_id)
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


program_executor: ProgramExecutor = ProgramExecutor()
