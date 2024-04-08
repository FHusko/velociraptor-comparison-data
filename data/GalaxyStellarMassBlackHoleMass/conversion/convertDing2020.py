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

input_filename = "../raw/Ding2020.txt"
delimiter = " "

output_filename = "Ding2020.hdf5"
output_directory = "../"

log_M_star, log_M_star_err_neg, log_M_star_err_pos, log_M_bh, log_M_bh_err = (
    [],
    [],
    [],
    [],
    [],
)
with open(input_filename, "r") as file:
    rows = file.readlines()[1:]
    for row in rows:
        try:
            elements = row.split("\t")
            star_mass, star_mass_err_neg, star_mass_err_pos, bh_mass = (
                elements[2],
                elements[3],
                elements[4],
                elements[5].strip("\n"),
            )

            log_M_bh.append(float(bh_mass))
            # Assume constant BH mass uncertainty of 0.4 dex
            log_M_bh_err.append(0.4)
            log_M_star.append(float(star_mass))
            log_M_star_err_neg.append(-1 * float(star_mass_err_neg))
            log_M_star_err_pos.append(float(star_mass_err_pos))
        except ValueError:
            pass

log_M_bh, log_M_star = np.array(log_M_bh), np.array(log_M_star)
log_M_bh_err, log_M_star_err_neg, log_M_star_err_pos = (
    np.array(log_M_bh_err),
    np.array(log_M_star_err_neg),
    np.array(log_M_star_err_pos),
)

M_bh = unyt.unyt_array(np.power(10.0, log_M_bh), units="Msun")
M_star = unyt.unyt_array(np.power(10.0, log_M_star), units="Msun")

M_bh_lower = np.power(10.0, log_M_bh) - np.power(10.0, log_M_bh - log_M_bh_err)
M_bh_upper = np.power(10.0, log_M_bh + log_M_bh_err) - np.power(10.0, log_M_bh)

M_star_lower = np.power(10.0, log_M_star) - np.power(
    10.0, log_M_star - log_M_star_err_neg
)
M_star_upper = np.power(10.0, log_M_star + log_M_star_err_pos) - np.power(
    10.0, log_M_star
)

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

comment = (
    f"A (black hole mass)-(galaxy stellar mass) relation based on observed "
    f"AGN with broad lines."
)
citation = f"Ding et al. (2020) (BL-AGN)"
bibcode = "2020ApJ...888...37D"
name = f"Black hole mass - stellar mass relation"
plot_as = "points"
# This data is only contained within z = 1.2 and z = 1.7, but we make it show
# outside that range as well.
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
