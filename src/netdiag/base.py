from .parse import parse_csv
from .domain.models import Topology
from .parse.convert_raw import (
    convert_raw_topology,
)
import logging

# from .make_res import make_result
# from .structures import Result

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def run():
    raw_devices = parse_csv("data/input/table.csv")
    # print(raw_devices)
    topology = convert_raw_topology(raw_devices)
    print(topology)

    # 2) make structured result
    # result = make_result(devices_raw, network_agg, network_interfaces)

    # # 3) output (for debug)
    # print(result)


if __name__ == "__main__":
    run()
