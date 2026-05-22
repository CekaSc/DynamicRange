import subprocess
import os
from .selection import get_selection_output_files

def plot_all(config):
    sim = config["simulation"]
    plot_cfg = config["plots"]
    os.makedirs(plot_cfg["output_dir"], exist_ok=True)

    for theta_min, theta_max in sim["theta_bins"]:
        for mode in plot_cfg["modes"]:
            print(f"Plotting theta [{theta_min},{theta_max}] mode {mode}")
            subprocess.run([
                "root", "-l", "-b", "-q",
                f"plot_layers.cxx({theta_min},{theta_max},{mode})"
            ], check=True)
