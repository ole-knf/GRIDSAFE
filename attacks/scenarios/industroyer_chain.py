from attacks.attack import Attack
from attacks.catalog.IEC_104.industroyer import Industroyer


class Industroyer_Attackchain:
    def __init__(self, project_name: str, project_path: str) -> None:
        self.project_name = project_name
        self.project_path = project_path
        self.attacks: list[Attack] = []

    def get_attack_list(self):

        # knowledable attacker, nows system
        # Open all connections: first for DSS (test for command which are not actually seen), then TSS -> brings down grid

        self.attacks.append(
            Industroyer(
                executing_host="n848",
                targets_ip="172.16.3.12,172.16.3.22,172.16.3.9",
                project_path=self.project_path,
                scenario_file="DSS-all.yml",
                pause_duration=120,
                attack_duration=120,
            )
        )

        self.attacks.append(
            Industroyer(
                executing_host="n848",
                targets_ip="172.16.2.5,172.16.2.6",
                project_path=self.project_path,
                scenario_file="TSS-all.yml",
                pause_duration=120,
                attack_duration=120,
            )
        )

        return self.attacks
