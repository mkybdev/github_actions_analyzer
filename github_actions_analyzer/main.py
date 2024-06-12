import argparse
import os

from .clustering import Clustering
from .common import constants, logger
from .cooccurrence import Cooccurrence
from .intersection import Intersection
from .preprocessing import load, preprocess
from .run_all import run_all
from .statistics import Statistics


def main():

    parser = argparse.ArgumentParser(
        description="Analyze GitHub Actions workflow files."
    )
    parser.add_argument(
        "target",
        type=str,
        help="Path to the directory containing workflow files / Name of dumped dataset",
    )
    parser.add_argument(
        "-s", "--sample", type=int, default=-1, help="Number of samples to analyze"
    )
    parser.add_argument(
        "-n", "--name", type=str, default="", help="Name of the dataset to be dumped"
    )
    parser.add_argument(
        "-o",
        "--out",
        type=str,
        default=os.path.join(os.path.expanduser("~"), "Downloads"),
        help="Output directory (default: ~/Downloads)",
    )
    parser.add_argument(
        "-v",
        "--visualize",
        action="store_true",
        help="Whether to visualize the workflow files",
    )
    args = parser.parse_args()

    if os.path.exists(args.out):
        if args.name == "":
            constants.OUTPUT_PATH = os.path.join(args.out, "gaa_output")
        else:
            constants.OUTPUT_PATH = os.path.join(args.out, args.name)
        os.makedirs(constants.OUTPUT_PATH, exist_ok=True)
    else:
        logger.error("Output directory does not exist.")

    rawData = load(args.target, args.sample, args.name, args.out, args.visualize)
    data = preprocess(rawData)

    Statistics(data).run()

    logger.info("\nAll analysis completed.\n")


if __name__ == "__main__":
    main()
