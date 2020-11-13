#include "windage.h"
#include "advection_schemes.h"

vector windage_meters(particle p, field3d wind, double dt, double windage_coeff) {
    vector wind_displacement_meters = eulerian_displacement(p, wind, dt);
    wind_displacement_meters.x *= windage_coeff;
    wind_displacement_meters.y *= windage_coeff;
    return wind_displacement_meters;
}
