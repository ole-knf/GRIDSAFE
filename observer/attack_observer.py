import json
import operator
import os

from attacks.attack import Attack


class AttackObserver:
    def __init__(self, project_name: str):
        """
        Extract execution data of each attack the framework executes 

        :param str project_name: Name of the directory in the /data folder
        """
        self.project_name = project_name
        self.datafile: list[dict] = []

    def digest(self, attack_object_list: list[Attack]):
        """
        Extract information from the attack objects

        :param list[Attack] attack_object_list: List of attacks to evaluate
        """
        for attack_object in attack_object_list:
            for index in range(len(attack_object.timecodes_start)):
                entry = {}
                entry["attack_type"] = attack_object.attack_type
                entry["target"] = attack_object.target
                entry["start"] = attack_object.timecodes_start[index]
                entry["end"] = attack_object.timecodes_end[index]
                self.datafile.append(entry)

    def save(self):
        """
        Save the extracted data to a file
        """
        # Sort attacks chronologically
        self.datafile.sort(key=operator.itemgetter("start"))

        filename = (
            f"/home/wattson/Documents/code/data/{self.project_name}/attacks.jsonl"
        )
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            for entry in self.datafile:
                json.dump(entry, f)
                f.write("\n")
