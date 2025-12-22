# export_yaml.py
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from parse import parse_csv_topology


def _nonempty(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, str) and not v.strip():
        return False
    return True


def _mask_to_prefix(mask: Optional[str]) -> str:
    """
    Маска в CSV может быть '/24' или '24' или None.
    Для записи ip/prefix нужно вернуть '24' (без слэша) либо ''.
    """
    if not mask:
        return ""
    m = str(mask).strip()
    if not m:
        return ""
    return m[1:] if m.startswith("/") else m


def _ip_with_prefix(device_ip: str, mask: Optional[str]) -> str:
    ip = (device_ip or "").strip()
    if not ip:
        return ""
    pfx = _mask_to_prefix(mask)
    return f"{ip}/{pfx}" if pfx else ip


def _role_from_raw(
    devices_raw: Dict[str, Dict[str, Any]], device_name: str, fallback: str
) -> str:
    raw = devices_raw.get(device_name, {})
    role = str(raw.get("role", "") or "").strip().lower()
    return role if role else fallback


def _network_vlan_value(
    result_devices_raw: Dict[str, Dict[str, Any]], net_name: str
) -> Optional[Union[int, str]]:
    """
    VLAN — свойство сети. Берём:
      1) если у Network-объекта есть vlan_id — используем int (обрабатывается выше)
      2) иначе пытаемся найти vlan_raw (строковый VLAN, например 'trunk') в devices_raw
    """
    found_vlan_raw: Optional[str] = None
    for d in result_devices_raw.values():
        for iface in d.get("interfaces", []):
            nf = iface.get("network") or {}
            if nf.get("name") == net_name and _nonempty(nf.get("vlan_raw")):
                found_vlan_raw = str(nf.get("vlan_raw")).strip()
                break
        if found_vlan_raw:
            break
    return found_vlan_raw if _nonempty(found_vlan_raw) else None


# --- YAML dump (PyYAML preferred, fallback if not installed) ---
def _dump_yaml_fallback(obj: Any, indent: int = 0) -> str:
    sp = "  " * indent

    if obj is None:
        return "null"
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, (int, float)):
        return str(obj)
    if isinstance(obj, str):
        s = obj
        if (
            s == ""
            or s.strip() != s
            or any(c in s for c in [":", "#", "{", "}", "[", "]"])
        ):
            return f'"{s.replace(chr(34), r"\"")}"'
        return s

    if isinstance(obj, list):
        if not obj:
            return "[]"
        lines: List[str] = []
        for item in obj:
            val = _dump_yaml_fallback(item, indent + 1)
            if "\n" in val:
                first, *rest = val.splitlines()
                lines.append(f"{sp}- {first}")
                for r in rest:
                    lines.append(f"{'  ' * (indent + 1)}{r}")
            else:
                lines.append(f"{sp}- {val}")
        return "\n".join(lines)

    if isinstance(obj, dict):
        if not obj:
            return "{}"
        lines: List[str] = []
        for k, v in obj.items():
            key = str(k)
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{sp}{key}:")
                lines.append(_dump_yaml_fallback(v, indent + 1))
            else:
                lines.append(f"{sp}{key}: {_dump_yaml_fallback(v, indent + 1)}")
        return "\n".join(lines)

    return _dump_yaml_fallback(str(obj), indent)


def dump_yaml(obj: Any) -> str:
    try:
        import yaml  # type: ignore

        return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)
    except Exception:
        return _dump_yaml_fallback(obj) + "\n"


def build_yaml_document(csv_path: Union[str, Path]) -> Dict[str, Any]:
    csv_path = Path(csv_path)
    result = parse_csv_topology(csv_path)

    doc: Dict[str, Any] = {
        "links": [],
        "networks": [],
        "meta": {"id": csv_path.name, "name": csv_path.name},
        "nodes": [],
    }

    # -----------------
    # NETWORKS (только тут: vlan, network_ip, mask)
    # -----------------
    networks_block: List[Dict[str, Any]] = []
    for net_name in sorted(result.network_interfaces.keys()):
        members = [
            f"{dev}.{iface}" for dev, iface in result.network_interfaces[net_name]
        ]

        net_entry: Dict[str, Any] = {"members": members}

        net_obj = result.networks.get(net_name)
        if net_obj is not None:
            # network_ip, mask
            if _nonempty(net_obj.ip):
                net_entry["network_ip"] = net_obj.ip
            if _nonempty(net_obj.subnet_mask):
                net_entry["mask"] = net_obj.subnet_mask

            # vlan (int)
            if _nonempty(net_obj.vlan_id):
                net_entry["vlan"] = net_obj.vlan_id

        # vlan (string), если vlan_id отсутствует, но в raw есть vlan_raw
        if "vlan" not in net_entry:
            vlan_raw = _network_vlan_value(result.devices_raw, net_name)
            if _nonempty(vlan_raw):
                net_entry["vlan"] = vlan_raw

        networks_block.append({net_name: net_entry})

    doc["networks"] = networks_block

    # -----------------
    # NODES (интерфейсы: без vlan/network_ip/mask)
    # -----------------
    nodes_block: List[Dict[str, Any]] = []
    for dev_name in sorted(result.devices.keys()):
        device = result.devices[dev_name]
        role_fallback = type(device).__name__.lower()
        role = _role_from_raw(result.devices_raw, dev_name, role_fallback)

        node: Dict[str, Any] = {
            "role": role,
            "name": device.name,
            "interfaces": [],
        }

        for iface in device.interfaces:
            iface_items: List[Dict[str, Any]] = []

            network_name = iface.network.name if iface.network else None
            mask = iface.network.subnet_mask if iface.network else None

            # Если есть IP-адреса — пишем ip/prefix + default_gateway + network (+ mode при наличии)
            if iface.ips:
                for ip_obj in iface.ips:
                    entry: Dict[str, Any] = {}

                    ip_comp = _ip_with_prefix(ip_obj.ip_str, mask)
                    if _nonempty(ip_comp):
                        entry["ip"] = ip_comp

                    if _nonempty(network_name):
                        entry["network"] = network_name

                    dg = getattr(ip_obj, "default_gateway", None)
                    if _nonempty(dg):
                        entry["default_gateway"] = dg

                    if _nonempty(iface.mode):
                        entry["mode"] = iface.mode

                    # добавляем только если есть хоть что-то
                    if entry:
                        iface_items.append(entry)

            else:
                # Нет IP — оставим network/mode (например для switch портов)
                entry: Dict[str, Any] = {}
                if _nonempty(network_name):
                    entry["network"] = network_name
                if _nonempty(iface.mode):
                    entry["mode"] = iface.mode
                if entry:
                    iface_items.append(entry)

            node["interfaces"].append({iface.name: iface_items})

        nodes_block.append(node)

    doc["nodes"] = nodes_block
    return doc


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Export topology parsed from CSV to YAML (network props only under networks)"
    )
    ap.add_argument("csv", help="Path to input CSV")
    ap.add_argument("-o", "--out", help="Path to output YAML (default: <csv>.yaml)")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    out_path = Path(args.out) if args.out else csv_path.with_suffix(".yaml")

    doc = build_yaml_document(csv_path)
    out_path.write_text(dump_yaml(doc), encoding="utf-8")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
