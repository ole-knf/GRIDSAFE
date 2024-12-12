from attacks.attack import Attack
from attacks.catalog.bruteforce.ssh import BruteforceSSH
from attacks.catalog.DoS.ping_flooding import PingFlooding
from attacks.catalog.MitM.arp_spoof import ArpSpoof
from attacks.catalog.physical.RTU_disconnect import PhysicalFaultRTU
from attacks.catalog.reconnaissance.port_scan import PortScan


class IntegrationValidation:
    def __init__(self, project_name: str, project_path: str) -> None:
        self.project_name = project_name
        self.project_path = project_path
        self.attacks: list[Attack] = []

    def get_attack_list(self):

        if "recon" in self.project_name:
            self.attacks.append(
                PortScan(
                    target="172.16.1.2",
                    executing_host="n848",
                    project_path=self.project_path,
                    attack_duration=120,
                    pause_duration=120,
                )
            )

        elif "bruteforce" in self.project_name:
            self.attacks.append(
                BruteforceSSH(
                    target="172.16.1.2",
                    node_name="n389",
                    executing_host="n848",
                    project_path=self.project_path,
                    attack_duration=120,
                    pause_duration=120,
                )
            )

        elif "dos" in self.project_name:
            self.attacks.append(
                PingFlooding(
                    target="172.16.1.2",
                    executing_host="n848",
                    attack_duration=120,
                    pause_duration=120,
                )
            )

        elif "mitm" in self.project_name:
            self.attacks.append(
                ArpSpoof(
                    target="172.16.3.26",
                    executing_host="n848",
                    project_path=self.project_path,
                    gateway="172.16.3.28",
                    attack_duration=120,
                    pause_duration=120,
                )
            )

        elif "physical" in self.project_name:
            self.attacks.append(
                PhysicalFaultRTU(target="n848", attack_duration=120, pause_duration=120)
            )

        # for int. val we want to run every attack twice
        self.attacks.append(self.attacks[0])

        return self.attacks
