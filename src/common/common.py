# Program state
from typing import Optional


class ProgramState:
    def __init__(self):
        self.running_series_start: Optional[float] = (
            None  # Timestamp when the series started, or None if not running
        )
        self.program_id: Optional[int] = None
        self.current_series_index: Optional[int] = None
        self.current_event_index: Optional[int] = None
        self.target_status_shown: bool = False


class EventType:
    PROGRAM_UPLOADED: str = "program_uploaded"
    PROGRAM_STARTED: str = "program_started"
    PROGRAM_COMPLETED: str = "program_completed"
    SERIES_STARTED: str = "series_started"
    SERIES_COMPLETED: str = "series_completed"
    SERIES_STOPPED: str = "series_stopped"
    SERIES_NEXT: str = "series_next"
    EVENT_STARTED: str = "event_started"
    TARGET_STATUS: str = "target_status"
    AUDIO_ADDED: str = "audio_added"
    AUDIO_DELETED: str = "audio_deleted"
    CHRONO: str = "chrono"


# Create a single, shared instance
program_state = ProgramState()
