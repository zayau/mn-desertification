# Data inventory

Earth Engine IDs, periods and resolutions were checked against the public Earth Engine catalog on 3 October 2026. "Present" means the catalog held data from the last two months. End years of yearly products are read from the catalog's date range and may be off by one. Citations for dataset papers are in [references.bib](references.bib).

## Imagery and vegetation

| Dataset | Earth Engine ID | Period | Resolution | Note |
|---|---|---|---|---|
| Landsat 5 surface reflectance | `LANDSAT/LT05/C02/T1_L2` | 1984–2012 | 30 m | How many scenes cover Mongolia in the 1980s and 1990s still has to be counted |
| Landsat 7 surface reflectance | `LANDSAT/LE07/C02/T1_L2` | 1999–2024 | 30 m | Striped gaps in every scene after May 2003 |
| Landsat 8 surface reflectance | `LANDSAT/LC08/C02/T1_L2` | 2013–present | 30 m | |
| Landsat 9 surface reflectance | `LANDSAT/LC09/C02/T1_L2` | 2021–present | 30 m | |
| Harmonized Landsat Sentinel-2 | `NASA/HLS/HLSL30/v002` | 2013–present | 30 m | |
| Sentinel-2 surface reflectance | `COPERNICUS/S2_SR_HARMONIZED` | 2017–present | 10–60 m | The catalog starts in March 2017 |
| Sentinel-1 radar | `COPERNICUS/S1_GRD` | 2014–present | 10 m | Sees through cloud |
| MODIS vegetation indices | `MODIS/061/MOD13Q1` | 2000–present | 250 m, 16 days | NDVI and EVI |
| MODIS reflectance | `MODIS/061/MCD43A4` | 2000–present | 500 m, daily | The product behind the release's site table. Each daily value is fitted to the cloud-free observations of 16 days and carries the date of the ninth day. Its [guide](https://www.umb.edu/spectralmass/modis-user-guide-v006-and-v0061/mcd43a4-nbar-product/) advises the full-inversion values for scientific use; a quality band marks them. Read on 6 October 2026 |
| MODIS land surface temperature | `MODIS/061/MOD11A2` | 2000–present | 1 km, 8 days | |
| MODIS net primary production | `MODIS/061/MOD17A3HGF` | 2001–2024 | 500 m, yearly | |
| MODIS vegetation continuous fields | `MODIS/061/MOD44B` | 2000–2025 | 250 m, yearly | Tree, other vegetation and bare ground fractions |
| MODIS burned area | `MODIS/061/MCD64A1` | 2000–present | 500 m, monthly | |
| GIMMS NDVI3g | `NASA/GIMMS/3GV0` | 1981–2013 | about 9 km | The catalog copy ends in 2013. PKU GIMMS NDVI runs from 1982 to 2022 (Li et al. 2023) and is outside the catalog |
| AVHRR NDVI climate data record | `NOAA/CDR/AVHRR/NDVI/V5` | 1981–2013 | about 5.6 km | |

## Climate

| Dataset | Earth Engine ID | Period | Resolution | Note |
|---|---|---|---|---|
| ERA5-Land, monthly | `ECMWF/ERA5_LAND/MONTHLY_AGGR` | 1950–present | about 11 km | Temperature, precipitation, soil moisture, wind, snow. Best daily precipitation of the products tested over the plateau (Xin et al. 2022) |
| TerraClimate | `IDAHO_EPSCOR/TERRACLIMATE` | 1958–2024 | about 4.6 km | Monthly climate and water balance |
| CHIRPS precipitation | `UCSB-CHG/CHIRPS/DAILY` | 1981–present | about 5.6 km | Covers 50°S to 50°N only, so northern Mongolia is missing |
| GPM IMERG, monthly | `NASA/GPM_L3/IMERG_MONTHLY_V07` | 1998–2025 | about 11 km | |
| SMAP soil moisture | `NASA/SMAP/SPL4SMGP/008` | 2015–present | about 11 km | |
| SPEIbase drought index | `CSIC/SPEI/2_10` | 1901–2022 | about 55 km | The catalog marks this version as deprecated |
| MERRA-2 aerosol | `NASA/GSFC/MERRA/aer/2` | 1980–present | about 50 km | Dust |
| NEX-GDDP-CMIP6 projections | `NASA/GDDP-CMIP6` | 1950–2100 | about 28 km | Scenario input. CMIP6 missed the runoff drop around 2000 on the plateau (Qi et al. 2024) |

