import pytest

from common.program import Program, Series, Event

class TestEvent:
    def test_to_dict_and_from_dict(self):
        event = Event(duration=10, command="show", audio_ids=[1, 2])
        d = event.to_dict()
        assert d == {"duration": 10, "command": "show", "audio_ids": [1, 2]}
        event2 = Event.from_dict(d)
        assert event2.duration == 10
        assert event2.command == "show"
        assert event2.audio_ids == [1, 2]

class TestSeries:
    def test_to_dict_and_from_dict(self):
        events = [Event(duration=5), Event(duration=10, command="hide")]
        series = Series(name="Test Series", optional=True, events=events)
        d = series.to_dict()
        assert d["name"] == "Test Series"
        assert d["optional"] is True
        assert isinstance(d["events"], list)
        series2 = Series.from_dict(d)
        assert series2.name == "Test Series"
        assert series2.optional is True
        assert len(series2.events) == 2
        assert series2.events[1].command == "hide"

class TestProgram:
    def test_to_dict_and_from_dict(self):
        events = [Event(duration=5), Event(duration=10, command="hide")]
        series = [Series(name="Test Series", optional=False, events=events)]
        program = Program(id=1, title="Test", description="Desc", series=series)
        d = program.to_dict()
        assert d["id"] == 1
        assert d["title"] == "Test"
        assert d["description"] == "Desc"
        assert isinstance(d["series"], list)
        program2 = Program.from_dict(d)
        assert program2.id == 1
        assert program2.title == "Test"
        assert program2.description == "Desc"
        assert len(program2.series) == 1
        assert program2.series[0].name == "Test Series"