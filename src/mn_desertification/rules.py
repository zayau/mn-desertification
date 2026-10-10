"""The rules of the analysis, set before any trend was computed.

docs/design.md explains each rule under "Rules set before the results", and
docs/data-checks.md gives the evidence for it. The robustness checks in
notebook 03 change them one at a time.
"""

# Years in the release, and the main period. NAMEM's standard method began in 2011.
ALL_YEARS = (2007, 2020)
MAIN_YEARS = (2011, 2020)

# Biomass below this (c/ha) is raised to it before taking logs. 364 of the 366
# values below it are exactly 0.01, 0.05 or 0.001, stand-ins for zero, and
# biomass is otherwise recorded in steps of 0.1.
FLOOR = 0.1

# Values above this (c/ha) are listed in the data checks and left out in one
# robustness check.
HIGH_LIMIT = 30

# A site needs this many of the ten main-period years to get a trend.
MIN_YEARS = 8

# One-sided significance level for a decline.
ALPHA = 0.05

# Ecological zones from driest to wettest, the order used in tables.
ZONES = [
    "Desert zone",
    "Semi desert steppe zone",
    "Steppe zone",
    "Forest steppe zone",
    "Mountain taiga belt",
]

# Sheep units per head, the National Statistics Office weights
# (Purevjav et al. 2025, supplement Table S3).
SHEEP_UNITS = {"sheep": 1, "goat": 0.9, "cattle": 6, "horse": 7, "camel": 5}

# The satellite check. docs/design.md explains these under "Rules set before
# the extraction".

# The weeks of each year that satellite greenness is summarised over, as
# (month, day): 1 July to 31 August, up to and around the August clipping.
SEASON_FIRST = (7, 1)
SEASON_LAST = (8, 31)

# Greenness is averaged within this many metres of each plot, the radius the
# release used, and within a smaller circle as a check.
FOOTPRINT_M = 100
CHECK_FOOTPRINT_M = 50

# The weeks that are extracted, as (month, day): June to September, the widest
# window that any check needs.
EXTRACT_FIRST = (6, 1)
EXTRACT_LAST = (9, 30)

# A scene counts for a site when at least this share of the circle is clear.
# A check uses the stricter share.
MIN_CLEAR = 0.5
CHECK_MIN_CLEAR = 0.9

# Landsat 8 and 9 reflectance on the Landsat 7 scale: intercept and slope for
# each band (Roy et al. 2016, Table 2, ordinary least squares on surface
# reflectance).
TO_LANDSAT7 = {"red": (0.0123, 0.9372), "nir": (0.0448, 0.8339)}
