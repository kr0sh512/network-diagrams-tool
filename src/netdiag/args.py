import argparse


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Network Diagrams Tool - Generate network diagrams from CSV input"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default="data/input/table.csv",
        help="Path to the input CSV file (default: data/input/table.csv)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="data/output",
        help="Directory for output files (default: data/output)",
    )
    return parser.parse_args(args=argv)
