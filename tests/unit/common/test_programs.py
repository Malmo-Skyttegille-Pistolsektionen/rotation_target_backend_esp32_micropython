from common.program import Program, Series, Event
from common.programs import Programs

class TestPrograms:
    def test_add_and_get(self):
        programs = Programs()
        data = {
            "id": "42",
            "title": "My Program",
            "description": "A test program",
            "series": [
                {
                    "name": "S1",
                    "optional": False,
                    "events": [{"duration": 5}]
                }
            ]
        }
        program = programs.add(data)
        assert program.id == "42"
        assert programs.get("42") is program

    def test_load_all_from_dir_real_programs(self):
        programs = Programs()
        programs.load_all_from_dir(directory="src/resources/programs")
        ids = [p.id for p in programs.list()]
        assert 1 in ids
        assert 2 in ids

    # Remove or update this test if you do not track loaded program in Programs
    # def test_load_and_get_loaded(self):
    #     programs = Programs()
    #     data = {
    #         "id": "1",
    #         "title": "P",
    #         "description": "D",
    #         "series": [{"name": "S", "optional": False, "events": [{"duration": 1}]}]
    #     }
    #     programs.add(data)
    #     assert programs.load("1") is True
    #     # Use program_state if you want to check loaded program

    def test_list_and_list_json(self):
        programs = Programs()
        data1 = {
            "id": "1",
            "title": "P1",
            "description": "D1",
            "series": [{"name": "S1", "optional": False, "events": [{"duration": 1}]}]
        }
        data2 = {
            "id": "2",
            "title": "P2",
            "description": "D2",
            "series": [{"name": "S2", "optional": False, "events": [{"duration": 2}]}]
        }
        programs.add(data1)
        programs.add(data2)
        lst = programs.list()
        assert len(lst) == 2
        json_str = programs.list_json()
        assert '"id": "1"' in json_str and '"id": "2"' in json_str