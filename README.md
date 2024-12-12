# GRIDSAFE - Grid Security Assessment and Framework Evaluation

A Comprehensive Framework for Evaluating Intrusion Detection Systems in Power Grids and Beyond.

This tool performs autonomous and data rich IDS assessments, specifically designed for industrial control networks and intrusion detection systems in power grids. While traditional evaluation procedures for IDS lack the complexity and consitency necessary to draw comparisons between results, GRIDSAFE and its underlying methodology strives to provide the most meaningful data possible. By mirroring every possible circumstance of the system, in which the IDS will operate in the future, we can ensure the most meaningful evaluation results, actually representing how the system will behave. For this to work, we perform an intial threat modeling specific to the power grid scenario, on which basis we make calulated decisions regarding the evaluation's cyberattack selection, and IDS integration into the network. GRIDSAFE then autonomously executes these attacks against Wattson's power grid simulation, collects all necesarry data, and represents the results concisely. 

GRIDSAFE is the product of my master thesis "Evaluating Intrusion Detection Systems in Power Grids: A practical Framework". The thesis dicusses a precise description of a complex evaluation methodology, which lays the groudnwork for this framework, a technical descirption of the framework, as well as a dicussion of our Evaluation of Omicron's StationGuard an Suricata. For more insight, please refer to the thesis: https://oleknief.com/files/academic-works/master-thesis.pdf.

NOTE: Due to ethical considerations, we refrain from publishing the attack catalog in "/attacks". However, we provide the general attack layout and an exemplary attack, as well as our attack scenarios to provide an example how to use the framework.


## Installation

In order to simulate power grids an their network infrastructure, we utilize the highly versatile simulation tool Wattson. For more information about how to work with this simulation, please refer to the website https://wattson.it/, which also includes installation instruction for the repository https://github.com/fkie-cad/wattson. Additionally, the tool requires the following dependencies: 

´´´
termcolor, paramiko, syslog_rfc5424_parser, dateutil, matplotlib, numpy, pillow
´´´

For our evaluation, we use our own developed attacks, as well as a selection of Wattson's attack library from https://gitlab.fkie.fraunhofer.de/cad-energy/wattson/wattson-attacks. However, both of these are not publically accessible due to ethical considerations.

- Install New dependencies (some of them might be covered by the Wattson install): termcolor, paramiko, syslog_rfc5424_parser, dateutil, matplotlib, numpy, pillow
- Install Attack Tools: hydra, hping3, arpspoof, Nmap, scapy. For some of theses tools, such as hydra, the framework additionally requires a wordlist to execute the password brute-force, which is not yet included in this repository.  

## Setup

After choosing a power grid compatible with Wattson, we still need to add the IDS to the environment and define our attacks. This section details this procedure. The “scenarios” folder contains the power grid scenario we use for the our evaluation, as well as our adaptions to integrate an IDS (ids_extension.py). Apart from this extension, the scenario is part of Wattson and not my own work.


### VM based IDS Integration into Wattson 

1. Setup VM in any virtualization software, pref. VirtualBox
2. Add a host to wattson, which will represent the VM in the network. This host will not actually be used, but will start the initialization of the used interfaces that we will need. To ensure a correct routing procedure, the addition of a host should be part of a scenario extension. 

```{python}
from wattson.cosimulation.control.interface.wattson_client import WattsonClient
from wattson.cosimulation.simulators.network.remote_network_emulator import RemoteNetworkEmulator

# Create the network emulator which will interfact with wattson

wattson_client = WattsonClient(namespace="auto", wait_for_namespace=True)
wattson_client.require_connection()
wattson_client.register()
network_emulator = RemoteNetworkEmulator(wattson_client=wattson_client)

# Define the switch to which the VM will connect

switch_to_connect_to = "THE SWITCH YOU WANT TO CONNECT TO"
target_switch = network_emulator.get_switch(switch="switch_to_connect_to")
subnet = target_switch.get_subnets(include_management=False)[0]

# Create the host
print("Creating host")
host = network_emulator.create_host("NAME OF YOUR VM")
ip = network_emulator.get_unused_ip(subnet)
interface_options = {"ip_address": ip, "subnet_prefix_length": 24}
network_emulator.connect_nodes(host, target_switch, interface_a_options=interface_options)
print("Updating default route")
host.update_default_route()

```
3. Identify the created network adapter, which was created for the new host. To do this, issue the following command in the wattson-CLI. The last result will be the new interface which will look something like "s25-eth2"

```
switch info NAME_OF_THE_SWITCH
```
4. In the virtualization software for the VM, go into the network settings. For a simple VM only one interface should be present. The adapter type needs to be "bridged". The adapter to bridge to will be the adapter identified in step 3.
5. As the last step, boot into the VM. Within the OS settings, change the IP of the network adapter. The IP needs to be different to all other devices in the subnet. Important: It also may not be the same as the IP of the new host in wattson!

```
IP: 172.16.X.X, some unique IP in the subnet
Subnetmask: 255.255.255.0, dependent of the set subnet_prefix_length
Gateway: 172.16.X.1, the router of the subnet the VM is in
```
Sidenote: In order the use the same IP as the new host in wattson, the MAC Addresses most likely need to be the same, which can be set in the VM's network settings.

We also provide an explicit example for integrating Omicron's StationGuard in the "StationGuard" folder. The respective scenario extension can be found under /scenarios/powerowl_test/ids_extension.py

### Connect IDS with Framework

The framework supports automatic parsing of IDS alerts. However, this is highly dependent on the IDS.

- For IDS with SIEM integration:
1. Modify the IP and port of the IDS in the network in phases.py
2. Adjust the alert parsing based on the alert structure in metrics/metrics_preprocessor.py and observer/alert_observer.py

- For IDS generating an alert file:
1. Ensure that the files is accessible by the framework.
2. Adjust the alert parsing based on the alert structure in metrics/metrics_preprocessor.py


### Attack Selection

The attack selection is not yet accessible via parameters, as there would be too many choices. To adjust the attacks the framework executes, modify the "attack_phase()" of "phases.py" and add the attacks to "attack_queue". Implemented attack can be found in "attacks/catalog", while we also offer "attacks/scenarios", which return attack chains, which we use in the thesis. The framework will iterate through the queue, executing the attack one by one. For each attack, you can adjust several parameters, such as targets, duration, and idle time of the framework after the attack ends.


## Framework Parameters

To start the framework, we need to adjust several parameters, each of which is explained in the framework's help page, accessible via "python3 main.py -h".
Most parameters define, how the folder in /data should be called, which phases should be executed (attack vs evaluation), which metrics to use, and which visualizations should be uses. The IDS choice (StationGuard vs Suricata) defines the way, in which the IDS alerts are being parsed.

## Framework Execution

TO execute the framework, use the "enable_terminal.py" to connect to a network node of the simulation, such as "python3 enable_terminal n389". Once a node is joined, the framework can be started.

## Output

Besides the attack files, the framework will output several data representations of the data, if the user activated them as part of the parameter choices. The tool can generate a time-based view, which entails the attack time windows, the attack state on the grid, the IDS alerts, and potential critical grid states. The metric view visually represents all computed metrics in a single visualization. The framework also return the pprecise metric values and confusion matrix entrys in their own files. Examples can be seen in "data/example"

## Framework Extensions

Possible extensions to the tool:

- Grid scenarios
- New IDS support
- New Attacks
- New Observers for new data types
- New Metrics 
- New Visualization

## Auxiliary Tools

- "data-summary/summary" can give concise summaries of multiple attacks, such as metric averages and confidence intervals