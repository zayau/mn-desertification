# Data checks

Checks of downloaded data, run before the design is fixed. Each one says what was looked at, what it showed and how to rerun it.

## 1. Ground biomass in the Purevjav et al. 2025 release, 3 October 2026

**Data.** The release (Dryad, doi:10.5061/dryad.bg79cnpmz) is in `data/raw/namem/`, with the data files in `tables/`. `bms_plot.dta` holds biomass in centners per hectare (1 c/ha = 100 kg/ha) by site and year, with coordinates. The authors' code labels it August biomass. `vegi_plot_modis_aug.dta` holds August MODIS indices for the same sites from 2000 to 2024.

**What it holds.**

- 18,152 records at 1,488 sites from 2007 to 2020. 1,137 sites have 12 or more years and 773 have all 14.
- Median 2.4 c/ha (240 kg/ha). 366 records are below 0.1 c/ha and 22 above 30 c/ha, and these need checking.
- The source is NAMEM's monitoring plots. The paper's supplementary materials (p. S5) call it "NAMEM plot-level, ground-based biomass data over 2007-2020" and say the authors used it to check their vegetation indices. The network clips biomass at 1 cm every year (Densambuu et al. 2018). That report gives standing biomass by plant group, unpalatable groups such as sages and annuals included. So the clipping is not limited to forage plants. The release has one total per site and year, and whether it sums all groups is still to be confirmed with NAMEM.
- A soum-level biomass series in `wrk_soum.dta` covers 2001 to 2020, at about 300 soums a year. The supplement describes it as NAMEM field measurements averaged over June to August. For 2007 to 2020 it closely follows the average of the plots nearest each soum centre (r = 0.96), so it is the same measurements summed up by soum. Its new information is the six years from 2001 to 2006, whose source is not described.

**How well greenness tracks it.** Correlation of log biomass with August MODIS NDVI:

| Comparison | r |
|---|---|
| Across sites, using each site's mean | 0.77 |
| Within sites, from year to year | 0.38 |
| National yearly means, 14 years | 0.82 |

**How much of it is predictable.** Each site's average explains 38% of the variance in log biomass. Adding a national effect for each year raises that to 46%. A site's departure from normal in one year barely predicts the next year's (r = 0.11).

**Caveats.** This is a first look. The MODIS pixel is 500 m across and the clipping plot is much smaller, the clipping dates are not in the file, and the very low and very high values have not been screened. Measurement error lowers every correlation here. The check used all years, so from here on the test years have to be set aside before any modelling.

**What it means for the design.**

- A public field record of biomass over time exists for most of the national network up to 2020. A biomass target can be trained and tested against field data now, without waiting for NAMEM.
- NDVI is a fair guide to where biomass is high and a poor guide to how a site changes from year to year. An accurate NDVI forecast would not show that the biomass forecast is right.
- A model explains 38% of the variance just by learning each site's average, so skill has to be judged on departures from that average.
- Little carries over from one year to the next at a site, so forecasts years ahead are unlikely to beat the site average. Forecasts within the season, from spring weather and soil moisture, are more promising.
- The record ends in 2020. Test years would have to come from 2018 to 2020 unless NAMEM supplies later years.

**Rerun.** `python3 scripts/check_biomass.py`, which needs pandas.

## 2. Very low and very high values, 4 October 2026

Most of these numbers are reproduced in notebook 1 ([../notebooks/01-data.ipynb](../notebooks/01-data.ipynb)).

**Very low values.** 366 records are below 0.1 c/ha.

- 247 of them fall in 2007–2010, the years before the standard method. As a share of each year's records that is 8.4% in 2007, falling to 3.2% in 2010.
- From 2011 to 2019 the share is about 1% or less. In 2017, the poorest year, no record is below 0.1. Its 78 near-empty sites were recorded as exactly 0.1.
- 2020 has 73, or 5.2%, clustered in the south-central Gobi.
- Among the 773 sites measured in all 14 years, 2007 still has 70 (9.1%), spread from west to east. A change in which sites were measured does not explain the early values.
- 364 of the 366 are exactly 0.01 (302), 0.05 (45) or 0.001 (17), which look like stand-ins for zero rather than weights. Biomass is otherwise recorded in steps of 0.1 c/ha (96.6% of all values), and 400 records are exactly 0.1, the smallest step.
- The limits of 0.1 and 30 c/ha began as round screening values. 0.1 is kept as the floor because it is the smallest recorded step. 30 only flags values to inspect (the top 0.12%), since the rule for very high values is relative to each site.
- No site has more than four.

