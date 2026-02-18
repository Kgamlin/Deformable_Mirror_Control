from pathlib import Path

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
    timestamp = "2026-01-29_15-02-00"
    timestamp ="Wave_spectrum_RIN_data"
    base_folder = Path(Path(__file__).resolve().parents[1]
                /"RIN_data"
                /f"{timestamp}")
    campaign_tdms = {
        "base_folder": base_folder,
        "tdms_settings": {
            "slot": "Oscilloscope (PXI1Slot7)",
            "channel": "0",
        },

        "measurements": [

            {
                "file": "0.99_A.tdms",
                "V_mean_V": 1.0633,
                "label": "0.99 A"
            },

            {
                "file": "1.50_A.tdms",
                "V_mean_V": 1.556,
                "label": "1.50 A"
            },
            {
                "file": "2.20_A.tdms",
                "V_mean_V": 2.068,
                "label": "2.20 A"
            },
            # {
            #     "file": "zero_driver_off_no_pinhole.tdms",
            #     "V_mean_V": 4.09,
            #     "label": "driver off no pinhole"
            # },
            # {
            #     "file": "zero_driver_on_no_pinhole.tdms",
            #     "V_mean_V": 4.10,
            #     "label": "driver on no pinhole"
            # },
            # {
            #     "file": "zero_driver_off_w_pinhole.tdms",
            #     "V_mean_V": 1.818,
            #     "label": "driver off with pinhole"
            # },
            # {
            #     "file": "zero_driver_on_w_pinhole.tdms",
            #     "V_mean_V": 1.820,
            #     "label": "driver on with pinhole"
            # },


            # {
            #     "file": "offset_0_no_pinhole.tdms",
            #     "V_mean_V": 4.190,
            #     "label": "all to zero"
            # },
            # {
            #     "file": "offset_0.5_no_pinhole.tdms",
            #     "V_mean_V": 4.333,
            #     "label": "offset 0.5$\lambda$"
            # },
            # {
            #     "file": "offset_1_no_pinhole.tdms",
            #     "V_mean_V": 4.440,
            #     "label": "offset 1$\lambda$"
            # },
            # {
            #     "file": "offset_2_no_pinhole.tdms",
            #     "V_mean_V": 4.432,
            #     "label": "offset 2$\lambda$"
            # },


            # {
            #     "file": "offset_0_w_pinhole.tdms",
            #     "V_mean_V": 0.923,
            #     "label": "all to zero"
            # },
            #
            # {
            #     "file": "offset_0.5_w_pinhole.tdms",
            #     "V_mean_V": 1.013,
            #     "label": "offset 0.5$\lambda$"
            # },
            #
            #
            # {
            #     "file": "offset_1_w_pinhole.tdms",
            #     "V_mean_V": 1.054,
            #     "label": "offset 1$\lambda$"
            # },
            # {
            #     "file": "offset_1.5_no_pinhole.tdms",
            #     "V_mean_V": 4.432,
            #     "label": "offset 1.5$\lambda$"
            # },
            # {
            #     "file": "offset_1.5_w_pinhole.tdms",
            #     "V_mean_V": 1.105,
            #     "label": "offset 1.5$\lambda$"
            # },

            # {
            #     "file": "offset_2_w_pinhole.tdms",
            #     "V_mean_V": 1.057,
            #     "label": "offset 2$\lambda$"
            # }

            # {
            #     "file": "offset_0.5_no_pinhole.tdms",
            #     "V_mean_V": 3.005,
            #     "label": "offset 0.5$\lambda$"
            # },
            # # {
            # #     "file": "offset_0.5_w_pinhole.tdms",
            # #     "V_mean_V": 0.610,
            # #     "label": "offset 0.5$\lambda$ (w/ pinhole)"
            # # },
            # {
            #     "file": "offset_1_no_pinhole.tdms",
            #     "V_mean_V": 3.155,
            #     "label": "offset 1$\lambda$"
            # },
            # # {
            # #     "file": "offset_1_w_pinhole.tdms",
            # #     "V_mean_V": 0.632,
            # #     "label": "offset 1$\lambda$ (w/ pinhole)"
            # # },
            # {
            #     "file": "offset_2_no_pinhole.tdms",
            #     "V_mean_V": 3.147,
            #     "label": "offset 2$\lambda$"
            # },
            # {
            #     "file": "offset_2_w_pinhole.tdms",
            #     "V_mean_V": 0.963,
            #     "label": "offset 2$\lambda$ (w/ pinhole)"
            # },
            # {
            #     "file": "DM_w_pinhole_rest_state_all_zero.tdms",
            #     "V_mean_V": 0.580,
            #     "label": "All to zero"
            # },
            # {
            #     "file": "DM_on_rest_state.tdms",
            #     "V_mean_V": 2.82280,
            #     "label": "DM ON (rest state)"
            # },
            # {
            #     "file": "DM_w_pinhole_offset_0.15.tdms",
            #     "V_mean_V": 0.604,
            #     "label": f"offset 0.15$\lambda$"
            # },
            # {
            #     "file": "DM_w_pinhole_offset_0.5.tdms",
            #     "V_mean_V": 0.581,
            #     "label": f"offset 0.5$\lambda$"
            # },
            # {
            #     "file": "DM_w_pinhole_offset_1.tdms",
            #     "V_mean_V": 0.655,
            #     "label": f"offset 1$\lambda$, (Ref-alignement profile)"
            # },
            # {
            #     "file": "DM_w_pinhole_offset_1.5.tdms",
            #     "V_mean_V": 0.652,
            #     "label": f"offset 1.5$\lambda$"
            # },
            # {
            #     "file": "DM_w_pinhole_offset_2.tdms",
            #     "V_mean_V": 0.654,
            #     "label": f"offset 2$\lambda$"
            # }
        ]
    }
    plot_RIN_campaign_tdms(campaign_tdms)


