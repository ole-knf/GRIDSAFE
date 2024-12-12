import copy
from pathlib import Path

from wattson.cosimulation.control.scenario_extension import ScenarioExtension
from wattson.cosimulation.simulators.network.components.wattson_network_host import (
    WattsonNetworkHost,
)


class LocalPacketbeat(ScenarioExtension):

    def provides_pre_physical(self) -> bool:
        return True

    def extend_pre_physical(self):
        rtus_to_replace = self.config.get("rtu_ids", [])
        elk_ip_config = self.config.get("elk_ip_config")
        enable_internet = self.config.get("enable_internet", False)
        working_dir = self.config.get("working_dir")
        network_emulator = self.co_simulation_controller.network_emulator
        logger = self.co_simulation_controller.logger.getChild("Local Packetbeat")
        for rtu_id in rtus_to_replace:
            rtu = network_emulator.get_host(rtu_id)
            if rtu is None:
                logger.error(
                    f"Cannot upgrade non-existing RTU {rtu_id} to a packetbeat host"
                )
                continue
            if not rtu.has_role("rtu"):
                logger.error(f"Host {rtu_id} is not an RTU")
                continue
            rtu_config = rtu.get_config()
            config = copy.deepcopy(rtu_config)
            config["services"] = [
                {
                    "module": "wattson.services.monitoring.wattson_local_packetbeat",
                    "service-type": "python",
                    "class": "WattsonLocalPacketbeat",
                    "config": {
                        "autostart": False,
                        "autostart_delay": 30,  # Wait for 30 seconds before autostarting the service
                        "elk_ip": elk_ip_config,
                        "working_dir": working_dir,
                    },
                }
            ]
            packetbeat_rtu = WattsonNetworkHost(id=config["id"], config=config)
            network_emulator.replace_node(rtu, packetbeat_rtu)
            logger.info(
                f"Upgraded RTU {packetbeat_rtu.entity_id} to a Docker-based RTU with packetbeat."
            )
            if enable_internet:
                nat = network_emulator.add_nat_to_management_network()
                nat.allow_traffic_from_host(packetbeat_rtu)
                nat.set_internet_route(packetbeat_rtu)
