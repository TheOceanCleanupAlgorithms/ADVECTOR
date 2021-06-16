import subprocess
from pathlib import Path

import matplotlib.animation as manimation
import matplotlib.cm as cm
import matplotlib.colors as mcol
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from tqdm import tqdm


def plot_ocean_trajectories(
    outputfile_path: str, current_path: str, current_varname_map: dict = None
):
    fig, ax = plt.subplots(figsize=[14, 8])
    plot_grid(ax=ax, current_path=current_path, current_varname_map=current_varname_map)

    # plot trajectories
    P = xr.open_dataset(outputfile_path)
    ax.plot(P.lon.transpose("time", "p_id"), P.lat.transpose("time", "p_id"), ".")
    plt.show()


def animate_ocean_advection(
    outputfile_path: str,
    current_path: str,
    current_varname_map: dict = None,
    save: bool = False,
    colorbar_depth=None,
):
    P = xr.open_dataset(outputfile_path)
    # plot le advection
    fig, ax = plt.subplots(figsize=[14, 8])
    plot_grid(ax=ax, current_path=current_path, current_varname_map=current_varname_map)

    # initialize the scatter plot with dummy data.
    trunc_winter = mcol.ListedColormap(cm.winter(np.linspace(0, 0.8, 100)))
    if "depth" in P.variables:
        vmin = colorbar_depth if colorbar_depth is not None else P.depth.min()
        dot = ax.scatter(
            np.zeros(len(P.p_id)),
            np.zeros(len(P.p_id)),
            c=np.zeros(len(P.p_id)),
            cmap=trunc_winter,
            s=5,
            norm=mcol.Normalize(vmin=vmin, vmax=0),
        )
        cbar = plt.colorbar(mappable=dot, ax=ax)
        cbar.ax.set_ylabel("Depth (m)")
    else:
        dot = ax.scatter(
            np.zeros(len(P.p_id)), np.zeros(len(P.p_id)), c="tab:blue", s=5
        )

    def base_update(i, P, ax, dot, timestr):
        dot.set_offsets(np.c_[np.array([P.isel(time=i).lon, P.isel(time=i).lat]).T])
        ax.set_title(timestr[i])
        ax.set_ylim(-90, 90)

    if "depth" in P.variables:

        def update_func(i, P, ax, dot, timestr):
            base_update(i, P, ax, dot, timestr)
            dot.set_array(P.isel(time=i).depth.values)

    else:
        update_func = base_update

    timestr = P.time.dt.strftime("%Y-%m-%dT%H:%M:%S").values
    if save:
        animate_ocean_advection_to_disk(
            outputfile_path, P, fig, ax, dot, timestr, update_func
        )
    else:
        for i in range(len(P.time)):
            update_func(i, P, ax, dot, timestr)
            plt.pause(0.005)
        plt.show()


def animate_ocean_advection_to_disk(
    outputfile_path, P, fig, ax, dot, timestr, update_func
):
    FFMpegWriter = manimation.writers["ffmpeg"]
    writer = FFMpegWriter(fps=30)
    outfile = Path(outputfile_path).with_suffix(".mp4")
    print("Creating Movie...")
    with writer.saving(fig, outfile=outfile, dpi=150):
        for i in tqdm(range(len(P.time))):
            update_func(i, P, ax, dot, timestr)
            writer.grab_frame()

    plt.close()
    print("Opening Movie...")
    subprocess.call(["open", outfile])  # this won't work except on mac.


def plot_grid(ax, current_path: str, current_varname_map: dict = None):
    # show current data grid
    grid = (
        xr.open_dataset(current_path).rename(current_varname_map).U.squeeze().isnull()
    )
    if "depth" in grid.dims:
        grid = grid.sel(depth=0, method="nearest")
    if grid.lon.max() > 180:
        grid["lon"] = ((grid.lon + 180) % 360) - 180
        grid = grid.sortby("lon")
    xspacing = np.diff(grid.lon).mean()
    yspacing = np.diff(grid.lat).mean()
    lon_edges = np.append((grid.lon - xspacing / 2), grid.lon[-1] + xspacing / 2)
    lat_edges = np.append((grid.lat - yspacing / 2), grid.lat[-1] + yspacing / 2)
    return ax.pcolormesh(lon_edges, lat_edges, ~grid, cmap="gray")
