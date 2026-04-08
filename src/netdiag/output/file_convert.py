from pathlib import Path

import yaml

from ..domain.models import Topology


def make_yaml(topology: Topology, output_path: Path) -> None:
    data = dict()

    data["meta"] = {
        "id": output_path.name,
        "name": output_path.name,
    }

    data["networks"] = []
    for _, network in topology.networks.items():
        interfaces_with_device = [
            iface for iface in network.interfaces if iface.device is not None
        ]

        if len(interfaces_with_device) >= 2:
            data["networks"].append(
                {
                    "name": network.name,
                }
            )

    data["nodes"] = []

    for _, device in topology.devices.items():
        interfaces = dict()
        bridges = []
        vlans = []

        for interface_name, interface in device.interfaces.items():
            ip = interface.ip_address if interface.ip_address else None

            mask = interface.subnet_mask if interface.subnet_mask else None

            if mask is not None:
                mask = mask.split("/")[1] if "/" in mask else mask
                ip = f"{interface.ip_address}/{mask}" if interface.ip_address else None

            index = None
            # check regex Adapter[0-9]+
            if interface.adapter:
                if (
                    not interface.adapter.startswith("Adapter")
                    or not interface.adapter[7:].isdigit()
                ):
                    raise ValueError(
                        f"Invalid adapter name '{interface.adapter}' for interface '{interface_name}' on device '{device.name}'. Adapter name must be in the format 'AdapterX' where X is a number."
                    )
                index = int(interface.adapter[7:])

            if interface.itype == "bridge":
                bridges.append(
                    {
                        "name": interface.name,
                        "members": interface.slave_interfaces,
                        "ip": ip,
                        "gateway": (
                            interface.default_gateway
                            if interface.default_gateway
                            else None
                        ),
                    }
                )
                continue
            if interface.itype == "vlan":
                vlans.append(
                    {
                        "name": interface.name,
                        "parent": interface.parent_interface,
                        "ip": ip,
                        "gateway": (
                            interface.default_gateway
                            if interface.default_gateway
                            else None
                        ),
                        "id": interface.vlan,
                    }
                )
                continue
            interfaces[interface_name] = {
                "ip": ip,
                "network": interface.network if interface.network else None,
                "gateway": (
                    interface.default_gateway if interface.default_gateway else None
                ),
                "index": index,
            }

        data["nodes"].append(
            {
                "role": device.role,
                "name": device.name,
                "interfaces": interfaces,
                "bridges": bridges,
                "vlans": vlans,
            }
        )

    with open(str(output_path), "w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            indent=2,
        )
