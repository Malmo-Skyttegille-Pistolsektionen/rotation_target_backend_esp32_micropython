from common.program import Program
import json
import os


class Programs:
    def __init__(self):
        self._programs = {}

    def load_all_from_dir(self, directory="src/resources/programs"):
        print(f"[Programs] Loading all programs from directory: {directory}")
        for fname in os.listdir(directory):
            if fname.endswith(".json"):
                path = directory + "/" + fname  # join paths manually
                print(f"[Programs] Loading file: {path}")
                try:
                    with open(path) as f:
                        data = json.load(f)
                        program = Program.from_dict(data)
                        self._programs[program.id] = program
                        print(
                            f"[Programs] Loaded program id={program.id}, title={program.title}"
                        )
                except Exception as e:
                    print(f"[Programs] Failed to load {path}: {e}")
        print(f"[Programs] Total programs loaded: {len(self._programs)}")
        # for program in self._programs.values():
        #     print(program)
        #     print(program.detailed_info())

    def list(self):
        return [
            {
                "id": program.id,
                "title": program.title,
                "description": program.description,
            }
            for program in self._programs.values()
        ]

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

    def list_json(self):
        return json.dumps([p.to_dict() for p in self.list()])

    def get_json(self, program_id):
        program = self.get(program_id)
        if program:
            return program.to_json()
        return None


# Create a single, shared instance
programs = Programs()
