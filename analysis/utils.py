import ROOT
import math
import analysis.constants as C

_noise_cache = {}

def _get_noise_file(noise_file_path):
    if noise_file_path not in _noise_cache:
        f = ROOT.TFile.Open(noise_file_path, "READ")
        if not f or f.IsZombie():
            raise RuntimeError(f"Cannot open noise file: {noise_file_path}")
        _noise_cache[noise_file_path] = f
    return _noise_cache[noise_file_path]

def get_ENC(layer, theta, noise_file_path):
    ff = _get_noise_file(noise_file_path)
    hist = ff.Get(f"h_elecNoise_fcc_{layer}")
    if not hist:
        print(f"Error: h_elecNoise_fcc_{layer} not found.")
        return None
    return hist.Interpolate(theta)

def get_dn_vd(n, mode):
    sumFront = sum(C.LENGTH[:n-1])
    length_n = sumFront + C.LENGTH[n-1] / 2
    dn = C.D_MIN + (length_n / C.SUM_L) * (C.D_MAX - C.D_MIN)
    match mode:
        case 1: E_mag = C.HV / dn
        case 2: E_mag = C.HV / dn if n <= 6 else C.HV2 / dn
        case 3: E_mag = 10.0
    vd = _calculate_vd(C.T_LAR, E_mag)
    return dn * 1e-2, vd * 1e3  # m, m/s

def _calculate_vd(T, E):
    p1,p2,p3,p4,p5,p6,T0 = -0.01481,-0.0075,0.141,12.4,1.627,0.317,90.371
    term1 = p1 * (T - T0) + 1
    term2 = p3 * E * math.log(1 + p4/E) + p5 * (E**p6)
    term3 = p2 * (T - T0)
    return term1 * term2 + term3

def get_theta(x, y, z):
    r = math.sqrt(x**2 + y**2 + z**2)
    return math.degrees(math.acos(z / r))
