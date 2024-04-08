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

input_filename = "../raw/Graham2023.txt"
delimiter = " "

output_filenames = ["Graham2023_S.hdf5", "Graham2023_ESS0.hdf5", "Graham2023_E.hdf5"]
galaxy_types = ["S", "ES/S0", "E"]
output_directory = "../"

# conversion for Mstar from_Kroupa (2002) to Chabrier (2003) IMF
# (table 2, Bernardi et al, 2010, 2010MNRAS.404.2087B)
log_M_offset = 0.05

log_M_bh, log_M_bh_err, log_M_star, log_M_star_err, Gal_type = [], [], [], [], []
with open(input_filename, "r") as file:
    rows = file.readlines()
    for row in rows:
        try:
            elements = row.split(" ")
            gal_type, bh_mass_and_err, stellar_mass_and_err = (
                elements[1],
                elements[6],
                elements[10],
            )
            bh_mass, bh_mass_err = (float(x) for x in bh_mass_and_err.split("±"))
            stellar_mass, stellar_mass_err = (
                float(x) for x in stellar_mass_and_err.split("±")
            )

            log_M_bh.append(bh_mass)
            log_M_bh_err.append(bh_mass_err)
            log_M_star.append(stellar_mass + log_M_offset)
            log_M_star_err.append(stellar_mass_err)
            Gal_type.append(gal_type)
        except ValueError:
            pass

Gal_type = np.array(Gal_type)
log_M_bh, log_M_star = np.array(log_M_bh), np.array(log_M_star)
log_M_bh_err, log_M_star_err = np.array(log_M_bh_err), np.array(log_M_star_err)

M_bh = unyt.unyt_array(np.power(10.0, log_M_bh), units="Msun")
M_star = unyt.unyt_array(np.power(10.0, log_M_star), units="Msun")

M_bh_lower = np.power(10.0, log_M_bh) - np.power(10.0, log_M_bh - log_M_bh_err)
M_bh_upper = np.power(10.0, log_M_bh + log_M_bh_err) - np.power(10.0, log_M_bh)

M_star_lower = np.power(10.0, log_M_star) - np.power(10.0, log_M_star - log_M_star_err)
M_star_upper = np.power(10.0, log_M_star + log_M_star_err) - np.power(10.0, log_M_star)

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

for galaxy_type, output_filename in zip(galaxy_types, output_filenames):

    mask = Gal_type == galaxy_type

    # Meta-data
    comment = (
        f"A (black hole mass)-(galaxy stellar mass) relation based on colour-dependent stellar mass-to-light ratios "
        f" for {galaxy_type} galaxies. Converted from the Kroupa (2002) to Chabrier (2003) IMF."
        f" The whole sample consists of 73 ETGs plus 31 LTGs, coming from the larger sample of 84 ETGs "
        f" (Sahu et al. 2019) and 43 LTGs (Davis et al. 2019)."
    )
    citation = f"Graham & Sahu (2023) ({galaxy_type})"
    bibcode = "2023MNRAS.518.2177G"
    name = f"Black hole mass - stellar mass relation ({galaxy_type} galaxies)"
    plot_as = "points"
    # We purposely make this data show up not only a z=0 but also at higher z
    redshift_lower, redshift_upper = -0.1, 0.5
    redshift = 0.0
    h = h_sim

    M_bh_scatter = unyt.unyt_array([M_bh_lower[mask], M_bh_upper[mask]], units="Msun")
    M_star_scatter = unyt.unyt_array(
        [M_star_lower[mask], M_star_upper[mask]], units="Msun"
    )

    # Write everything
    processed = ObservationalData()
    processed.associate_x(
        M_star[mask],
        scatter=M_star_scatter,
        comoving=True,
        description="Galaxy Stellar Mass",
    )
    processed.associate_y(
        M_bh[mask],
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
