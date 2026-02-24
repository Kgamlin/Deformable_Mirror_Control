# dm_wrapper.py
from typing import Dict, Optional

import numpy as np
import matplotlib.pyplot as plt
import bmc
import copy


class DMClass:
    """
    Hardware + geometry wrapper for the DM.
    """

    def __init__(self, serial, grid_size=13, cmap="jet"):
        self.serial = serial
        self.grid_size = grid_size
        self.cmap = cmap

        self.dm = bmc.BmcDm()
        self.n_act = None

        self._last_vector = None
        self._last_grid_masked = None

    # ──────────────────────────────
    # Connection
    # ──────────────────────────────
    def open(self):
        err = self.dm.open_dm(self.serial)
        if err:
            raise RuntimeError(self.dm.error_string(err))

        self.n_act = self.dm.num_actuators()
        self._last_vector = np.zeros(self.n_act)

        print(f"[DM] Opened DM {self.serial} with {self.n_act} actuators")

    def close(self):
        self.dm.close_dm()
        print("[DM] Closed DM")

    # ──────────────────────────────
    # Low-level send
    # ──────────────────────────────
    def send(self, vector):
        vector = np.asarray(vector, dtype=float)

        if len(vector) != self.n_act:
            raise ValueError(f"Expected {self.n_act} actuators, got {len(vector)}")

        if np.any(vector < 0) or np.any(vector > 1):
            raise ValueError("DM values must be in [0,1]")

        self.dm.send_data(vector.tolist())
        self._last_vector = vector.copy()

    # ──────────────────────────────
    # Grid interface
    # ──────────────────────────────
    def send_grid(self, grid):
        grid = np.asarray(grid, dtype=float)

        if grid.shape != (self.grid_size, self.grid_size):
            raise ValueError("Grid has wrong shape")

        masked = self._apply_circular_mask(grid)
        vector = masked[masked >= 0]

        if len(vector) != self.n_act:
            raise ValueError("Masked grid does not match actuator count")

        self._last_grid_masked = masked.copy()
        self.send(vector)

    # ──────────────────────────────
    # Visualization
    # ──────────────────────────────
    def plot_last(self, params=None, save_path=None):
        # type: (Optional[Dict], Optional[str]) -> None
        if self._last_grid_masked is None:
            raise RuntimeError("No grid has been sent yet")

        masked_data = np.ma.masked_where(
            self._last_grid_masked < 0,
            self._last_grid_masked
        )

        cmap = copy.copy(plt.cm.get_cmap(self.cmap))
        cmap.set_bad(color="lightgray")

        fig, ax = plt.subplots(figsize=(6, 6))
        im = ax.imshow(
            masked_data,
            cmap=cmap,
            vmin=0,
            vmax=1,
            origin="upper"
        )

        # ───── Title handling ─────
        if params is None:
            title = "DM Actuator Map"
        else:
            # one parameter per line for readability
            parts = []
            if "zernike_amplitudes" in params :
                gen_params = params["general"]
                for k, v in gen_params.items():
                    parts.append(f"{k}={v}")
                params =params["zernike_amplitudes"]
                parts.append("\n")

            for k, v in params.items():
                if v!=0: # only when plotting the superpositions
                    parts.append(f"{k}={v} ")#$\lambda$
                if k == "m" or k == "amplitude_lambda":
                    parts.append("\n")
            title = "DM Actuator Map\n" + ", ".join(parts)

        ax.set_title(title, fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])

        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Normalized Command")

        plt.tight_layout()

        if save_path is not None:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            plt.close(fig)
        else:
            plt.show()

    def save_pattern_data(self, save_dir, zernike_params=None, filename_stem="dm_pattern"):
        """
        Save DM actuator data to *save_dir*/dm_pattern/.

        Files written
        -------------
        {filename_stem}.csv          raw actuator grid (masked cells = -1)
        {filename_stem}.npy          same, as numpy array
        {filename_stem}.png          actuator map plot (same style as plot_last)
        {filename_stem}_params.json  zernike_params dict (only if provided)

        Must be called after send_grid() so that _last_grid_masked is populated.

        Parameters
        ----------
        save_dir : str or path-like
            Parent directory.  A ``dm_pattern/`` subfolder is created inside it.
        zernike_params : dict or None
            Zernike parameter dict to serialise as JSON.
        filename_stem : str
            Base name for every saved file.
        """
        import json as _json
        import os

        if self._last_grid_masked is None:
            raise RuntimeError("No grid has been sent yet — call send_grid() first.")

        dm_dir = os.path.join(str(save_dir), "dm_pattern")
        os.makedirs(dm_dir, exist_ok=True)

        # CSV  (masked cells stored as -1)
        np.savetxt(
            os.path.join(dm_dir, filename_stem + ".csv"),
            self._last_grid_masked,
            delimiter=",",
            fmt="%.6f",
        )

        # NPY
        np.save(os.path.join(dm_dir, filename_stem + ".npy"), self._last_grid_masked)

        # PNG — reuse plot_last with save_path.
        # zernike_params can be either the raw user dict (has "zernike_amplitudes")
        # or a scan-step wrapper (has "zernike_params" → inner dict).
        if isinstance(zernike_params, dict):
            if "zernike_params" in zernike_params:
                plot_params = zernike_params["zernike_params"]   # scan-step wrapper
            else:
                plot_params = zernike_params                     # raw user dict
        else:
            plot_params = None
        self.plot_last(
            params=plot_params,
            save_path=os.path.join(dm_dir, filename_stem + ".png"),
        )

        # JSON
        if zernike_params is not None:
            with open(os.path.join(dm_dir, filename_stem + "_params.json"), "w") as fh:
                _json.dump(zernike_params, fh, indent=2)

    # ──────────────────────────────
    # Geometry
    # ──────────────────────────────
    def _apply_circular_mask(self, grid):
        N = self.grid_size
        y, x = np.indices((N, N))
        cx = cy = (N - 1) / 2
        r2 = (x - cx)**2 + (y - cy)**2
        radius2 = (N / 2)**2

        return np.where(r2 <= radius2, grid, -1)