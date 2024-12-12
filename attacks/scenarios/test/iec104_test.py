from attacks.attack import Attack
from attacks.catalog.IEC_104.arp import IEC104_ARP
from attacks.catalog.IEC_104.arp_dos import IEC104_ARP_dos
from attacks.catalog.IEC_104.arp_false_data_injection import \
    IEC104_ARP_false_data_injection


class IEC104_Test:
    def __init__(self, project_name: str, project_path: str) -> None:
        self.project_name = project_name
        self.project_path = project_path
        self.attacks: list[Attack] = []

    def get_attack_list(self):

        self.attacks.append(
            IEC104_ARP(
                executing_host="n848",
                project_path=self.project_path,
                attack_duration=120,
                pause_duration=120,
                ownip="172.16.3.24",
                targetsip="172.16.3.26,172.16.3.27",
                gatewaysip="172.16.3.28,172.16.3.29",
                gatewaysmac="02:c8:99:68:00:04,02:c8:99:68:00:05",
                mtuip="172.16.1.2",
            )
        )

        self.attacks.append(
            IEC104_ARP_dos(
                executing_host="n848",
                project_path=self.project_path,
                attack_duration=120,
                pause_duration=120,
                ownip="172.16.3.24",
                targetsip="172.16.3.26,172.16.3.27",
                gatewaysip="172.16.3.28,172.16.3.29",
                gatewaysmac="02:c8:99:68:00:04,02:c8:99:68:00:05",
                mtuip="172.16.1.2",
            )
        )

        self.attacks.append(
            IEC104_ARP_false_data_injection(
                executing_host="n848",
                project_path=self.project_path,
                attack_duration=120,
                pause_duration=120,
                ownip="172.16.3.24",
                targetsip="172.16.3.26,172.16.3.27",
                gatewaysip="172.16.3.28,172.16.3.29",
                gatewaysmac="02:c8:99:68:00:04,02:c8:99:68:00:05",
                mtuip="172.16.1.2",
            )
        )

        return self.attacks
