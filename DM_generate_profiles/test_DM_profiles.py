from DM_generate_Profile import DMShape


if __name__ == "__main__":

    params = {
        "n_actuators": 137,
        "stroke": 1.5e-6,         # meters
        "wavelength": 514e-9,     # meters
        "N": 13,                  # grid size
        "paths": {
            "directory": "output_shapes",
            "filename": "dm_gradient_k6.csv"
        }
    }


    dm =DMShape(config=params)
    # ---- THE ONLY USER CALL ----
    dm.generate_gradient_file(k_lambda=6)
