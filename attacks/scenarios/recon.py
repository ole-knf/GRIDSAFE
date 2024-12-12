from attacks.attack import Attack
from attacks.catalog.bruteforce.ssh import BruteforceSSH
from attacks.catalog.IEC_104.arp import IEC104_ARP
from attacks.catalog.IEC_104.enumerate import IEC104_IOA_Enum
from attacks.catalog.reconnaissance.host_discovery import HostDiscovery
from attacks.catalog.reconnaissance.port_scan import PortScan


class Recon_Attackchain:
    def __init__(self, project_name: str, project_path: str) -> None:
        self.project_name = project_name
        self.project_path = project_path
        self.attacks: list[Attack] = []

    def get_attack_list(self):

        # adversary wants to spy on the network, no stealth
        # access to RTU in a substation n848
        # host discovery across the subnets
        # scan all of these targets with a full port scan
        # try to ssh  bruteforce into router n947, which doesnt work
        # instead intercept communication via arp from two substations, 4 RTUS
        self.attacks.append(
            HostDiscovery(
                subnet="172.16.0-4.0-255",
                executing_host="n848",
                project_path=self.project_path,
                pause_duration=120,
            )
        )

        self.attacks.append(
            PortScan(
                target="172.16.1.1-2 172.16.3.1-29 172.16.2.1-6",
                executing_host="n848",
                ports="--top-ports 10000",
                project_path=self.project_path,
                pause_duration=120,
            )
        )

        self.attacks.append(
            IEC104_IOA_Enum(
                target="172.16.3.1-27 172.16.2.2-6",
                executing_host="n848",
                project_path=self.project_path,
                pause_duration=120,
            )
        )

        self.attacks.append(
            BruteforceSSH(
                target="172.16.3.28",
                node_name="n947",
                executing_host="n848",
                project_path=self.project_path,
                attack_duration=120,
                pause_duration=180,
            )
        )

        self.attacks.append(
            IEC104_ARP(
                executing_host="n848",
                project_path=self.project_path,
                attack_duration=120,
                pause_duration=60,
                ownip="172.16.3.24",
                targetsip="172.16.3.26,172.16.3.27",
                gatewaysip="172.16.3.28,172.16.3.29",
                gatewaysmac="02:c8:99:68:00:04,02:c8:99:68:00:05",
                mtuip="172.16.1.2",
            )
        )  # THIS WAS WITHOUT FORWARDING AFTERWARDS FOR STEALTHY ARP TERMINATION

        self.attacks.append(
            IEC104_ARP(
                executing_host="n848",
                project_path=self.project_path,
                attack_duration=120,
                pause_duration=120,
                ownip="172.16.3.24",
                targetsip="172.16.3.22,172.16.3.23",
                gatewaysip="172.16.3.28,172.16.3.29",
                gatewaysmac="02:c8:99:68:00:04,02:c8:99:68:00:05",
                mtuip="172.16.1.2",
            )
        )  # THIS WAS WITHOUT FORWARDING AFTERWARDS FOR STEALTHY ARP TERMINATION

        return self.attacks
