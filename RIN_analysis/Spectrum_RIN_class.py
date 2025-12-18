from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


class SpectrumRIN:
    """
    Computes RIN from a DSA spectrum measured in dBm.

    User provides configuration dictionary:
        {
            "responsivity_A_per_W": ...,
            "transimpedance_V_per_A": ...,   # effective gain G_eff
            "optical_power_W": ...,
        }

    IMPORTANT:
        If the measurement device was 50 Ω terminated,
        the user must manually supply:

            G_eff = G_nominal / 2

        because voltage is halved by output/input matching.
    """

    def __init__(self, filepath: str, config: dict):
        self.filepath = filepath

        # Required config entries
        self.R_A_per_W = config["responsivity_A_per_W"]
        self.G_V_per_A = config["transimpedance_V_per_A"]  # effective gain already!
        self.RBW_Hz = config["res_bandwidth_Hz"]

        self.PD_voltage_V = config["PD_voltage_mV"]*1e-3
        self.P0_W = config["optical_power_W"]

        # Storage
        self.params = {}
        self.traces = {}

        self._load_csv()

    # ----------------------------------------------------------------------
    def _load_csv(self):
        with open(self.filepath, "r") as f:
            lines = [ln.strip() for ln in f.readlines()]

        idx = 0
        current_trace = None

        while idx < len(lines):
            parts = lines[idx].split(",")

            # Metadata
            if parts[0] not in ["Trace Name", "Trace Data"]:
                if len(parts) > 1:
                    self.params[parts[0]] = parts[1:]
                idx += 1
                continue

            # New trace
            if parts[0] == "Trace Name":
                current_trace = parts[1]
                self.traces[current_trace] = {"freq_Hz": [], "power_dBm": []}
                idx += 1
                continue

            # Read Trace Data
            if parts[0] == "Trace Data":
                idx += 1
                while idx < len(lines):
                    row = lines[idx].split(",")
                    if len(row) < 2:
                        break
                    try:
                        f = float(row[0])
                        p = float(row[1])
                        self.traces[current_trace]["freq_Hz"].append(f)
                        self.traces[current_trace]["power_dBm"].append(p)
                        idx += 1
                    except ValueError:
                        break
                continue

            idx += 1

        # Convert to numpy
        for name, tr in self.traces.items():
            tr["freq_Hz"] = np.array(tr["freq_Hz"])
            tr["power_dBm"] = np.array(tr["power_dBm"])

        print(f"[INFO] Loaded {len(self.traces)} traces.")
        for t in self.traces:
            print(f"   - {t}: {len(self.traces[t]['freq_Hz'])} points")

    # ----------------------------------------------------------------------
    def compute_RIN_dBc_per_Hz(self, trace_name: str):
        tr = self.traces[trace_name]
        freq_Hz = tr["freq_Hz"]
        power_dBm = tr["power_dBm"]

        # dBm → electrical power integrated over RBW [W]
        P_elec_W = 10 ** ((power_dBm - 30) / 10)

        # Divide by RBW to get power spectral density [W/Hz]
        S_P_W_per_Hz = P_elec_W / self.RBW_Hz

        # Convert electrical power to voltage noise PSD:
        # dBm is always referenced to 50 Ω system unless otherwise specified

        # P = V^2 / R → V^2 = P * 50
        #voltage noise PSD
        S_V_V2_per_Hz = S_P_W_per_Hz * 50.0


        # DC photovoltage either calculate with PD params or directly measure on the Osci (much more precise)
        V0_V = self.R_A_per_W * self.G_V_per_A * self.P0_W if self.PD_voltage_V is None else self.PD_voltage_V

        # RIN PSD = S_I / I0^2
        RIN_linear = S_V_V2_per_Hz / (V0_V)**2

        # Convert to dBc/Hz
        RIN_dBc_per_Hz = 10 * np.log10(RIN_linear)

        return freq_Hz, RIN_dBc_per_Hz

    def get_RIN(self, trace_name: str):
        freq, rin = self.compute_RIN_dBc_per_Hz(trace_name)
        return freq, rin

    # ----------------------------------------------------------------------
    def create_title(self, trace_name: str, user_comment: str | None = None):
        """
        Create a standardized plot title including key measurement parameters.

        Parameters shown:
        - Trace name
        - RBW
        - DC photovoltage source (measured vs computed)
        - Optional user comment (e.g. 'DM off')
        """

        if self.PD_voltage_V is None:
            v0_str = "V0 from G·R·P0"
        else:
            v0_str = f"V0_PD = {self.PD_voltage_V*1e3:.3g} mV (measured)"

        title = (
            f"{trace_name} | "
            f"RBW = {self.RBW_Hz:.3g} Hz | "
            f"{v0_str}"
        )

        if user_comment is not None:
            title += f" | {user_comment}"

        return title

    # ----------------------------------------------------------------------

    def plot_trace(self, trace_name: str, user_comment:str|None = None):
        tr = self.traces[trace_name]
        plt.figure(figsize=(8, 4))
        plt.semilogx(tr["freq_Hz"], tr["power_dBm"])
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Power (dBm)")
        plt.title(self.create_title(trace_name,user_comment))
        plt.grid(True, which="both")
        # plt.show()

    # ----------------------------------------------------------------------
    def plot_RIN(self, freq_Hz, RIN_dBc_per_Hz, trace_name: str, user_comment:str|None = None):
        plt.figure(figsize=(8, 4))
        plt.semilogx(freq_Hz, RIN_dBc_per_Hz)
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("RIN (dBc/Hz)")
        plt.title(self.create_title(trace_name,user_comment))
        plt.grid(True, which="both")
        # plt.show()

    def plot_spectrum_and_RIN(self, trace_name: str, user_comment:str|None = None):
        """
        Plot raw DSA spectrum (dBm/Hz) and RIN (dBc/Hz) on the same frequency axis
        using twin y-axes.
        """

        tr = self.traces[trace_name]
        freq_Hz = tr["freq_Hz"]
        power_dBm = tr["power_dBm"]

        # Compute RIN
        freq, RIN_dBc = self.compute_RIN_dBc_per_Hz(trace_name)

        fig, ax1 = plt.subplots(figsize=(8, 4))

        # Left axis: raw electrical spectrum
        ax1.semilogx(freq_Hz, power_dBm, color="tab:blue", label="DSA Spectrum")
        ax1.set_xlabel("Frequency (Hz)")
        ax1.set_ylabel("Power Spectral Density (dBm/Hz)", color="tab:blue")
        ax1.tick_params(axis="y", labelcolor="tab:blue")
        ax1.grid(True, which="both")

        # Right axis: RIN
        ax2 = ax1.twinx()
        ax2.semilogx(freq, RIN_dBc, color="tab:red", label="RIN")
        ax2.set_ylabel("RIN (dBc/Hz)", color="tab:red")
        ax2.tick_params(axis="y", labelcolor="tab:red")

        # Title
        plt.title(f"Spectrum vs RIN - " + self.create_title(trace_name,user_comment))

        # Legend handling
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

        plt.tight_layout()
        # plt.show()

def plot_RIN_campaign(campaign: dict):
    base = Path(campaign["base_folder"])
    global_cfg = campaign["global"]

    plt.figure(figsize=(9, 5))

    for meas in campaign["measurements"]:
        csv_path = base / meas["csv"]

        cfg = {
            **global_cfg,
            "optical_power_W": meas["optical_power_W"],
            "PD_voltage_mV": meas["PD_voltage_mV"],
        }

        rin = SpectrumRIN(csv_path, cfg)
        freq, rin_dBc = rin.get_RIN(meas["trace"])

        label = f'{meas["label"]} ({meas["PD_voltage_mV"]:.0f} mV)'

        plt.semilogx(freq, rin_dBc, label=label)

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("RIN (dBc/Hz)")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.show()