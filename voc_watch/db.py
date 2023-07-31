import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class DB:
    path: Optional[Path] = None
    db: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.path:
            return None
        self.path = Path(self.path)
        if not self.path.exists():
            self._create_db()
        if not self.db:
            self._load()

    def __iter__(self):
        self.current_index = 0
        self.keys = list(self.db.keys())
        return self

    def __next__(self):
        if self.current_index < len(self.keys):
            key = self.keys[self.current_index]
            self.current_index += 1
            return key
        raise StopIteration

    def _create_db(self):
        with open(self.path, "w") as f:
            json.dump(self.db, f)

    def _load(self):
        if not self.path:
            return None
        with open(self.path) as f:
            db = json.load(f)
            self.db = db

    def _save(self):
        if not self.path:
            return None
        with open(self.path, "w") as f:
            json.dump(self.db, f, indent=6)

    def transaction(func):
        def wrapper(self, *args, **kwargs):
            self._load()
            res = func(self, *args, **kwargs)
            self._save()
            return res
        return wrapper

    @transaction
    def get(self, key):
        return self.db.get(key)

    @transaction
    def put(self, key, data):
        self.db[key] = data
