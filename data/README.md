# Data

Git tracks only this file. The data themselves stay on your machine, in the layout below, which the notebooks and the `mn_desertification` package expect.

```
data/
├── raw/
│   └── namem/                     the Purevjav et al. 2025 release, unpacked
│       ├── tables/                bms_plot.dta, vegi_plot_modis_aug.dta, wrk_soum.dta
│       ├── maps/                  mn_soum_*.dta, mn_pas_*.dta and other boundaries
│       ├── code/                  the authors' Stata files
│       ├── README.md              the authors' description of every file and column
│       └── science.adn0005_sm.pdf the paper's supplementary materials (optional)
└── processed/                     tables written by the notebooks
```

To keep the data somewhere else, set the environment variable `MN_DESERTIFICATION_DATA` to a folder with the same layout.

## The raw data

NAMEM's August biomass at its rangeland monitoring sites was published with Purevjav et al. (2025), "Climate rather than overgrazing explains most rangeland primary productivity change in Mongolia", *Science*. The replication data are on Dryad, [doi:10.5061/dryad.bg79cnpmz](https://doi.org/10.5061/dryad.bg79cnpmz), under CC0.

| File | Content |
|---|---|
| `tables/bms_plot.dta` | August biomass clipped at 1,488 NAMEM sites, 2007–2020, in centners per hectare (1 c/ha = 100 kg/ha), with site coordinates |
| `tables/vegi_plot_modis_aug.dta` | MODIS vegetation indices (500 m) at the same sites, 2000–2024 |
| `tables/wrk_soum.dta` | One row per soum and year: weather on the soum's seasonal grazing ranges, the livestock census and other soum variables |
| `maps/mn_soum_xy.dta`, `maps/mn_soum_db.dta` | Soum outlines and names |
| `maps/mn_pas_xy.dta`, `maps/mn_pas_db.dta` | The land agency's seasonal pasture map, 16 areas drawn with 42 million points (5.3 GB) |

To set it up:

1. Download the zip, about 5.2 GB, from the Dryad page in a browser. Dryad refuses downloads from the command line.
2. Unzip it. It holds three folders, `code`, `data` and `map`.
3. Put them in `data/raw/namem/` as `code/`, `tables/` (the release's `data` folder) and `maps/` (its `map` folder), and copy the release's `README.md` next to them.
4. Optionally, save the supplementary materials PDF from the paper's page on science.org into the same folder. The notebooks do not need it.

## Processed tables

The notebooks write their tables to `processed/`. Run the notebooks in order, `01` to `09`, to rebuild them. The Landsat extraction takes about an hour and runs as a script, `.venv/bin/python scripts/extract_landsat.py`, which can be stopped and started again.

| File | Written by | Content |
|---|---|---|
| `sites.csv` | 01 | One row per site: coordinates, soum, aimag, ecological zone and seasonal pasture |
| `site_year.csv` | 01 | One row per site and year, 2007–2020: biomass, the soum's rain, and rain as a percent of the soum's 2011–2020 normal |
| `flags.csv` | 01 | The three values flagged as likely recording errors |
| `remainders.csv` | 02 | One row per site and year, 2011–2020: what the two weather models leave unexplained |
| `site_trends.csv` | 02 | One row per site and weather model: trend slopes, p-values and false-discovery-adjusted p-values |
| `detection_test.csv` | 03 | Every run of the detection test |
| `robustness.csv` | 03 | The robustness checks |
| `soums.csv` | 04 | One row per soum: biomass and greenness responses, herd measures, zone and aimag |
| `herd_tests.csv` | 04 | The herd tests |
| `pasture_tests.csv` | 04 | The pasture-type tests |
| `modis_candidates.csv` | 05 | MODIS greenness at every site in three test years, in twelve versions of window, summary and quality |
| `modis_august_mean.csv` | 05 | One row per site and year, 2000–2024: the August mean of MODIS NDVI and MSAVI within 100 m of the plot, and the number of days behind it |
| `modis_jul_aug_median.csv` | 05 | The same for the median of July and August, the rule of the satellite check |
| `landsat_conversions.csv` | 07 | The lines that put Landsat 5, 8 and 9 reflectance on the Landsat 7 scale, fitted to pairs of observations at the sites |
| `landsat_site_years.csv` | 08 | One row per site and year, 1985–2024: the median Landsat NDVI of July and August on the Landsat 7 scale, and the number of observations behind it |
| `era5_land_monthly.csv` | 09 | One row per site, year and month, March to August of 1989–2024: ERA5-Land's precipitation, snowfall and mean temperature at the grid cell that holds the plot |
| `landsat/landsat5_1986.csv` and so on | `scripts/extract_landsat.py` | One file per Landsat sensor and year. One row per site, circle (100 m and 50 m) and overpass from June to September: the mean red and near-infrared reflectance of the clear pixels, the mean of their NDVI and MSAVI, and the number of clear pixels |

## NAMEM's full monitoring records

NAMEM's full records, with plant cover and the years after 2020, are not public. If they become available, keep them in their own folder under `raw/`, such as `raw/namem-monitoring/`, and out of git like everything else here.
