import ast
from typing import Dict
import numpy as np
from zernike import RZern


class PatternGenerator:
    """
    Pattern generation for BMC DM.

    Hardware mapping:
      command in [0,1]  <->  surface displacement in [0, stroke_um]

    User-facing inputs are passed via a dictionary.
    """

    def __init__(self, N: int, wavelength_nm: float = 632.8, stroke_um: float = 1.5):
        self.N = int(N)
        self.wavelength_um = float(wavelength_nm) * 1e-3  # nm -> µm
        self.stroke_um = float(stroke_um)

        # Pixel coordinate grid centered on array
        cx = cy = (self.N - 1) / 2
        y, x = np.indices((self.N, self.N))
        self.x_px = x - cx
        self.y_px = y - cy
        self.r_px = np.sqrt(self.x_px**2 + self.y_px**2)

        self._rz_cache: Dict[int, RZern] = {}

    # ─────────────────────────────────────────────
    # Utilities
    # ─────────────────────────────────────────────
    def _lambda_to_command(self, surface_lambda: np.ndarray) -> np.ndarray:
        surface_um = surface_lambda * self.wavelength_um
        return surface_um / self.stroke_um

    @staticmethod
    def title_from_params(params: Dict) -> str:
        """
        Generate a readable plot title from a parameter dictionary.
        """
        parts = []
        for k, v in params.items():
            parts.append(f"{k}={v}")
            if k=="m" or k=="amplitude_lambda":
                parts.append("\n")
        return ", ".join(parts)


    @staticmethod
    def _check_command_validity(cmd: np.ndarray, clip: bool = True) -> np.ndarray:
        """
        Check the validity of a final DM command.
        Ensures values lie within the system bounds [0, 1].

        Parameters
        ----------
        cmd : np.ndarray
            Command array to be checked.
        clip : bool, optional
            If True, out-of-range values are clipped to [0, 1].
            If False, a ValueError is raised when out-of-range values are detected.

        Returns
        -------
        np.ndarray
            Valid command array (clipped if necessary).
        """

        below = cmd < 0.0
        above = cmd > 1.0

        if np.any(below) or np.any(above):
            n_low = np.count_nonzero(below)
            n_high = np.count_nonzero(above)

            print(
                f"[PatternGenerator WARNING] DM command out of range: "
                f"{n_low} below 0, {n_high} above 1."
            )

            if not clip:
                raise ValueError(
                    f"DM command out of range "
                    f"(min={cmd.min():.3f}, max={cmd.max():.3f})"
                )

            print("[PatternGenerator WARNING] Clipping applied.")
            cmd = np.clip(cmd, 0.0, 1.0)

        return cmd

    # ─────────────────────────────────────────────
    # Gradient pattern
    # ─────────────────────────────────────────────
    def column_gradient(self, params: Dict, clip: bool = True) -> np.ndarray:
        amplitude_lambda = params["amplitude_lambda"]
        offset_lambda = params["offset_lambda"]
        radius_px = float(params["radius_px"])

        if radius_px <= 0:
            raise ValueError("radius_px must be > 0")

        x_norm = self.x_px / radius_px
        surface_lambda = offset_lambda + amplitude_lambda * x_norm
        surface_lambda = np.where(self.r_px <= radius_px,
                                  surface_lambda,
                                  offset_lambda)

        cmd = self._lambda_to_command(surface_lambda)
        cmd = self._check_command_validity(cmd)
        return cmd

    # ─────────────────────────────────────────────
    # Zernike helpers
    # ─────────────────────────────────────────────
    def _is_valid_zernike(self, n: int, m: int) -> bool:
        return (n >= 0 and abs(m) <= n and (n - abs(m)) % 2 == 0)

    def nm_to_noll(self, n: int, m: int) -> int:
        m_abs = abs(m)
        base = n * (n + 1) // 2 + 1
        if m_abs == 0:
            offset = 0
        else:
            k_group = (m_abs - (n % 2)) // 2
            offset = 2 * k_group - (1 if n % 2 == 0 else 0)
            if m < 0:
                offset += 1
        return base + offset - 1

    def _rzern(self, n_max: int) -> RZern:
        rz = self._rz_cache.get(n_max)
        if rz is None:
            rz = RZern(n_max)
            self._rz_cache[n_max] = rz
        return rz

    # ─────────────────────────────────────────────
    # Zernike pattern
    # ─────────────────────────────────────────────
    def zernike(self, params: Dict, Check_ampl:bool=True) -> np.ndarray:
        n = int(params["n"])
        m = int(params["m"])
        amplitude_lambda = params["amplitude_lambda"]
        offset_lambda = params.get("offset_lambda", 0.0)
        radius_px = float(params["radius_px"])

        if not self._is_valid_zernike(n, m):
            raise ValueError(f"Invalid Zernike indices n={n}, m={m}")

        x_unit = self.x_px / radius_px
        y_unit = self.y_px / radius_px

        rz = self._rzern(n)
        rz.make_cart_grid(x_unit, y_unit)

        j = self.nm_to_noll(n, m)

        c = np.zeros(rz.nk)
        if j >= rz.nk:
            raise ValueError("Noll index exceeds basis size")
        c[j] = 1.0

        Phi = np.array(rz.eval_grid(c, matrix=True))
        Phi = np.where(self.r_px <= radius_px, Phi, 0.0)
        peak = np.max(np.abs(Phi[self.r_px <= radius_px]))
        if peak > 0:
            Phi /= peak
        # print(Phi, np.min(Phi),np.max(Phi))

        surface_lambda = offset_lambda + amplitude_lambda * Phi
        cmd = self._lambda_to_command(surface_lambda)
        if Check_ampl :
            cmd = self._check_command_validity(cmd)

        return cmd


    def sup_zernike(self, zernike_superpos_params:Dict) -> np.ndarray:
        """
        Create a superposition of Zernike polynomials and return a DM command grid.

        The input dictionary must contain:
            - "general": shared parameters (e.g. offset_lambda, radius_px)
            - "zernike_amplitudes": mapping "(n,m)" -> amplitude_lambda
        """
        cmd = np.zeros_like(self.r_px)
        print(zernike_superpos_params["general"])
        general_params = zernike_superpos_params["general"]
        og_rad_px = zernike_superpos_params["general"]["radius_px"]
        zernike_amplitudes = zernike_superpos_params["zernike_amplitudes"]

        for key_str, value in zernike_amplitudes.items():


            if "_and_radius_px" in key_str:
                # split off the suffix
                base_key = key_str.replace("_and_radius_px", "")

                # extract (n, m)
                n, m = ast.literal_eval(base_key)

                # unpack tuple value
                amplitude, radius_px = value
                general_params["radius_px"]=radius_px
                kept_og_rad = False

            else:
                # normal case
                n, m = ast.literal_eval(key_str)
                amplitude = value

                kept_og_rad = True

                # print(f"n={n}, m={m}, amp={amplitude_lambda}, radius_px={radius_px}")
            if kept_og_rad is True:
                general_params["radius_px"] = og_rad_px
            ind_params = {
                "n": n,
                "m": m,
                "amplitude_lambda": amplitude,
                **general_params
            }
            # print(ind_params)
            cmd += self.zernike(ind_params,Check_ampl=False)

            #reset the general_params radius value:


        cmd = self._check_command_validity(cmd)
        return cmd




    # ─────────────────────────────────────────────
    # Superposition of Zernike pattern
    # ─────────────────────────────────────────────

