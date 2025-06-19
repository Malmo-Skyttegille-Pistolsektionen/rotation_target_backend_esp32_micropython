# Program state
import json


program_state = {
    "running_series_start": None,  # Timestamp when the series started, or None if not running
    "program_id": None,
    "current_series_index": None,
    "current_event_index": None,
    "target_status_shown": False,
}

class EventType:
    PROGRAM_UPLOADED = 'program_uploaded'
    PROGRAM_STARTED = 'program_started'
    PROGRAM_COMPLETED = 'program_completed'
    SERIES_STARTED = 'series_started'
    SERIES_COMPLETED = 'series_completed'
    SERIES_STOPPED = 'series_stopped'
    SERIES_NEXT = 'series_next'
    EVENT_STARTED = 'event_started'
    TARGET_STATUS = 'target_status'
    AUDIO_ADDED = 'audio_added'
    AUDIO_DELETED = 'audio_deleted'
    CHRONO = 'chrono'