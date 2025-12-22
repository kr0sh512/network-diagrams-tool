# parse.py
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from structures import Device, Host, Router, Switch, Network, Interface


# ===========================
# CSV -> canonical fields
# ===========================
COLUMN_MAP: Dict[str, str] = {
    "Name": "device_name",
    "Role": "role",
    "Interface": "interface_name",
    "Network": "network_name",
    "VLAN": "vlan",
    "Network IP": "network_ip",
    "Mask": "mask",
    "Device IP": "device_ip",
    "Default Gateway": "default_gateway",
}

ROLE_MAP = {
    "host": Host,
    "switch": Switch,
    "router": Router,
}


def _clean(v: Any) -> str:
    return str(v).strip() if v is not None else ""


def _to_int(v: str) -> Optional[int]:
    v = _clean(v)
    if v.isdigit():
        return int(v)
    return None


def _gateway_or_none(v: str) -> Optional[str]:
    v = _clean(v)
    if not v or v == "0.0.0.0":
        return None
    return v


def _infer_mode(network_name: str, vlan: str) -> str:
    """
    Принятое допущение под ваш пример:
    - если VLAN == 'trunk' или Network == 'tr'/'trunk' => mode='trunk'
    - иначе => mode='access'
    """
    n = _clean(network_name).lower()
    v = _clean(vlan).lower()
    if v == "trunk" or n in {"tr", "trunk"}:
        return "trunk"
    return "access"


@dataclass
class ParseResult:
    # словарь, пригодный для сериализации/отладки и последующего создания структур
    devices_raw: Dict[str, Dict[str, Any]]
    # готовые python-объекты ваших классов Host/Switch/Router
    devices: Dict[str, Device]
    # агрегированные сети (по имени сети)
    networks: Dict[str, Network]
    # Network -> список (device_name, interface_name)
    network_interfaces: Dict[str, List[Tuple[str, str]]]


def parse_csv_topology(path: Union[str, Path], encoding: str = "utf-8") -> ParseResult:
    path = Path(path)

    devices_raw: Dict[str, Dict[str, Any]] = {}
    network_interfaces: Dict[str, List[Tuple[str, str]]] = {}
    network_agg: Dict[str, Dict[str, Any]] = {}

    with path.open(newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV is empty or has no header row")

        for row in reader:
            # 1) rename columns -> canonical keys
            canon: Dict[str, str] = {}
            for k, v in row.items():
                kk = COLUMN_MAP.get(
                    k, k
                )  # если встретили неизвестную колонку — оставим как есть
                canon[kk] = _clean(v)

            device_name = canon.get("device_name", "")
            role = canon.get("role", "")
            iface_name = canon.get("interface_name", "")
            network_name = canon.get("network_name", "")
            vlan_raw = canon.get("vlan", "")
            net_ip = canon.get("network_ip", "")
            mask = canon.get("mask", "")
            dev_ip = canon.get("device_ip", "")
            gw = canon.get("default_gateway", "")

            if not device_name:
                continue

            # 2) init device record
            dev_rec = devices_raw.setdefault(
                device_name,
                {"name": device_name, "role": role, "interfaces": []},
            )

            # если роль у устройства не была проставлена ранее, но появилась сейчас — заполним
            if role and not dev_rec.get("role"):
                dev_rec["role"] = role

            # если интерфейс не указан — дальше нечего собирать
            if not iface_name:
                continue

            mode = _infer_mode(network_name, vlan_raw)

            # 3) network fields (для интерфейса) + агрегирование сетей
            network_fields: Optional[Dict[str, Any]] = None

            if network_name:
                vlan_id = _to_int(vlan_raw)  # trunk -> None
                network_fields = {
                    "name": network_name,
                    "vlan_id": vlan_id,  # для структур (Network берёт vlan_id)
                    "vlan_raw": vlan_raw or None,  # для YAML/отладки (как в CSV)
                    "ip": net_ip or None,  # Network IP
                    "mask": mask or None,  # Mask
                }

                # агрегируем сеть: берём первое непустое значение
                agg = network_agg.setdefault(network_name, {"name": network_name})
                if vlan_id is not None and agg.get("vlan_id") is None:
                    agg["vlan_id"] = vlan_id
                if vlan_raw and not agg.get("vlan_raw"):
                    agg["vlan_raw"] = vlan_raw
                if net_ip and not agg.get("ip"):
                    agg["ip"] = net_ip
                if mask and not agg.get("mask"):
                    agg["mask"] = mask

                network_interfaces.setdefault(network_name, []).append(
                    (device_name, iface_name)
                )

            # 5) ips list
            ips: List[Interface.IP] = []
            if dev_ip:
                ips.append(
                    Interface.IP(ip_str=dev_ip, default_gateway=_gateway_or_none(gw))
                )

            iface_fields: Dict[str, Any] = {
                "name": iface_name,
                "mode": mode,
                "network": network_fields,
                "ips": ips,
            }

            dev_rec["interfaces"].append(iface_fields)

    # 6) Instantiate Network objects
    networks: Dict[str, Network] = {}
    for n_name, fields in network_agg.items():
        # Network.__init__ у вас принимает dict-like "fields"
        networks[n_name] = Network(fields)

    # 7) Instantiate Device objects (Host/Switch/Router)
    devices: Dict[str, Device] = {}
    for d_name, fields in devices_raw.items():
        role = _clean(fields.get("role", "")).lower()
        cls = ROLE_MAP.get(
            role, Device
        )  # если роль неизвестна — создадим базовый Device
        devices[d_name] = cls(fields)

    return ParseResult(
        devices_raw=devices_raw,
        devices=devices,
        networks=networks,
        network_interfaces=network_interfaces,
    )


if __name__ == "__main__":
    result = parse_csv_topology("table.csv")

    print("=== devices_raw (dict for debugging/serialization) ===")
    for k, v in result.devices_raw.items():
        print(k, "=>", v)

    print("\n=== networks (Network objects) ===")
    for k, v in result.networks.items():
        print(k, "=>", v)

    print("\n=== network_interfaces (Network -> [(device, iface), ...]) ===")
    for net, items in result.network_interfaces.items():
        print(net, "=>", items)

    print("\n=== devices (Device objects) ===")
    for k, v in result.devices.items():
        print(k, "=>", v)
