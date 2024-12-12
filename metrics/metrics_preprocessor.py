import copy
import json
from os import path

from dateutil.parser import isoparse


class MetricsPreprocessor:
    def __init__(self, project_name: str, padding: int, ids: str) -> None:
        """
        Preprocessor for the evaluation data

        :param str project_name: Name of the directory in the /data folder
        :param int padding: The second from the start and end that should not be part of the results. By default, we use the framework's idle time at the start and end.
        :param str ids: The IDS in use
        """
        self.project_name = project_name
        self.padding = padding
        self.ids = ids
        self.critical_voltage_deviation = (
            0.10  # when is a voltage level deviation considered as dangerous. This value is based on Wattson's values
        )
        self.alerts: list[dict] = [{}]
        self.attacks: list[dict] = [{}]
        self.network_dump: list[float] = []
        self.grid: list[dict] = [{}]
        self.time_intervals: dict[int, dict] = {}
        self.true_positives = -1
        self.true_negatives = -1
        self.false_positives = -1
        self.false_negatives = -1

    def load_data(self):
        """
        Load all data from the project folder
        """
        alert_file = (
            f"/home/wattson/Documents/code/data/{self.project_name}/alerts.jsonl"
        )
        attack_file = (
            f"/home/wattson/Documents/code/data/{self.project_name}/attacks.jsonl"
        )
        grid_file = f"/home/wattson/Documents/code/data/{self.project_name}/grid.jsonl"

        with open(alert_file, "r") as f:
            self.alerts = [json.loads(line) for line in f]

        with open(attack_file, "r") as f:
            self.attacks = [json.loads(line) for line in f]

        # if network dumps exist, use load them for each attack. Everytime a corresponding data dump does not exist, use the general attack info instead
        for attackcount in range(len(self.attacks)):
            strace_file = f"/home/wattson/Documents/code/data/{self.project_name}/{attackcount}networkdump.out"
            log_file = f"/home/wattson/Documents/code/data/{self.project_name}/{attackcount}attack_packets.jsonl"
            if path.exists(strace_file):  # if strace file exists, use it
                with open(strace_file, "r") as f:
                    sockets = []
                    for line in f:
                        # filter for network sockets in use
                        if "socket(AF_INET" in line:
                            split_line = line.split()
                            sockets.append(split_line[-1])
                        # for each socket, check if connections are made. If they are, log the timestamp
                        for socket in sockets:
                            if (
                                f"recvfrom({socket}," in line
                                or f"sendto({socket}," in line
                            ):
                                split_line = line.split()
                                timestamp = float(split_line[1])
                                self.network_dump.append(timestamp)
            elif path.exists(log_file):  # if artifical log file exists, use it instead
                with open(log_file, "r") as f:
                    for line in f:
                        line = json.loads(line)
                        timestamp = float(line["timestamp"])
                        self.network_dump.append(timestamp)
            else:  # if neither exists, use the entry in the attack file
                attack_start = float(self.attacks[attackcount]["start"])
                attack_end = float(self.attacks[attackcount]["end"])
                current_timestamp = attack_start

                while current_timestamp < attack_end:
                    self.network_dump.append(current_timestamp)
                    current_timestamp = current_timestamp + 0.1

                self.network_dump.append(attack_end)

        with open(grid_file, "r") as f:
            self.grid = [json.loads(line) for line in f]

        self.generate_attack_alert_time_list()
        self.update_tp_tn_fp_fn()

    # For point based metrics:
    # Create list of small time intervals and check whether
    # there was an alert within the frame or not

    def __compute_critical_voltage_intervals(self, bus_list: list[int]):
        """
        Based on the wattson data, mark critical grid states

        :param list[int] bus_list: A list of integers, which refer to each bus
        """
        # assumption: voltage is not critical before first measurement
        bus_data_collection = {}
        # For each bus, get all behavior intervals. If they are ciritcal, mark them as such 
        for bus in bus_list:
            bus_data = [
                entry for entry in self.grid if f"bus {bus}" in entry["location"]
            ]
            intervals = []
            current_interval = {"start": None, "end": None}
            under_threshold = False

            for entry in bus_data:
                time = entry["time"]
                voltage = float(entry["value"])

                if voltage < (1 - self.critical_voltage_deviation) or voltage > (
                    1 + self.critical_voltage_deviation
                ):  # if critical
                    if not under_threshold:  # and a the first time in the interval
                        current_interval["start"] = time
                    under_threshold = True
                else:
                    if under_threshold:
                        under_threshold = False
                        current_interval["end"] = time
                        intervals.append(current_interval)

                        current_interval = {"start": None, "end": None}
            if current_interval["end"] == None and current_interval["start"] != None:
                intervals.append(current_interval)

            bus_data_collection[bus] = intervals

        self.grid = bus_data_collection

    def generate_attack_alert_time_list(self):
        """
        Map each data point of IDS alert data, attack information, and malicious network packets onto the data structure
        """
        list_start_time = (
            int((self.attacks[0]["start"]) - self.padding) * 2
        )  # first whole number before attack
        list_end_time = (
            int((self.attacks[-1]["end"]) + self.padding + 1) * 2
        )  # first whole number after attack

        for half_second in range(list_start_time, list_end_time):
            entry = {}
            entry["attack"] = False
            entry["network_activity"] = False
            entry["alert"] = False
            entry["critical_voltage"] = False
            self.time_intervals[half_second] = entry

        # add attacks to the list
        for attack in self.attacks:
            attack_start = int(attack["start"] * 2)
            attack_end = int(attack["end"] * 2) + 1

            for half_second in range(attack_start, attack_end + 1):
                self.time_intervals[half_second]["attack"] = True

        # add attack network packets to the list
        for packet in self.network_dump:
            half_second = int(packet * 2)
            try:
                self.time_intervals[half_second]["network_activity"] = True
            except (
                KeyError
            ):  # can happen if an alert was made before the first idle time started or unremoved entrys of prior attack. Can simple be ignored
                continue

        # add alerts to the list
        # For stationguard, use events with critical severity 
        if self.ids == "stationguard":
            for alert in self.alerts:
                try:
                    if alert["severity"] != "crit":
                        continue

                    alert_time = int(alert["msg"]["start"])
                    # this is in milliseconds unix, so remove last 2 digits
                    # alert_time = int(alert_time / 100) + 1 # +1 is needed, since the vm seems to be 0.1 seconds in the past or atleast before strace
                    alert_time = int(
                        alert_time / 500
                    )
                    self.time_intervals[alert_time]["alert"] = True
                except (
                    KeyError
                ):  # can happen if an alert was made before the first idle time started. Can simple be ignored
                    continue
        # For suricata, load timestamp of every line
        elif self.ids == "suricata":

            for alert in self.alerts:
                try:
                    time = isoparse(alert["timestamp"])
                    alert_time = time.timestamp()
                    alert_time = int(alert_time * 2)

                    self.time_intervals[alert_time]["alert"] = True
                except (
                    KeyError
                ):  # can happen if an alert was made before the first idle time started. Can simple be ignored
                    continue

        # compute for 15 busses, 0-14
        self.__compute_critical_voltage_intervals(
            range(15)
        )  

        # For each critical interval, add it to the global data structure
        for bus in self.grid:
            for critical_interval in self.grid[bus]:
                interval_start = int(critical_interval["start"]) * 2
                # if the interval didnt end, e.g. has None as the end, ensure it is still processed
                if critical_interval["end"] == None:
                    interval_end = list_end_time 
                else:
                    interval_end = int(critical_interval["end"]) * 2 + 1

                for second in range(interval_start, interval_end + 1):
                    try:
                        self.time_intervals[second]["critical_voltage"] = True
                    except (
                        KeyError
                    ):  # can happen if an critical voltage was induced before the first idle time started. Can simple be ignored
                        continue

    def update_tp_tn_fp_fn(self):
        """
        Compute entries of the confusion matrix
        """
        count_tp = 0
        count_tn = 0
        count_fp = 0
        count_fn = 0

        # copy time_intervals sicne we need to modify it for this calculation
        time_intervals = copy.deepcopy(self.time_intervals)

        for interval in time_intervals:
            # did an alert happen in the next 2 intervals including this one (in the next 1 second)?
            # if that is the case, identify it and remove the alert for the next instances

            attack = False
            alert = False

            if time_intervals[interval]["alert"]:
                alert = True
                alert_interval = interval

            for i in range(2): 
                try:
                    if time_intervals[interval - i]["network_activity"]:
                        attack = True
                        attack_interval = interval - i
                        time_intervals[alert_interval]["alert"] = False
                        break
                finally:
                    continue

            if attack and alert:
                count_tp += 1
            elif not attack and not alert:
                count_tn += 1
            elif not attack and alert:
                count_fp += 1
            else:
                count_fn += 1

        # add the values to the global scope
        self.true_positives = count_tp
        self.true_negatives = count_tn
        self.false_positives = count_fp
        self.false_negatives = count_fn
