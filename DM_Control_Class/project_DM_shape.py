from patterns import PatternGenerator
from dm_wrapper import DMClass
import numpy as np
import matplotlib.pyplot as plt
import copy


def plot_grid(grid, title="", vmin=0, vmax=1):
    masked = np.ma.masked_where(grid < 0, grid)
    cmap = copy.copy(plt.cm.jet)
    cmap.set_bad("lightgray")

    fig, ax = plt.subplots(figsize=(5, 5))
    im = ax.imshow(masked, vmin=vmin, vmax=vmax, origin="upper", cmap=cmap)
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.colorbar(im, ax=ax)
    plt.show()


if __name__ == "__main__":

    # -----------------------------
    # Setup
    # -----------------------------
    GRID_SIZE = 13
    SERIAL = "25CW012#060"
    wavelength_nm = 632.8

    patterns = PatternGenerator(
        N=GRID_SIZE,
        wavelength_nm=wavelength_nm,
        stroke_um=1.5,
    )

    dm = DMClass(serial=SERIAL, grid_size=GRID_SIZE)

    # -----------------------------
    # Generate patterns
    # -----------------------------
    #
    # grad_params = {
    #     "type": "gradient",
    #     "amplitude_lambda": 0.3,
    #     "offset_lambda": 0.7,
    #     "radius_px": 4,
    # }
    #
    # grid_grad = patterns.column_gradient(grad_params)

    # zernike_params = {
    #     "type": "zernike",
    #     "n": 2,
    #     "m": 0,  # defocus
    #     "amplitude_lambda": 0.9,
    #     "offset_lambda": 1.1,
    #     "radius_px": 6.5,
    # }

    sup_zernike_params ={
        "general":{
            "wavlength_nm": wavelength_nm,
            "radius_px": 5.5,
        },
        "zernike_amplitudes":{
            "(0,0)_and_radius_px" : (0,6.5),
            "(1,-1)": 0,
            "(1,1)" : 0,
            "(2,-2)": 0,
            "(2,0)" : 0,
            "(2,2)" : 0,
            "(3,-3)": 0,
            "(3,-1)": 0,
            "(3,1)" : 0,
            "(3,3)" : 0,
        }
    }


    # grid_zernike = patterns.zernike(zernike_params)

    sup_grid_zernike = patterns.sup_zernike(sup_zernike_params)
    # -----------------------------
    # Visualize BEFORE DM
    # -----------------------------
    # plot_grid(
    #     grid_grad,
    #     patterns.title_from_params(grad_params)
    # )

    # plot_grid(
    #     sup_grid_zernike,
    #     "superposition of Zenike"
    # )

    # -----------------------------
    # Send to DM
    # -----------------------------
    dm.open()

    # print("Sending gradient...")
    # dm.send_grid(grid_grad)
    # dm.plot_last()

    # input("Press ENTER to send Zernike...")

    print("Sending Zernike...")
    dm.send_grid(sup_grid_zernike)
    dm.plot_last(sup_zernike_params)

    dm.close()


