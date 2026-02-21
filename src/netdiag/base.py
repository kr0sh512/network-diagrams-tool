from .parse import parse_csv
from .domain.models import Topology
from .parse.convert_raw import (
    convert_raw_topology,
)
from .output.graphviz import generate_diagram
from .output.file_convert import make_yaml
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def run():
    raw_devices = parse_csv("data/input/table.csv")
    # print(raw_devices)
    topology = convert_raw_topology(raw_devices)
    # print(topology)

    generate_diagram(topology, "data/output/diagram.png")
    make_yaml(topology, "data/output/topology.yaml")


if __name__ == "__main__":
    run()
