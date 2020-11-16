from pathlib import Path
import xarray as xr
import netCDF4 as nc
import numpy as np
import os
import pandas as pd


class OutputWriter:
    def __init__(self, out_path: Path):
        if not out_path.is_dir():
            out_path.mkdir(out_path)

        self.folder_path = out_path
        self.current_year = None
        self.current_path = None
    
    def _set_current_year(self, year: int):
        self.current_year = year
        self.current_path = self.folder_path.joinpath(f"parts_{year}.nc")

    def write_output_chunk(self, chunk: xr.Dataset):
        times = pd.DatetimeIndex(chunk.time.values)
        beginning_year = times[0].year
        end_year = times[-1].year

        if beginning_year == end_year:
            if beginning_year != self.current_year:
                self._set_current_year(beginning_year)
                self._write_first_chunk(chunk)
            else:
                self._append_chunk(chunk)
        else:
            for year in range(beginning_year, end_year + 1):
                chunk_year = chunk.loc[{'time': times.year == year}]
                if year != self.current_year:
                    self._set_current_year(year)
                    self._write_first_chunk(chunk_year)
                else:
                    self._append_chunk(chunk_year)

    def _write_first_chunk(self, chunk: xr.Dataset):
        with nc.Dataset(self.current_path, mode="w") as ds:
            ds.createDimension("time", None)  # unlimited dimension
            ds.createDimension("p_id", len(chunk.p_id))

            time = ds.createVariable("time", np.float64, ("time",))
            time.units = "seconds since 1970-01-01 00:00:00.0"
            time.calendar = "gregorian"
            time[:] = chunk.time.values.astype('datetime64[s]').astype(np.float64)

            p_id = ds.createVariable("p_id", chunk.p_id.dtype, ("p_id",))
            p_id[:] = chunk.p_id.values

            lon = ds.createVariable("lon", chunk.lon.dtype, ("p_id", "time"))
            lon.units = "Degrees East"
            lon[:] = chunk.lon.values

            lat = ds.createVariable("lat", chunk.lat.dtype, ("p_id", "time"))
            lat.units = "Degrees North"
            lat[:] = chunk.lat.values

            release_date = ds.createVariable("release_date", np.float64, ("p_id",))
            release_date.units = "seconds since 1970-01-01 00:00:00.0"
            release_date.calendar = "gregorian"
            release_date[:] = chunk.release_date.values.astype('datetime64[s]').astype(np.float64)

    def _append_chunk(self, chunk: xr.Dataset):
        with nc.Dataset(self.current_path, mode="a") as ds:
            time = ds.variables['time']
            start_t = len(time)
            time[start_t:] = chunk.time.values.astype('datetime64[s]').astype(np.float64)

            lon = ds.variables['lon']
            lon[:, start_t:] = chunk.lon.values

            lat = ds.variables['lat']
            lat[:, start_t:] = chunk.lat.values
