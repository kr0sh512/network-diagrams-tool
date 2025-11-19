from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Device:
    name: str
    model: str
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.name:
            raise ValueError("Device name cannot be empty")
        if not self.model:
            raise ValueError("Device model cannot be empty")
        if not isinstance(self.properties, dict):
            raise TypeError("properties must be a dict")


@dataclass
class Switch(Device):
    def __post_init__(self):
        super().__post_init__()

        if "ports" not in self.properties:
            raise ValueError(f"Switch '{self.name}' must define 'ports'")
        if (
            not isinstance(self.properties["ports"], int)
            or self.properties["ports"] <= 0
        ):
            raise ValueError("'ports' must be a positive integer")


@dataclass
class Router(Device):
    def __post_init__(self):
        super().__post_init__()

        if "interfaces" not in self.properties:
            raise ValueError(f"Router '{self.name}' must define 'interfaces'")
        if (
            not isinstance(self.properties["interfaces"], int)
            or self.properties["interfaces"] <= 0
        ):
            raise ValueError("'interfaces' must be a positive integer")


@dataclass
class Host(Device):
    def __post_init__(self):
        super().__post_init__()

        ip = self.properties.get("ip")
        if not ip or not isinstance(ip, str):
            raise ValueError(f"Host '{self.name}' must contain a valid 'ip' string")


@dataclass
class Wire:
    from_device: Device
    to_device: Device