## Land surface and people

| Dataset | Earth Engine ID | Period | Resolution | Note |
|---|---|---|---|---|
| SRTM elevation | `USGS/SRTMGL1_003` | 2000 | 30 m | Extends to 60°N, which covers Mongolia |
| ESA WorldCover | `ESA/WorldCover/v200` | 2021 | 10 m | |
| Dynamic World land cover | `GOOGLE/DYNAMICWORLD/V1` | 2015–present | 10 m | |
| MODIS land cover | `MODIS/061/MCD12Q1` | 2001–2024 | 500 m, yearly | Guo et al. 2024 judged it the best of five products for the plateau |
| JRC Global Surface Water | `JRC/GSW1_4/YearlyHistory` | 1984–2021 | 30 m | Lakes and rivers |
| Satellite Embedding | `GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL` | 2017 onward, yearly | 10 m | Output of the AlphaEarth Foundations model (Brown et al. 2025) |
| OpenLandMap soil organic carbon | `OpenLandMap/SOL/SOL_ORGANIC-CARBON_USDA-6A1C_M/v02` | static | 250 m | |
| WorldPop population | `WorldPop/GP/100m/pop` | 2000–2020 | about 100 m | |
| geoBoundaries, second level | `WM/geoLab/geoBoundaries/600/ADM2` | 2023 | vector | Whether it matches soum boundaries still has to be checked |

Global land cover products should be checked over sparse vegetation before use. Two 30 m land cover datasets for Mongolia already disagree on the trend in barren land (Hao et al. 2023, Wang et al. 2022).

## Mongolia-specific data

