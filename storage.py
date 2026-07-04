"""
storage.py
==========

Persistence layer for the clinic attendance application.

Data is stored locally as a single JSON file (no database required). This
module is the only place that knows about file I/O, so swapping the storage
backend in the future (e.g. to SQLite) only requires changes here.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from models import ClinicData

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Raised when data cannot be loaded from or saved to disk."""


class JsonStorage:
    """Handles reading and writing :class:`ClinicData` to a JSON file on disk."""

    def __init__(self, filepath: Path) -> None:
        """Initialize the storage handler.

        Args:
            filepath: Path to the JSON file used for persistence.
        """
        self.filepath = filepath

    def load(self) -> ClinicData:
        """Load clinic data from disk.

        Returns:
            A :class:`ClinicData` instance. If the file does not exist yet,
            an empty (default) instance is returned instead of raising.

        Raises:
            StorageError: If the file exists but cannot be parsed.
        """
        if not self.filepath.exists():
            logger.info("No existing data file found at %s. Starting fresh.", self.filepath)
            return ClinicData()

        try:
            with self.filepath.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            return ClinicData.from_dict(raw)
        except (json.JSONDecodeError, OSError) as exc:
            raise StorageError(f"לא ניתן לטעון את קובץ הנתונים: {exc}") from exc

    def save(self, data: ClinicData) -> None:
        """Persist clinic data to disk atomically.

        Writes to a temporary file first and then replaces the target file,
        to minimize the risk of data corruption if the app is closed mid-write.

        Args:
            data: The :class:`ClinicData` instance to save.

        Raises:
            StorageError: If the data cannot be written to disk.
        """
        tmp_path = self.filepath.with_suffix(".tmp")
        try:
            with tmp_path.open("w", encoding="utf-8") as f:
                json.dump(data.to_dict(), f, ensure_ascii=False, indent=2)
            tmp_path.replace(self.filepath)
        except OSError as exc:
            raise StorageError(f"לא ניתן לשמור את קובץ הנתונים: {exc}") from exc
