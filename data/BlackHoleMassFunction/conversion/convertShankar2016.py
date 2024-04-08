from velociraptor.observations.objects import ObservationalData

import unyt
import numpy as np
import os
import sys

# Exec the master cosmology file passed as first argument
with open(sys.argv[1], "r") as handle:
    exec(handle.read())

input_filename = "../raw/Shankar2016.txt"
delimiter = None

output_filenames = [
    "Shankar2016_Mstar_observed.hdf5",
    "Shankar2016_Mstar_unbiased.hdf5",
    "Shankar2016_sigma_observed.hdf5",
    "Shankar2016_sigma_unbiased.hdf5",
]
citations = [
    "(Mbh - Mstar, observed)",
    "(Mbh - Mstar, unbiased)",
    "(Mbh - sigma, observed)",
    "(Mbh - sigma, unbiased)",
]
output_directory = "../"

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

processed = ObservationalData()

# Read the data
raw = np.loadtxt(input_filename, delimiter=delimiter, usecols=(0, 1, 2, 3, 4, 5, 6))

M_BH = 10 ** raw[:, 0] * unyt.Solar_Mass

Phi_Mstar_observed = 10 ** raw[:, 1] / unyt.Mpc ** 3
Phi_Mstar_unbiased = 10 ** raw[:, 3] / unyt.Mpc ** 3
Phi_sigma_observed = 10 ** raw[:, 5] / unyt.Mpc ** 3
Phi_sigma_unbiased = 10 ** raw[:, 6] / unyt.Mpc ** 3
Phis = [Phi_Mstar_observed, Phi_Mstar_unbiased, Phi_sigma_observed, Phi_sigma_unbiased]

Phi_Mstar_observed_high = 10 ** (raw[:, 1] + raw[:, 2]) / unyt.Mpc ** 3
Phi_Mstar_observed_low = 10 ** (raw[:, 1] - raw[:, 2]) / unyt.Mpc ** 3
Phi_Mstar_unbiased_high = 10 ** (raw[:, 3] + raw[:, 4]) / unyt.Mpc ** 3
Phi_Mstar_unbiased_low = 10 ** (raw[:, 3] - raw[:, 4]) / unyt.Mpc ** 3

Phi_Mstar_observed_scatter = unyt.unyt_array(
    (
        Phi_Mstar_observed - Phi_Mstar_observed_low,
        Phi_Mstar_observed_high - Phi_Mstar_observed_low,
    )
)
Phi_Mstar_unbiased_scatter = unyt.unyt_array(
    (
        Phi_Mstar_unbiased - Phi_Mstar_unbiased_low,
        Phi_Mstar_unbiased_high - Phi_Mstar_unbiased,
    )
)
Phi_scatter = [Phi_Mstar_observed_scatter, Phi_Mstar_unbiased_scatter, None, None]

comment = (
    " The black hole mass function estimate taken from Shankar et al. (2016):"
    " 2020NatAs...4..282S.These estimates are based on convolving the observed"
    " relation between black hole mass and stellar mass or stellar velocity"
    " dispersion, with the probability density function (mass function) of"
    " those two quantities. The units of black hole masses are Msol. The units"
    " of the black hole mass function are Mpc^-3 dex^-1."
)
name = "Black Hole Mass Function"
bibcode = "2020NatAs...4..282S"
redshift = 0.0

for i in range(4):
    citation = "Shankar et al. (2020) " + citations[i]

    if i < 2:
        plot_as = "points"
    if i >= 2:
        plot_as = "line"

    processed.associate_x(
        M_BH, scatter=None, comoving=False, description="Black hole mass"
    )
    processed.associate_y(
        Phis[i],
        scatter=Phi_scatter[i],
        comoving=False,
        description="Black hole mass function",
    )
    processed.associate_citation(citation, bibcode)
    processed.associate_name(name)
    processed.associate_comment(comment)
    processed.associate_redshift(redshift)
    processed.associate_plot_as(plot_as)
    processed.associate_cosmology(cosmology)

    output_path = f"{output_directory}/{output_filenames[i]}"

    if os.path.exists(output_path):
        os.remove(output_path)

    processed.write(filename=output_path)
