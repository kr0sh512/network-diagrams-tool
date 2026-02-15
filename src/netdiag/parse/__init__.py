from typing import Dict, Any, List
import csv
import logging


class RawDevices:
    id: int
    fields: Dict[str, Any]

    def __init__(self, id: int, fields: Dict[str, Any]):
        if not isinstance(id, int):
            raise ValueError("RawDevices 'id' must be an integer")
        if not isinstance(fields, dict):
            raise ValueError("RawDevices 'fields' must be a dictionary")
        if any(not isinstance(k, str) for k in fields.keys()):
            raise ValueError("RawDevices 'fields' keys must be strings")

        self.id = id
        self.fields = fields

    def __repr__(self) -> str:
        return f"RawDevices(id={self.id}, fields={self.fields})"


def parse_csv(file_path: str, delimiter: str = ",") -> List[RawDevices]:
    logging.info(f"Parsing CSV file: {file_path}")

    with open(file_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        devices = [RawDevices(idx + 1, row) for idx, row in enumerate(reader)]

    return devices
