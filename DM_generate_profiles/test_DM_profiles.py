from DM_generate_Profile import DMShape
from numpy import pi

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

    config = {
            "n_actuators": 137,
            "stroke": 1.5e-6,
            "wavelength": 514e-9,
            "N": 13,
            "paths": {
                "directory": "output_shapes",
                "filename": "zernike_n2_m0_v2.csv"
            }
        }

    dm = DMShape(config)

    # Defocus with π phase peak
    dm.generate_zernike_file(
        n=2,
        m=0,
        amplitude_rad=2*pi,
        radius_actuators=6.5
    )
