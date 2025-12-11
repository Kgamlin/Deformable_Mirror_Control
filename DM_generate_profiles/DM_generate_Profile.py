import numpy as np
import os


class DMShape:
    def __init__(self, config: dict):
        """
        Expected dictionary keys:
        {
            "n_actuators": int,
            "stroke": float (meters),
            "wavelength": float (meters),
            "N": int (default 12),
            "paths": {
                "directory": str,
                "filename": str
            }
        }
        """

        # Unpack dictionary
        self.n_act = config["n_actuators"]
        self.stroke = config["stroke"]
        self.wavelength = config["wavelength"]

        # Optional override of grid size
        self.N = config.get("N", 12)

        # Save paths dict
        self.paths = config["paths"]

        # Precompute stroke in λ units
        self.max_phase_units_Lambda = 2 * self.stroke / self.wavelength

        # Initialize pixel grid
        self.map = np.zeros((self.N, self.N), dtype=float)

    # ───────────────────────────────────────────────────────────
    def gradient(self, k_lambda: int):
        """
        Creates a column-wise gradient normalized to stroke.
        """
        max_height = min(self.stroke/2, k_lambda * self.wavelength/2) / self.stroke
        col_values = np.round(
                            np.linspace(max_height + 0.5, 0.5 - max_height, self.N),
                            2
                    )
        self.map = np.tile(col_values, (self.N, 1))

    # ───────────────────────────────────────────────────────────
    def apply_circular_mask(self):
        """
        Keep values inside circular region, set outside to -1.
        """
        y, x = np.indices((self.N, self.N))
        cx, cy = (self.N - 1) / 2, (self.N - 1) / 2
        radius = self.N / 2
        inside = (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2

        self.map = np.where(inside, self.map, -1)

    # ───────────────────────────────────────────────────────────
    def unwrap_and_save(self):
        """
        Turn the 12×12 grid into a 1D vector, remove -1 entries,
        and save to CSV using paths from config["paths"].
        """
        # Flatten in row-major order (left→right, top→bottom)
        unwrapped = self.map.flatten()
        print(self.map)
        # Remove masked areas
        cleaned = unwrapped[unwrapped != -1]
        print(len(cleaned))
        # Build output path
        dirpath = self.paths["directory"]
        filename = self.paths["filename"]
        os.makedirs(dirpath, exist_ok=True)

        fullpath = os.path.join(dirpath, filename)

        # Save as CSV
        np.savetxt(fullpath, cleaned, delimiter=",", fmt="%.6f")

        print(f"[INFO] Saved unwrapped DM shape ({len(cleaned)} values) to:\n{fullpath}")

    # ───────────────────────────────────────────────────────────
    def generate_gradient_file(self, k_lambda: int):
        """
        One-call interface for the user.
        """
        self.gradient(k_lambda)
        self.apply_circular_mask()
        self.unwrap_and_save()
#
# DM = DMShape(137, 1.5e-6,514e-9)
# DM.gradient(6)
# DM.apply_circular_mask()
# print(DM.__repr__())