from pathlib import Path

from powerowl.derivators.default_derivator import DefaultDerivator
from powerowl.performance.timing import Timing
import pandapower.networks as ppn
from powerowl.power_owl import PowerOwl
from powerowl.simulators.pandapower import PandaPowerGridModel

Timing.enabled = True
Timing.sub_timing_visibility_level = 3

with Timing("Total"):
    with Timing("Power Grid Parsing"):
        net = ppn.create_cigre_network_mv(with_der="all")
        grid_model = PandaPowerGridModel()
        grid_model.from_external(net)
        # Import pandapower model into PowerOwl
        owl = PowerOwl(power_grid=grid_model)
        owl.derive(
            derivator_class=DefaultDerivator,
            config={
                "abstract-from-field-devices": True,
                "field-device-attachment": "rtu-hub",
                "network-segregation-degree": 1,
                "force-subnet-tree": True,
            },
        )

    with Timing("Visualization"):
        with Timing("Layout"):
            owl.layout()
    with Timing("Export"):
        # owl.save_to_file(Path("cigre_mv_all_dpp.json"))
        owl.export_scenario(Path(__file__).parent)
