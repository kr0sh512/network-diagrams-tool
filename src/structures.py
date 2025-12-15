from dataclasses import dataclass, field
from typing import List, Optional, Dict

# ===========================
# Network / Subnet
# ===========================

@dataclass
class Network:
    name: str
    vlan_id : Optional[int] = None
    ip: Optional[str] = None
    subnet_mask: Optional[str] = None
    
    def __init__(self, fields):
        self.name = fields.get("name")
        self.vlan_id = fields.get("vlan", fields.get("vlan_id"))
        self.ip = fields.get("ip")
        self.subnet_mask = fields.get("mask", fields.get("subnet_mask"))
        self.__post_init__()
        
    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Network 'name' must be a non-empty string")

# ===========================
# Interface Classes
# ===========================


@dataclass
class Interface:
    class IP:
        def __init__(self, ip_str: str, default_gateway: Optional[str] = None):
            self.ip_str = ip_str
            self.default_gateway = default_gateway

        def __str__(self):
            return self.ip_str
    
    name: str
    mode: Optional[str] = None
    network: Optional[Network] = None
    ips: Optional[List[IP]] = None
    mac_address: Optional[str] = None
    speed: Optional[str] = None

    def __init__(self, fields):
        self.name = fields.get("name")
        ips = fields.get("ips", [])
        if isinstance(ips, str):
            ips = [self.IP(ip_str=ip.strip()) for ip in ips.split(",") if ip.strip()]
        self.ips = ips
        
        # возможно передаём просто field
        self.network = Network(fields.get("network", {})) if fields.get("network") else None
        
        self.mac_address = fields.get("mac")
        self.speed = fields.get("speed")
        self.__post_init__()

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Interface 'name' must be a non-empty string")


# ===========================
# Device Base Class (Abstract)
# ===========================


@dataclass
class Device:
    name: str
    interfaces: List[Interface] = field(default_factory=list)

    def __init__(self, fields):
        self.name = fields.get("name")
        # тут точно понять, какие поля передаются
        self.interfaces = [Interface(iface) for iface in fields.get("interfaces", [])]
        self.__post_init__()

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Device 'name' must be a non-empty string")


# ===========================
# Host / Router / Switch
# ===========================


@dataclass
class Host(Device):
    # operating_system: Optional[str] = None

    def __init__(self, fields):
        super().__init__(fields)
        # self.operating_system = fields.get("operatingSystem")
        self.__post_init__()

    def __post_init__(self):
        super().__post_init__()


@dataclass
class Router(Device):
    # routing_table: Dict[str, str] = field(default_factory=dict)
    # routing_protocols: List[str] = field(default_factory=list)

    def __init__(self, fields):
        super().__init__(fields)
        # self.routing_table = fields.get("routingTable", {})
        # self.routing_protocols = fields.get("routingProtocols", [])
        self.__post_init__()

    def __post_init__(self):
        super().__post_init__()


@dataclass
class Switch(Device):
    # mac_table: Dict[str, str] = field(default_factory=dict)
    # vlan_database: Dict[int, str] = field(default_factory=dict)

    def __init__(self, fields):
        super().__init__(fields)
        # self.mac_table = fields.get("macTable", {})
        # self.vlan_database = fields.get("vlanDatabase", {})
        self.__post_init__()

    def __post_init__(self):
        super().__post_init__()

