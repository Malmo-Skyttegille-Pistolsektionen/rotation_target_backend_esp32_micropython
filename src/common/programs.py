from typing import Dict, List, Optional, Any
from common.program import Program
import json
import os


class Programs:
    def __init__(self) -> None:
        self._programs: Dict[int, Program] = {}

    def add(self, program_data: Dict[str, Any]) -> Program:
        program = Program.from_dict(program_data)
        id = int(program.id)
        self._programs[id] = program
        print(f"[Programs] Added program id={program.id}, title={program.title}")
        return program

    # def delete(self, program_id: str) -> None:
    #     del self._programs[program_id]
    #     print(f"[Programs] Deleted program id={program_id}")

    def get(self, program_id: int) -> Optional[Program]:
        return self._programs.get(program_id)

    def get_all(self) -> Dict[int, Program]:
        return self._programs

    def load_all_from_dir(self, directory: str = "src/resources/programs") -> None:
        for fname in os.listdir(directory):
            if fname.endswith(".json"):
                path = directory + "/" + fname  # join paths manually
                print(f"[Programs] Loading file: {path}")
                try:
                    with open(path) as f:
                        data = json.load(f)
                        self.add(data)
                except Exception as e:
                    print(f"[Programs] Failed to load {path}: {e}")
        print(f"[Programs] Total programs loaded: {len(self._programs)}")
        # for program in self._programs.values():
        #     print(program)
        #     print(program.detailed_info())


# Create a single, shared instance
programs = Programs()
