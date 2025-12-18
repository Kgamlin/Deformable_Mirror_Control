from nptdms import TdmsFile
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def readTdms(path, slot="Oscilloscope (PXI1Slot7)", channel="0"):
    tdms_file = TdmsFile.read(path)
    group = tdms_file["Oscilloscope - Waveform Data"]
    try:
        config_channel = tdms_file["Panel Configurations"][slot]
    except KeyError as e:
        print(tdms_file["Panel Configurations"].as_dataframe())
        print(tdms_file["Panel Configurations"].channels())
        print(tdms_file["Panel Configurations"].properties)
        raise KeyError(e)
    config = json.loads(config_channel.data[0])
    sample_rate = config["Instrument"]["Instrument Configuration"]["Timing"][
        "Manual Sample Rate"
    ]
    sample_pts = config["Instrument"]["Instrument Configuration"]["Timing"][
        "Manual Record Length"
    ]
    bManual_sample_rate = config["Instrument"]["Instrument Configuration"]["Timing"][
        "Manual Timing Settings"
    ]["Use Manual Sample Rate"]
    bManual_record_length = config["Instrument"]["Instrument Configuration"]["Timing"][
        "Manual Timing Settings"
    ]["Use Manual Record Length"]
    fft_data = group[
        f"FFT 1 (Channel {channel}) V/√Hz"
    ].data[
        1:
    ]  # somehow the fft data size is always 1 size larger than the sample_size/2, maunally ignoring the first points
    fft_freq = np.fft.fftfreq(n=sample_pts, d=1 / sample_rate)[: fft_data.shape[0]]
    print(
        f"bManual_sample_rate: {bManual_sample_rate}\n"
        f"bManual_record_length: {bManual_record_length}\n"
        f"sample_rate: {sample_rate}\n"
        f"sample_pts: {sample_pts}\n"
    )
    return_dict = {"freq": fft_freq, "VHz": fft_data}
    return pd.DataFrame(return_dict), return_dict


def calculate_rin_dBc_per_Hz(VHz, V_mean_V):
    """Calculate Relative Intensity Noise (RIN) from V/√Hz data.
    Parameters:
    ===========
        VHz (np.ndarray): Voltage noise spectral density in V/√Hz.
        V_mean (float): Mean voltage of the signal.
    Returns:
    ===========
        np.ndarray: RIN in dBc/Hz.
    """
    rin_linear = VHz / V_mean_V
    rin_dBc_per_Hz = 20 * np.log10(rin_linear)
    return rin_dBc_per_Hz


def plot_RIN_campaign_tdms(campaign: dict):
    base = Path(campaign["base_folder"])
    slot = campaign["tdms_settings"].get("slot")
    channel = campaign["tdms_settings"].get("channel")

    plt.figure(figsize=(9, 5))

    for meas in campaign["measurements"]:
        tdms_path = base / meas["file"]
        V_mean_V = meas["V_mean_V"]
        label = f'{meas["label"]} ({V_mean_V:.3f} V)'
        df, raw = readTdms(tdms_path, slot=slot, channel=channel)

        freq = df["freq"].to_numpy()
        VHz = df["VHz"].to_numpy()

        rin_dBc = calculate_rin_dBc_per_Hz(VHz, V_mean_V)

        plt.semilogx(freq, rin_dBc, label=label)

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("RIN (dBc/Hz)")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.show()