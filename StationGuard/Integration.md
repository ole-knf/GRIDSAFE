
# How to integrate Stationguard into Wattson

### Sidenote

The StationGuard IDS does not come with any display output on the VM itself. It is only accessible over a web interface, which requires a different host in the network to access it. Since the tools for the first setup are .exe files, it is strongly recommended setting up a Windows VM in the network.

### Instructions

1. Set up a Windows VM the way it is described above for later access
2. Download and import the Stationguard VM in VirtualBox
3. Enable EFI for the VM (Settings - System - Motherboard - Extended Features - Enable EFI)
4. Modify the network connections. This needs to be done carefully, since StationGuard is not very transparent about this. The VM needs 5 Network adapters, which will already exist for the VM. If not, create them. All 5 need to be set to "bridged" mode. For every adapter except the second one (by default adapter 1, since the first one will be adapter 0), are required to be set to Promiscuous Mode (Settings - Network - Adapter - Advanced - Promiscuous Mode: Allow All). If this is not set, StatonGuard will not be able to monitor network packets which do not specifically mention the IDS' MAC Address.
5. Understand StationGuard's network settings. Since the VM is only accessible over the network, one network adapter is reserved for this communication. Out of the 5 adapters, the second is utilized for this (I have no clue why not the first or the last, but the second). The other 4 do not necessarily need to be set up, one would theoretically be enough if the network should only be monitored at one spot.
6. Create the network setup in wattson. Use the information above and the instructions from before to create one network adapter for the second interface, and up to 4 others for the network surveillance in places of your choice.
7. After this is done, be sure to bridge the network adapters of the StationGuard VM to the correct newly created interfaces
8. Activate port mirroring for all the surveilling ports. This can be done for one port as follows

```{python}

from wattson.cosimulation.control.interface.wattson_client import WattsonClient
from wattson.cosimulation.simulators.network.remote_network_emulator import RemoteNetworkEmulator

# Create the network emulator which will interfact with wattson

wattson_client = WattsonClient(namespace="auto", wait_for_namespace=True)
wattson_client.require_connection()
wattson_client.register()
network_emulator = RemoteNetworkEmulator(wattson_client=wattson_client)

# Define the switch and its interface for which the mirror should be started
node = network_emulator.get_node("YOUR SWITCH")
interface = node.get_interface("YOUR INTERFACE")

node.enable_mirror(interface)
print("Mirror for " + switch + " started")
```

9.  Boot the StationGuard VM. There is nothing to interact with, so continue with the next step
10. Boot into the Windows VM. Here you can use StationGuard 'Device Link', which will search for the StationGuard VM in the network. It will find one, over the specified interface (the second interface, interface 1), but most likely over a completely different IP in its own subnet. The device link lets you change this IP, which is not necessary, but recommendable. Here, the same constraints hold for the IP choice as for the VM integration in general.
11. Connect to the VM over the Web interface (port 20499, I think), or use the tool from StationGuard itself. Set a password and enter StationGuard. Remember to check if all interfaces in the web interface are set to passive.

A script for a full integration can be found in 'add_IDS_setup_own_subnet.py'. This script goes one step further and separates the StationGuard and Windows communication in a separate subnet

### Editing the fifth interface

The GUI of VirtualBox does only allow for 4 adapters to be adjustable in detail (the adapter to bridge to can still be changed if the interface was already created). In case this needs to be done, e.g. for enabling promiscuous mode, the VM can be edited over the CLI. To do so, open the '.vbox' file of the VM with a text editor of choice and adjust the settings.