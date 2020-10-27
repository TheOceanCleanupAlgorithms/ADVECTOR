"""
the master advection runner.  Takes as input a path to a particle sourcefile, and a wildcard path for each current
variable.  Outputs the advection results to a particle sourcefile.
"""
import datetime
import json
import click
from pathlib import Path
from typing import Tuple
from dateutil import parser

from drivers.opencl_driver_2D import openCL_advect
from kernel_wrappers.Kernel2D import AdvectionScheme
from tools.open_currentfiles import open_currentfiles
from tools.open_sourcefile import open_sourcefile

DEFAULT_EDDY_DIFFUSIVITY = 0
DEFAULT_SAVE_PERIOD = 1


def run_advector(
    sourcefile_path: str,
    outputfile_path: str,
    u_path: str,
    v_path: str,
    advection_start: str,
    timestep_seconds: float,
    num_timesteps: int,
    advection_scheme: AdvectionScheme,
    eddy_diffusivity: float = DEFAULT_EDDY_DIFFUSIVITY,
    save_period: int = DEFAULT_SAVE_PERIOD,
    sourcefile_varname_map: dict = None,
    currents_varname_map: dict = None,
    platform_and_device: Tuple[int, int] = None,
    verbose: bool = False,
) -> str:
    """
    :param sourcefile_path: path to the particle sourcefile netcdf file.  Absolute path safest, use relative paths with caution.
    :param outputfile_path: path which will be populated with the outfile.
    :param u_path: wildcard path to the zonal current files.  Fed to glob.glob.  Assumes sorting paths by name == sorting paths in time
    :param v_path: wildcard path to the zonal current files.  See u_path for more details.
    :param advection_start: ISO 8601 datetime string.
    :param timestep_seconds: duration of each timestep in seconds
    :param num_timesteps: number of timesteps
    :param advection_scheme: which numerical advection scheme to use
    :param eddy_diffusivity: (m^2 / s) constant controlling the scale of each particle's random walk; model dependent
    :param save_period: how often to write output.  Particle state will be saved every {save_period} timesteps.
    :param sourcefile_varname_map: mapping from names in sourcefile to advector standard variable names
            advector standard names: ('id', 'lat', 'lon', 'release_date')
    :param currents_varname_map: mapping from names in current file to advector standard variable names
            advector standard names: ('U', 'V', 'W', 'lat', 'lon', 'time', 'depth')
    :param platform_and_device: [index of opencl platform, index of opencl device] to specify hardware for computation
    :param verbose: whether to print out a bunch of extra stuff
    :return: absolute path to the particle outputfile
    """
    if sourcefile_varname_map is None:
        sourcefile_varname_map = {}
    p0 = open_sourcefile(
        sourcefile_path=sourcefile_path, variable_mapping=sourcefile_varname_map
    )
    currents = open_currentfiles(
        u_path=u_path, v_path=v_path, variable_mapping=currents_varname_map
    )

    start_date = parser.isoparse(advection_start)  # python datetime.datetime
    dt = datetime.timedelta(seconds=timestep_seconds)

    openCL_advect(
        field=currents,
        out_path=Path(outputfile_path),
        p0=p0,
        start_time=start_date,
        dt=dt,
        num_timesteps=num_timesteps,
        save_every=save_period,
        advection_scheme=advection_scheme,
        eddy_diffusivity=eddy_diffusivity,
        platform_and_device=platform_and_device,
        verbose=verbose,
    )

    return outputfile_path


@click.command()
@click.option("--source", "sourcefile_path", required=True,
              type=click.Path(exists=True, dir_okay=False, readable=True),
              )
@click.option("--output", "outputfile_path", required=True,
              type=click.Path(exists=False, dir_okay=False, readable=True),
              )
@click.option("--u", "u_path", required=True, type=click.STRING)
@click.option("--v", "v_path", required=True, type=click.STRING)
@click.option("--start", "advection_start", required=True, type=click.STRING)
@click.option("--dt", "timestep_seconds", required=True, type=click.FLOAT)
@click.option("--nt", "num_timesteps", required=True, type=click.INT)
@click.option('--scheme', "advection_scheme", required=True,
              type=click.Choice([s.name for s in AdvectionScheme], case_sensitive=True))
@click.option('--eddy_diff', "eddy_diffusivity", required=False, default=DEFAULT_EDDY_DIFFUSIVITY)
@click.option("--save_period", "num_timesteps", required=False, default=DEFAULT_SAVE_PERIOD)
@click.option("--source_name_map", "sourcefile_varname_map", required=False, type=click.STRING)
@click.option("--currents_name_map", "sourcefile_varname_map", required=False, type=click.STRING)
@click.option("--cl_platform", "cl_platform", required=False, type=click.INT)
@click.option("--cl_device", "cl_device", required=False, type=click.INT)
@click.option("--verbose", "-v", is_flag=True)
def run_advector_CLI(
    advection_scheme: str,
    sourcefile_varname_map: str = None,
    currents_varname_map: str = None,
    cl_platform: int = None,
    cl_device: int = None,
    **kwargs,
):
    platform_and_device = None if cl_platform is None or cl_device is None else (cl_platform, cl_device)
    if sourcefile_varname_map:
        sourcefile_varname_map = json.loads(sourcefile_varname_map)
    if currents_varname_map:
        currents_varname_map = json.loads(currents_varname_map)

    run_advector(advection_scheme=AdvectionScheme[advection_scheme],
                 sourcefile_varname_map=sourcefile_varname_map,
                 currents_varname_map=currents_varname_map,
                 platform_and_device=platform_and_device,
                 **kwargs)


if __name__ == '__main__':
    run_advector_CLI()