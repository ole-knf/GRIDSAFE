import os
import signal
import subprocess
import sys
from time import sleep, time

from wattson.cosimulation.control.interface.wattson_client import WattsonClient
from wattson.cosimulation.simulators.network.remote_network_emulator import \
    RemoteNetworkEmulator


class Attack:
    def __init__(self, target: str, attack_duration: int, pause_duration: int) -> None:
        """
        Basic attack class

        :param str target: Target node of the simulation
        :param int attack_duration: Duration of the attck in seconds
        :param int pause_duration: Duration of the pause after the attack
        """
        self.attack_type = "Undefined"
        self.target = target
        self.network_emulator = None
        self.attack_duration = attack_duration
        self.pause_duration = pause_duration
        self.timecodes_start: list[float] = []
        self.timecodes_end: list[float] = []

        # Wattson client for interaction with wattson
        wattson_client = WattsonClient(wattson_socket_ip="10.0.0.1")
        wattson_client.require_connection()
        self.network_emulator = RemoteNetworkEmulator(wattson_client=wattson_client)
        self.node_connection = None

    def logger(self):
        """
        Logs the successful setup of the attack
        """
        print(f"Attack {self.attack_type} for target {self.target} sucessfully set up")

    def add_start_time(self):
        """
        Saves start time of the attack
        """

        self.timecodes_start.append(time())

    def add_end_time(self):
        """
        Saves end time of the attack
        """

        self.timecodes_end.append(time())

    def execute_command_on_node(
        self, node, command, attack_counter=None, duration=None, project_path=None
    ):
        """
        Executes a command in the namespace of any node in the wattson simulation

        :param node: Node on which the command should be executes
        :param command: Command to execute
        :param attack_counter: Counter of the attacks in the attack execution.
        :param duration: Duration of the attack. If non is given, the framework waits for the attack to finish by itself
        :param project_path: Name of the folder in /data for saving strace files. If none is given, strace will not be used
        """
        namespace = f"w_{node}"
        # connect to namespace
        subprocess.run(
            f"sudo -E ip netns exec {namespace} ibus-daemon --xim -d -r", shell=True
        )
        # Use strace, if there is a project path
        if project_path != None:
            command = (
                f"sudo strace -e trace=network -ttt -f -s 20000 -o {project_path}{attack_counter}networkdump.out "
                + command
            )

        # Build bash command
        cmd = [
            "sudo",
            "-E",
            "ip",
            "netns",
            "exec",
            namespace,
            "/bin/bash",
            "-c",
            f"'{command}'",
        ]
        cmd = " ".join(cmd)
        try:
            print(f"running: {cmd}")
            p = subprocess.Popen(
                "exec " + cmd,
                shell=True,
                stdin=sys.stdin,
                stderr=sys.stderr,
                stdout=sys.stdout,
            )
            if duration == None:
                p.wait()
            else:
                p.wait(duration)
        except subprocess.TimeoutExpired:
            p.terminate()
            p.kill()
            p.wait()

    def execute(self, attackcount: int):
        return True

    def restore(self, attack_counter=-1):
        return True
