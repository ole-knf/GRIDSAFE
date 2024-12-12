import time

from attacks.attack import Attack
from wattson.cosimulation.control.interface.wattson_client import WattsonClient
from wattson.cosimulation.simulators.network.remote_network_emulator import \
    RemoteNetworkEmulator


class PhysicalFaultRTU(Attack):
    def __init__(self, target: str, attack_duration=60, pause_duration=60) -> None:
        super().__init__(target, attack_duration, pause_duration)
        """
        Disconnects the network interface of a node in the simulation
        """
        self.attack_type = "Physical Fault RTU"
        self.target_list = self.target.split(",")
        # self.target_host = self.network_emulator.get_host(self.target)
        # self.target_interface = self.target_host.get_interfaces()[1]
        self.logger()

    def execute(self, attack_counter):

        for target in self.target_list:
            target_host = self.network_emulator.get_host(target)
            target_interface = target_host.get_interfaces()[1]
            target_interface.down()
        self.add_start_time()

        return True

    def restore(self, attack_counter):

        for target in self.target_list:
            target_host = self.network_emulator.get_host(target)
            target_interface = target_host.get_interfaces()[1]
            interface_status = target_interface.up()
            route_status = target_host.update_default_route()
        self.add_end_time()
        return interface_status and route_status
