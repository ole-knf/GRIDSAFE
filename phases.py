import asyncio
import datetime
import json
import os
import subprocess
import sys
import time

from termcolor import colored

from attacks.attack import Attack
from attacks.scenarios.control_freeze_chain import Control_Freeze_Attackchain
from attacks.scenarios.disrupt_communication import Disrupt_Communication_Attackchain
from attacks.scenarios.industroyer_chain import Industroyer_Attackchain
from attacks.scenarios.manipulate_grid import Manipulate_Grid_Attackchain
from attacks.scenarios.recon import Recon_Attackchain
from attacks.scenarios.test.iec104_test import IEC104_Test
from attacks.scenarios.test.integration import IntegrationValidation
from attacks.scenarios.voltage_drift_off_chain import Voltage_Drift_Off_Attackchain
from metrics.metrics import Metrics
from metrics.metrics_preprocessor import MetricsPreprocessor
from metrics.visualizer import Visualizer
from observer.alert_observer import AlertObserver
from observer.attack_observer import AttackObserver
from observer.grid_observer import GridObserver


async def attack_phase(
    project_name: str, idle_before_after_attacks: int, path: str, ids: str
):
    """
    Executes the attack phase and records all data

    :param str project_name: Name of the directory in the /data folder
    :param int idle_before_after_attacks: Idle time before the first attack starts
    :param str path: Path of the /data folder
    :param str ids: Name of the IDS in use to adjust the alerts collection NOT ACTUALLY IN USE
    """

    # storage for the attack objects, so we can reuse the same attacks if so desired
    attack_list: list[Attack] = []
    # order in which the attack objects should be executed
    attack_queue: list[Attack] = []
    # Init observer for IDS with SIEM support (such as StationGuard) for a IP and port.
    # If there are no alerts, nothing will happen
    alert_observer = AlertObserver(
        udp_ip="172.16.10.2", udp_port=514, project_name=project_name
    )
    # Init observer, which collects and oders data from individual attacks
    attack_observer = AttackObserver(project_name=project_name)
    # Init observer, which collects data from wattson
    grid_observer = GridObserver(project_name=project_name)

    # Start the IDS and grid data collection
    alert_observe_task = asyncio.create_task(alert_observer.start())
    grid_observer.start()
    print(colored("Observer started", "green"))

    # Init path for collected data
    project_path = f"{path}/data/{project_name}/"

    # Load attacks based on project_name.
    # For automation purposes, we load from predefined scenarios
    # For other purposes: Import individual attacks
    attack_scenario: Attack
    print(f"loading attacks for scenario {project_name}")

    if "integration-validation" in project_name:
        attack_scenario = IntegrationValidation(
            project_name=project_name, project_path=project_path
        )
    elif "iec104-test" in project_name:
        attack_scenario = IEC104_Test(
            project_name=project_name, project_path=project_path
        )
    elif "recon-attackchain" in project_name:
        attack_scenario = Recon_Attackchain(
            project_name=project_name, project_path=project_path
        )
    elif "disrupt-communication-attackchain" in project_name:
        attack_scenario = Disrupt_Communication_Attackchain(
            project_name=project_name, project_path=project_path
        )
    elif "manipulate-grid-attackchain" in project_name:
        attack_scenario = Manipulate_Grid_Attackchain(
            project_name=project_name, project_path=project_path
        )
    elif "industroyer-attackchain" in project_name:
        attack_scenario = Industroyer_Attackchain(
            project_name=project_name, project_path=project_path
        )
    elif "control-freeze-attackchain" in project_name:
        attack_scenario = Control_Freeze_Attackchain(
            project_name=project_name, project_path=project_path
        )
    elif "voltage-drift-off-attackchain" in project_name:
        attack_scenario = Voltage_Drift_Off_Attackchain(
            project_name=project_name, project_path=project_path
        )
    else:
        # Remove this, if you import new and custom scenarios
        print("bad project name: no attack scenario found")
        quit()

    # Load attacks from scenarios as a list and add them to the attack queue
    attack_list = attack_scenario.get_attack_list()
    attack_queue = attack_list

    # Give a rough time estimate, which might not be accurate for every attack
    duration = 0
    duration += idle_before_after_attacks * 2

    for attack in attack_queue:
        duration += attack.attack_duration
        duration += attack.pause_duration

    print(
        colored(
            f"The execution will take {str(datetime.timedelta(seconds=duration))}",
            "red",
        )
    )

    # Let the observers run for a while before attacks starts, based on the intial idle time
    # This lets us identify false positives
    await asyncio.sleep(idle_before_after_attacks)

    # Init a counter to gather data from individual attacks
    attack_counter = -1
    # Execute attacks for each attack in the queue
    for attack in attack_queue:

        attack_counter += 1
        print(colored(f"Starting execution of attack {attack.attack_type}", "green"))

        # Compute the time it takes for the attack to execute
        start_time = time.time()
        status = attack.execute(attack_counter)
        elapsed_time = time.time() - start_time
        remaining_time = attack.attack_duration - elapsed_time

        if status:
            print(
                colored(f"Attack {attack.attack_type} successfully executed", "green")
            )
        else:
            print(
                colored(
                    f"ERROR: Attack {attack.attack_type} could not be executed", "red"
                )
            )

        # If the attack finishes quickly (such as for a port scan), idle for the remaining duration
        if remaining_time > 0:
            await asyncio.sleep(remaining_time)

        # Undo the attack
        # oftentimes a dummy line, since most network attacks forcefully end after the execution time
        status = attack.restore(attack_counter)
        if status:
            print(
                colored(f"Restore {attack.attack_type} successfully executed", "green")
            )
        else:
            print(
                colored(
                    f"ERROR: {attack.attack_type} Restore could not be executed", "red"
                )
            )

        # Let the IDS react to the attack, if so desired
        await asyncio.sleep(attack.pause_duration)

    print(colored("All attacks finished", "green"))

    # Sleep for the remaining idle time after all attacks are finished
    await asyncio.sleep(idle_before_after_attacks)

    # Stop the IDS data collection
    await alert_observer.stop()
    grid_observer.stop()
    print(colored("Observer stopped", "green"))

    # Close the observer cleanly
    await alert_observe_task

    # Save data from live observers
    alert_observer.save()
    grid_observer.save()

    # Safe attack data for each attack objects in the list
    attack_observer.digest(attack_list)
    attack_observer.save()


