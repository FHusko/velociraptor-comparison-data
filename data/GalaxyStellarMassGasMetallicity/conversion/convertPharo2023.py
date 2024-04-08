from velociraptor.observations.objects import ObservationalData

import csv
import numpy as np
import os
import sys
import unyt

# Exec the master cosmology file passed as first argument
with open(sys.argv[1], "r") as handle:
    exec(handle.read())

h_obs = 0.7
h_sim = cosmology.h

input_filename = f"../raw/Pharo2023.csv"

comment = (
    "The relationship between stellar mass and gas-phase metallicity "
    "at 0.3<z<0.85 from the HALO7D survey. "
    "Uses Kroupa initial mass function and h=0.7. "
    f"h-corrected for SWIFT using cosmology: {cosmology.name}. "
    "The metallicity is calculated using 4 different methods. "
    "The stellar mass for each method is offset by 0.03 dex "
)
bibcode = "2023ApJ...959...48P"
name = "Galaxy Stellar Mass - Gas Metallicity"
plot_as = "points"
redshift = 0.7

all_indicators = ["Ne3O2", "O3HB", "O3O2", "R23"]
indicators, Mstar, Zgas, Zgas_std = [], [], [], []

with open(input_filename, "r") as file:
    data = csv.reader(file, delimiter=",")
    for c, row in enumerate(data):
        # Skip header
        if c > 2:
            m = float(row[1])
            # Add a stellar mass offset so datapoints from different
            # methods are not plotted atop each other
            m += 0.03 * (all_indicators.index(row[0]) - 1.5)
            indicators.append(row[0])
            Mstar.append(10 ** m * (h_sim / h_obs) ** -2)
            Zgas.append(float(row[2]))
            Zgas_std.append(float(row[3]))

Mstar = unyt.unyt_array(Mstar, units=unyt.Msun)
Zgas = unyt.unyt_array(Zgas, units=unyt.dimensionless)
Zgas_std = unyt.unyt_array(Zgas_std, units=unyt.dimensionless)

for indicator in all_indicators:
    processed = ObservationalData()

    mask = np.array(indicators) == indicator
    processed.associate_x(
        Mstar[mask], scatter=None, comoving=False, description="Galaxy Stellar Mass"
    )
    processed.associate_y(
        Zgas[mask],
        scatter=Zgas_std[mask],
        comoving=False,
        description="Galaxy Gas Metallicity",
    )
    citation = f"Pharo et al. (2023, {indicator})"
    processed.associate_citation(citation, bibcode)
    processed.associate_name(name)
    processed.associate_comment(comment)
    processed.associate_redshift(redshift)
    processed.associate_plot_as(plot_as)
    processed.associate_cosmology(cosmology)

    output_path = f"../Pharo2023_{indicator}.hdf5"

    if os.path.exists(output_path):
        os.remove(output_path)

    processed.write(filename=output_path)
