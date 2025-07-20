from typing import Optional

from backend.dataclasses.program import Program


class ProgramState:
    def __init__(self):
        self.running_series_start: Optional[int] = (
            None  # Timestamp when the series started, or None if not running
        )
        self.program: Optional[Program] = None
        self.current_series_index: Optional[int] = None
        self.current_event_index: Optional[int] = None
        self.target_status_shown: bool = False


# Create a single, shared instance
program_state = ProgramState()