def evaluation_phase(
    project_name: str,
    idle_before_after_attacks: int,
    metrics_list: list[str],
    visualize: bool,
    path: str,
    ids: str,
):
    """
    Executes the evaluation phase and computes the evaluation results

    :param str project_name: Name of the directory in the /data folder
    :param int idle_before_after_attacks: Idle time before the first attack starts
    :param list[str] metrics_list: Metrics which the framework should compute
    :param bool visualize: Enable visual output of the framework in form of a time-based view of the evaluation and radar chart of metrics
    :param str path: Path of the /data folder
    :param str ids: Name of the IDS in use to adjust data parsing
    """

    # Init the proprocessor
    metrics_preprocessor = MetricsPreprocessor(
        project_name=project_name, padding=idle_before_after_attacks, ids=ids
    )
    # Load data from files the attack phase created
    metrics_preprocessor.load_data()

    # Compute metrics
    metrics = Metrics(metrics_preprocessor=metrics_preprocessor)

    # Init the visualization
    visualizer = Visualizer(metrics=metrics)

    # If so desired, compute a timeview
    if visualize:
        visualizer.create_timeview()

    # Gather entries of the confusion metrics and save them in the project folder
    confusion_matrix: dict[str, int] = {}
    confusion_matrix["TP"] = metrics.true_positives
    confusion_matrix["FP"] = metrics.false_positives
    confusion_matrix["TN"] = metrics.true_negatives
    confusion_matrix["FN"] = metrics.false_negatives

    filename = f"{path}/data/{project_name}/confusion-matrix.jsonl"

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(confusion_matrix, f)
        f.write("\n")

    # Based on the paramter choice, load all metrics for representation
    metrics_to_present: dict[str, float] = {}

    for metric in metrics_list:
        if metric in dir(metrics):
            value = getattr(metrics, metric)()
            metrics_to_present[metric] = value

    # save metrics in file as json
    filename = f"{path}/data/{project_name}/metrics.jsonl"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(metrics_to_present, f)
        f.write("\n")

    # only generate radar chart if its desired and there are 3 or more metrics to represent
    if visualize and (len(metrics_to_present) >= 3):
        visualizer.create_radar_chart(metrics_to_present)

    # Print confusion matrix entries to console
    print(
        colored(
            f"TP:{metrics_preprocessor.true_positives}, TN:{metrics_preprocessor.true_negatives}, FP:{metrics_preprocessor.false_positives}, FN:{metrics_preprocessor.false_negatives}",
            "cyan",
        )
    )

    # Print computed metrics to console
    for entry in metrics_to_present:
        print(colored(f"{entry}: {round(metrics_to_present[entry], 3)}", "cyan"))

    # Compute all evaluation data again, but for eevry attack
    # Get timeintervals for each attack
    time_intervals = metrics_preprocessor.time_intervals
    start_interval = None
    interval_list = []
    for interval in time_intervals:
        if start_interval == None and time_intervals[interval]["attack"]:
            start_interval = interval
        if start_interval != None and not time_intervals[interval]["attack"]:
            interval_list.append([start_interval, interval])
            start_interval = None

    # Generate metrics for each attack and save them
    for i in range(len(interval_list)):
        working_metrics_preprocessor = MetricsPreprocessor(
            project_name=project_name, padding=idle_before_after_attacks, ids=ids
        )
        working_metrics_preprocessor.load_data()
        working_metrics_preprocessor.time_intervals = {
            k: v
            for k, v in metrics_preprocessor.time_intervals.items()
            if interval_list[i][0] <= k <= interval_list[i][1]
        }
        working_metrics_preprocessor.update_tp_tn_fp_fn()
        metrics = Metrics(metrics_preprocessor=working_metrics_preprocessor)
        visualizer = Visualizer(metrics=metrics)

        confusion_matrix: dict[str, int] = {}
        confusion_matrix["TP"] = metrics.true_positives
        confusion_matrix["FP"] = metrics.false_positives
        confusion_matrix["TN"] = metrics.true_negatives
        confusion_matrix["FN"] = metrics.false_negatives

        filename = f"{path}/data/{project_name}/attack{i}-confusion-matrix.jsonl"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            json.dump(confusion_matrix, f)
            f.write("\n")

        metrics_to_present: dict[str, float] = {}

        for metric in metrics_list:
            if metric in dir(metrics):
                value = getattr(metrics, metric)()
                metrics_to_present[metric] = value

        # save metrics in file as json
        filename = f"{path}/data/{project_name}/attack{i}-metrics.jsonl"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            json.dump(metrics_to_present, f)
            f.write("\n")

        # only generate radar chart with 3 or more metrics
        if visualize and (len(metrics_to_present) >= 3):
            visualizer.create_radar_chart(
                metrics_to_present, filename_prefix=f"attack{i}-"
            )
        print(f"Calculated metrics for attack {i}:")
        print(metrics_to_present)
