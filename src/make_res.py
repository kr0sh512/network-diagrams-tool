from check_correct import check_correct
from parse import parse_csv_to_structure
import sys
from structures import Host, Wire, Interface
import yaml


"""
meta:
  id: "lab-02-basic-utils"
  name: "Basic Network Utilities & Traffic Monitoring"
  description: "Two hosts connected directly to each other."

links:
  - endpoints: ["PC1", "PC2"]

nodes:
  - name: PC1
    role: host
    interfaces:
      - ip: "10.0.12.1/24"

  - name: PC2
    role: host
    interfaces:
      - ip: "10.0.12.2/24"
"""


def make_res(data, name):
    res = {
        "meta": {
            "id": name,
            "name": name,
        },
        "links": [],
        "nodes": [],
    }

    host_int = {}

    for key, value in data.items():
        if value.get("type") == "host":
            value["name"] = key
            host = Host(value)
            node_entry = {
                "name": host.name,
                "role": "host",
                "interfaces": [
                    {"ip": Interface(data[iface]).ip_address}
                    for iface in host.interfaces
                ],
            }
            res["nodes"].append(node_entry)

            host_int[host.interfaces[0]] = host.name

    for key, value in data.items():
        if value.get("type") == "wire":
            wire = Wire(value)
            link_entry = {
                "endpoints": [
                    host_int[wire.endpoints[0]],
                    host_int[wire.endpoints[1]],
                ]
            }
            res["links"].append(link_entry)

    return res


if __name__ == "__main__":
    data = parse_csv_to_structure(sys.argv[1])
    print(data)
    if check_correct(data):
        print("Data is correct.")
    res = make_res(data, sys.argv[1])
    print(res)

    with open("output.yaml", "w") as f:
        yaml.dump(res, f)
