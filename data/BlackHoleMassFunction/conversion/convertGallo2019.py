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

input_filename = "../raw/Gallo2019.txt"
delimiter = None

output_filename = "Gallo2019_Data.hdf5"
output_directory = "../"

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

processed = ObservationalData()

# Read the data (only those columns we need here)
raw = np.loadtxt(input_filename, delimiter=delimiter, usecols=(0, 1, 2))

M_BH = 10 ** raw[:, 0] * unyt.Solar_Mass

Phi = 10 ** raw[:, 1] / unyt.Mpc ** 3 * (h_sim / h_obs) ** 3
Phi_low = 10 ** (raw[:, 1] - raw[:, 2]) / unyt.Mpc ** 3 * (h_sim / h_obs) ** 3
Phi_high = 10 ** (raw[:, 1] + raw[:, 2]) / unyt.Mpc ** 3 * (h_sim / h_obs) ** 3

# Define the scatter as offset from the mean value
y_scatter = unyt.unyt_array((Phi - Phi_low, Phi_high - Phi))

comment = (
    "The black hole mass function estimate taken from Gallo et al. (2019):"
    " 2019ApJ...883L..18G # These estimates are based on black hole"
    " occupation fractions as determined from X-ray detections. The units"
    " of the BH mass function are Mpc^-3 dex^-1. An h-correction was applied"
    f" from h=0.7 to a {cosmology.name} cosmology."
)
citation = "Gallo et al. (2019) (X-ray occupation fractions)"
bibcode = "2019ApJ...883L..18G"
name = "Black Hole Mass Function"
plot_as = "points"
redshift = 0.0

processed.associate_x(M_BH, scatter=None, comoving=False, description="Black hole mass")
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
