import argparse
import yaml
from analysis import run_simulation, run_selection, make_histograms, plot_all

def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="ALLEGRO EDM4HEP analysis pipeline")
    parser.add_argument("--config",    default="config.yaml", help="path to config file")
    parser.add_argument("--simulate",  action="store_true",   help="run ddsim simulation")
    parser.add_argument("--select",    action="store_true",   help="run selection (EDM4HEP -> TTree)")
    parser.add_argument("--histogram", action="store_true",   help="make histograms from TTree")
    parser.add_argument("--plot",      action="store_true",   help="run plot_layers.cxx")
    parser.add_argument("--all",       action="store_true",   help="run full pipeline")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.all or args.simulate:  run_simulation(config)
    if args.all or args.select:    run_selection(config)
    if args.all or args.histogram: make_histograms(config)
    if args.all or args.plot:      plot_all(config)

if __name__ == "__main__":
    main()
