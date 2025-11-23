from dataclasses import dataclass, field
from typing import List, Optional, Dict


# ===========================
# Interface Classes
# ===========================

@dataclass
class Interface:
    name: str
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    speed: Optional[str] = None
    duplex: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Interface 'name' must be a non-empty string")


@dataclass
class VirtualInterface(Interface):
    vlan_id: int = 0
    parent_physical: Optional[Interface] = None

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.vlan_id, int) or self.vlan_id < 0:
            raise ValueError("VirtualInterface 'vlan_id' must be a non-negative integer")
        if not isinstance(self.parent_physical, Interface):
            raise TypeError("VirtualInterface 'parent_physical' must reference an Interface")


# ===========================
# Network / Subnet
# ===========================

@dataclass
class Network:
    cidr: str
    gateway: Optional[str] = None
    interfaces: List[Interface] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.cidr, str) or not self.cidr:
            raise ValueError("Network 'cidr' must be a non-empty string")
        if self.gateway is not None and not isinstance(self.gateway, str):
            raise ValueError("Network 'gateway' must be a string")


# ===========================
# Device Base Class (Abstract)
# ===========================

@dataclass
class Device:
    name: str
    mgmt_ip: Optional[str] = None
    interfaces: List[Interface] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Device 'name' must be a non-empty string")
        if self.mgmt_ip is not None and not isinstance(self.mgmt_ip, str):
            raise ValueError("Device 'mgmtIP' must be a string")


# ===========================
# Host / Router / Switch
# ===========================

@dataclass
class Host(Device):
    operating_system: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.operating_system, str):
            raise ValueError("Host 'operatingSystem' must be a string")


@dataclass
class Router(Device):
    routing_table: Dict[str, str] = field(default_factory=dict)
    routing_protocols: List[str] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()


@dataclass
class Switch(Device):
    mac_table: Dict[str, str] = field(default_factory=dict)
    vlan_database: Dict[int, str] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()


# ===========================
# Physical Link (Wire)
# ===========================

@dataclass
class Wire:
    type: str
    endpoints: List[Interface]  # Must contain exactly 2 interfaces
    bandwidth: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.type, str) or not self.type:
            raise ValueError("Wire 'type' must be a non-empty string")
        if len(self.endpoints) != 2:
            raise ValueError("Wire 'endpoints' must contain exactly 2 Interface objects")
        if not all(isinstance(i, Interface) for i in self.endpoints):
            raise TypeError("Wire 'endpoints' must be Interface objects")
