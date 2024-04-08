from velociraptor.observations.objects import ObservationalData

import unyt
import numpy as np
import os
import sys

# Exec the master cosmology file passed as first argument
with open(sys.argv[1], "r") as handle:
    exec(handle.read())

input_filename = "../raw/Botticella_2017.txt"

output_filename = "Botticella2017.hdf5"
output_directory = "../"

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

processed = ObservationalData()
raw = np.loadtxt(input_filename)

comment = "Based on the COSMOS and CDFS sky-fields [$0.15<z<0.75$]"
citation = "Botticella et al. (2017)"
bibcode = "2017A&A...598A..50B"
name = "Galaxy Stellar Mass-SNIa rate"
plot_as = "points"
redshift = 0.15
h_obs = 0.7
h = cosmology.h

Mstar = unyt.unyt_array(10 ** raw.T[0], units="Msun")
SNIa_rate = unyt.unyt_array(10 ** raw.T[1], units="yr**(-1) * Msun**(-1)")

SNIa_log_err_up = raw.T[2]
SNIa_log_err_down = raw.T[3]
SNIa_err = unyt.unyt_array(
    [
        10 ** raw.T[1] - 10 ** (SNIa_log_err_down),
        10 ** (SNIa_log_err_up) - 10 ** raw.T[1],
    ],
    units="yr**(-1) * Msun**(-1)",
)
dMstar = 0.5 / 2.0
Mstar_err = unyt.unyt_array(
    [
        10 ** (raw.T[0]) - 10 ** (raw.T[0] - dMstar),
        10 ** (raw.T[0] + dMstar) - 10 ** (raw.T[0]),
    ],
    units="Msun",
)

processed.associate_x(
    Mstar, scatter=Mstar_err, comoving=True, description="Galaxy Stellar Mass"
)
processed.associate_y(
    SNIa_rate,
    scatter=SNIa_err,
    comoving=False,
    description="SNIa rate per stellar mass",
)
processed.associate_citation(citation, bibcode)
processed.associate_name(name)
processed.associate_comment(comment)
processed.associate_redshift(redshift, 0, 10)
processed.associate_plot_as(plot_as)
processed.associate_cosmology(cosmology)

output_path = f"{output_directory}/{output_filename}"

if os.path.exists(output_path):
    os.remove(output_path)

processed.write(filename=output_path)
