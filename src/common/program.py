import json

class Event:
    def __init__(self, duration, command=None, audio_ids=None):
        self.duration = duration
        self.command = command
        self.audio_ids = audio_ids or []

    def to_dict(self):
        d = {"duration": self.duration}
        if self.command is not None:
            d["command"] = self.command
        if self.audio_ids:
            d["audio_ids"] = self.audio_ids
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
            duration=d.get("duration"),
            command=d.get("command"),
            audio_ids=d.get("audio_ids", [])
        )

class Series:
    def __init__(self, name, optional, events):
        self.name = name
        self.optional = optional
        self.events = events  # List of Event objects

    def to_dict(self):
        return {
            "name": self.name,
            "optional": self.optional,
            "events": [e.to_dict() for e in self.events]
        }

    @classmethod
    def from_dict(cls, d):
        events = [Event.from_dict(e) for e in d.get("events", [])]
        return cls(
            name=d.get("name"),
            optional=d.get("optional", False),
            events=events
        )

class Program:
    def __init__(self, id, title, description, series):
        self.id = id
        self.title = title
        self.description = description
        self.series = series  # List of Series objects

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "series": [s.to_dict() for s in self.series]
        }

    def __str__(self):
        return f"Program(id={self.id}, title={self.title}, description={self.description}, series_count={len(self.series)})"

    def detailed_info(self):
        info = []
        total_events = 0
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
            "Series details:"
        ] + info
        return "\n".join(result)

    @classmethod
    def from_dict(cls, d):
        series = [Series.from_dict(s) for s in d.get("series", [])]
        return cls(
            id=d.get("id"),
            title=d.get("title"),
            description=d.get("description"),
            series=series
        )

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str):
        return cls.from_dict(json.loads(json_str))