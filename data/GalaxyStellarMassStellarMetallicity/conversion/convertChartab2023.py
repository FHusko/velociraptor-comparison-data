from velociraptor.observations.objects import ObservationalData

import os
import sys
import numpy as np
import unyt

# Exec the master cosmology file passed as first argument
with open(sys.argv[1], "r") as handle:
    exec(handle.read())

# Cosmology
h_obs = 0.7
h_sim = cosmology.h

input_filename = "../raw/Chartab2023.txt"
raw = np.loadtxt(input_filename)

comment = (
    "The relationship between stellar mass and stellar metallicity "
    "at 2<z<3 from the LATIS survey. "
    "Uses Chabrier initial mass function and h=0.7. "
    f"h-corrected for SWIFT using cosmology: {cosmology.name}. "
    "Metallicity is effectively [Fe/H]. "
)
citation = "Chartab et al. (2023)"
bibcode = "2023arXiv231012200C"
name = "Galaxy Stellar Mass - Gas Metallicity"
plot_as = "points"
redshift = 2.5

Mstar = 10.0 ** raw[:, 0] * (h_sim / h_obs) ** -2 * unyt.Solar_Mass
Zstar = 10.0 ** raw[:, 1] * unyt.dimensionless
Zstar_err_hi = 10.00 ** (raw[:, 1] + raw[:, 2]) * unyt.dimensionless
Zstar_err_lo = 10.00 ** (raw[:, 1] - raw[:, 3]) * unyt.dimensionless
Zstar_err = unyt.unyt_array((Zstar - Zstar_err_lo, Zstar_err_hi - Zstar))

processed = ObservationalData()
processed.associate_x(
    Mstar, scatter=None, comoving=False, description="Galaxy Stellar Mass"
)
processed.associate_y(
    Zstar, scatter=Zstar_err, comoving=False, description="Stellar metallicity"
)
processed.associate_citation(citation, bibcode)
processed.associate_name(name)
processed.associate_comment(comment)
processed.associate_redshift(redshift)
processed.associate_plot_as(plot_as)
processed.associate_cosmology(cosmology)

output_path = f"../Chartab2023.hdf5"

if os.path.exists(output_path):
    os.remove(output_path)

processed.write(filename=output_path)
