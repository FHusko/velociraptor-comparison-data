from velociraptor.observations.objects import (
    ObservationalData,
    MultiRedshiftObservationalData,
)

import unyt
import numpy as np
import os
import sys

# Exec the master cosmology file passed as first argument
with open(sys.argv[1], "r") as handle:
    exec(handle.read())

comment = ("Paper assumes a Kroupa IMF so stellar masses are converted to Chabrier.",)
citation = f"Weibel et al. (2024)"
bibcode = "2024arXiv240308872W"
name = f"Galaxy Stellar Mass Function"
plot_as = "line"
multi_z = MultiRedshiftObservationalData()
multi_z.associate_citation(citation, bibcode)
multi_z.associate_name(name)
multi_z.associate_comment(comment)
multi_z.associate_cosmology(cosmology)
multi_z.associate_maximum_number_of_returns(1)

input_filename = f"../raw/Weibel2024.txt"
raw = np.loadtxt(input_filename)

h_sim = cosmology.h
h_obs = 0.7

for z in [4, 5, 6, 7, 8, 9]:

    zmin = z - 0.5
    zmax = z + 0.5
    mask = raw[:, 0] == zmin

    Mstar = 10.0 ** raw[:, 2] * unyt.Msun
    Mstar *= (h_sim / h_obs) ** (-2)
    Mstar *= kroupa_to_chabrier_mass

    phi = 10.0 ** raw[:, 3]
    phi_hi = 10.0 ** (raw[:, 3] + raw[:, 4])
    phi_lo = 10.0 ** (raw[:, 3] - raw[:, 5])
    phi_scatter = (
        unyt.unyt_array(
            (phi[mask] - phi_lo[mask], phi_hi[mask] - phi[mask]),
            units=1.0 / unyt.Mpc ** 3,
        )
        * (h_sim / h_obs) ** 3
    )
    phi = unyt.unyt_array(phi, units=1.0 / unyt.Mpc ** 3) * (h_sim / h_obs) ** 3

    processed = ObservationalData()
    processed.associate_x(
        Mstar[mask], scatter=None, comoving=False, description="Galaxy Stellar Mass"
    )
    processed.associate_y(
        phi[mask],
        scatter=phi_scatter,
        comoving=True,
        description="Galaxy Stellar Mass Function",
    )
    processed.associate_redshift(z, zmin, zmax)
    processed.associate_plot_as(plot_as)

    multi_z.associate_dataset(processed)

output_path = f"../Weibel2024.hdf5"

if os.path.exists(output_path):
    os.remove(output_path)

multi_z.write(filename=output_path)
