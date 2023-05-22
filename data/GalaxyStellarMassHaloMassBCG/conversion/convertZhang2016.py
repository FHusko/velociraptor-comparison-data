from velociraptor.observations.objects import ObservationalData

import unyt
import numpy as np
import os
import sys

# Exec the master cosmology file passed as first argument
with open(sys.argv[1], "r") as handle:
    exec(handle.read())

# Cosmology
h_sim = cosmology.h

output_filename = "Zhang2016_30kpc.hdf5"
output_directory = "../"

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

data = np.loadtxt("../raw/Zhang2016.txt")
M_200 = (10 ** data[:, 0]) * unyt.Solar_Mass

Mstar_30kpc_log = data[:, 1]
Mstar_30kpc = (10 ** Mstar_30kpc_log) * unyt.Solar_Mass
Mstar_30kpc_scatter_log = data[:, 2]

Mstar_30kpc_scatter_low = (
    10 ** Mstar_30kpc_log - 10 ** (Mstar_30kpc_log - Mstar_30kpc_scatter_log)
) * unyt.Solar_Mass
Mstar_30kpc_scatter_high = (
    10 ** (Mstar_30kpc_log + Mstar_30kpc_scatter_log) - 10 ** Mstar_30kpc_log
) * unyt.Solar_Mass
Mstar_30kpc_scatter = unyt.unyt_array(
    (Mstar_30kpc_scatter_low, Mstar_30kpc_scatter_high), units=unyt.Solar_Mass
)

# Meta-data
comment = (
    "Halo and stellar masses from Zhang et al. (2016) (2016ApJ...816...98Z). "
    "Halo masses are defined using the critical overdensity (factor 200) "
    "definition. Stellar mass and cosmology corrections are not needed. "
    "Stellar masses were measured in a 32 kpc projected aperture, so they are "
    "used to compare with 30 kpc projected apertures from the simulations."
)
citation = "Zhang et al. (2016)"
bibcode = "2016ApJ...816...98Z"
name = "BCG stellar mass-halo mass relation at z=0.4"
plot_as = "points"
redshift = 0.4
redshift_lower = 0.0
redshift_upper = 0.8
h = h_sim

# Write everything
processed = ObservationalData()
processed.associate_x(
    M_200, scatter=None, comoving=True, description="Halo Mass ($M_{200, {\rm crit}}$)"
)
processed.associate_y(
    Mstar_30kpc,
    scatter=Mstar_30kpc_scatter,
    comoving=True,
    description="Galaxy Stellar Mass",
)
processed.associate_citation(citation, bibcode)
processed.associate_name(name)
processed.associate_comment(comment)
processed.associate_redshift(redshift, redshift_lower, redshift_upper)
processed.associate_plot_as(plot_as)
processed.associate_cosmology(cosmology)

output_path = f"{output_directory}/{output_filename}"

if os.path.exists(output_path):
    os.remove(output_path)

processed.write(filename=output_path)