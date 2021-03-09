from typing import Optional

import xarray as xr
import glob
import dask
import numpy as np


def open_netcdf_vectorfield(u_path: str, v_path: str, variable_mapping: Optional[dict], desampling_res: Optional[float]):
    """
    :param u_path: wildcard path to the zonal vector files.  Fed to glob.glob.  Assumes sorting paths by name == sorting paths in time
    :param v_path: wildcard path to the meridional vector files.  See u_path for more details.
    :param variable_mapping: mapping from names in vector file to advector standard variable names
    """
    U = xr.open_mfdataset(sorted(glob.glob(u_path)), data_vars="minimal", parallel=True)
    V = xr.open_mfdataset(sorted(glob.glob(v_path)), data_vars="minimal", parallel=True)
    vectors = xr.merge((U, V))
    vectors = vectors.rename(variable_mapping)
    vectors = vectors[['U', 'V']]  # drop any additional variables
    vectors = vectors.squeeze()  # remove any singleton dimensions

    # Allow desampling based on an arbitrary resolution (has to be lower than metocean resolution)
    if desampling_res is not None:
        tol = 0.001

        vectors = vectors.where(
            np.abs((vectors.lon - vectors.lon[0]) / desampling_res - np.round((vectors.lon - vectors.lon[0]) / desampling_res)) < tol, drop=True
        )
        vectors = vectors.where(
            np.abs((vectors.lat - vectors.lat[0]) / desampling_res - np.round((vectors.lat - vectors.lat[0]) / desampling_res)) < tol, drop=True
        )

    if "depth" in vectors.dims:
        vectors = vectors.sel(depth=0, method='nearest')

    assert set(vectors.dims) == {'lat', 'lon', 'time'}, f"Unexpected/missing dimension(s) ({vectors.dims})"

    # convert longitude [0, 360] --> [-180, 180]
    # this operation could be expensive because of the resorting.  You may want to preprocess your data.
    if max(vectors.lon) > 180:
        with dask.config.set(**{'array.slicing.split_large_chunks': True}):
            vectors['lon'] = ((vectors.lon + 180) % 360) - 180
            vectors = vectors.sortby('lon')

    return vectors


def empty_vectorfield():
    return xr.Dataset(
        data_vars={
            "U": (["lat", "lon", "time"], np.ndarray((0, 0, 0))),
            "V": (["lat", "lon", "time"], np.ndarray((0, 0, 0))),
        },
        coords={"lon": [], "lat": [], "time": []},
    )
