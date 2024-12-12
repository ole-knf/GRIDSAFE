import copy
import logging

from wattson.cosimulation.control.scenario_extension import ScenarioExtension
from wattson.cosimulation.simulators.network.components.wattson_network_docker_host import (
    WattsonNetworkDockerHost,
)


class DockerMtuSSHPacketbeat(ScenarioExtension):
    def provides_pre_physical(self) -> bool:
        return True

    def extend_pre_physical(self):
        mtu_id = self.config.get("mtu_id", None)
        if not mtu_id:
            logging.error("Provided no MTU id.")
            return
        elk_ip_config = self.config.get("elk_ip_config")
        enable_internet = self.config.get("enable_internet", False)
        network_emulator = self.co_simulation_controller.network_emulator
        logger = self.co_simulation_controller.logger.getChild("DockerMTU")
        mtu = network_emulator.get_host(mtu_id)
        if mtu is None:
            logger.error(f"Cannot upgrade non-existing MTU {mtu_id} to a docker host")
            return
        if not mtu.has_role("mtu"):
            logger.error(f"Host {mtu_id} is not an MTU")
            return
        mtu_config = mtu.get_config()
        docker_config = copy.deepcopy(mtu_config)
        docker_config["type"] = "docker-host"
        docker_config["image"] = "wattson-mtu-ssh-packetbeat"
        docker_config["services"] = [
            {
                "module": "wattson.services.monitoring.wattson_packetbeat",
                "service-type": "python",
                "class": "WattsonPacketbeat",
                "config": {
                    "autostart": True,  # autostart==True can fail if ELK stack is not up yet
                    "autostart_delay": 60,  # Wait for 5 seconds before autostarting the service
                    "elk_ip": elk_ip_config,
                },
            }
        ]
        docker_mtu = WattsonNetworkDockerHost(
            id=docker_config["id"], config=docker_config
        )
        network_emulator.replace_node(mtu, docker_mtu)
        logger.info(
            f"Upgraded MTU {docker_mtu.entity_id} to a Docker-based MTU with an ssh server and packetbeat service."
        )
        if enable_internet:
            nat = network_emulator.add_nat_to_management_network()
            nat.allow_traffic_from_host(docker_mtu)
            nat.set_internet_route(docker_mtu)
