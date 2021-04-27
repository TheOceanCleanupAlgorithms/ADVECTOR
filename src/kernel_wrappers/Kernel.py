from typing import Tuple

import xarray as xr
import pandas as pd
import pyopencl as cl

from abc import ABC, abstractmethod

from enums.advection_scheme import AdvectionScheme
from enums.forcings import Forcing


class Kernel(ABC):
    @abstractmethod
    def __init__(
        self,
        forcing_data: dict[Forcing, xr.Dataset],
        p0: xr.Dataset,
        advect_time: pd.DatetimeIndex,
        save_every: int,
        advection_scheme: AdvectionScheme,
        config: dict,
        context: cl.Context,
    ):
        """
        :param forcing_data: dict containing forcing datasets; keys in {"current", "wind", "seawater_density"}
        :param p0: initial state of particles
        :param advect_time: the timeseries which the kernel advects on
        :param save_every: number of timesteps between each writing of particle state
        :param advection_scheme: specifies which advection formulation to use
        :param config: dictionary with any extra settings needed by subclass implementation
        :param context: PyopenCL context for executing OpenCL programs
        """
        pass

    @abstractmethod
    def execute(self):
        """execute the kernel"""
        pass

    @abstractmethod
    def get_final_state(self) -> xr.Dataset:
        """
        :return: the state at the end of execution, formatted such that it can be used as an initial state
            for a subsequent kernel execution
        """
        pass

    @abstractmethod
    def get_memory_footprint(self) -> dict:
        pass

    @abstractmethod
    def get_data_loading_time(self) -> float:
        pass

    @abstractmethod
    def get_buffer_transfer_time(self) -> float:
        pass

    @abstractmethod
    def get_kernel_execution_time(self) -> float:
        pass
