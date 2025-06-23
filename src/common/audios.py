import json
import os
from typing import Any, Dict, List, Optional
from common.utils import dir_exists, make_dirs


class Audio:
    def __init__(
        self, id: int, title: str, filename: str, readonly: bool = False
    ) -> None:
        self.id = id
        self.title = title
        self.filename = filename
        self.readonly = readonly

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "filename": self.filename,
            "readonly": self.readonly,
        }


class Audios:
    def __init__(self) -> None:
        self._audios: Dict[int, Audio] = {}

    def load_all(self) -> None:
        # Load built-in audios
        index_file = "src/resources/audio/index.json"
        with open(index_file) as f:
            print(f"[Audios] Loading shipped audio files from: {index_file}")

            for entry in json.load(f):
                audio = Audio(
                    entry["id"], entry["title"], entry["filename"], readonly=True
                )
                self._add(audio)

        # Load uploaded audios
        uploaded_path = "resources/audio"
        if dir_exists(uploaded_path):
            index_file = uploaded_path + "/" + "index.json"
            with open(index_file) as f:
                print(f"[Audios] Loading uploaded audio files from: {index_file}")

                for entry in json.load(f):
                    audio = Audio(
                        entry["id"], entry["title"], entry["filename"], readonly=False
                    )
                    self._add(audio)

    def _add(self, audio: Audio) -> None:
        print(
            f"Adding audio: id={audio.id}, title={audio.title}, filename={audio.filename}, readonly={audio.readonly}"
        )
        self._audios[audio.id] = audio

    def get(self, audio_id: int) -> Optional[Audio]:
        return self._audios.get(audio_id)

    def get_all(self) -> Dict[int, Audio]:
        return self._audios

    async def add_uploaded(self, title: str, filename: str) -> Audio:
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
