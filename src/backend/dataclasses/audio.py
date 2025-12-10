from typing import Dict, Any


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
