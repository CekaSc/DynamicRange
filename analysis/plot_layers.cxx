void plot_layers(int thetaMin, int thetaMax, int mode) {
    // 1. Setup global style for a cleaner look
    gROOT->SetStyle("ATLAS");
    gStyle->SetOptStat(0);          // Remove those messy statistics boxes
    gStyle->SetPadTickX(1);         // Ticks on all sides
    gStyle->SetPadTickY(1);
    gStyle->SetPalette(kRainBow);   // Professional color gradient
				    //
    //gStyle->SetPadRightMargin(0.07);
    //h_maxE_Layer8_top5
    string f_name = "sel_output/mum_10GeV_";
    f_name.append(to_string(thetaMin));
    f_name.append("_");
    f_name.append(to_string(thetaMax));
    f_name.append("deg_output.root");
    TFile *f = TFile::Open(f_name.c_str());
    cout<<f_name<<endl;
    if (!f || f->IsZombie()) return;

    TCanvas *c1 = new TCanvas("c1", "Layer Comparison", 800, 600);
    //c1->SetLogy();
    // 2. Create a legend (Top Right)
    auto legend = new TLegend(0.72, 0.50, 0.88, 0.88);
    legend->SetBorderSize(0);
    legend->SetFillStyle(0); // Transparent background

    std::vector<TH1D*> hists;
    double max_val = 0;

    // 3. Retrieve and style histograms
    for (int i = 1; i <= 11; ++i) {
        TString name;
	switch(mode){
	    case 1:
		name = TString::Format("h_allE_Layer%d", i);
		break;
	    case 2:
		name = TString::Format("h_allE_Layer%d_toQ", i);
		break;
	    case 3:
		name = TString::Format("h_allE_Layer%d_toI", i);
		break;
	    case 4:
		name = TString::Format("h_sumE_Layer%d", i);
		break;
	    case 5:
		name = TString::Format("h_sumQ_Layer%d", i);
		break;
	    case 6:
		name = TString::Format("h_sumSNR_Layer%d", i);
		break;
	    case 7:
		name = TString::Format("h_SNR_Layer%d", i);
		break;
	}
        TH1D *h = (TH1D*)f->Get(name);
        
        if (!h) continue;

        // Pick a color from the palette based on index
        int color_idx = gStyle->GetColorPalette(i * (gStyle->GetNumberOfColors() / 12.0));
        cout<<color_idx<<endl;
	h->SetLineColor(color_idx);
        h->SetLineWidth(2);
        
        // Find the global maximum to scale the Y-axis correctly
        if (h->GetMaximum() > max_val) max_val = h->GetMaximum();
	//h->SetMinimum(0.01);
        
        hists.push_back(h);
        legend->AddEntry(h, TString::Format("Layer %d", i), "l");
    }

    // 4. Draw them on the same canvas
    for (size_t i = 0; i < hists.size(); ++i) {
        hists[i]->GetYaxis()->SetRangeUser(0., max_val * 1.15); // Add 15% head room
        switch(mode){
	    case 1:
	        hists[i]->GetXaxis()->SetTitle("Energy Deposit [MeV]");
		break;
	    case 2:
	        hists[i]->GetXaxis()->SetTitle("Charge [fC]");
		break;
	    case 3:
	        hists[i]->GetXaxis()->SetTitle("Current [#muA]");
		break;
	    case 4:
	        hists[i]->GetXaxis()->SetTitle("Sum Energy Deposit [MeV]");
		break;
	    case 5:
	        hists[i]->GetXaxis()->SetTitle("Sum Charge [fC]");
		break;
	    case 6:
	        hists[i]->GetXaxis()->SetTitle("SNR");
		break;
	    case 7:
	        hists[i]->GetXaxis()->SetTitle("SNR");
		break;
	}
        hists[i]->GetYaxis()->SetTitle("Events");

        // "SAME" is the magic keyword to overlay plots
        hists[i]->Draw(i == 0 ? "HIST" : "HIST SAME");
    }

    legend->Draw();

    double leg_left = 0.4;

    TLatex atlaslabel;
    atlaslabel.SetTextAlign(12);
    atlaslabel.SetTextSize(0.04);
    atlaslabel.SetNDC();
    atlaslabel.DrawLatex(leg_left, 0.85, "#font[52]{#bf{ALLEGRO}} Simulation");

    TLatex sublabel;
    sublabel.SetTextAlign(12);
    sublabel.SetTextSize(0.035);
    sublabel.SetNDC();
    sublabel.DrawLatex(leg_left, 0.8 , "Gun particle: #mu^{-}");
    sublabel.DrawLatex(leg_left, 0.75, "Gun Energy: 10 GeV");
    sublabel.DrawLatex(leg_left, 0.7 , Form("Gun Theta: [%i^{#circ}, %i^{#circ}]", thetaMin, thetaMax));
    //sublabel.DrawLatex(leg_left, 0.65, "Simulated Events: 5000");

    // 5. Save the result
    string p_name = "plots/Muon_10GeV_";
    p_name.append(to_string(thetaMin));
    p_name.append("_");
    p_name.append(to_string(thetaMax));
    switch(mode){
	case 1:
            p_name.append("_Energy");
	    break;
	case 2:
            p_name.append("_Charge");
	    break;
	case 3:
            p_name.append("_Current");
	    break;
	case 4:
            p_name.append("_SumEnergy");
	    break;
	case 5:
            p_name.append("_SumCharge");
	    break;
	case 6:
            p_name.append("_SumSNR");
	    break;
	case 7:
            p_name.append("_SNR");
	    break;
    }
    p_name.append(".pdf");
    c1->SaveAs(p_name.c_str());
}
