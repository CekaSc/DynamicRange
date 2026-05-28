import ROOT
import math
from .selection import get_selection_output_files
from .utils import get_ENC, get_dn_vd
import analysis.constants as C

def make_histograms(config):
    sim     = config["simulation"]
    histo_cfg = config["histograms"]
    noise_file = histo_cfg["noise_file"]

    input_files = get_selection_output_files(config)

    for (theta_min, theta_max), input_file in zip(sim["theta_bins"], input_files):
        print(f"Making histograms: {input_file}")
        _process_one(
            file_path=input_file,
            tree_name="Energy",
            theta_min=theta_min,
            theta_max=theta_max,
            hv_mode=histo_cfg["hv_mode"],
            noise_file=noise_file,
        )

def _process_one(file_path, tree_name, theta_min, theta_max, hv_mode, noise_file):
    f = ROOT.TFile.Open(file_path, "UPDATE")
    if not f or f.IsZombie():
        print(f"Error: could not open {file_path}")
        return

    df   = ROOT.RDataFrame(tree_name, file_path)
    theta_mid = (theta_min + theta_max) / 2.0

    for i in range(1, 12):
        ENC  = get_ENC(i, theta_mid, noise_file)
        d, vd = get_dn_vd(i, hv_mode)

        EtoQ = (C.Q * C.R * C.GEV2EV / C.W_LAR / 2) * 1e12  # GeV -> fC
        EtoI = (EtoQ * vd / d) * 1e-6                         # fC -> uA

        leaf      = f"allE_Layer{i}"
        sumE_leaf = f"sumE_Layer{i}"
        sumQ_leaf = f"sumQ_Layer{i}"

        top_data  = df.AsNumpy(columns=[leaf])
        sumE_data = df.AsNumpy(columns=[sumE_leaf])

        hists = {
            "allE":   ROOT.TH1D(f"h_{leaf}",          f"{leaf}",          100, 0, 5),
            "allQ":   ROOT.TH1D(f"h_{leaf}_toQ",       f"{leaf} charge",   100, 0, 5*EtoQ),
            "maxE":   ROOT.TH1D(f"h_maxE_Layer{i}",    f"maxE Layer {i}",  100, 0, 5),
            "maxQ":   ROOT.TH1D(f"h_maxQ_Layer{i}",    f"maxQ Layer {i}",  100, 0, 5*EtoQ),
            "sumE":   ROOT.TH1D(f"h_{sumE_leaf}",      f"{sumE_leaf}",     100, 0, 15),
            "sumQ":   ROOT.TH1D(f"h_{sumQ_leaf}",      f"{sumQ_leaf}",     100, 0, 15*EtoQ),
            "SNR":    ROOT.TH1D(f"h_SNR_Layer{i}",     f"SNR Layer {i}",   100, 0, 50),
            "maxSNR": ROOT.TH1D(f"h_maxSNR_Layer{i}",  f"maxSNR Layer {i}",100, 0, 50),
            "sumSNR": ROOT.TH1D(f"h_sumSNR_Layer{i}",  f"sumSNR Layer {i}",100, 0, 50),
        }

        for val in sumE_data[sumE_leaf]:
            hists["sumE"].Fill(val * 1e3)
            hists["sumQ"].Fill(val * 1e3 * EtoQ)
            hists["sumSNR"].Fill(val * 1e3 * EtoQ * 6241.5 / (ENC * math.sqrt(3)))

        for val_event in top_data[leaf]:
            if len(val_event) > 0:
                max_val = max(val_event)
                hists["maxE"].Fill(max_val * 1e3)
                hists["maxQ"].Fill(max_val * 1e3 * EtoQ)
                hists["maxSNR"].Fill(max_val * 1e3 * EtoQ * 6241.5 / ENC)
            for val in val_event:
                hists["allE"].Fill(val * 1e3)
                hists["allQ"].Fill(val * 1e3 * EtoQ)
                hists["SNR"].Fill(val * 1e3 * EtoQ * 6241.5 / ENC)

        f.cd()
        for h in hists.values():
            h.Write("", ROOT.TObject.kOverwrite)
        print(f"  Layer {i} done")

    f.Close()
