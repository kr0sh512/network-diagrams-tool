from typing import Dict, List, Optional
import logging

# TODO rewrite to dataclasses with validation


class Interface:
    name: str
    itype: Optional[str]
    adapter: Optional[str]
    slave_interfaces: Optional[List[str]]
    parent_interface: Optional[str]
    ip_address: Optional[str]
    network: Optional[str]
    subnet_mask: Optional[str]
    default_gateway: Optional[str]
    vlan: Optional[str]
    # ---
    device: "Device"  # set by Device.add_interface() when the interface is added to a device

    def __init__(
        self,
        name: str,
        adapter: Optional[str] = None,
        slave_interfaces: Optional[List[str]] = None,
        parent_interface: Optional[str] = None,
        ip_address: Optional[str] = None,
        network: Optional[str] = None,
        subnet_mask: Optional[str] = None,
        default_gateway: Optional[str] = None,
        vlan: Optional[str] = None,
    ):
        if not isinstance(name, str):
            raise ValueError("Interface 'name' must be a string")
        if ip_address is not None and not isinstance(ip_address, str):
            raise ValueError("Interface 'ip_address' must be a string or None")
        if network is not None and not isinstance(network, str):
            raise ValueError("Interface 'network' must be a string or None")
        if subnet_mask is not None and not isinstance(subnet_mask, str):
            raise ValueError("Interface 'subnet_mask' must be a string or None")
        if default_gateway is not None and not isinstance(default_gateway, str):
            raise ValueError("Interface 'default_gateway' must be a string or None")
        if adapter is not None and not isinstance(adapter, str):
            raise ValueError("Interface 'adapter' must be a string or None")
        if slave_interfaces is not None and not isinstance(slave_interfaces, list):
            raise ValueError(
                "Interface 'slave_interfaces' must be a list of strings or None"
            )
        if parent_interface is not None and not isinstance(parent_interface, str):
            raise ValueError("Interface 'parent_interface' must be a string or None")
        if vlan is not None and not isinstance(vlan, str):
            raise ValueError("Interface 'vlan' must be a string or None")

        # edit this
        adapter = None if adapter == "" else adapter
        slave_interfaces = None if slave_interfaces == [] else slave_interfaces
        parent_interface = None if parent_interface == "" else parent_interface
        vlan = None if vlan == "" else vlan

        logging.debug(
            f"Creating interface '{name}' with adapter='{adapter}', slave_interfaces='{slave_interfaces}', parent_interface='{parent_interface}'"
        )

        # looks like shit
        if (
            (adapter is not None)
            + (slave_interfaces is not None)
            + (parent_interface is not None)
        ) != 1:
            raise ValueError(
                "Interface must have exactly one of 'adapter', 'slave_interfaces', or 'parent_interface' defined"
            )

        if slave_interfaces is not None:
            itype = "bridge"
            network = None
        elif parent_interface is not None:
            if vlan is None:
                raise ValueError(
                    "Interface with 'parent_interface' must have 'vlan' defined"
                )
            itype = "vlan"
            network = None
        else:
            itype = "physical"

        # sort all this values
        self.name = name
        self.itype = itype
        self.ip_address = ip_address
        self.network = network
        self.subnet_mask = subnet_mask
        self.default_gateway = default_gateway
        self.adapter = adapter
        self.slave_interfaces = slave_interfaces
        self.parent_interface = parent_interface
        self.vlan = vlan

    def __repr__(self) -> str:
        return f"Interface(name={self.name}, itype={self.itype}, ip_address={self.ip_address}, network={self.network}, default_gateway={self.default_gateway}, subnet_mask={self.subnet_mask}, adapter={self.adapter}, slave_interfaces={self.slave_interfaces}, vlan={self.vlan})"


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
    network_ip: Optional[str]  # а что он делает?

    def __init__(
        self,
        name: str,
        vlan: Optional[str] = None,
        network_ip: Optional[str] = None,
    ):
        if not isinstance(name, str):
            raise ValueError("Network 'name' must be a string")
        if vlan is not None and not isinstance(vlan, str):
            raise ValueError("Network 'vlan' must be a string or None")
        if network_ip is not None and not isinstance(network_ip, str):
            raise ValueError("Network 'network_ip' must be a string or None")

        self.name = name
        self.interfaces = []
        self.vlan = vlan
        self.network_ip = network_ip

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
        return f"Network(name={self.name}, interfaces={self.interfaces}), vlan={self.vlan}, network_ip={self.network_ip})"


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
