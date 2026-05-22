from podio import root_io
import ROOT
import math
from g4units import GeV
from array import array
import dd4hep as dd4hepModule
from ROOT import dd4hep
import os

from .simulation import get_sim_output_files

def get_selection_output_files(config):
    sim = config["simulation"]
    sel = config["selection"]
    energy_str = sim["energy"].replace("*", "").replace(" ", "")
    files = []
    for theta_min, theta_max in sim["theta_bins"]:
        f = (
            f"{sel['output_dir']}"
            f"/{sim['particle'].replace('-','m').replace('+','p')}"
            f"_{energy_str}"
            f"_{theta_min}_{theta_max}deg"
            f"_output.root"
        )
        files.append(f)
    return files

def run_selection(config):
    sim = config["simulation"]
    os.makedirs(config["selection"]["output_dir"], exist_ok=True)

    input_files  = get_sim_output_files(config)
    output_files = get_selection_output_files(config)

    for (theta_min, theta_max), sim_file, output_file in zip(
        sim["theta_bins"], input_files, output_files
    ):
        print(f"Processing {sim_file} -> {output_file}")
        _process_one(
            sim_file=sim_file,
            output_file=output_file,
            capacitance_file=config["selection"]["capacitance_file"],
        )

def _process_one(sim_file, output_file, capacitance_file):
    decoder = dd4hep.BitFieldCoder(
        "system:4,cryo:1,type:3,subtype:3,layer:8,module:11,theta:10"
    )
    reader = root_io.Reader(sim_file)

    out = ROOT.TFile(output_file, "RECREATE")
    tree = ROOT.TTree("Energy", "MaxE Tree")

    layer_vectors = {}
    sumE_layer = {}
    for i in range(1, 12):
        layer_vectors[i] = ROOT.std.vector('double')()
        tree.Branch(f"allE_Layer{i}", layer_vectors[i])
        sumE_layer[i] = array('d', [0.0])
        tree.Branch(f"sumE_Layer{i}", sumE_layer[i], f"sumE_Layer{i}/D")

    sumE_buffer = array('d', [0.0])
    tree.Branch("sumE", sumE_buffer, "sumE/D")

    for event in reader.get("events"):
        hits = event.get("ECalBarrelModuleThetaMerged")
        if not hits:
            continue

        sum_energy_per_layer = {i: 0 for i in range(1, 12)}

        for i in range(1, 12):
            layer_vectors[i].clear()

        sumE = 0
        for hit in hits:
            cellID = hit.getCellID()
            pos = hit.getPosition()
            layer = decoder.get(cellID, "layer") + 1
            energy = hit.getEnergy()
            sumE += energy
            sum_energy_per_layer[layer] += energy
            layer_vectors[layer].push_back(energy)

        for i in range(1, 12):
            sumE_layer[i][0] = sum_energy_per_layer[i]
        sumE_buffer[0] = sumE
        tree.Fill()

    tree.Write()
    out.Close()
