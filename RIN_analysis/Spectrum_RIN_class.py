import numpy as np
import matplotlib.pyplot as plt


class SpectrumRIN:
    def __init__(self, filepath, pd_gain_dB=35, responsivity=0.22):
        self.filepath = filepath

        # Photodiode parameters
        self.pd_gain_dB = pd_gain_dB
        self.Z = 10**(pd_gain_dB / 20)   # transimpedance V/A
        self.responsivity = responsivity

        # Storage
        self.params = {}
        self.traces = {}   # {"Trace A": {"freq": ..., "power_dBm": ...}}

        # Load the CSV
        self._load_csv()

    # ---------------------------------------------------------------
    def _load_csv(self):
        with open(self.filepath, "r") as f:
            lines = [ln.strip() for ln in f.readlines()]

        idx = 0
        current_trace_name = None

        while idx < len(lines):
            line = lines[idx]
            parts = line.split(",")

            # CASE 1: Metadata before any trace
            if parts[0] not in ["Trace Name", "Trace Data"]:
                key = parts[0]
                self.params[key] = parts[1:]
                idx += 1
                continue

            # CASE 2: New trace begins
            if parts[0] == "Trace Name":
                current_trace_name = parts[1]
                self.traces[current_trace_name] = {"freq": [], "power_dBm": []}
                idx += 1
                continue

            # CASE 3: Trace Data section begins
            if parts[0] == "Trace Data":
                idx += 1  # move to first numeric line
                # Read numeric rows until we hit a non-numeric line
                while idx < len(lines):
                    row = lines[idx].split(",")
                    if len(row) < 2:
                        break
                    try:
                        f = float(row[0])
                        p = float(row[1])
                        self.traces[current_trace_name]["freq"].append(f)
                        self.traces[current_trace_name]["power_dBm"].append(p)
                        idx += 1
                    except ValueError:
                        break
                continue

            idx += 1

        # Convert to numpy arrays
        for name, tr in self.traces.items():
            tr["freq"] = np.array(tr["freq"])
            tr["power_dBm"] = np.array(tr["power_dBm"])

        print(f"[INFO] Loaded {len(self.traces)} traces:")
        for t in self.traces:
            print(f"   - {t}: {len(self.traces[t]['freq'])} points")

    # ---------------------------------------------------------------
    def compute_RIN(self, trace_name, optical_power_mW):
        tr = self.traces[trace_name]

        freq = tr["freq"]
        P_dBm = tr["power_dBm"]

        # dBm → W
        P_watts = 10**((P_dBm - 30) / 10)

        # Voltage PSD
        S_V = P_watts * 50

        # Current PSD
        S_I = S_V / (self.Z**2)

        # DC photocurrent
        P_W = optical_power_mW * 1e-3
        I_dc = self.responsivity * P_W

        # RIN
        RIN_linear = S_I / (I_dc**2)
        RIN_dBc = 10 * np.log10(RIN_linear)

        return freq, RIN_dBc

    # ---------------------------------------------------------------
    def plot_trace(self, trace_name):
        tr = self.traces[trace_name]
        plt.figure(figsize=(8,4))
        plt.plot(tr["freq"], tr["power_dBm"])
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Power (dBm)")
        plt.title(f"{trace_name} – Spectrum")
        plt.grid(True)
        plt.show()

    # ---------------------------------------------------------------
    def plot_RIN(self, freq, RIN_dBc, trace_name):
        plt.figure(figsize=(8,4))
        plt.semilogx(freq, RIN_dBc)
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("RIN (dBc/Hz)")
        plt.title(f"RIN – {trace_name}")
        plt.grid(True, which="both")
        plt.show()


