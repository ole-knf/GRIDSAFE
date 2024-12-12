import argparse
import asyncio
import os

from termcolor import colored

import phases


def parse_metric_choice(arg):
    """
    Parse parameter choice for metrics to list

    :param str arg: parameter string of metrics
    :return: metrics as list of strings
    :rtype: list
    """

    if arg == "":
        return []
    if arg == "all":
        return [
            "accuracy",
            "precision",
            "inverse_precision",
            "recall",
            "inverse_recall",
            "fallout",
            "missrate",
            "detection_rate",
            "f_score",
        ]
    return arg.split(",")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="Auto-IDS-Eval", description="Framework for comparing IDS capabilities"
    )

    parser.add_argument(
        "-n", "--name", type=str, default="dev", help="Name of the project folder"
    )
    parser.add_argument(
        "-t",
        "--time",
        type=int,
        default=60,
        help="Idle time before and after attack stage to capture IDS behavior",
    )
    parser.add_argument(
        "-p",
        "--phases",
        type=str,
        default="all",
        choices=["all", "attack", "eval"],
        help="The stages to be executed",
    )
    parser.add_argument(
        "-m",
        "--metrics",
        type=str,
        help="Metrics which will be visualized in the evaluation. Choose 'all' for all available ones",
        default="",
    )
    parser.add_argument(
        "-l", "--list", action="store_true", help="Return list of supported metrics"
    )
    parser.add_argument(
        "-v",
        "--visualize",
        action="store_true",
        help="Enable visualization of metrics in form of a time view and radar chart",
    )
    parser.add_argument(
        "-i", "--ids", type=str, default="stationguard", help="Which IDS is utilized"
    )

    # parse all args necessary for phases
    args = parser.parse_args()
    metrics = parse_metric_choice(args.metrics)

    # define path of this tool
    path = os.path.dirname(os.path.realpath(__file__))
    if args.list:
        print(
            "Possible choices: ['accuracy', 'precision', 'inverse_precision', 'recall', 'inverse-recall', 'fallout', 'missrate', 'detection_rate', 'f_score']"
        )
        quit()

    # Only execute specified phases
    if args.phases in {"all", "attack"}:
        asyncio.run(
            phases.attack_phase(
                project_name=args.name,
                idle_before_after_attacks=args.time,
                path=path,
                ids=args.ids,
            )
        )
        print(colored("Attack phase finished", "yellow"))
    if args.phases in {"all", "eval"}:
        phases.evaluation_phase(
            project_name=args.name,
            idle_before_after_attacks=args.time,
            metrics_list=metrics,
            visualize=args.visualize,
            path=path,
            ids=args.ids,
        )
        print(colored("Evaluation phase finished", "yellow"))

    print(colored("Quitting...", "yellow"))
    quit()
