from typing import Dict, Optional, Any
from common.program import Program
import json
import os

from common.utils import dir_exists, make_dirs
from common.common import EventType
from web.sse import emit_sse_event
import logging


class Programs:
    def __init__(self) -> None:
        self._programs: Dict[int, Program] = {}

    def add(self, program_data: Dict[str, Any], readonly: bool = False) -> Program:
        program_data = dict(program_data)  # Copy to avoid mutating input
        program_data["readonly"] = readonly
        program = Program.from_dict(program_data)
        id = int(program.id)
        self._programs[id] = program
        logging.debug(
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
                    logging.debug(f"[Programs] Loading shipped program file: {file}")
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
                        logging.debug(
                            f"[Programs] Loading uploaded program file: {file}"
                        )
                        with open(file) as f:
                            data = json.load(f)
                            self.add(data, readonly=False)
                    except OSError:
                        continue

        logging.debug(f"[Programs] Total programs loaded: {len(self._programs)}")

    async def add_uploaded(self, program_data: Dict[str, Any]) -> Program:
        directory = "resources/programs"
        logging.debug(f"[add_uploaded] Checking if directory exists: {directory}")

        if not dir_exists(directory):
            logging.debug(
                f"[add_uploaded] Directory does not exist. Creating: {directory}"
            )
            make_dirs(directory)
        else:
            logging.debug(f"[add_uploaded] Directory exists: {directory}")

        # Find all used ids in the directory
        used_ids = set()
        logging.debug(f"[add_uploaded] Scanning for used IDs in directory: {directory}")
        for fname in os.listdir(directory):
            logging.debug(f"[add_uploaded] Found file: {fname}")
            if fname.endswith(".json"):
                if fname[:-5].isdigit():  # Check if the filename is a number
                    id_str = fname[:-5]
                    used_ids.add(int(id_str))
                    logging.debug(f"[add_uploaded] Found used id: {id_str}")

        # Find the next available id starting from 100
        next_id = 100
        logging.debug(
            f"[add_uploaded] Searching for next available id starting from {next_id}"
        )
        while next_id in used_ids:
            logging.debug(f"[add_uploaded] id {next_id} is already used")
            next_id += 1
        logging.debug(f"[add_uploaded] Next available id: {next_id}")

        program_data["id"] = next_id
        program_data["readonly"] = False

        # Write to file
        file = directory + "/" + f"{next_id}.json"
        logging.debug(f"[add_uploaded] Writing program data to file: {file}")
        with open(file, "w") as f:
            json.dump(program_data, f)
        logging.debug(f"[Programs] Uploaded program id={next_id} to {file}")

        # Add to in-memory store
        logging.debug(f"[add_uploaded] Adding program to in-memory store")
        program = self.add(program_data, readonly=False)

        # Emit SSE event
        await emit_sse_event(EventType.PROGRAM_ADDED, {"program_id": program.id})

        return program

    async def delete(self, program_id: int) -> bool:
        program = self._programs.get(program_id)
        if program and not program.readonly:
            del self._programs[program_id]

            file = f"resources/programs/{program.id}.json"
            try:
                os.remove(file)
                logging.debug(f"[Programs] Deleted program id={program_id} from {file}")

                # Emit SSE event
                await emit_sse_event(
                    EventType.PROGRAM_DELETED, {"program_id": program.id}
                )

                return True
            except OSError as e:
                logging.debug(f"[Programs] Failed to delete file {file}: {e}")
        else:
            logging.debug(f"[Programs] Program id={program_id} not found")

        return False


# Create a single, shared instance
programs = Programs()
