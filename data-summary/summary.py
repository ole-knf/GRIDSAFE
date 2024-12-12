import json
import os
import statistics
import sys
from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def plot_confidence_interval(
    x, values, z=1.96, color="#2187bb", horizontal_line_width=0.25
):
    """
    Based on data, compute 95% confidence intervals for each metric
    """
    mean = statistics.mean(values)
    stdev = statistics.stdev(values)
    confidence_interval = z * stdev / sqrt(len(values))

    left = x - horizontal_line_width / 2
    top = mean - confidence_interval
    right = x + horizontal_line_width / 2
    bottom = mean + confidence_interval

    # Add all values to the plot
    plt.plot([x, x], [top, bottom], color=color)
    plt.plot([left, right], [top, top], color=color)
    plt.plot([left, right], [bottom, bottom], color=color)
    plt.plot(x, mean, "o", color="#f44336")

    # Roate acis for better clarity
    plt.xticks(rotation=15)

    return mean, confidence_interval


def visualize(data: dict):
    """
    For each metric, plot its mean value and their confience intervals
    """
    # Get all labels
    labels = []
    for metric in data:
        labels.append(metric)
    plt.xticks(range(1, len(data) + 1), labels)
    plt.title("Averages of Evaluation Results and Confidence Intervals")
    x_counter = 0
    metrics_dump = []

    # Add each metric
    for metric in data:
        x_counter += 1
        # Compute mean an confidence intervals
        mean, confidence_interval = plot_confidence_interval(x_counter, data[metric])
        entry = {}
        entry[metric] = {"mean": mean, "confidence_interval": confidence_interval}
        metrics_dump.append(entry)

    return metrics_dump


def visualize_attack_patterns(transparency: int, folder_prefix, start, end):
    """
    Load all time-based views and use transparency to lay them ontop of each other
    """

    num_images = end - start + 1
    individual_transparency = int(255 / num_images)

    baseimage = None
    for i in range(start, end + 1):
        # Load each picture
        folder_name = f"{folder_prefix}{i}"
        file_path = os.path.join(
            f"/home/wattson/Documents/code/data/{folder_name}", "timeview.png"
        )
        image = Image.open(file_path).convert("RGBA")
        # Apply transparency
        alpha = int(individual_transparency * transparency)
        transparent_image = image.copy()
        transparent_image.putalpha(alpha)
        if baseimage == None:
            baseimage = transparent_image
        else:
            baseimage = Image.alpha_composite(baseimage, image)

    return baseimage


def main(folder_prefix: str, start: int, end: int, file_prefix: str):
    """
    Computes a summary of multiple evaluation results.

    :param str folder_prefix: Name prefix of the folder in /data
    :param int start: First postfix number of the folder 
    :param int end: Last postfix number of the folder 
    :param str file_prefix: File prefix for addressing specific attacks
    """

    plt.rcParams["figure.dpi"] = 600

    # For each relevant folder, load metrics
    metrics_data = {}
    for i in range(start, end + 1):
        folder_name = f"{folder_prefix}{i}"
        file_path = os.path.join(
            f"/home/wattson/Documents/code/data/{folder_name}",
            f"{file_prefix}metrics.jsonl",
        )
        try:
            with open(file_path, "r") as f:
                metrics_data[i] = json.load(f)
        except FileNotFoundError:
            print("File not found! Might be intended!")
            print(file_path)
            exit()

    # Load values of the data
    metrics_list = []
    for metric in metrics_data[1]:
        metrics_list.append(metric)

    summary_data = {}
    for metric in metrics_data[1]:
        l = []
        for file in metrics_data:
            l.append(metrics_data[file][metric])
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
        summary_data[metric] = l

    # Copmute Plot
    metrics_data = visualize(summary_data)
    # Save figure
    fig_path = f"/home/wattson/Documents/code/data-summary/metrics-{folder_prefix}{start}-{end}{file_prefix}.png"
    plt.tight_layout()
    plt.savefig(fig_path)

    # Save average metric values
    metric_path = f"/home/wattson/Documents/code/data-summary/metrics-{folder_prefix}{start}-{end}{file_prefix}.jsonl"
    with open(metric_path, "w") as f:
        for entry in metrics_data:
            json.dump(entry, f)
            f.write("\n")

    # If the summary is not attack specific, but for whole attack chains, also generate average of time-based view across attack iterations 
    if file_prefix == "":
        image = visualize_attack_patterns(0.5, folder_prefix, start, end)
        image.save(
            f"/home/wattson/Documents/code/data-summary/timeview-{folder_prefix}{start}-{end}.png"
        )


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 summary.py <folder_prefix> <start> <end> <file_prefix>")
        sys.exit(1)

    # Parse args
    folder_prefix = sys.argv[1]
    start = int(sys.argv[2])
    end = int(sys.argv[3])
    if len(sys.argv) == 5:
        file_prefix = sys.argv[4]
    else:
        file_prefix = ""

    main(folder_prefix, start, end, file_prefix)
