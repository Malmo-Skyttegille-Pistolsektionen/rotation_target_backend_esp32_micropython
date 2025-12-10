import json
import os
from typing import Any, Dict, Optional
from backend.common.io_utils import dir_exists, file_exists, make_dirs, path_join
import logging

from backend.dataclasses.audio import Audio


class Audios:
    def __init__(self) -> None:
        self._audios: Dict[int, Audio] = {}

    def _load_audios_from_file(self, path_to_audios_json: str, readonly: bool) -> None:
        filename = path_join(path_to_audios_json, "audios.json")

        if not file_exists(filename):
            logging.warning(f"[Audios] Audio index file not found: {filename}")
            return

        with open(filename) as f:
            logging.info(f"[Audios] Loading from audio index file: {filename}")
            entries = json.load(f)

            # Support both dict and list formats
            if isinstance(entries, dict):
                items = entries.items()
            else:
                items = ((entry["id"], entry) for entry in entries)

            for audio_id, entry in items:
                audio = Audio(
                    int(audio_id),
                    entry["title"],
                    path_join(path_to_audios_json, entry["filename"]),
                    readonly=readonly,
                )
                self._add(audio)

    def load_all(self) -> None:

        # Load built-in audios
        self._load_audios_from_file("src/resources/audio", readonly=True)

        # Load uploaded audios
        uploaded_path = "resources/audio"
        if dir_exists(uploaded_path):
            self._load_audios_from_file(os.path.join(uploaded_path), readonly=False)

        logging.info(f"[Audios] Total audios loaded: {len(self._audios)}")

    def _add(self, audio: Audio) -> None:
        logging.trace(
            f"[Audios] Adding audio: id={audio.id}, title={audio.title}, filename={audio.filename}, readonly={audio.readonly}"
        )
        self._audios[audio.id] = audio

    def get(self, audio_id: int) -> Optional[Audio]:
        return self._audios.get(audio_id)

    def get_all(self) -> Dict[int, Audio]:
        return self._audios

    async def add_uploaded(self, title: str, filename: str, codec: str) -> Audio:
        # Find next available id (start at 100 for uploads)
        next_id = 100
        while next_id in self._audios:
            next_id += 1
        audio = Audio(next_id, title, filename, readonly=False)
        self._audios[next_id] = audio

        # Ensure the resources/audio directory exists
        if not dir_exists("resources/audio"):
            make_dirs("resources/audio")
        # Save to uploaded.json
        index_json_path = "resources/audio/index.json"

        uploaded = [a.to_dict() for a in self._audios.values() if not a.readonly]
        with open(index_json_path, "w") as f:
            json.dump(uploaded, f)
        return audio

    def delete_uploaded(self, audio_id: int) -> bool:
        audio = self._audios.get(audio_id)
        if audio and not audio.readonly:
            try:
                os.remove(f"resources/audio/{audio.filename}")
            except OSError:
                pass
            del self._audios[audio_id]
            # Update uploaded.json
            uploaded_path = "resources/audio/uploaded.json"
            uploaded = [a.to_dict() for a in self._audios.values() if not a.readonly]
            with open(uploaded_path, "w") as f:
                json.dump(uploaded, f)
            return True
        return False


# Singleton instance
audios = Audios()
