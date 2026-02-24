import shutil
import subprocess
from pathlib import Path

from ..domain.models import Topology

#! WIP

"""
D2 example:

com_left; com_right

VLAN 2: {
  PC2: |md
    # PC2
    10.0.0.2/24
  |
  PC2.shape: rectangle
}

VLAN 3: {
  PC3: |md
    # PC3
    10.0.0.3/24
  |
  PC3.shape: rectangle
}

VLAN 4: {
  PC1: |md
    # PC1
    10.0.0.1/24
  |
  PC1.shape: rectangle
  PC4: |md
    # PC4
    10.0.0.4/24
  |
  PC4.shape: rectangle
}

com_left -- com_right : {
  source-arrowhead.label: eth1
  target-arrowhead.label: eth1
}

VLAN 2.PC2 -- com_left : {
  source-arrowhead.label: eth1
  target-arrowhead.label: eth3
}
VLAN 4.PC1 -- com_left : {
  source-arrowhead.label: eth1
  target-arrowhead.label: eth2
}
VLAN 4.PC4 -- com_right : {
  source-arrowhead.label: eth1
  target-arrowhead.label: eth2
}
VLAN 3.PC3 -- com_right : {
  source-arrowhead.label: eth1
  target-arrowhead.label: eth3
}

"""

# https://d2lang.com/tour/themes/
THEME_NUMBER = 200

# https://icons.terrastruct.com/
icons = {
    "router": "https://icons.terrastruct.com/tech%2Frouter.svg",
    "host": "https://icons.terrastruct.com/tech%2F065-monitor-4.svg",
    "switch": "https://icons.terrastruct.com/tech%2Fswitch.svg",
    "device": "https://icons.terrastruct.com/azure%2FCompute%20Service%20Color%2FVM%2FVM-non-azure.svg",
    "vlan": "https://icons.terrastruct.com/azure%2FNetworking%20Service%20Color%2FVirtual%20Networks.svg",
}


def _check_d2_installed() -> bool:
    return shutil.which("d2") is not None


def generate_d2_diagram(topology: Topology, output_path: Path) -> None:
    if not _check_d2_installed():
        raise EnvironmentError(
            "D2 is not installed or 'd2' command is not found in PATH. Please install D2 to use this feature."
        )

    diagram_path = Path()
    picture_path = Path()

    if output_path.is_dir():
        diagram_path = output_path / "diagram.d2"
        picture_path = output_path / "diagram.png"
    else:
        diagram_path = output_path.with_suffix(".d2")
        picture_path = output_path.with_suffix(".png")

    file: list[str] = []

    # some logic

    # ---

    with open(diagram_path, "w", encoding="utf-8") as f:
        f.write("\n".join(file))

    _generate_picture(diagram_path, picture_path)


def _generate_picture(diagram: Path, output_path: Path) -> None:
    res = subprocess.run(
        ["d2", "validate", str(diagram)],
        check=True,
        capture_output=True,
    )

    if res.returncode != 0:
        raise RuntimeError(
            f"D2 validation failed (code {res.returncode})\n"
            f"Stdout: {res.stdout.decode()}\n"
            f"Stderr: {res.stderr.decode()}"
        )

    res = subprocess.run(
        ["d2", f"--theme={THEME_NUMBER}", str(diagram), str(output_path)],
        check=True,
        capture_output=True,
    )

    if res.returncode != 0:
        raise RuntimeError(
            f"D2 diagram generation failed (code {res.returncode})\n"
            f"Stdout: {res.stdout.decode()}\n"
            f"Stderr: {res.stderr.decode()}"
        )
