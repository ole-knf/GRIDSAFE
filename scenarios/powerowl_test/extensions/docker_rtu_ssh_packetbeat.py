import copy

from wattson.cosimulation.control.scenario_extension import ScenarioExtension
from wattson.cosimulation.simulators.network.components.wattson_network_docker_host import (
    WattsonNetworkDockerHost,
)


class DockerRtuSSHPacketbeat(ScenarioExtension):
    def provides_pre_physical(self) -> bool:
        return True

    def extend_pre_physical(self):
        rtus_to_replace = self.config.get("rtu_ids", [])
        elk_ip_config = self.config.get("elk_ip_config")
        enable_internet = self.config.get("enable_internet", False)
        network_emulator = self.co_simulation_controller.network_emulator
        logger = self.co_simulation_controller.logger.getChild("DockerRTU")
        for rtu_id in rtus_to_replace:
            rtu = network_emulator.get_host(rtu_id)
            if rtu is None:
                logger.error(
                    f"Cannot upgrade non-existing RTU {rtu_id} to a docker host"
                )
                continue
            if not rtu.has_role("rtu"):
                logger.error(f"Host {rtu_id} is not an RTU")
                continue
            rtu_config = rtu.get_config()
            docker_config = copy.deepcopy(rtu_config)
            docker_config["type"] = "docker-host"
            docker_config["image"] = "wattson-rtu-ssh-packetbeat"
            docker_config["services"] = [
                {
                    "module": "wattson.services.monitoring.wattson_packetbeat",
                    "service-type": "python",
                    "class": "WattsonPacketbeat",
                    "config": {
                        "autostart": True,  # autostart==True can fail if ELK stack is not up yet
                        "autostart_delay": 30,  # Wait for 5 seconds before autostarting the service
                        "elk_ip": elk_ip_config,
                    },
                }
            ]
            docker_rtu = WattsonNetworkDockerHost(
                id=docker_config["id"], config=docker_config
            )
            network_emulator.replace_node(rtu, docker_rtu)
            logger.info(
                f"Upgraded RTU {docker_rtu.entity_id} to a Docker-based RTU with an ssh server and packetbeat service."
            )
            if enable_internet:
                nat = network_emulator.add_nat_to_management_network()
                nat.allow_traffic_from_host(docker_rtu)
                nat.set_internet_route(docker_rtu)