| Data | Holder | Access | Note |
|---|---|---|---|
| Livestock census by soum, yearly | National Statistics Office, 1212.mn | Public. The [livestock table by type, bag, soum and aimag](https://data.1212.mn/pxweb/en/NSO/NSO__Industry,%20service__Livestock/DT_NSO_1001_021V1.px/), used by Van Laere et al. 2026, answers through the PX-Web API at `https://data.1212.mn/api/v1/en/NSO/Industry,%20service/Livestock/DT_NSO_1001_021V1.px`. On 3 October 2026 it held 1970 to 2025, six livestock types and 2,222 areas down to bag level. Not yet downloaded | Purevjav et al. 2025 used 41 years at soum level. Counts carry reporting bias. Large herds tend to be under-reported because of the livestock tax, and small herds over-reported to secure loans (Gonchigsumlaa and Sukhbaatar 2021, as cited by Van Laere et al. 2026) |
| Replication data for Purevjav et al. 2025 | Dryad, doi:10.5061/dryad.bg79cnpmz | Public, CC0. Downloaded through a browser on 3 October 2026, since Dryad refuses command-line downloads. Kept in `data/raw/namem/`, with the data files in `tables/`, the boundaries in `maps/`, the Stata code in `code/`, the README and the paper's supplement. The authors' git history, a duplicate README and empty output folders were left out | By soum and year, 1984–2024: herd sizes from the December census and the June survey, Landsat and MODIS vegetation indices, biomass for 2001–2020, and seasonal weather on summer and winter grazing ranges. `bms_plot.dta` holds August biomass at 1,488 sites with coordinates, 2007–2020, most sites in 12 to 14 years. The supplement names NAMEM's monitoring plots as the source. The soum biomass is the same measurements averaged by soum for 2007–2020, plus 2001–2006 from an undescribed source. Maps of aimag, soum and bag boundaries, ecological zones and seasonal pastures in Stata format. See [../docs/data-checks.md](../docs/data-checks.md). Stata code |
| Gridded livestock at 1 km, 2000–2024 | Liu et al. 2026, Zenodo, doi:10.5281/zenodo.22658481 | Public, CC BY 4.0. 25 yearly GeoTIFFs of 6.4 MB each | Standard sheep units per 1 km cell for Mongolia and Inner Mongolia. The method paper has not been found yet |
| Rangeland monitoring at 1,516 sites | National Agency for Meteorology and Environmental Monitoring (NAMEM) | No public download found. Held by NAMEM. The land agency's recent reports say the data go into an integrated land monitoring database (search-result summary, not opened). The 2018 report points to tsag-agaar.mn for web information on plot conditions | One site per bag. Meteorology technicians in 320 soums measure each site yearly since 2011: line-point intercept cover, gaps between perennial plants, plant height, species composition, biomass clipped at 1 cm and photo points. Aimag engineers check the data and enter them into the National Rangeland Monitoring Database, adapted from DIMA. Degradation levels and recovery classes come from state-and-transition models (Densambuu et al. 2018). Recovery class maps are produced yearly and national reports every three years (Sainnemekh et al. 2022). The strongest candidate for ground truth |
| Weather station archive, archive.weather.gov.mn | NAMEM | Registration and payment through a Mongolian payment system, or by email to archivemeteo@gmail.com for those who cannot pay that way. Seen on 3 October 2026 | More than 130 stations since 1985. Daily, monthly and yearly air and soil temperature, precipitation, pressure, humidity and wind. The value 16448 means no precipitation in the precipitation series and a missing value in all other series. Not rangeland data. Useful only to check ERA5-Land against stations |
| Photo-point monitoring at 4,200 sites | Agency for Land Management, Geodesy and Cartography | Unknown, to be asked | Plant group cover by seasonal pasture in 278 soums (Densambuu et al. 2018) |
| Ecological zone map | National Agency for Meteorology and Environmental Monitoring, through eic.mn/geodata | Cited by Purevjav et al. 2025. Not yet opened | Needed to model by zone |
| Field plots at 143 sites | Jamsranjav et al. 2018 | Public on Dryad, doi:10.5061/dryad.3ch50. A zip of 83 kB and a README | Winter pastures in 36 soums |
| Vegetation plots at 11 sites, 2019–2020 | Jäschke et al. 2026 | Public on Zenodo, doi:10.5281/zenodo.18936374. Ten text, spreadsheet and R files, about 0.5 MB in all. Not yet opened | 275 plots of 10 × 10 m with cover by species, in the central and eastern steppe. The paper classes each species as palatable or not |
| Forage monitoring at 297 Gobi sites, from 2004 | Gobi Forage early warning system, run by Mercy Corps with Texas A&M University (Bolor-Erdene et al. 2008) | Unknown | Vegetation, soil and grazing data at set-up, and biomass clipped 2 to 4 times per site up to 2007 (Angerer et al. 2008). Ground truth for the Gobi if it can be found |
| Above-ground biomass map of the central and eastern steppe | Ji et al. 2024 | Availability to be checked in the paper | Random forest on Sentinel-1 and Sentinel-2, trained on more than 600 field samples. Van Laere et al. 2026 used it for 2019–2021 |
| Land cover at 30 m for 1990, 2000, 2010, 2020 | Wang et al. 2022, *Geoscience Data Journal* | Published as a dataset paper. Location to be taken from the paper | 11 classes |
| Desertification maps, 1990 to 2020 | Meng et al. 2021, Xu et al. 2024 | Meng et al. 2021 has no data availability statement. Xu et al. 2024 still to be checked | Landsat, 30 m. Meng's classes are set by vegetation cover, so the naturally sparse Gobi counts as extremely severe |
| National desertification assessment maps | Ministry of Environment and Climate Change | Not obtained | Their figures are known only from secondary sources |

## Methods and tools

| Purpose | Reference key |
|---|---|
| Platform | `gorelick2017` (Google Earth Engine) |
| Change detection in time series | `verbesselt2010` (BFAST), `kennedy2010` (LandTrendr), `zhu2014` (CCDC) |
| Removing the rainfall signal from a trend | `evans2004`, `wessels2007`, `burrell2017` |
| Testing what a trend method can detect | `wessels2012` (losses of known size inserted into real series) |
| Segmentation | `ronneberger2015` (U-Net) |
| Spatio-temporal forecasting | `shi2015` (ConvLSTM), `benson2024` (Contextformer, open code and weights) |
| Pretrained geospatial models | `szwarcman2024` (Prithvi-EO-2.0), `brown2025` (AlphaEarth Foundations) |
| Validation | `roberts2017`, `ploton2020`, `meyer2022` |
| Field-trained cover mapping | `allred2021` (Rangeland Analysis Platform, rangelands.app) |
| Forecasting shifts by lead time | `bernardino2025`, code and data on Zenodo, doi:10.5281/zenodo.10636821 |
| Vegetation model with livestock | `vanlaere2026`, model, data and code on Zenodo as one zip of 48.8 GB, doi:10.5281/zenodo.17465156 (the version the paper cites; doi:10.5281/zenodo.17465155 covers all versions) |
