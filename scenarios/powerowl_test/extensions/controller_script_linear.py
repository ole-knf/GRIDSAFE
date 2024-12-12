import numpy as np
import pandas as pd

from wattson.apps.script_controller.interface import SoloScript
from time import sleep

from typing import TYPE_CHECKING

from wattson.iec104.common import MTU_READY_EVENT

if TYPE_CHECKING:
    from wattson.apps.script_controller import ScriptControllerApp


# noinspection DuplicatedCode
class EvaluationScript(SoloScript):
    def __init__(self, controller: "ScriptControllerApp"):
        super().__init__(controller)
        self.crd = True  # Command Realization Delay
        self.rrd = True  # Read Response Delay

        self.request_delay = 0.1  # One command every 80ms
        self.warmup = 10
        self.cool_down = 10
        self.iteration_gap = 5  # seconds between steps
        self.steps = 10  # 10 commands
        self.logger = self.controller.logger.getChild("EvaluationScript")

    def run(self):
        # self.logger.info("Waiting for MTU to be ready")
        # self.controller.coord_client.wait_for_event(MTU_READY_EVENT)
        self.logger.info("Warm-Up delay...")
        sleep(self.warmup)
        self.run_combined()
        sleep(self.cool_down)
        # Y U request shutdown? i like my sim running!
        # self.logger.info("Sending shutdown request..."),
        # self.controller.wattson_client.request_shutdown()

    def run_combined(self):
        crd_logger = self.logger.getChild("CRD")
        rrd_logger = self.logger.getChild("RRD")

        def crd_action(_pp_index, _coa, _ioa, _p_mw, _req, _total_req, _id, _total_id):
            crd_logger.info(
                f"[104] {_req}/{_total_req} -- {_id}/{_total_id} SGEN.{_pp_index}.p_mw = {_p_mw} MW ({_coa}.{_ioa})"
            )
            self.controller.set_data_point(coa=_coa, ioa=_ioa, value=_p_mw, timeout=5)

        def rrd_action(_coa, _ioa, _req, _total_req, _id, _total_id):
            rrd_logger.info(
                f"[104] {_req}/{_total_req} -- {_id}/{_total_id} Reading {_coa}.{_ioa}..."
            )
            val = self.controller.get_data_point(coa=_coa, ioa=_ioa)
            if val is None:
                rrd_logger.error(
                    f"[104] FAILED to read {_coa}.{_ioa} in step {_req}/{_total_req}"
                )

        gm = self.controller.remote_grid_model
        generators = gm.get_elements_by_type(
            "sgen"
        )  # gm.get_pandapower_elements("sgen")
        busses = gm.get_elements_by_type("bus")  # gm.get_pandapower_elements("bus")
        gen_count = len(generators)
        bus_count = len(busses)
        gen_list = [i.index for i in generators]
        bus_list = [i.index for i in busses]

        self.logger.info(f"Grid has {gen_count} generators")
        self.logger.info(f"Grid has {bus_count} busses")
        point_info = {"bus": {}, "sgen": {}}

        if self.crd:
            for pp_index in gen_list:
                for host, dps in self.controller.datapoints.items():
                    for p in dps:
                        protocol_data = p["protocol_data"]
                        coa = protocol_data["coa"]
                        ioa = protocol_data["ioa"]
                        providers = p["providers"]
                        for direction in ["targets"]:
                            if direction in providers:
                                for provider in providers[direction]:
                                    provider_data = provider["provider_data"]
                                    if (
                                        provider_data["grid_element"].split(".")[0]
                                        == "sgen"
                                    ):
                                        if (
                                            provider_data["attribute"]
                                            == "target_active_power"
                                        ):
                                            context = provider_data["context"]
                                            attribute = provider_data["attribute"]
                                            grid_element = provider_data["grid_element"]
                                            grid_value = self.controller.power_grid_model.get_grid_value_by_identifier(
                                                f"{grid_element}.{context}.{attribute}"
                                            )
                                            pmw = grid_value.get_value()
                                            point_info["sgen"][pp_index] = {
                                                "coa": coa,
                                                "ioa": ioa,
                                                "max_pmw": pmw,
                                            }

        if not self.rrd:
            for pp_index in bus_list:
                for host, dps in self.controller.datapoints.items():
                    for p in dps:
                        protocol_data = p["protocol_data"]
                        coa = protocol_data["coa"]
                        ioa = protocol_data["ioa"]
                        providers = p["providers"]
                        for direction in ["sources", "targets"]:
                            if direction in providers:
                                for provider in providers[direction]:
                                    provider_data = provider["provider_data"]
                                    if (
                                        provider_data["grid_element"].split(".")[0]
                                        == "bus"
                                    ):
                                        if provider_data["attribute"] == "active_power":
                                            context = provider_data["context"]
                                            attribute = provider_data["attribute"]
                                            grid_element = provider_data["grid_element"]
                                            grid_value = self.controller.power_grid_model.get_grid_value_by_identifier(
                                                f"{grid_element}.{context}.{attribute}"
                                            )
                                            pmw = grid_value.get_value()
                                            point_info["bus"][pp_index] = {
                                                "coa": coa,
                                                "ioa": ioa,
                                                "max_pmw": pmw,
                                            }

        requests_per_step = 0
        if self.crd:
            requests_per_step += gen_count
        if self.rrd:
            requests_per_step += bus_count
        total_requests = requests_per_step * self.steps
        requests = 0
        if total_requests == 0:
            self.logger.warning("No requests scheduled...")
            return

        self.logger.info("Starting linear test")
        for step in range(self.steps):
            self.logger.info(f"Step {step+1}/{self.steps}")
            if self.crd:
                for pp_index in gen_list:
                    sleep(self.request_delay)
                    requests += 1
                    info = point_info["sgen"][pp_index]
                    ioa = info["ioa"]
                    coa = info["coa"]
                    max_pmw = info["max_pmw"]
                    p_mw = 0.5 * max_pmw if step % 2 == 0 else max_pmw
                    crd_action(
                        pp_index,
                        coa,
                        ioa,
                        p_mw,
                        requests,
                        total_requests,
                        pp_index,
                        gen_count,
                    )
                sleep(self.iteration_gap)
            if not self.rrd:
                for pp_index in bus_list:
                    sleep(self.request_delay)
                    requests += 1
                    info = point_info["bus"][pp_index]
                    ioa = info["ioa"]
                    coa = info["coa"]
                    rrd_action(coa, ioa, requests, total_requests, pp_index, bus_count)
                sleep(self.iteration_gap)
