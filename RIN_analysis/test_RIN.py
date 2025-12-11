
from Spectrum_RIN_class import SpectrumRIN

if __name__ == "__main__":
    rin = SpectrumRIN(r"C:\Users\kaiga\Documents\User\ETH\11.Semester JILA\PythonProject\CSV1.csv",
                      pd_gain_dB=35,
                      responsivity=0.22)
    # Plot raw Trace A
    rin.plot_trace("Trace A")

    # Compute RIN assuming 10 mW optical power
    freq, RIN_dBc = rin.compute_RIN("Trace A", optical_power_mW=10)

    # Plot RIN
    rin.plot_RIN(freq, RIN_dBc, "Trace A")