import os
from .plot_layers import plot_one


def plot_all(config):
    sim = config["simulation"]
    plot_cfg = config["plots"]
    os.makedirs(plot_cfg["output_dir"], exist_ok=True)

    for theta_min, theta_max in sim["theta_bins"]:
        for hist_name in plot_cfg["histograms"]:
            print(f"Plotting theta [{theta_min},{theta_max}] {hist_name}")
            plot_one(config, theta_min, theta_max, hist_name)
