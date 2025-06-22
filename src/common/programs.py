from typing import Dict, List, Optional, Any
from common.program import Program
import json
import os


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
        # Load shipped/readonly programs from src/resources/programs
        shipped_dir = "src/resources/programs"
        # MicroPython compatibility: use os.stat to check for files
        try:
            os.stat(shipped_dir)
            loaded_any = False
            # Try loading files named 0.json, 1.json, ... up to 999.json
            for idx in range(1000):
                fname = f"{idx}.json"
                path = shipped_dir + "/" + fname
                try:
                    os.stat(path)
                    print(f"[Programs] Loading shipped program file: {path}")
                    with open(path) as f:
                        data = json.load(f)
                        readonly = True
                        self.add(data, readonly=readonly)
                        loaded_any = True
                except OSError:
                    continue
            if not loaded_any:
                print(f"[Programs] No shipped programs found in {shipped_dir}")
        except OSError:
            pass  # Directory does not exist
        except AttributeError:
            print("[Programs] os.stat not available (MicroPython?)")

        # Load user programs from resources/programs
        user_dir = "resources/programs"
        try:
            os.stat(user_dir)
            loaded_any = False
            for idx in range(1000):
                fname = f"{idx}.json"
                path = os.path.join(user_dir, fname)
                try:
                    os.stat(path)
                    print(f"[Programs] Loading uploaded program file: {path}")
                    with open(path) as f:
                        data = json.load(f)
                        # User programs are not readonly
                        self.add(data, readonly=False)
                        loaded_any = True
                except OSError:
                    continue
            if not loaded_any:
                print(f"[Programs] No user programs found in {user_dir}")
        except OSError:
            pass  # Directory does not exist
        except AttributeError:
            print("[Programs] os.stat not available (MicroPython?)")

        print(f"[Programs] Total programs loaded: {len(self._programs)}")
        # Since both shipped_dir and user_dir always exist, we can remove the try/except blocks
        # and simplify the code accordingly.

        def load_all(self) -> None:
            shipped_dir = "src/resources/programs"
            loaded_any = False
            for idx in range(1000):
                fname = f"{idx}.json"
                path = shipped_dir + "/" + fname
                try:
                    os.stat(path)
                    print(f"[Programs] Loading shipped program file: {path}")
                    with open(path) as f:
                        data = json.load(f)
                        readonly = True
                        self.add(data, readonly=readonly)
                        loaded_any = True
                except OSError:
                    continue
            if not loaded_any:
                print(f"[Programs] No shipped programs found in {shipped_dir}")

            user_dir = "resources/programs"
            loaded_any = False
            for idx in range(1000):
                fname = f"{idx}.json"
                path = os.path.join(user_dir, fname)
                try:
                    os.stat(path)
                    print(f"[Programs] Loading uploaded program file: {path}")
                    with open(path) as f:
                        data = json.load(f)
                        self.add(data, readonly=False)
                        loaded_any = True
                except OSError:
                    continue
            if not loaded_any:
                print(f"[Programs] No user programs found in {user_dir}")

            print(f"[Programs] Total programs loaded: {len(self._programs)}")
    def upload(self, program_data: Dict[str, Any]) -> Program:
        directory = "src/resources/programs"
        os.makedirs(directory, exist_ok=True)
        # Find all used ids in the directory
        used_ids = set()
        for fname in os.listdir(directory):
            if fname.endswith(".json"):
                try:
                    id_str = fname.split(".")[0]
        directory = "src/resources/programs"
        try:
            os.makedirs(directory)
        except OSError:
            pass  # Directory may already exist

        # Find all used ids in the directory by checking for 0.json, 1.json, ...
        used_ids = set()
        for idx in range(1000):
            fname = f"{idx}.json"
            path = os.path.join(directory, fname)
            try:
                os.stat(path)
                used_ids.add(idx)
            except OSError:
                continue

        # Find the next available id starting from 100
        next_id = 100
        while next_id in used_ids:
            next_id += 1
        program_data["id"] = next_id
        program_data["readonly"] = False
        # Write to file
        path = os.path.join(directory, f"{next_id}.json")
        with open(path, "w") as f:
            json.dump(program_data, f, indent=2)
        print(f"[Programs] Uploaded program id={next_id} to {path}")

        # Add to in-memory store
        return self.add(program_data, readonly=False)
            path = f"src/resources/programs/{program_id}.json"
            try:
                os.remove(path)
                print(f"[Programs] Deleted program id={program_id} from {path}")
                return True
            except OSError as e:
                print(f"[Programs] Failed to delete file {path}: {e}")
        else:
            print(f"[Programs] Program id={program_id} not found")
        return False


# Create a single, shared instance
programs = Programs()
