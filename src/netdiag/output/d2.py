import shutil
import subprocess

from ..domain.models import Topology
from pathlib import Path
from py_d2 import D2Diagram, D2Shape, D2Connection
from py_d2.shape import Shape
from py_d2.connection import Direction

# https://d2lang.com/tour/themes/
THEME_NUMBER = 200


def _check_d2_installed() -> bool:
    return shutil.which("d2") is not None


def _check_magick_installed() -> bool:
    return shutil.which("magick") is not None


def generate_d2_diagram(topology: Topology, output_path: Path) -> None:
    shapes = []
    connections = []

    for device in topology.devices.values():
        for interface in device.interfaces.values():
            if interface.itype != "physical":
                continue  # Skip virtual interfaces for now

            shape = D2Shape(
                name=f"{device.name}.{interface.adapter}",
                shape=Shape("parallelogram"),
            )
            shapes.append(shape)

            if interface.network:
                network_shape = D2Shape(
                    name=interface.network,
                    shape=Shape("cloud"),
                )
                shapes.append(network_shape)

                connection = D2Connection(
                    shape_1=f"{device.name}.{interface.adapter}",
                    shape_2=interface.network,
                    direction=Direction("--"),
                )
                connections.append(connection)

    diagram = D2Diagram(shapes=shapes, connections=connections)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(diagram))

    _generate_picture(
        output_path, output_path.with_suffix(".png")
    )  # output_path not used

    _run_magick_command(
        output_path.with_suffix(".svg"), output_path.with_suffix(".png")
    )


def _run_magick_command(input_path: Path, output_path: Path) -> None:
    if not _check_magick_installed():
        raise EnvironmentError(
            "ImageMagick is not installed or 'magick' command is not found in PATH. Please install ImageMagick to use this feature."
        )

    res = subprocess.run(
        ["magick", "convert", str(input_path), str(output_path)],
        check=True,
        capture_output=True,
    )

    if res.returncode != 0:
        raise RuntimeError(
            f"Image conversion failed (code {res.returncode})\n"
            f"Stdout: {res.stdout.decode()}\n"
            f"Stderr: {res.stderr.decode()}"
        )


def _generate_picture(diagram: Path, output_path: Path) -> None:
    if not _check_d2_installed():
        raise EnvironmentError(
            "D2 is not installed or 'd2' command is not found in PATH. Please install D2 to use this feature."
        )

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
        ["d2", str(diagram)],
        check=True,
        capture_output=True,
    )

    if res.returncode != 0:
        raise RuntimeError(
            f"D2 diagram generation failed (code {res.returncode})\n"
            f"Stdout: {res.stdout.decode()}\n"
            f"Stderr: {res.stderr.decode()}"
        )
