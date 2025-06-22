import json
from typing import List, Optional, Dict, Any


class Event:
    def __init__(
        self,
        duration: int,
        command: Optional[str] = None,
        audio_ids: Optional[List[int]] = None,
    ) -> None:
        self.duration: int = duration
        self.command: Optional[str] = command
        self.audio_ids: List[int] = audio_ids or []

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"duration": self.duration}
        if self.command is not None:
            d["command"] = self.command
        if self.audio_ids:
            d["audio_ids"] = self.audio_ids
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Event":
        return cls(
            duration=d.get("duration"),
            command=d.get("command"),
            audio_ids=d.get("audio_ids", []),
        )


class Series:
    def __init__(self, name: str, optional: bool, events: List[Event]) -> None:
        self.name: str = name
        self.optional: bool = optional
        self.events: List[Event] = events

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "optional": self.optional,
            "events": [e.to_dict() for e in self.events],
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Series":
        events = [Event.from_dict(e) for e in d.get("events", [])]
        return cls(
            name=d.get("name"),
            optional=d.get("optional", False),
            events=events,
        )


class Program:
    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        series: List[Series],
        readonly: bool = False,
    ) -> None:
        self.id: str = id
        self.title: str = title
        self.description: str = description
        self.series: List[Series] = series
        self.readonly = readonly

    def __str__(self):
        return f"Program(id={self.id}, title={self.title}, description={self.description}, series_count={len(self.series)})"

    def detailed_info(self):
        info = []
        for s in self.series:
            num_events = len(s.events)
            total_duration = sum(e.duration for e in s.events if e.duration is not None)
            info.append(
                f"Series '{s.name}' (optional={s.optional}): {num_events} events, total duration={total_duration}s"
            )
        result = [
            f"Program '{self.title}' (ID: {self.id})",
            f"Description: {self.description}",
            f"Total series: {len(self.series)}",
            "Series details:",
        ] + info
        return "\n".join(result)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "series": [s.to_dict() for s in self.series],
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Program":
        series = [Series.from_dict(s) for s in d.get("series", [])]
        return cls(
            id=d.get("id"),
            title=d.get("title"),
            description=d.get("description"),
            series=series,
            readonly=d.get("readonly", False),
        )
