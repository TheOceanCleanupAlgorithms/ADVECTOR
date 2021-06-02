"""
advect on ECCO currents
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

examples_root = Path(__file__).parent
sys.path.append(str(examples_root))
sys.path.append(str(examples_root.parent / "src"))

from plotting.plot_advection import animate_ocean_advection
from run_advector_3D import run_advector_3D

WINDAGE_MULTIPLIER = (
    1  # multiplier of default windage formulation (based on emerged surface area)
)

sourcefile = str(examples_root / "sourcefiles/3D_uniform_source_2015.nc")
if __name__ == "__main__":
    out_paths = run_advector_3D(
        output_directory=str(
            examples_root / f"outputfiles/ECCO_2015_3D/{Path(sourcefile).stem}/"
        ),
        sourcefile_path=sourcefile,
        configfile_path=str(examples_root / "configfiles/config.nc"),
        u_water_path=str(examples_root / "ECCO/currents/U_2015*.nc"),
        v_water_path=str(examples_root / "ECCO/currents/V_2015*.nc"),
        w_water_path=str(examples_root / "ECCO/currents/W_2015*.nc"),
        u_wind_path=str(examples_root / "ncep_ncar_doe_ii/uwnd.10m.gauss.2015.nc"),
        v_wind_path=str(examples_root / "ncep_ncar_doe_ii/vwnd.10m.gauss.2015.nc"),
        wind_varname_map={"uwnd": "U", "vwnd": "V", "level": "depth"},  # wind
        seawater_density_path=str(examples_root / "ECCO/seawater_density/RHO_2015.nc"),
        advection_start_date=datetime(year=2015, month=1, day=1, hour=12),
        timestep=timedelta(hours=1),
        num_timesteps=24 * 365,
        save_period=24,
        advection_scheme="taylor2",
        windage_multiplier=WINDAGE_MULTIPLIER,
        wind_mixing_enabled=True,
        memory_utilization=0.4,
    )

    for out_path in out_paths:
        animate_ocean_advection(out_path, save=False)
