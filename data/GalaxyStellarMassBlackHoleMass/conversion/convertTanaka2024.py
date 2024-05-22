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

input_filename = "../raw/Tanaka2024.txt"
delimiter = " "

output_filename = "Tanaka2024.hdf5"
output_directory = "../"

# Load data
input_file = np.genfromtxt(input_filename, comments="#")

log_M_star = input_file[:, -2]
log_M_star_err = input_file[:, -1]
log_M_bh = input_file[:, -5]
log_M_bh_err = input_file[:, -4]

M_bh = unyt.unyt_array(np.power(10.0, log_M_bh), units="Msun")
M_star = (
    unyt.unyt_array(np.power(10.0, log_M_star), units="Msun") * (h_sim / h_obs) ** -2
)

M_bh_lower = np.power(10.0, log_M_bh) - np.power(10.0, log_M_bh - log_M_bh_err)
M_bh_upper = np.power(10.0, log_M_bh + log_M_bh_err) - np.power(10.0, log_M_bh)

M_star_lower = (
    np.power(10.0, log_M_star)
    - np.power(10.0, log_M_star - log_M_star_err) * (h_sim / h_obs) ** -2
)
M_star_upper = (
    np.power(10.0, log_M_star + log_M_star_err)
    - np.power(10.0, log_M_star) * (h_sim / h_obs) ** -2
)

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

comment = (
    f"A (black hole mass)-(galaxy stellar mass) relation based on observed "
    f"AGN with broad lines. An h-correction was "
    f"applied from h=0.7 to a {cosmology.name} cosmology."
)
citation = f"Tanaka et al. (2024) (BL-AGN)"
bibcode = "2024arXiv240113742T"
name = f"Black hole mass - stellar mass relation"
plot_as = "points"
redshift_lower, redshift_upper = 1, 2
redshift = 1.5
h = h_sim

M_bh_scatter = unyt.unyt_array([M_bh_lower, M_bh_upper], units="Msun")
M_star_scatter = unyt.unyt_array([M_star_lower, M_star_upper], units="Msun")

# Write everything
processed = ObservationalData()
processed.associate_x(
    M_star,
    scatter=M_star_scatter,
    comoving=True,
    description="Galaxy Stellar Mass",
)
processed.associate_y(
    M_bh,
    scatter=M_bh_scatter,
    comoving=True,
    description="Black Hole Mass",
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
