from ..domain.models import Topology
import graphviz


def generate_diagram(topology: Topology, output_path: str) -> None:
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

    output_path = output_path[:-4] if output_path.endswith(".png") else output_path
    dot.render(output_path, cleanup=True)

    return
