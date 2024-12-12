import matplotlib.pyplot as plt
import numpy as np

from metrics.metrics import Metrics


class Visualizer:
    def __init__(self, metrics: Metrics) -> None:
        """
        Visualizer object, which visualizes the evaluation results

        :param Metrics metrics: Metrics object which contains all metric calulcations
        """
        self.metrics = metrics
        self.metrics_preprocessor = metrics.metrics_preprocessor

    def create_timeview(self):
        """
        Creates a time-based view of the evaluation. Strongly correlates to the overarching evaluation data structure
        """

        # Ensure high resultion and thin ticks, as we have quite a lot
        plt.rcParams["figure.dpi"] = 600
        tick_count = len(self.metrics_preprocessor.time_intervals)
        ticks = np.arange(0, tick_count)

        # sort dict based on key
        ordered_intervals = dict(
            sorted(self.metrics_preprocessor.time_intervals.items())
        )

        # map data structure values to each tick
        attack_ticks: list[int] = []
        network_ticks: list[int] = []
        alert_ticks: list[int] = []
        grid_ticks: list[int] = []
        for key in ordered_intervals:
            attack_ticks.append(int(ordered_intervals[key]["attack"]))
            network_ticks.append(int(ordered_intervals[key]["network_activity"]))
            alert_ticks.append(int(ordered_intervals[key]["alert"]))
            grid_ticks.append(int(ordered_intervals[key]["critical_voltage"]))

        #Add an axis for each data source
        fig, ax = plt.subplots()
        ax.bar(
            ticks,
            attack_ticks,
            width=1.0,
            color="red",
            label="Attacks",
            alpha=0.7,
            bottom=3,
        )
        ax.bar(
            ticks,
            network_ticks,
            width=1.0,
            color="orange",
            label="Attack impact on network/grid",
            alpha=0.7,
            bottom=2,
        )
        ax.bar(
            ticks,
            alert_ticks,
            width=1.0,
            color="black",
            label="Alerts",
            alpha=0.7,
            bottom=1,
        )
        ax.bar(
            ticks,
            grid_ticks,
            width=1.0,
            color="blue",
            label="Critical Voltage",
            alpha=0.7,
            bottom=0,
        )

        ax.set_yticks(ticks=[0.5, 1.5, 2.5, 3.5])
        ax.set_yticklabels(
            ["Critical Grid States", "IDS Alerts", "Malicious Activity", "Attacks"]
        )
        ax.set_xlabel("Elapsed Time in 0.5 second intervals")
        ax.set_title("Time-based View of Evaluation")

        # Save figure to the path
        fig_path = f"/home/wattson/Documents/code/data/{self.metrics_preprocessor.project_name}/timeview.png"
        plt.tight_layout()
        plt.savefig(fig_path, dpi=2000)

        return True

    def create_radar_chart(self, metrics: dict[str, float], filename_prefix=""):
        """
        Create a radar chart of all metrics

        :param list[str, float] metrics: A list of metrics with their corresponding values
        :param str filename_prefix: Prefic for the filename, if we compute this chart for only one of multiple attacks 
        """
        plt.rcParams["figure.dpi"] = 600
        num_metrics = len(metrics)
        values = []
        names = []
        
        # Get each metric with the values and make names readable
        for metric in metrics:
            values.append(metrics[metric])
            if metric == "inverse_precision":
                metric = "inv. prec."
            if metric == "detection_rate":
                metric = "det. rate"
            if metric == "missrate":
                metric = "miss rate"
            if metric == "inverse_recall":
                metric = "inv. rec."
            if metric == "f_score":
                metric = "f-score"
            names.append(metric)

        # angles for the metrics
        angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        # Add every metric for its own angle
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.fill(angles, values, color="blue", alpha=0.25)
        ax.plot(angles, values, color="blue", linewidth=2)

        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(names)
        ax.set_theta_offset(np.pi / 2)
        ax.set_title("Radar Chart of Evaluation Results")

         # Factor to adjust distance
        label_distance = 1.6 
        # Adjust padding proportionally
        ax.tick_params(
            axis="x", pad=20 * (label_distance - 1)
        )  

        # save figure
        fig_path = f"/home/wattson/Documents/code/data/{self.metrics_preprocessor.project_name}/{filename_prefix}metrics.png"
        # plt.tight_layout()
        plt.savefig(fig_path, bbox_inches="tight")

        return True
