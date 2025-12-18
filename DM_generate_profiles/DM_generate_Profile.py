import numpy as np
import os
from zernike import RZern

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
    def _is_valid_zernike(self, n, m):
        return (n >= 0 and abs(m) <= n and (n - abs(m)) % 2 == 0)

    def _nm_to_k(self, n, m):
        """
        Convert (n, m) → Noll index (0-based).
        """
        m_abs = abs(m)
        base = n * (n + 1) // 2 + 1

        if m_abs == 0:
            offset = 0
        else:
            k_group = (m_abs - (n % 2)) // 2
            if n % 2 == 0:
                offset = 2 * k_group - 1
            else:
                offset = 2 * k_group
            if m < 0:
                offset += 1

        return base + offset - 1

    def zernike(self, n, m, amplitude_rad, radius_actuators=None):
        """
        Generate a Zernike phase pattern on the DM grid.

        Parameters
        ----------
        n, m : int
            Zernike indices
        amplitude_rad : float
            Peak phase amplitude (≤ 2π)
        radius_actuators : float
            Radius of the Zernike disk in actuator units.
            Defaults to full DM radius.
        """

        if not self._is_valid_zernike(n, m):
            raise ValueError(f"Invalid Zernike indices (n={n}, m={m})")

        if amplitude_rad > 2 * np.pi:
            raise ValueError("Maximum allowed amplitude is 2π radians")

        if radius_actuators is None:
            radius_actuators = self.N / 2

        # Create actuator-centered coordinate grid
        y, x = np.indices((self.N, self.N))
        cx = cy = (self.N - 1) / 2

        X = x - cx
        Y = y - cy
        r = np.sqrt(X**2 + Y**2)

        # Normalize to unit disk
        Xn = X / radius_actuators
        Yn = Y / radius_actuators

        # Zernike evaluation
        zern = RZern(n)
        zern.make_cart_grid(Xn, Yn)

        k = self._nm_to_k(n, m)
        coeffs = np.zeros(zern.nk)
        coeffs[k] = 1.0

        phase = zern.eval_grid(coeffs, matrix=True)

        # Mask outside radius
        phase = np.where(r <= radius_actuators, phase, np.nan)
        phase = np.nan_to_num(phase)

        # Normalize to requested amplitude
        phase = phase / np.max(np.abs(phase)) * amplitude_rad

        # Map from [-A, A] → [0, 1]
        self.map = phase / (2 * amplitude_rad) + 0.5


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

    def generate_zernike_file(self, n, m, amplitude_rad, radius_actuators=None):
        """
        One-call interface for Zernike DM patterns.
        """
        self.zernike(n, m, amplitude_rad, radius_actuators)
        self.apply_circular_mask()
        self.unwrap_and_save()

#
# DM = DMShape(137, 1.5e-6,514e-9)
# DM.gradient(6)
# DM.apply_circular_mask()
# print(DM.__repr__())