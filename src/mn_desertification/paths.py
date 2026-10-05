"""Where the data and the derived tables live.

By default the data are in the ``data`` folder at the top of the repository,
laid out as ``data/README.md`` describes. To keep them elsewhere, set the
environment variable ``MN_DESERTIFICATION_DATA`` to a folder with the same
layout.
"""

import os
from pathlib import Path

# This file is src/mn_desertification/paths.py, so the root is two levels up.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = Path(os.environ.get("MN_DESERTIFICATION_DATA", PROJECT_ROOT / "data"))

# The release of Purevjav et al. 2025, unpacked (see data/README.md).
RAW_DIR = DATA_DIR / "raw" / "namem"
TABLES_DIR = RAW_DIR / "tables"
MAPS_DIR = RAW_DIR / "maps"

# Tables written by the notebooks.
PROCESSED_DIR = DATA_DIR / "processed"
