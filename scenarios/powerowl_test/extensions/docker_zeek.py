import copy

from wattson.cosimulation.control.scenario_extension import ScenarioExtension
from wattson.cosimulation.simulators.network.components.network_link_model import (
    NetworkLinkModel,
)
from wattson.cosimulation.simulators.network.components.wattson_network_docker_host import (
    WattsonNetworkDockerHost,
)
from wattson.cosimulation.simulators.network.components.wattson_network_interface import (
    WattsonNetworkInterface,
)


class DockerZeek(ScenarioExtension):
    def provides_pre_physical(self) -> bool:
        return True

    def extend_pre_physical(self):
        network_emulator = self.co_simulation_controller.network_emulator
        logger = self.co_simulation_controller.logger.getChild("DockerZeek")
        docker_config = {"id": "zeek"}
        docker_config["type"] = "docker-host"
        docker_config["image"] = "wattson-zeek"
        docker_config["memory_limit"] = "8g"
        docker_config["services"] = [
            {
                "module": "wattson.services.monitoring.wattson_zeek",
                "service-type": "python",
                "class": "WattsonZeek",
                "config": {
                    "autostart": True,
                    "interface": "h35-eth2",
                    "inter_startup_delay_s": 15,
                },
            }
        ]
        zeek_host = WattsonNetworkDockerHost(
            id=docker_config["id"], config=docker_config
        )
        network_emulator.add_host(zeek_host)

        switch = network_emulator.get_switch("n1171")
        subnet = switch.get_subnets(include_management=False)[0]
        # create interface to access graylog UI
        server_ip = network_emulator.get_unused_ip(subnet)
        link_model_server = NetworkLinkModel()
        link_model_server.delay_ms = 5
        network_emulator.connect_nodes(
            zeek_host,
            switch,
            interface_a_options={
                "ip_address": server_ip,
                "subnet_prefix_length": subnet.prefixlen,
            },
            link_options={"link_model": link_model_server},
        )
        # create mirror interface to listen for traffic
        server_ip = network_emulator.get_unused_ip(subnet)
        link_model_server = NetworkLinkModel()
        link_model_server.delay_ms = 5
        network_emulator.connect_nodes(
            zeek_host,
            switch,
            interface_a_options={
                "ip_address": server_ip,
                "subnet_prefix_length": subnet.prefixlen,
            },
            interface_b_options={
                "config": {"mirror": True},
            },
            link_options={"link_model": link_model_server},
        )
        logger.info(
            f"Added host {zeek_host.entity_id} with ZEEK and a mirror port on switch n1171."
        )
