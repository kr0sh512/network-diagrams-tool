from ..domain.models import Topology
from pathlib import Path
import graphviz
import shutil


def _check_graphviz_installed() -> bool:
    return shutil.which("dot") is not None


def generate_diagram(topology: Topology, output_path: Path) -> None:
    if not _check_graphviz_installed():
        raise EnvironmentError(
            "Graphviz is not installed or 'dot' command is not found in PATH. Please install Graphviz to use this feature."
        )

    dot = graphviz.Graph(name="Network Topology", format="png", engine="neato")
    dot.attr(overlap="false", splines="true")

    for device in topology.devices.values():
        shape = "box"
        dot.node(device.name, label=device.name, shape=shape)

    for network in topology.networks.values():
        interfaces_with_device = [
            iface for iface in network.interfaces if iface.device is not None
        ]

        for i, iface_a in enumerate(interfaces_with_device):
            for iface_b in interfaces_with_device[i + 1 :]:
                label = network.name or ""
                dot.edge(iface_a.device.name, iface_b.device.name, label=label)

    output_path = (
        output_path.with_suffix("") if output_path.suffix == ".png" else output_path
    )

    dot.render(str(output_path), cleanup=True)

    return
