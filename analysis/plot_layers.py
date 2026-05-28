import ROOT
import os

HISTOGRAM_CONFIG = {
    "allE_Layer":     ("Energy Deposit [MeV]",   "_Energy"),
    "allE_Layer_toQ": ("Charge [fC]",            "_Charge"),
    "allE_Layer_toI": ("Current [#muA]",         "_Current"),
    "maxE_Layer":     ("Max Energy Deposit [MeV]", "_MaxEnergy"),
    "maxQ_Layer":     ("Max Charge [fC]",         "_MaxCharge"),
    "maxSNR_Layer":   ("Max SNR",                 "_MaxSNR"),
    "sumE_Layer":     ("Sum Energy Deposit [MeV]", "_SumEnergy"),
    "sumQ_Layer":     ("Sum Charge [fC]",          "_SumCharge"),
    "SNR_Layer":      ("SNR",                      "_SNR"),
    "sumSNR_Layer":   ("Sum SNR",                  "_SumSNR"),
}


def plot_one(config, theta_min, theta_max, hist_base_name):
    sim = config["simulation"]
    plot_cfg = config["plots"]
    sel_cfg = config["selection"]

    energy_str = sim["energy"].replace("*", "").replace(" ", "")
    particle_str = sim["particle"].replace("-", "m").replace("+", "p")

    input_file = (
        f"{sel_cfg['output_dir']}/{particle_str}_{energy_str}"
        f"_{theta_min}_{theta_max}deg_output.root"
    )

    x_label, out_suffix = HISTOGRAM_CONFIG[hist_base_name]

    ROOT.gROOT.SetStyle("ATLAS")
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetPalette(ROOT.kRainBow)

    f = ROOT.TFile.Open(input_file)
    if not f or f.IsZombie():
        print(f"Error: cannot open {input_file}")
        return

    c = ROOT.TCanvas("c", "Layer Comparison", 800, 600)
    legend = ROOT.TLegend(0.72, 0.50, 0.88, 0.88)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)

    hists = []
    max_val = 0

    for layer in range(1, 12):
        hname = f"h_{hist_base_name}{layer}"
        h = f.Get(hname)
        if not h:
            continue

        color_idx = ROOT.gStyle.GetColorPalette(
            layer * (ROOT.gStyle.GetNumberOfColors() / 12.0)
        )
        h.SetLineColor(color_idx)
        h.SetLineWidth(2)

        if h.GetMaximum() > max_val:
            max_val = h.GetMaximum()

        hists.append((h, layer))

    for i, (h, layer) in enumerate(hists):
        h.GetYaxis().SetRangeUser(0.0, max_val * 1.15)
        h.GetXaxis().SetTitle(x_label)
        h.GetYaxis().SetTitle("Events")
        h.Draw("HIST SAME" if i > 0 else "HIST")
        legend.AddEntry(h, f"Layer {layer}", "l")

    legend.Draw()

    leg_left = 0.4
    latex = ROOT.TLatex()
    latex.SetTextAlign(12)
    latex.SetTextSize(0.04)
    latex.SetNDC()
    latex.DrawLatex(leg_left, 0.85, "#font[52]{#bf{ALLEGRO}} Simulation")

    latex.SetTextSize(0.035)
    latex.DrawLatex(leg_left, 0.80, f"Gun particle: {sim['particle']}")
    latex.DrawLatex(leg_left, 0.75, f"Gun Energy: {sim['energy']}")
    latex.DrawLatex(leg_left, 0.70, f"Gun Theta: [{theta_min}^{{#circ}}, {theta_max}^{{#circ}}]")

    out_file = (
        f"{plot_cfg['output_dir']}/{particle_str}_{energy_str}"
        f"_{theta_min}_{theta_max}{out_suffix}.pdf"
    )
    c.SaveAs(out_file)
    print(f"  Saved {out_file}")
