import time
from common.common import EventType
import target  

class ProgramExecutor:
    def __init__(self, program, sse_send):
        self.program = program
        self.sse_send = sse_send  # function(event_type, data_dict)
        self.running = False
        self.current_series_index = 0
        self.current_event_index = 0

    def start(self):
        if self.running:
            print("[ProgramExecutor] Already running.")
            return
        print(f"[ProgramExecutor] Starting program id={self.program.id}")
        self.running = True
        self.current_series_index = 0
        self.current_event_index = 0
        self.sse_send(EventType.PROGRAM_STARTED, {'program_id': self.program.id})
        self._run_from(self.current_series_index, self.current_event_index)

    def stop(self):
        if not self.running:
            print("[ProgramExecutor] Not running, nothing to stop.")
            return
        print(f"[ProgramExecutor] Stopping program id={self.program.id}")
        self.running = False
        self.sse_send(EventType.PROGRAM_COMPLETED, {'program_id': self.program.id})

    def skip_to(self, series_index):
        if not (0 <= series_index < len(self.program.series)):
            print(f"[ProgramExecutor] Invalid series_index: {series_index}")
            return False
        print(f"[ProgramExecutor] Skipping to series_index={series_index}")
        self.current_series_index = series_index
        self.current_event_index = 0
        if self.running:
            self._run_from(self.current_series_index, self.current_event_index)
        return True

    def _run_from(self, series_index, event_index):
        print(f"[ProgramExecutor] Running from series {series_index}, event {event_index}")
        for s_idx in range(series_index, len(self.program.series)):
            series = self.program.series[s_idx]
            print(f"[ProgramExecutor] Starting series {s_idx}: {series.name}")
            self.sse_send(EventType.SERIES_STARTED, {
                'program_id': self.program.id,
                'series_index': s_idx
            })
            for e_idx in range(event_index, len(series.events)):
                if not self.running:
                    print(f"[ProgramExecutor] Stopped at series {s_idx}, event {e_idx}")
                    self.sse_send(EventType.SERIES_STOPPED, {
                        'program_id': self.program.id,
                        'series_index': s_idx,
                        'event_index': e_idx
                    })
                    return
                event = series.events[e_idx]
                print(f"[ProgramExecutor] Starting event {e_idx}: {event.__dict__}")
                self.sse_send(EventType.EVENT_STARTED, {
                    'program_id': self.program.id,
                    'series_index': s_idx,
                    'event_index': e_idx
                })
                # Use target.show/hide for event commands
                if hasattr(event, 'command'):
                    if event.command == 'show':
                        print("[ProgramExecutor] Executing target.show()")
                        target.show()
                        self.sse_send(EventType.TARGET_STATUS, {'status': 'shown'})
                    elif event.command == 'hide':
                        print("[ProgramExecutor] Executing target.hide()")
                        target.hide()
                        self.sse_send(EventType.TARGET_STATUS, {'status': 'hidden'})
                start = time.ticks_ms()
                elapsed = 0
                while elapsed < event.duration * 1000:
                    elapsed = time.ticks_diff(time.ticks_ms(), start)
                    print(f"[ProgramExecutor] Event chrono: elapsed={elapsed // 1000}, remaining={event.duration - (elapsed // 1000)}")
                    self.sse_send(EventType.CHRONO, {
                        'elapsed': elapsed // 1000,
                        'remaining': event.duration - (elapsed // 1000),
                        'total': event.duration
                    })
                    time.sleep(1)
            print(f"[ProgramExecutor] Series {s_idx} completed.")
            self.sse_send(EventType.SERIES_COMPLETED, {
                'program_id': self.program.id,
                'series_index': s_idx
            })
            # Optionally: series_next
            if s_idx + 1 < len(self.program.series):
                print(f"[ProgramExecutor] Next series: {s_idx + 1}")
                self.sse_send(EventType.SERIES_NEXT, {
                    'program_id': self.program.id,
                    'series_index': s_idx + 1
                })
            event_index = 0  # Reset for next series
        print(f"[ProgramExecutor] Program {self.program.id} completed.")
        self.sse_send(EventType.PROGRAM_COMPLETED, {'program_id': self.program.id})
        self.running = False