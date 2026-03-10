import logging

from ..domain.models import (
    Device,
    Host,
    Interface,
    Network,
    Router,
    Switch,
    Topology,
    VirtualInterface,
)
from . import RawDevices

name_matching = {
    "DEVICE_TYPE": "Role",
    "DEVICE_NAME": "Name",
    "ADAPTER": "Adapter",
    "MASTER": "Master Interface",
    "INTERFACE_NAME": "Interface",
    "NETWORK_NAME": "Network",
    "VLAN": "VLAN",
    "NETWORK_IP": "Network IP",
    "SUBNET_MASK": "Mask",
    "IP_ADDRESS": "Device IP",
    "DEFAULT_GATEWAY": "Default Gateway",
    # --- In-cell fields ---
    "TRUNK": "trunk",
    "HOST": "Host",
    "ROUTER": "Router",
    "SWITCH": "Switch",
}


def _get_from_field(fields: dict, field_name: str) -> str:
    return fields.get(name_matching[field_name], "").strip()


def parse_devices(raw_devices: list[RawDevices]) -> list[Device]:
    devices = []

    for raw_device in raw_devices:
        device_type = raw_device.fields.get(name_matching["DEVICE_TYPE"], "").strip()
        device_name = raw_device.fields.get(name_matching["DEVICE_NAME"], "").strip()

        if not device_type or not device_name:
            raise ValueError(
                f"Device with ID {raw_device.id} is missing required fields 'DEVICE_TYPE' and 'DEVICE_NAME'"
            )

        if device_name in [d.name for d in devices]:
            continue

        if device_type == name_matching["HOST"]:
            device = Host(name=device_name)
        elif device_type == name_matching["ROUTER"]:
            device = Router(name=device_name)
        elif device_type == name_matching["SWITCH"]:
            device = Switch(name=device_name)
        else:
            raise ValueError(
                f"Device with ID {raw_device.id} has unrecognized DEVICE_TYPE '{device_type}'"
            )

        devices.append(device)

    return devices


def add_interfaces(devices: list[Device], raw_devices: list[RawDevices]) -> None:
    for raw_device in raw_devices:
        device_name = raw_device.fields.get(name_matching["DEVICE_NAME"], "").strip()
        device = next(
            (d for d in devices if d.name == device_name), None
        )  # some other way?

        if not device:
            raise ValueError(
                f"Device with name '{device_name}' not found for interface parsing"
            )

        if not raw_device.fields.get(name_matching["ADAPTER"], "").strip():
            interface = VirtualInterface(
                name=_get_from_field(raw_device.fields, "INTERFACE_NAME"),
                master_interface=_get_from_field(raw_device.fields, "MASTER"),
                ip_address=_get_from_field(raw_device.fields, "IP_ADDRESS"),
                network=_get_from_field(raw_device.fields, "NETWORK_NAME"),
                default_gateway=_get_from_field(raw_device.fields, "DEFAULT_GATEWAY"),
            )

        else:
            interface = Interface(
                name=_get_from_field(raw_device.fields, "INTERFACE_NAME"),
                adapter=_get_from_field(raw_device.fields, "ADAPTER"),
                master_interface=_get_from_field(raw_device.fields, "MASTER"),
                ip_address=_get_from_field(raw_device.fields, "IP_ADDRESS"),
                network=_get_from_field(raw_device.fields, "NETWORK_NAME"),
                default_gateway=_get_from_field(raw_device.fields, "DEFAULT_GATEWAY"),
            )
        device.add_interface(interface)

    return


def parse_networks(raw_devices: list[RawDevices]) -> list[Network]:
    networks = []

    for raw_device in raw_devices:
        network_name = raw_device.fields.get(name_matching["NETWORK_NAME"], "").strip()
        if not network_name:
            continue

        vlan = (raw_device.fields.get(name_matching["VLAN"], "").strip(),)
        network_ip = (raw_device.fields.get(name_matching["NETWORK_IP"], "").strip(),)
        subnet_mask = (raw_device.fields.get(name_matching["SUBNET_MASK"], "").strip(),)

        if network_name in [n.name for n in networks]:  # update if already exists
            network = next(n for n in networks if n.name == network_name)

            if not network.vlan and vlan:
                network.vlan = vlan
            if not network.network_ip and network_ip:
                network.network_ip = network_ip
            if not network.subnet_mask and subnet_mask:
                network.subnet_mask = subnet_mask
            continue

        network = Network(
            name=network_name,
            vlan=raw_device.fields.get(name_matching["VLAN"], "").strip(),
            network_ip=raw_device.fields.get(name_matching["NETWORK_IP"], "").strip(),
            subnet_mask=raw_device.fields.get(name_matching["SUBNET_MASK"], "").strip(),
        )
        networks.append(network)

    return networks


def assign_interfaces_to_networks(
    networks: list[Network], devices: list[Device]
) -> None:
    for network in networks:
        for device in devices:
            for _, interface in device.interfaces.items():
                if interface.network == network.name:
                    network.add_interface(interface)

    return


def convert_raw_topology(raw_devices: list[RawDevices]) -> Topology:
    topology = Topology()

    logging.info(f"Parsing {len(raw_devices)} raw devices to devices")
    devices = parse_devices(raw_devices)
    logging.info(f"Parsing interfaces from raw devices")
    add_interfaces(devices, raw_devices)

    for device in devices:
        topology.add_device(device)

    logging.info(f"Parsing networks from raw devices")
    networks = parse_networks(raw_devices)
    assign_interfaces_to_networks(networks, devices)

    for network in networks:
        topology.networks[network.name] = network

    return topology
