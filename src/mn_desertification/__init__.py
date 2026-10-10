"""Analysis code for the study of desertification in Mongolia's rangelands.

The package holds the steps that the notebooks in ``notebooks/`` share:

- ``paths``: where the data and the derived tables live.
- ``rules``: the rules set before any trend was computed (docs/design.md).
- ``data``: readers for the tables and maps of the Purevjav et al. 2025 release.
- ``sites``: placing the monitoring sites in soums and seasonal pastures.
- ``quality``: the floor and the flags for likely recording errors.
- ``weather``: the weather model and what it leaves unexplained.
- ``trends``: trend tests for sites and for yearly means.
- ``detection``: the detection test, the permutation test and the robustness checks.
- ``grazing``: herd measures and soum-level responses.
- ``satellite``: greenness at the sites from Google Earth Engine. It needs the
  optional ``satellite`` dependencies and is imported only where it is used.
- ``greenness``: the extracted satellite observations, and which of them count.
"""

__version__ = "0.1.0"
