# GRIDSAFE - Grid Security Assessment and Framework Evaluation

**A Comprehensive Framework for Evaluating Intrusion Detection Systems in Power Grids and Beyond**

This tool performs autonomous and data rich IDS assessments, specifically designed for industrial control networks and intrusion detection systems in power grids. While traditional evaluation procedures for IDS lack the complexity and consistency necessary to draw comparisons between results, GRIDSAFE and its underlying methodology strives to provide the most meaningful data possible. By mirroring every possible circumstance of the system, in which the IDS will operate in the future, we can ensure the most meaningful evaluation results, actually representing how the system will behave. For this to work, we perform an initial threat modeling specific to the power grid scenario, on which basis we make calculated decisions regarding the evaluation's cyberattack selection, and IDS integration into the network. GRIDSAFE then autonomously executes these attacks against Wattson's power grid simulation, collects all necessary data, and represents the results concisely. 

<img src="figures\Framework layout.png" alt="Relation Framework and Methodology" width="100%"/>

GRIDSAFE is the product of my master thesis "Evaluating Intrusion Detection Systems in Power Grids: A practical Framework". The thesis discusses a precise description of a complex evaluation methodology, which lays the groundwork for this framework, a technical description of the framework, as well as a discussion of our evaluation of Omicron's StationGuard and Suricata. For more insight, please refer to the [thesis](https://oleknief.com/files/academic-works/master-thesis.pdf).

<img src="figures/Methodology Framework Relation.png" alt="Relation Framework and Methodology" width="50%"/>

NOTE: Due to ethical considerations, we refrain from publishing the attack catalog in "/attacks". However, we provide the general attack layout (attack.py), an exemplary attack (RTU_disconnect.py), as well as our attack scenarios (scenarios/) to provide an example how to use the framework.


## Installation

In order to simulate power grids and their network infrastructure, we utilize the highly versatile simulation tool Wattson. For more information about how to work with this simulation, please refer to the website https://wattson.it/, which also includes installation instruction for the repository https://github.com/fkie-cad/wattson. Additionally, the tool requires the following dependencies: 

```
termcolor, paramiko, syslog_rfc5424_parser, dateutil, matplotlib, numpy, pillow
```

For our evaluation, we use our own developed attacks, as well as a selection of Wattson's attack library from https://gitlab.fkie.fraunhofer.de/cad-energy/wattson/wattson-attacks. However, both of these are not publicly accessible due to ethical considerations.

## Setup

After choosing a power grid compatible with Wattson, we still need to add the IDS to the environment and define our attacks. This section details the technical side of this procedure. The thesis details guidelines on how one should approach IDS sensor placement and configurations.

The “scenarios” folder contains the power grid scenario we use for our evaluation, as well as our adaptions to integrate IDSs (scenarios/powerowl_test/ids_extension.py). Apart from this extension, the scenario is part of Wattson and NOT my own work.


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

We also provide an explicit example for integrating Omicron's StationGuard in the "StationGuard" folder. The respective scenario extension can be found under "/scenarios/powerowl_test/ids_extension.py"

### Connect IDS and Framework

The framework supports automatic parsing of IDS alerts. However, this is highly dependent on the IDS.

- For IDS with SIEM integration:
1. Modify the IP and port of the IDS in the network in "phases.py"
2. Adjust the alert parsing based on the alert structure in "metrics/metrics_preprocessor.py" and "observer/alert_observer.py"

- For IDS generating an alert file:
1. Ensure that the files is accessible by the framework.
2. Adjust the alert parsing based on the alert structure in "metrics/metrics_preprocessor.py"

In bash-scripts/eval-suricata.sh, we showcase how to use file links to automatically save the respective alert file in the correct folder.


### Attack Selection

The attack selection is not yet accessible via parameters, as there would be too many choices. To adjust the attacks the framework executes, modify the "attack_phase()" of "phases.py" and add the attacks to "attack_queue". Implemented attack can be found in "attacks/catalog" (add your attack here), while we also offer "attacks/scenarios", which return the attack chains we use in the thesis. The framework will iterate through the queue, executing the attack one by one. For each attack, you can adjust several parameters, such as targets, duration, and idle time of the framework after the attack ends.


## Framework Parameters

To start the framework, we need to adjust several parameters, each of which is explained in the framework's help page, accessible via 
```python
python3 main.py -h
```

Most parameters define, how the folder in /data should be called, which phases should be executed (attack vs evaluation), which metrics to use, and which visualizations should be used. The IDS choice (StationGuard vs Suricata) defines the way, in which the IDS alerts are being parsed.

## Framework Execution

To execute the framework, use "enable_terminal.py" to connect to a network node of the simulation, such as 
```python
python3 enable_terminal n389
```
Once a node was joined, the framework can be started.

## Output

Besides the attack files, the framework will output several representations of the data, if the user activated them as part of the parameter choices. The tool can generate a time-based view, which entails the attack time windows, the attack state on the grid, the IDS alerts, and potential critical grid states. 

<img src="figures\timeview_example.png" alt="Relation Framework and Methodology" width="100%"/>

The metric view visually represents all computed metrics in a single visualization. The framework also return the precise metric values and confusion matrix entries in their own files. "data/example" contains an example of these representations for one framework execution.

<img src="figures\metrics_example.png" alt="Relation Framework and Methodology" width="100%"/>

Lasty, "data-summary/summary" is a separate script, that can give concise summaries of multiple attacks, such as metric averages and 95% confidence intervals. 

<img src="figures\example_metrics_summary.png" alt="Relation Framework and Methodology" width="100%"/>

Throughout my thesis, we evaluated a total over 2500 attacks and generated over 10 GB of data. By using the summary tool, we can still showcase much of our evaluation results, which "/data-summary" contains. We differentiate between evaluation data of the StationGuard, Suricata, and our initial technical validation. 

## Framework Extensions

The framework was built in a way, which makes it easily adaptable to other use cases. The following lists some of the ways, in which it is extendable:

- **Grid scenarios**: Add your own power grid scenario, by building it with Wattson
- **Additional IDS support**: Make any IDS of your choice compatible with the framework, in order to evaluate it with GRIDSAFE 
- **New attacks**: Add your own attacks, based on your specific threat model
- **New observers**: If you want to track data apart from IDS effectiveness, add your own observer for new data types, such as CPU utilization
- **New metrics**: Either add metric representing data collected by new observers, or add additional effectiveness metrics to the collection
- **New visualization**: If you require a different result representation, add your own! 

## Auxiliary Tools

To automate long evaluations of multiple executions for different attack chains, we developed several bash scripts, which can be found in "/bash-scripts". To use these, ensure that you adapt them to your evaluation environment! 

