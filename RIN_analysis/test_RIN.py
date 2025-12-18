

from Spectrum_RIN_class import plot_RIN_campaign
from RIN_analysis_Kaizhao import plot_RIN_campaign_tdms

if __name__ == "__main__":
#     campaign = {
#         "base_folder": r"C:\Users\kaiga\Documents\User\ETH\11.Semester JILA\DM_Control\RIN_data\2025-12-15_14-00-00",
#
#         "global": {
#             "responsivity_A_per_W": None,
#             "transimpedance_V_per_A": None,
#             "res_bandwidth_Hz": 10,
#         },
#
#         "measurements": [
#             {
#                 "csv": "CSV1.csv",
#                 "trace": "Trace A",
#                 "PD_voltage_mV": 2.45 / 2 * 1e3,
#                 "optical_power_W": None,
#                 "label": "Background"
#             },
#             {
#                 "csv": "CSV2.csv",
#                 "trace": "Trace A",
#                 "PD_voltage_mV": 2.45 / 2 * 1e3,
#                 "optical_power_W": None,
#                 "label": "DM OFF"
#             },
#             {
#                 "csv": "CSV3.csv",
#                 "trace": "Trace A",
#                 "PD_voltage_mV": 2.52 / 2 * 1e3,
#                 "optical_power_W": None,
#                 "label": "DM ON"
#             },
#         ]
#     }
#
#     plot_RIN_campaign(campaign)

    campaign_tdms = {
        "base_folder": r"C:\Users\kaiga\Documents\User\ETH\11.Semester JILA\DM_Control\RIN_data\2025-12-15_15-22-00",

        "tdms_settings": {
            "slot": "Oscilloscope (PXI1Slot7)",
            "channel": "0",
        },

        "measurements": [

            {
                "file": "DM_OFF.tdms",
                "V_mean_V": 2.50626,
                "label": "DM OFF"
            },
            {
                "file": "DM_ON.tdms",
                "V_mean_V": 2.51048,
                "label": "DM ON"
            },
            {
                "file": "background.tdms",
                "V_mean_V": 2.50626,
                "label": "Background"
            }
        ]
    }
    plot_RIN_campaign_tdms(campaign_tdms)


