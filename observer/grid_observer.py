import json
import os
from math import isnan
from time import time

from wattson.cosimulation.control.interface.wattson_client import WattsonClient
from wattson.powergrid.remote.remote_power_grid_model import RemotePowerGridModel


class GridObserver:
    def __init__(self, project_name: str):
        """
        Collect information about the grid simulation. WATTSON SPECIFIC

        :param str project_name: Name of the directory in the /data folder
        """
        self.project_name = project_name
        self.datafile: list[dict] = []

        # Init of a wattson client to communicate with wattson
        self.wattson_client = WattsonClient(
            client_name="grid-observer", namespace="auto", wait_for_namespace=True
        )
        self.wattson_client.require_connection
        self.wattson_client.register()

    def __on_change(self, grid_value, old_value, new_value):
        """
        Parse wattson grid information and extract relevant data

        :param grid_value: The grid component
        :param old_value: Old value of grid component
        :param new_value: New value of grid component
        """

        # only collect voltage information for bus and load for lines
        if (
            "bus" in grid_value.get_identifier()
            and "voltage" in grid_value.get_identifier()
            and "angle" not in grid_value.get_identifier()
        ) or (
            "line" in grid_value.get_identifier()
            and "loading" in grid_value.get_identifier()
        ):
            location_str = grid_value.get_identifier()
            location_str = location_str.split(".")
            device = location_str[0]
            number = location_str[1]
            content = location_str[3]
            location = f"{device} {number} {content}"
            entry = {}
            entry["time"] = time()
            entry["location"] = location
            # If bus is down, NaN will be returned, which represents voltage level of 0
            if isnan(new_value):
                new_value = 0
            entry["value"] = new_value

            self.datafile.append(entry)

    def start(self):
        """
        Start the collection
        """
        remote_grid_model = RemotePowerGridModel(wattson_client=self.wattson_client)
        remote_grid_model.add_on_grid_value_change_callback(self.__on_change)

    def stop(self):
        """
        Stop the collection
        """
        self.wattson_client.stop()

    def save(self):
        """
        Save the collected data to file
        """
        filename = f"/home/wattson/Documents/code/data/{self.project_name}/grid.jsonl"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            for entry in self.datafile:
                json.dump(entry, f)
                f.write("\n")
