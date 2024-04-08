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

input_filename = "../raw/Koprowski2024.txt"
raw = np.loadtxt(input_filename)

comment = (
    "Assuming Chabrier IMF (2003), and a standard LCDM cosmology with H=70km/s/Mpc. "
    "Supplied h-free so no corrections have been made."
    "SFRs are based on UV+IR"
)
citation = "Koprowski et al. (2024)"
bibcode = "2024arXiv240306575K"
name = "Galaxy Stellar Mass-Star Formation Rate "
plot_as = "line"

for star_forming in [0, 1]:
    multi_z = MultiRedshiftObservationalData()
    multi_z.associate_citation(citation, bibcode)
    multi_z.associate_name(name)
    multi_z.associate_comment(comment)
    multi_z.associate_cosmology(cosmology)
    multi_z.associate_maximum_number_of_returns(1)
    for i, (zmin, zmax) in enumerate(
        [
            (0.25, 0.75),
            (0.75, 1.25),
            (1.25, 1.75),
            (1.75, 2.25),
            (2.25, 2.75),
            (2.75, 3.75),
            (3.75, 4.75),
            (4.75, 6.75),
        ]
    ):
        zmean = 0.5 * (zmin + zmax)
        # Select all or star-forming galaxies
        star_forming_mask = raw[:, 0] == star_forming
        # Select mass ranges with data at this redshift
        mass_mask = raw[:, 3 + 2 * i] != 0
        # Combine masks
        mask = star_forming_mask & mass_mask

        M = 10 ** ((raw[:, 1] + raw[:, 2]) / 2) * unyt.solar_mass
        sfr = 10 ** raw[:, 3 + 2 * i] * unyt.solar_mass / unyt.year
        sfr_lo = (
            10 ** (raw[:, 3 + 2 * i] - raw[:, 4 + 2 * i]) * unyt.solar_mass / unyt.year
        )
        sfr_hi = (
            10 ** (raw[:, 3 + 2 * i] + raw[:, 4 + 2 * i]) * unyt.solar_mass / unyt.year
        )
        # Need to apply mask here due to shape of sfr_scatter
        sfr_scatter = unyt.unyt_array(
            (sfr[mask] - sfr_lo[mask], sfr_hi[mask] - sfr[mask]),
            units=unyt.solar_mass / unyt.year,
        )

        processed = ObservationalData()
        processed.associate_x(
            M[mask], scatter=None, comoving=True, description="Galaxy Stellar Mass"
        )
        processed.associate_y(
            sfr[mask],
            scatter=sfr_scatter,
            comoving=True,
            description="Star Formation Rate",
        )
        processed.associate_redshift(zmean, zmin, zmax)
        processed.associate_plot_as(plot_as)

        multi_z.associate_dataset(processed)

    output_path = f'../Koprowski2024{"_SF" if star_forming else ""}.hdf5'

    if os.path.exists(output_path):
        os.remove(output_path)

    multi_z.write(filename=output_path)
