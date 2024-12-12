from attacks.attack import Attack
from attacks.catalog.IEC_104.voltage_drift_off import Voltage_Drift_Off


class Voltage_Drift_Off_Attackchain:
    def __init__(self, project_name: str, project_path: str) -> None:
        self.project_name = project_name
        self.project_path = project_path
        self.attacks: list[Attack] = []

    def get_attack_list(self):

        # fakes undervoltage for bus.8 and then overvoltage for same bus  (other bus such as bus.3 leads to mitm forwarding issues), visible

        self.attacks.append(
            Voltage_Drift_Off(
                executing_host="n848",
                own_ip="172.16.3.24",
                gateway_ip="172.16.3.28",
                targets_ip="172.16.3.26",
                bus="bus.8",
                voltage_mode="undervoltage",
                project_path=self.project_path,
                pause_duration=120,
                attack_duration=180,
            )
        )

        self.attacks.append(
            Voltage_Drift_Off(
                executing_host="n848",
                own_ip="172.16.3.24",
                gateway_ip="172.16.3.28",
                targets_ip="172.16.3.26",
                bus="bus.8",
                voltage_mode="overvoltage",
                project_path=self.project_path,
                pause_duration=120,
                attack_duration=180,
            )
        )

        return self.attacks
