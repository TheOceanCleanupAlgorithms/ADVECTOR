# ADVECTOR
The emerging interest in vertical dynamics and a constant trend towards increased spatial and temporal resolution necessitates a fully distributed, computationally efficient solution to the problem of modeling marine litter transport at sea.  As such, this software aims to be not just computationally efficient, but fully distributed as well, in order to take full advantage of massively parallel hardware architectures such as GPUs and CPU clusters.  The OpenCL paradigm accomplishes both of these goals.

## Features and Timeline
### V0: Sea Surface Advection
Version 0 aims to be a functionally equivalent to the TrashTracker model developed by Laurent Lebreton.  Intended for global dispersion studies, it will use a 2D, second-order advection scheme, and will include sea-surface-current advection, eddy diffusion, windage, "slippery" coastline handling (prevents beaching), and delayed particle release.
### V1.0: 3D Advection (Buoyancy Driven)
Version 1 will consider depth, and will require vertical current as an input.  It will use a 3D second-order advection scheme and will support buoyancy-driven vertical movement.
### V1.1: Elaborate Vertical Transport Mechanisms
Update 1.1 will add new vertical transport mechanisms, and will support trilinear field interpolation for the advection algorithm.
### V1.2: Boundary Processes (Coasts/Bathymetry)
Update 1.2 will expand the consideration of coastal processes beyond simple beaching, will consider processes at the seafloor, and may add support for new advection kernels.
## Installation
1. Install miniconda, found [here](https://docs.conda.io/en/latest/miniconda.html).
2. In a terminal, clone this repo and navigate to repo root.
3. Install dependencies
    ```
   conda env create -f environment.yml  # creates a conda environment, installs dependencies
   conda activate ADVECTOR  # activates the conda environment
    ```
4. Acquire forcing data

    At minimum, ADVECTOR requires surface current data; it can also use surface wind data.  Instructions for downloading forcing data or using existing data can be found in `examples/HYCOM/README.txt`

5. Run example advection

    Once you're all set up according to `examples/HYCOM/README.txt`, you can execute `python examples/HYCOM/HYCOM_advect_2d.py`
