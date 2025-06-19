import json
from common.program import Program

class Programs:
    def __init__(self):
        self._programs = {}  # id -> Program
        self._current_program_id = None

    def load_all_from_dir(self, directory="src/resources/programs"):
        import os
        for fname in os.listdir(directory):
            if fname.endswith(".json"):
                with open(directory + "/" + fname) as f:
                    data = json.load(f)
                    program = Program.from_dict(data)
                    self._programs[program.id] = program

    def list(self):
        return list(self._programs.values())

    def add(self, program_data):
        program = Program.from_dict(program_data)
        self._programs[program.id] = program
        return program

    def get(self, program_id):
        return self._programs.get(program_id)

    def load(self, program_id):
        if program_id in self._programs:
            self._current_program_id = program_id
            return True
        return False

    def get_loaded(self):
        if self._current_program_id is not None:
            return self._programs.get(self._current_program_id)
        return None

    def list_json(self):
        return json.dumps([p.to_dict() for p in self.list()])

    def get_json(self, program_id):
        program = self.get(program_id)
        if program:
            return program.to_json()
        return None

    def get_loaded_json(self):
        program = self.get_loaded()
        if program:
            return program.to_json()
        return None

# Create a single, shared instance
programs = Programs()

# Usage example (in backend or startup):
# programs.load_all_from_dir()