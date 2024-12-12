from attacks.attack import Attack
from attacks.catalog.IEC_104.control_freeze import Control_Freeze


class Control_Freeze_Attackchain:
    def __init__(self, project_name: str, project_path: str) -> None:
        self.project_name = project_name
        self.project_path = project_path
        self.attacks: list[Attack] = []

    def get_attack_list(self):

        # freezes sgen.4 and bus.8, visible but stealthy

        self.attacks.append(
            Control_Freeze(
                executing_host="n848",
                own_ip="172.16.3.24",
                gateway_ip="172.16.3.28",
                targets_ip="172.16.3.26,172.16.3.27",
                project_path=self.project_path,
                pause_duration=120,
                attack_duration=240,
            )
        )

        return self.attacks