**Very high values.** 22 records are above 30 c/ha, spread over 2009–2019. Most are in the north and east, where meadows can produce that much. A few are in the dry south and are candidates for recording errors.

**Plotting note.** A boxplot of skewed data on a log axis has to be calculated on the log values. Matplotlib calculates its whiskers on the values it is given, so on raw values no low value can show as an outlier.

**What was decided.** The rules for the main period, the floor, very high values and 2020 are in [design.md](design.md).

## 3. Rainfall, 4 October 2026

Reproduced in notebook 1. Rain is spring and summer precipitation on each soum's summer grazing range, from the Purevjav et al. 2025 release.

- **The years line up.** National mean biomass follows the same year's growing-season rain (r = 0.54 over 14 years), not the previous year's (r = −0.06) or the next year's (r = −0.27).
- **2017 was the driest year** of 2007–2020, at 179 mm of growing-season rain on average, and had the lowest mean biomass.
- **2007–2010 had ordinary rain,** 197 to 220 mm, yet low biomass. Rain does not explain the early low values, which supports 2011–2020 as the main period.
- **2020 was dry in the south-central Gobi.** Its 73 low values sit where growing-season rain was a median 48% of the soum's 2011–2020 normal, while the other sites that year got 112%. Across the whole country in 2017 the median was 79%. Most of these low values are in Bayankhongor (36), Ömnögovi (15) and Övörkhangai (13).
- Every site-year has a rain value and a zone. Sites per zone: steppe 627, forest steppe 374, desert steppe 325, desert 113, mountain taiga 49.
- **By zone and year,** each site compared with its own average in logs:
  - 2007–2009 are below normal in every zone, with desert steppe at about 38% of normal in 2007.
  - 2012–2013 are above normal almost everywhere.
  - 2017 is below normal in every zone.
  - 2020 is far below only in the desert (about 43%) and desert steppe.

## 4. Recording errors, 5 October 2026

Checked for 2011–2020 before the weather model was fitted. Notebook 1 applies the rules below.

**A size rule removes real data.** Dropping every value more than 10 times the median of the site's other years would remove 77 values.

- 52 of them are in 2012–2013, the best years in the dry zones.
- 29 have another flagged site within 3 IDs in the same year, which points to good years across an area rather than typos.
- 11 are ordinary amounts under 5 c/ha at desert sites whose other years are tiny.

Swings of tenfold or more are common in both directions. 121 values sit more than ten times below what their zone's year predicts.

**Values flagged instead.** Three values meet the rules in [design.md](design.md). They stay in the raw data, marked with a flag.

| Site | Year | Place | Coordinates | Value (c/ha) | Reason |
|---|---|---|---|---|---|
| 28 | 2012 | Arkhangai, Ulziit | 48.0066 N, 102.3773 E | 96.00 | More than twice any other value in the record (the next is 42). 25 times the site's usual |
| 1289 | 2013 | Khovd, Erdeneburen | 48.3206 N, 91.3602 E | 26.50 | Lone spike between 2.7 in 2011 and 2.7 in 2014, possibly 2.65 with a shifted decimal point |
| 759 | 2013 | Uvurkhangai, Bayangol | 45.9662 N, 103.2070 E | 39.58 | Lone spike between 5.6 and 9.6. Two decimal places, while nearly all values use steps of 0.1 |

To be confirmed with NAMEM against the original records.

**Effect on the earlier checks.** Negligible.

- Leaving the three out lowers the mean of all sites by 0.07 c/ha in 2012 and 0.04 in 2013, with no change to any median.
- The correlation between biomass and rain by year moves from 0.535 to 0.536.
- No cell of the zone-and-year heatmap moves by more than 0.004.

The descriptions of the data above therefore stay as they are, and the flags apply from the weather model on.
