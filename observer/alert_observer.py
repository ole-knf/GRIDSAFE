import asyncio
import json
import os
import re
import socket

from syslog_rfc5424_parser import SyslogMessage


class AlertObserver:
    def __init__(self, udp_ip: str, udp_port: int, project_name: str):
        """
        Collect IDS alerts

        :param str udp_ip: IP of the node executing the framework
        :param int udp_port: Port for the UDP connection
        :param str project_name: Name of the folder in /data
        """
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.project_name = project_name
        self.datafile: list[dict] = []
        self.collect = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)

    def __parse_message_field(self, msg):
        """
        Parse IDS alerts and extract relevant values. StationGuard specific

        :param str msg: A syslog message recieved over the port
        """
        # exclude everthing before smac
        pattern = re.compile(r"smac=.*")

        match = pattern.search(msg)
        # If there is no match, quit
        if not match:
            return {}

        relevant_part = match.group(0)
        key_value_pairs = []
        # message contains spaces, so split again
        parts = relevant_part.split(" msg=")
        if parts:
            key_value_pairs.extend(parts[0].split())

        if len(parts) > 1:
            key_value_pairs.append(f"msg={parts[1]}")

        # convert list of x=y to dict
        message_dict = {}
        for pair in key_value_pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)
                message_dict[key] = value

        return message_dict

    async def start(self):
        """
        Start the Observer
        """
        # Set the global flag
        self.collect = True

        # Create a UDP socket
        self.sock.bind((self.udp_ip, self.udp_port))
        print(f"Listening for UDP packets on {self.udp_ip}:{self.udp_port}")

        # Start loop until the global flag is changed
        loop = asyncio.get_event_loop()
        while self.collect:
            try:
                # Receive data from the socket
                data, addr = await loop.run_in_executor(None, self.sock.recvfrom, 1024)
                content = data.decode("utf-8")
                print(f"Received packet from {addr}: {content}")
                # Parse syslog message
                content = SyslogMessage.parse(content)
                self.datafile.append(content.as_dict())
            except BlockingIOError:
                await asyncio.sleep(0.001)
        self.sock.close()

    async def stop(self):
        """
        Stop data collection
        """
        self.collect = False

    def save(self):
        """
        Save all IDS alerts
        """
        # only for dev: save raw alerts, unparsed in case something goes wrong
        if self.project_name == "dev":
            filename = f"/home/wattson/Documents/code/data/{self.project_name}/alerts-raw.jsonl"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                for entry in self.datafile:
                    json.dump(entry, f)
                    f.write("\n")

        # parse msg field of all alerts for easy information access
        for index in range(len(self.datafile)):
            parsed_field = self.__parse_message_field(self.datafile[index]["msg"])
            self.datafile[index]["msg"] = parsed_field

        # Save alerts in proper format
        filename = f"/home/wattson/Documents/code/data/{self.project_name}/alerts.jsonl"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "a") as f:
            for entry in self.datafile:
                json.dump(entry, f)
                f.write("\n")
