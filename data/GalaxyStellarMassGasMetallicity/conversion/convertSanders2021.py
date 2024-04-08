from velociraptor.observations.objects import ObservationalData

import unyt
import numpy as np
import os
import sys

# Exec the master cosmology file passed as first argument
with open(sys.argv[1], "r") as handle:
    exec(handle.read())

h_obs = 0.7
h_sim = cosmology.h

input_filename = f"../raw/Sanders2021.txt"
raw = np.loadtxt(input_filename)

comment = (
    "The relationship between stellar mass and gas-phase metallicity "
    "at z~2.3 and z~3.3 from the MOSDEF survey. "
    "Uses Chabrier (2003) initial mass function and h=0.7. "
    f"h-corrected for SWIFT using cosmology: {cosmology.name}. "
    "Gas metallicity is absolute, so no conversion w.r.t solar metallicity value is needed. "
)
citation = "Sanders et al. (2021)"
bibcode = "2021ApJ...914...19S"
name = "Galaxy Stellar Mass - Gas Metallicity"
plot_as = "points"

z = raw[:, 0]
Mstar = 10.0 ** raw[:, 1] * (h_sim / h_obs) ** -2 * unyt.Solar_Mass
Mstar_err_hi = 10.0 ** (raw[:, 1] + raw[:, 2]) * (h_sim / h_obs) ** -2 * unyt.Solar_Mass
Mstar_err_lo = 10.0 ** (raw[:, 1] - raw[:, 3]) * (h_sim / h_obs) ** -2 * unyt.Solar_Mass
metal = raw[:, 4] * unyt.dimensionless
metal_err_hi = raw[:, 5] * unyt.dimensionless
metal_err_lo = raw[:, 6] * unyt.dimensionless

for redshift in [2.3, 3.3]:
    processed = ObservationalData()

    mask = z == redshift
    x_scatter = unyt.unyt_array(
        (Mstar[mask] - Mstar_err_lo[mask], Mstar_err_hi[mask] - Mstar[mask])
    )
    y_scatter = unyt.unyt_array((metal_err_lo[mask], metal_err_hi[mask]))

    processed.associate_x(
        Mstar[mask],
        scatter=x_scatter,
        comoving=False,
        description="Galaxy Stellar Mass",
    )
    processed.associate_y(
        metal[mask],
        scatter=y_scatter,
        comoving=False,
        description="Galaxy Gas Metallicity",
    )
    processed.associate_citation(citation, bibcode)
    processed.associate_name(name)
    processed.associate_comment(comment)
    processed.associate_redshift(redshift)
    processed.associate_plot_as(plot_as)
    processed.associate_cosmology(cosmology)

    output_path = f"../Sanders2021_z{redshift:.1f}.hdf5"

    if os.path.exists(output_path):
        os.remove(output_path)

    processed.write(filename=output_path)
