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
                # {
                #     network.name: [
                #         f"{iface.device.name}.{iface.name}"
                #         for iface in interfaces_with_device
                #     ]
                # }
                {
                    "name": network.name,
                }
            )

    data["nodes"] = []

    for _, device in topology.devices.items():
        interfaces = dict()
        for interface_name, interface in device.interfaces.items():
            ip = interface.ip_address if interface.ip_address else None

            mask = (
                topology.networks[interface.network].subnet_mask
                if interface.network
                else None
            )
            if mask is not None:
                mask = mask.split("/")[1] if "/" in mask else mask
                ip = f"{interface.ip_address}/{mask}" if interface.ip_address else None

            interfaces[interface_name] = {
                "ip": ip,
                "network": interface.network if interface.network else None,
                "gateway": (
                    interface.default_gateway if interface.default_gateway else None
                ),
            }

        data["nodes"].append(
            {"role": device.role, "name": device.name, "interfaces": interfaces}
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
