from velociraptor.observations.objects import ObservationalData

import unyt
import numpy as np
import os
import sys

# Exec the master cosmology file passed as first argument
with open(sys.argv[1], "r") as handle:
    exec(handle.read())

# Cosmology
h_obs = 0.7
h_sim = cosmology.h

input_filename = "../raw/Shankar2009.txt"
delimiter = None

output_filename = "Shankar2009_Data.hdf5"
output_directory = "../"

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

processed = ObservationalData()

# Read the data (only those columns we need here)
raw = np.loadtxt(input_filename, delimiter=delimiter, usecols=(0, 1, 2, 3, 4, 5))

M_BH = 10 ** raw[:, 0] * unyt.Solar_Mass
M_BH_low = 10 ** (raw[:, 0] - raw[:, 2]) * unyt.Solar_Mass
M_BH_high = 10 ** (raw[:, 0] + raw[:, 1]) * unyt.Solar_Mass

# We divide by black hole mass since the data given in Shankar et al. (2009) is not
# in the form of the usual mass function.
Phi = 10 ** raw[:, 3] / (M_BH / unyt.Solar_Mass) / unyt.Mpc ** 3 * (h_sim / h_obs) ** 3
Phi_low = (
    10 ** (raw[:, 5]) / (M_BH / unyt.Solar_Mass) / unyt.Mpc ** 3 * (h_sim / h_obs) ** 3
)
Phi_high = (
    10 ** (raw[:, 4]) / (M_BH / unyt.Solar_Mass) / unyt.Mpc ** 3 * (h_sim / h_obs) ** 3
)

# Define the scatter as offset from the mean value
x_scatter = unyt.unyt_array((M_BH - M_BH_low, M_BH_high - M_BH))
y_scatter = unyt.unyt_array((Phi - Phi_low, Phi_high - Phi))

comment = (
    " The black hole mass function estimate taken from Shankar et al. (2009):"
    " 2009ApJ...690...20S"
    " These estimates are based on convolving the observed relation between"
    " black hole mass and various quantities with the number density of those "
    " quantities. These quantities include the stellar mass, luminosity and "
    " bulge velocity dispersion. The estimates given here encompass all of the"
    " mentioned inferred black hole mass function estimates, within the error bars."
    " The units of black hole masses are Msol. The units of the black hole mass"
    " function are Mpc^-3 dex^-1 Msol, i.e. this is the black hole mass function"
    " multiplied by black hole mass. An h-correction was applied from"
    f" h=0.7 to a {cosmology.name} cosmology. "
)
citation = "Shankar et al. (2009)"
bibcode = "2009ApJ...690...20S"
name = "Black Hole Mass Function"
plot_as = "points"
redshift = 0.0

processed.associate_x(
    M_BH, scatter=x_scatter, comoving=False, description="Black hole mass"
)
processed.associate_y(
    Phi, scatter=y_scatter, comoving=False, description="Black hole mass function"
)
processed.associate_citation(citation, bibcode)
processed.associate_name(name)
processed.associate_comment(comment)
processed.associate_redshift(redshift)
processed.associate_plot_as(plot_as)
processed.associate_cosmology(cosmology)

output_path = f"{output_directory}/{output_filename}"

if os.path.exists(output_path):
    os.remove(output_path)

processed.write(filename=output_path)
