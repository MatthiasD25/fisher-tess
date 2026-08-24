# fisher-tess

This repository contains the analysis code used to generate the results and figures presented in:

**A New Probe of Dark Matter Subhalos: Stellar Aberration with TESS** 

Journal TBA: DOI

arXiv: TBA

If you use this software in your research, please cite the publication listed above.

## Repository contents

The repository provides tools to:

- generate apparent stellar aberration trails including TESS's orbital motion and DM-induced accelerations (see "Star_trails_jpl.ipynb"),
- identify bright TESS targets observed in the continuous viewing zones (CVZ) around the ecliptic poles (see "Get_reduced_TIC.ipynb", "Get_TICIDs_per_sector.py", and "Find_CVZ_TICIDs.ipynb"),
- compute acceleration sensitivities from the stars' sky distribution and TESS's observing characteristics using a Fisher-information approach (see "Fisher_analysis.ipynb"),
- derive constraints on detectable DM subhalo masses and distances (see "Reachable_parameter_space.ipynb").

The repository also contains:

- TESS spacecraft ephemerides from JPL Horizons for the first two operational orbits ("data"),
- figures presented in the associated publication ("figures_draft"),
- csv.files containing all TESS targets with Tmag $\leq$ 10 for each sector, as well as for the southern and northern CVZs ("tic").

## Data sources

The analysis uses publicly available data from:

- TESS Input Catalog (TIC):   
  MAST  
  https://archive.stsci.edu/tess/tic_ctl.html

- TESS spacecraft ephemerides:  
  JPL Horizons  
  https://ssd.jpl.nasa.gov/horizons/

## Requirements

The code requires the following Python packages:

- numpy
- pandas
- matplotlib
- astropy
- sys
- re
- os
- [tess-point](https://github.com/tessgi/tess-point)
- (multiprocessing)

## License
See LICENSE file.
