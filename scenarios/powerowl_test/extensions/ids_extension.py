from wattson.cosimulation.control.scenario_extension import ScenarioExtension
from wattson.cosimulation.simulators.network.components.wattson_network_router import (
    WattsonNetworkRouter,
)
from wattson.cosimulation.simulators.network.components.wattson_network_switch import (
    WattsonNetworkSwitch,
)
from wattson.cosimulation.simulators.network.components.wattson_network_host import (
    WattsonNetworkHost,
)

from copy import deepcopy


class IdsExtension(ScenarioExtension):

    def mirror(self, switch_str):

        network_emulator = self.co_simulation_controller.network_emulator
        switch = network_emulator.get_switch(switch_str)
        interfaces = switch.get_interfaces()
        last_interface = interfaces[len(interfaces) - 1]
        switch.enable_mirror(last_interface)
        print("Mirror for " + switch_str + " started, despite the error")
        # TODO This works, since the flag for mirror is still being set, but its not clean

    def extend_pre_physical(self):

        network_emulator = self.co_simulation_controller.network_emulator

        # New scenario already as a backbone router
        """
        target_switch = network_emulator.get_switch(node="n359")
        subnet = target_switch.get_subnets(include_management=False)[0]
        ip = network_emulator.get_unused_ip(subnet)
        interface_options = {"ip_address": ip, "subnet_prefix_length": subnet.prefixlen}
        print("Creating Router")
        router = network_emulator.add_router(WattsonNetworkRouter(id="IdsRouter"))
        network_emulator.connect_nodes(router, target_switch, interface_a_options=interface_options)
        """
        router = network_emulator.get_router(node="n947")

        print("Creating Switch")
        new_switch = network_emulator.add_switch(WattsonNetworkSwitch(id="n2000"))
        interface_options = {"ip": "172.16.10.1", "subnet_prefix_length": 24}
        network_emulator.connect_nodes(
            new_switch, router, interface_b_options=interface_options
        )

        target_switch = network_emulator.get_switch(node=new_switch)
        print("Creating Windows-Host")
        host = network_emulator.add_host(WattsonNetworkHost(id="windows"))
        interface_options = {"ip": "172.16.10.2", "subnet_prefix_length": 24}
        network_emulator.connect_nodes(
            host, target_switch, interface_a_options=interface_options
        )

        print("Creating IDS-Sensor")
        host = network_emulator.add_host(WattsonNetworkHost(id="ids-sensor"))
        interface_options = {"ip": "172.16.10.3", "subnet_prefix_length": 24}
        network_emulator.connect_nodes(
            host, target_switch, interface_a_options=interface_options
        )

        target = "n401"
        target_switch = network_emulator.get_switch(node=target)
        print("Creating Subnet connection")
        interface_options = {"ip": "172.16.2.200", "subnet_prefix_length": 24}
        network_emulator.connect_nodes(
            host, target_switch, interface_a_options=interface_options
        )
        self.mirror(target)

        target = "n375"
        target_switch = network_emulator.get_switch(node=target)
        print("Creating Subnet connection")
        interface_options = {"ip": "172.16.1.200", "subnet_prefix_length": 24}
        network_emulator.connect_nodes(
            host, target_switch, interface_a_options=interface_options
        )
        self.mirror(target)

        target = "n1035"
        target_switch = network_emulator.get_switch(node=target)
        print("Creating Subnet connection")
        interface_options = {"ip": "172.16.3.200", "subnet_prefix_length": 24}
        network_emulator.connect_nodes(
            host, target_switch, interface_a_options=interface_options
        )
        self.mirror(target)

        target = "n1079"
        target_switch = network_emulator.get_switch(node=target)
        print("Creating Subnet connection")
        interface_options = {"ip": "172.16.3.201", "subnet_prefix_length": 24}
        network_emulator.connect_nodes(
            host, target_switch, interface_a_options=interface_options
        )
        self.mirror(target)
