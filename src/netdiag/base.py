import logging
from pathlib import Path

from .args import parse_args
from .output.d2 import generate_d2_diagram
from .output.file_convert import make_yaml
from .output.graphviz import generate_diagram
from .parse import parse_csv
from .parse.convert_raw import (
    convert_raw_topology,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def run(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    raw_devices = parse_csv(Path(args.input))
    topology = convert_raw_topology(raw_devices)

    generate_diagram(topology, Path(args.output) / "diagram.png")
    make_yaml(topology, Path(args.output) / "topology.yaml")
    # generate_d2_diagram(topology, Path(args.output) / "diagram.d2")

    logging.info("All tasks completed successfully.")


if __name__ == "__main__":
    run()
