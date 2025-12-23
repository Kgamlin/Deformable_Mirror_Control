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
    def plot_last(self, params: Optional[Dict] = None):
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
        plt.show()

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