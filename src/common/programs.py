from typing import Dict, List, Optional, Any
from common.program import Program
import json
import os

from common.utils import dir_exists, make_dirs


class Programs:
    def __init__(self) -> None:
        self._programs: Dict[int, Program] = {}

    def add(self, program_data: Dict[str, Any], readonly: bool = False) -> Program:
        program_data = dict(program_data)  # Copy to avoid mutating input
        program_data["readonly"] = readonly
        program = Program.from_dict(program_data)
        id = int(program.id)
        self._programs[id] = program
        print(
            f"[Programs] Added program id={program.id}, title={program.title}, readonly={readonly}"
        )
        return program

    def get(self, program_id: int) -> Optional[Program]:
        return self._programs.get(program_id)

    def get_all(self) -> Dict[int, Program]:
        return self._programs

    def load_all(self) -> None:
        shipped_dir = "src/resources/programs"
        # Load shipped programs (readonly)
        for fname in os.listdir(shipped_dir):
            if fname.endswith(".json") and fname[:-5].isdigit():
                file = shipped_dir + "/" + fname
                try:
                    print(f"[Programs] Loading shipped program file: {file}")
                    with open(file) as f:
                        data = json.load(f)
                        readonly = True
                        self.add(data, readonly=readonly)
                except OSError:
                    continue

        user_dir = "resources/programs"
        # Load user-uploaded programs (not readonly)
        if dir_exists(user_dir):
            for fname in os.listdir(user_dir):
                if fname.endswith(".json") and fname[:-5].isdigit():
                    file = user_dir + "/" + fname
                    try:
                        print(f"[Programs] Loading uploaded program file: {file}")
                        with open(file) as f:
                            data = json.load(f)
                            self.add(data, readonly=False)
                    except OSError:
                        continue

        print(f"[Programs] Total programs loaded: {len(self._programs)}")

    def add_uploaded(self, program_data: Dict[str, Any]) -> Program:
        directory = "src/resources/programs"

        if not dir_exists(directory):
            make_dirs(directory)

        # Find all used ids in the directory
        used_ids = set()
        for fname in os.listdir(directory):
            if fname.endswith(".json"):
                if fname[:-5].isdigit():  # Check if the filename is a number
                    id_str = fname[:-5]
                    used_ids.add(int(id_str))

        # Find the next available id starting from 100
        next_id = 100
        while next_id in used_ids:
            next_id += 1
        program_data["id"] = next_id
        program_data["readonly"] = False
        # Write to file
        file = directory + "/" + f"{next_id}.json"
        with open(file, "w") as f:
            json.dump(program_data, f, indent=2)
        print(f"[Programs] Uploaded program id={next_id} to {file}")

        # Add to in-memory store
        return self.add(program_data, readonly=False)

    def delete(self, program_id: int) -> bool:
        program = self._programs.get(program_id)
        if program and not program.readonly:
            del self._programs[program_id]

            file = f"resources/programs/{program.id}.json"
            try:
                os.remove(file)
                print(f"[Programs] Deleted program id={program_id} from {file}")
                return True
            except OSError as e:
                print(f"[Programs] Failed to delete file {file}: {e}")
        else:
            print(f"[Programs] Program id={program_id} not found")

        return False


# Create a single, shared instance
programs = Programs()
