import yaml

from ..domain.models import Topology

"""
Example:
links:
networks:
    - A: [PC1.eth0, PC2.eth0]
meta:
  id: host-host.csv
  name: host-host.csv
nodes:
- role: host
  name: PC1
  interfaces:
  - eth0:
      - ip: 10.0.12.1/24
        network: A
- role: host
  name: PC2
  interfaces:
    - eth0:
      - ip: 10.0.12.2/24
        network: A
"""


def make_yaml(topology: Topology, output_path: str) -> None:
    pass
