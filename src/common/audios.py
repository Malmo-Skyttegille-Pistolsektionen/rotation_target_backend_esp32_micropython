import os
import json
from typing import Dict, List, Optional, Any


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
        common_path = "src/resources/audio/readonly.json"
        if os.path.exists(common_path):
            with open(common_path) as f:
                for entry in json.load(f):
                    audio = Audio(
                        entry["id"], entry["title"], entry["filename"], readonly=True
                    )
                    self._audios[audio.id] = audio

        # Load uploaded audios
        uploaded_path = "resources/audio/uploaded.json"
        if os.path.exists(uploaded_path):
            with open(uploaded_path) as f:
                for entry in json.load(f):
                    audio = Audio(
                        entry["id"], entry["title"], entry["filename"], readonly=False
                    )
                    self._audios[audio.id] = audio

    def get(self, audio_id: int) -> Optional[Audio]:
        return self._audios.get(audio_id)

    def get_all(self) -> Dict[int, Audio]:
        return self._audios

    def add_uploaded(self, title: str, filename: str) -> Audio:
        # Find next available id (start at 100 for uploads)
        next_id = 100
        while next_id in self._audios:
            next_id += 1
        audio = Audio(next_id, title, filename, readonly=False)
        self._audios[next_id] = audio
        # Save to uploaded.json
        uploaded_path = "resources/audio/uploaded.json"
        os.makedirs(os.path.dirname(uploaded_path), exist_ok=True)
        uploaded = [a.to_dict() for a in self._audios.values() if not a.readonly]
        with open(uploaded_path, "w") as f:
            json.dump(uploaded, f, indent=2)
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
                json.dump(uploaded, f, indent=2)
            return True
        return False


# Singleton instance
audios = Audios()
