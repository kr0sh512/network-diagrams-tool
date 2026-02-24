from typing import Any, Dict, List, Optional

# ===========================


class Interface:
    name: str
    ip_address: Optional[str]
    network: Optional[str]
    default_gateway: Optional[str]
    # ---
    device: "Device"  # set by Device.add_interface() when the interface is added to a device

    def __init__(
        self,
        name: str,
        ip_address: Optional[str] = None,
        network: Optional[str] = None,
        default_gateway: Optional[str] = None,
    ):
        if not isinstance(name, str):
            raise ValueError("Interface 'name' must be a string")
        if ip_address is not None and not isinstance(ip_address, str):
            raise ValueError("Interface 'ip_address' must be a string or None")
        if network is not None and not isinstance(network, str):
            raise ValueError("Interface 'network' must be a string or None")
        if default_gateway is not None and not isinstance(default_gateway, str):
            raise ValueError("Interface 'default_gateway' must be a string or None")

        self.name = name
        self.ip_address = ip_address
        self.network = network
        self.default_gateway = default_gateway

    def __repr__(self) -> str:
        return f"Interface(name={self.name}, ip_address={self.ip_address}, network={self.network}, default_gateway={self.default_gateway})"


class VirtualInterface(Interface):
    pass


# ===========================


class Device:
    name: str
    role: str = "device"
    interfaces: Dict[str, Interface]

    def __init__(self, name: str):
        if not isinstance(name, str):
            raise ValueError("Device 'name' must be a string")

        self.name = name
        self.interfaces = dict()

    def add_interface(self, interface: Interface):
        interface.device = (
            self  # set the device attribute of the interface to this device
        )
        self.interfaces[interface.name] = interface

    def rm_interface(self, interface: Interface):
        if interface.name in self.interfaces:
            del self.interfaces[interface.name]
            # interface.device = None  # clear the device attribute of the interface
            del interface
        else:
            raise ValueError(
                f"Interface '{interface.name}' not found in device '{self.name}'"
            )

    def __repr__(self) -> str:
        return f"Device(name={self.name}, interfaces={self.interfaces})"


class Host(Device):
    role: str = "host"


class Router(Device):
    role: str = "router"


class Switch(Device):
    role: str = "switch"


# ===========================


class Network:
    name: str
    interfaces: List[Interface]
    vlan: Optional[str]  # need a proper parse
    network_ip: Optional[str]
    subnet_mask: Optional[str]

    def __init__(
        self,
        name: str,
        vlan: Optional[str] = None,
        network_ip: Optional[str] = None,
        subnet_mask: Optional[str] = None,
    ):
        if not isinstance(name, str):
            raise ValueError("Network 'name' must be a string")
        if vlan is not None and not isinstance(vlan, str):
            raise ValueError("Network 'vlan' must be a string or None")
        if network_ip is not None and not isinstance(network_ip, str):
            raise ValueError("Network 'network_ip' must be a string or None")
        if subnet_mask is not None and not isinstance(subnet_mask, str):
            raise ValueError("Network 'subnet_mask' must be a string or None")

        self.name = name
        self.interfaces = []
        self.vlan = vlan
        self.network_ip = network_ip
        self.subnet_mask = subnet_mask

    def add_interface(self, interface: Interface):
        if not isinstance(interface, Interface):
            raise ValueError("Argument must be an instance of Interface")
        if interface in self.interfaces:
            raise ValueError(
                f"Interface '{interface.name}' already exists in network '{self.name}'"
            )

        interface.network = (
            self.name  # set the network attribute of the interface to this network
        )
        self.interfaces.append(interface)

    def rm_interface(self, interface: Interface):
        if interface in self.interfaces:
            self.interfaces.remove(interface)
            interface.network = None  # clear the network attribute of the interface
        else:
            raise ValueError(
                f"Interface '{interface.name}' not found in network '{self.name}'"
            )

    def __repr__(self) -> str:
        return f"Network(name={self.name}, interfaces={self.interfaces}), vlan={self.vlan}, network_ip={self.network_ip}, subnet_mask={self.subnet_mask})"


class Topology:
    devices: Dict[str, Device]
    networks: Dict[str, Network]

    def __init__(self):
        self.devices = dict()
        self.networks = dict()

    def add_device(self, device: Device):
        if not isinstance(device, Device):
            raise ValueError("Argument must be an instance of Device")

        if device.name in self.devices:
            raise ValueError(
                f"Device with name '{device.name}' already exists in topology"
            )

        self.devices[device.name] = device

    def rm_device(self, device: Device):
        if device.name in self.devices:
            del self.devices[device.name]
        else:
            raise ValueError(f"Device with name '{device.name}' not found in topology")

    def add_network(self, network: Network):
        if not isinstance(network, Network):
            raise ValueError("Argument must be an instance of Network")

        if network.name in self.networks:
            raise ValueError(
                f"Network with name '{network.name}' already exists in topology"
            )

        self.networks[network.name] = network

    def rm_network(self, network: Network):
        if network.name in self.networks:
            del self.networks[network.name]
        else:
            raise ValueError(
                f"Network with name '{network.name}' not found in topology"
            )

    def __repr__(self) -> str:
        return f"Topology(devices={self.devices}, networks={self.networks})"
