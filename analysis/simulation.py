import os
import subprocess

def run_simulation(config):
    sim = config["simulation"]
    os.makedirs(sim["output_dir"], exist_ok=True)

    for theta_min, theta_max in sim["theta_bins"]:
        output_file = (
            f"{sim['output_dir']}/sim"
            f"_{sim['particle'].replace('-','m').replace('+','p')}"
            f"_{theta_min}_{theta_max}deg"
            f"_{sim['n_events']}evts"
            f".root"
        )

        cmd = [
            "ddsim",
            "--enableGun",
            "--gun.distribution", "uniform",
            "--gun.energy", sim["energy"],
            "--gun.particle", sim["particle"],
            "--gun.thetaMin", f"{theta_min}*degree",
            "--gun.thetaMax", f"{theta_max}*degree",
            "--numberOfEvents", str(sim["n_events"]),
            "--outputFile", output_file,
            "--random.enableEventSeed",
            "--random.seed", str(sim["seed"]),
            "--compactFile", os.path.expandvars(sim["compact_file"]),
        ]

        print(f"Running: theta [{theta_min}, {theta_max}] deg -> {output_file}")
        subprocess.run(cmd, check=True)
