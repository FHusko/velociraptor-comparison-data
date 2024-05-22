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

input_filename = "../raw/Caramete2010.txt"
delimiter = None

output_filename = "Caramete2010_Data.hdf5"
output_directory = "../"

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

processed = ObservationalData()

# Read the data (only those columns we need here)
raw = np.loadtxt(input_filename, delimiter=delimiter, usecols=(0, 1, 2, 3, 4))

M_BH = 10 ** raw[:, 0] * unyt.Solar_Mass
M_BH_low = 10 ** (raw[:, 0] - raw[:, 2]) * unyt.Solar_Mass
M_BH_high = 10 ** (raw[:, 0] + raw[:, 1]) * unyt.Solar_Mass

Phi = 10 ** raw[:, 3] / unyt.Mpc ** 3 * (h_sim / h_obs) ** 3
Phi_low = 10 ** (raw[:, 3] - raw[:, 4]) / unyt.Mpc ** 3 * (h_sim / h_obs) ** 3
Phi_high = 10 ** (raw[:, 3] + raw[:, 4]) / unyt.Mpc ** 3 * (h_sim / h_obs) ** 3

# Define the scatter as offset from the mean value
x_scatter = unyt.unyt_array((M_BH - M_BH_low, M_BH_high - M_BH))
y_scatter = unyt.unyt_array((Phi - Phi_low, Phi_high - Phi))

comment = (
    " The black hole mass function estimate taken from Caramete et al. (2010):"
    " 2010A&A...521A..55C"
    " These estimates are based on convolving the observed relation between"
    " black hole mass and the luminosity function. "
    " The units of black hole masses are Msol. The units of the black hole mass"
    " function are Mpc^-3 dex^-1. An h-correction was applied from"
    f" h=0.7 to a {cosmology.name} cosmology."
)
citation = "Caramete et al. (2010) (Mbh - Mbulge)"
bibcode = "2010A&A...521A..55C"
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
