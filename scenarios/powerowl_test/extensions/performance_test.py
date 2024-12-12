from wattson.cosimulation.control.scenario_extension import ScenarioExtension
from wattson.cosimulation.exceptions import NetworkException
from wattson.cosimulation.simulators.network.components.network_link_model import (
    NetworkLinkModel,
)
from wattson.cosimulation.simulators.network.components.wattson_network_host import (
    WattsonNetworkHost,
)


class PerformanceTest(ScenarioExtension):
    def provides_pre_physical(self) -> bool:
        return True

    def extend_pre_physical(self):
        network_emulator = self.co_simulation_controller.network_emulator
        switch = network_emulator.get_switch("n1016")
        subnets = switch.get_subnets(include_management=False)
        if len(subnets) == 0:
            raise NetworkException("Cannot find subnet")
        subnet = subnets[0]

        server_host = WattsonNetworkHost(id="perf-s")
        link_model_server = NetworkLinkModel()
        link_model_server.delay_ms = 5
        server_ip = network_emulator.get_unused_ip(subnet)
        network_emulator.add_host(server_host)
        network_emulator.connect_nodes(
            server_host,
            switch,
            interface_a_options={
                "ip_address": server_ip,
                "subnet_prefix_length": subnet.prefixlen,
            },
            link_options={"link_model": link_model_server},
        )

        client_host = WattsonNetworkHost(id="perf-c")
        link_model_client = NetworkLinkModel()
        link_model_client.delay_ms = 5
        client_ip = network_emulator.get_unused_ip(subnet)
        network_emulator.add_host(client_host)
        network_emulator.connect_nodes(
            client_host,
            switch,
            interface_a_options={
                "ip_address": client_ip,
                "subnet_prefix_length": subnet.prefixlen,
            },
            link_options={"link_model": link_model_client},
        )
