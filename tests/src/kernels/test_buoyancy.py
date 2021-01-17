import pyopencl as cl
import numpy as np

from tests.config import ROOT_DIR, CL_CONTEXT, CL_QUEUE


def buoyancy_vertical_velocity(density: float, radius: float) -> float:
    """
    :param density: kg m^-3
    :param radius: m
    :return: vertical velocity due to buoyancy (m)
    """
    # setup
    prg = cl.Program(CL_CONTEXT, """
    #include "buoyancy.cl"

    __kernel void test_buoyancy_vertical_velocity(
        const double density,
        const double radius,
        __global double *out) {
        particle p = {.rho = density, .r = radius};
        out[0] = buoyancy_vertical_velocity(p);
    }
    """).build(options=["-I", str(ROOT_DIR / "src/kernels")])

    out = np.zeros(1).astype(np.float64)
    d_out = cl.Buffer(CL_CONTEXT, cl.mem_flags.WRITE_ONLY, out.nbytes)

    prg.test_buoyancy_vertical_velocity(
            CL_QUEUE, (1,), None,
            np.float64(density),
            np.float64(radius),
            d_out)
    CL_QUEUE.finish()

    cl.enqueue_copy(CL_QUEUE, out, d_out)

    return out[0]


def test_buoyancy_vertical_velocity():
    """check matches results in Dietrich 1982"""
    density = 970  # HDPE
    radius = np.linspace(1e-5, 1e-3, 10)
    dt = 1  # second
    z = np.array([buoyancy_vertical_velocity(density, r)*dt for r in radius])
    import matplotlib.pyplot as plt
    plt.plot(radius, z, '.-')
    plt.ylabel('m/s')
    plt.xlabel('radius (m)')

    assert False, "unfinished"