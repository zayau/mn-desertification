# Research design

Phase 3 output. Draft of 4 October 2026. The question was agreed on that day. The rest is open to revision as the steps below report back.

## Question

Where did Mongolia's rangelands lose productivity between 2007 and 2020 beyond what rainfall explains, and could it have been predicted?

## What counts as desertification here

Desertification is land degradation in drylands ([scope.md](scope.md)), and most of Mongolia's rangeland is dryland. This study measures one part of it: a lasting decline in rangeland productivity beyond what rainfall explains. It is measured on the ground as the trend in August biomass after the effect of rain is removed. This is the field version of the productivity sub-indicator of SDG 15.3.1.

A dry year that lowers biomass and recovers with the rain is drought, not degradation. The other parts of degradation, changes in plant composition and bare ground, need NAMEM's cover data and are left for a later study.

## Data

| Role | Data | Note |
|---|---|---|
| Field truth | NAMEM August biomass at 1,488 sites, 2007–2020, from the release of Purevjav et al. 2025 | See [data-checks.md](data-checks.md). Sites measured in 12 to 14 years for the most part |
| Rainfall | Spring and summer rain on each soum's summer grazing range, from the same release | A soum-level stand-in. ERA5-Land at each site's coordinates can replace it later |
| Places | Soum boundaries and ecological zones from the same release | Used to link sites to rain and to model by zone |
| Satellite (step 2) | Landsat and MODIS through Earth Engine | Extends the record to 1985–2025 if it agrees with the field |
| Predictors (step 3) | Aridity, herd density from the livestock census, past trend, satellite signals | Livestock by bag from the statistics office's API |

## Steps

**1. Field truth and the detection test.** Link each site to its soum and zone. Model log biomass against growing-season rain within each ecological zone, with each site's own average. Fit a trend to what remains at each site and express it as percent change per decade. Then insert declines of known size into the real series to find how large a decline can be detected, and at which level (site, soum or zone). The analysis is in notebooks 1 to 3 ([../notebooks/](../notebooks/)).

**2. Satellite check.** Apply standard satellite methods for rain-adjusted trends at the same sites and see whether they find the declines the field data show.

**3. Prediction.** Use information up to a cut-off year to predict which sites or areas decline afterwards. Score the predictions against simple baselines: aridity, herd density and the past trend.

## Rules set before the results

The first five were agreed on 4 October 2026, before any trend was computed. The evidence is in [data-checks.md](data-checks.md), check 2.

- **Main period.** Step 1 uses 2011–2020, the years of the standard method, and repeats every result for 2007–2020 as a check. Values below 0.1 c/ha make up 3 to 8% of records each year in 2007–2010, about 1% or less in 2011–2019, and none in the 2017 drought. The early share stays high among the 773 sites measured every year, so it is not a matter of which sites were measured.
- **Very low values.** Values below 0.1 c/ha are raised to 0.1 before taking logs. 364 of the 366 such values are exactly 0.01, 0.05 or 0.001, which look like stand-ins for zero rather than weights. Biomass is otherwise recorded in steps of 0.1 c/ha, so the floor puts the stand-ins level with near-empty sites recorded at the smallest step. Results are repeated with floors of 0.05 and 0.2.
- **Recording errors.** Revised on 5 October 2026, still before any trend. The first rule, which dropped any value more than 10 times the median of the site's other years, would have removed 77 values in 2011–2020, mostly real peaks of the good years 2012 and 2013. Now a value is flagged only on several pieces of evidence, and the raw data stay unchanged.
  - A lone spike is more than 10 times what the site's usual level and its zone's year predict, in a soum-year with less than 120% of normal rain, and with no other site in the soum above 3 times its expected value.
  - A value off the scale is more than twice any other value in the record.
  - Flagged values are left out of the main analysis, listed in [data-checks.md](data-checks.md), check 4, and brought back in a check. They should be confirmed against NAMEM's original records.
  - Errors no rule can find are handled by working in logs and by a slope that resists outliers.
- **2020.** Its low values cluster in the south-central Gobi, where growing-season rain was about half of its 2011–2020 normal (median 48%, against 112% at the other sites that year). Drought explains them, so they stay, under the floor ([data-checks.md](data-checks.md), check 3). Added on 5 October 2026, after the comparison with satellite greenness: the weather models predict less of the 2020 low than happened in the dry zones, so national results are also reported without 2020 ([findings.md](findings.md)).
- **Enough years.** A site needs at least 8 of the 10 years in 2011–2020 to get a trend, which 1,250 sites have. In the 2007–2020 check it needs 10 of the 14 years.
- The study works at the smallest level where a 20% decline is detected in at least 80% of trials. Degraded rangeland elsewhere sits 10 to 20% below intact land (Wessels et al. 2012). The detection test found that no level meets this, the best being 22–23% at zone level ([findings.md](findings.md)).
- **Weather model.** Rain only, as planned. Summer temperature was added as a second model after the site trends showed a shared pattern, and both are reported.
- When individual sites are flagged as declining, the false discovery rate is controlled. Otherwise results are reported as shares of sites.
- The cut-off year and test period for step 3 are fixed before any prediction model is trained.

## The satellite check (step 2)

Planned on 6 October 2026, before any satellite value was extracted for this study.

Step 1 changed what this step has to answer. Clipped biomass fell at the sites over 2011–2020, relative to the weather, while the release's MODIS greenness, measured at 500 m, did not ([findings.md](findings.md)). The release holds no Landsat values for the sites.

### Questions

1. **Replication.** Does greenness extracted here from the same MODIS product match the release's table? This tests the extraction, and shows which dates and footprint the release's values stand for.
2. **Scale.** Does Landsat greenness at 30 m, close to each plot, decline over 2011–2020 after rain and temperature, where MODIS at 500 m did not?
3. **Agreement with the field.** How closely does Landsat greenness follow biomass at the same sites, from year to year and between sites, compared with MODIS?
4. **The long record.** Relative to the weather, is 2011–2020 unusual within the Landsat record, which starts in the 1980s?

### Data

All of it comes through Earth Engine, with the dataset IDs in [../sources/datasets.md](../sources/datasets.md).

| Role | Data | Note |
|---|---|---|
| MODIS reflectance | MCD43A4, 500 m, daily, from 2000 | The product behind the release's site table |
| Landsat surface reflectance | Collection 2 Level 2, Tier 1, from Landsat 5, 7, 8 and 9, from 1984 | 30 m |
| Weather | The release's soum table, 1970–2024 | As in step 1 |

### Rules set before the extraction

The Landsat rules were changed on 11 October 2026, after the MODIS stage and before any Landsat value was analysed. Greenness is now extracted scene by scene and summarised afterwards. That allows the sensors to be compared scene by scene, and every check to run on one saved table. The MODIS stage followed the earlier order: each pixel's median over the season first, then the mean within the circle. The sensor checks measure what that difference in order does to the MODIS values.

- **Index.** NDVI is the main measure, as in step 1 and in the residual-trend method (Evans & Geerken 2004, Wessels et al. 2012). MSAVI, which corrects for bare soil between plants, is the check for sparse cover.
- **Observation.** One scene gives a site one observation: the mean red and the mean near-infrared reflectance of the clear pixels within 100 m of the plot, on the scene's own pixel grid. The indices are computed from those two means, as a sensor with that footprint would measure them.
  - Each pixel counts by the share of it that lies inside the circle, which Earth Engine measures in steps of about 1/256 of a pixel.
  - 100 m is the radius the release used. A check uses 50 m. The size of a NAMEM plot is not given in the sources read so far.
  - A second check uses the mean of the pixels' own NDVI in place of the NDVI of the mean reflectances.
  - A satellite pass is cut into scenes that overlap at their edges and share a pixel grid. The scenes of a pass are joined before the extraction, so a site in an overlap is counted once.
- **Clear pixels.** A Landsat pixel is clear when its quality band flags none of fill, cloud, dilated cloud, cirrus, cloud shadow and snow, when neither of the two bands is saturated, and when both reflectances lie between 0 and 1. An observation counts when at least half of the circle is clear. A check requires 90%.
  - The MODIS product has no such flags to apply. Each of its daily values is fitted to the cloud-free observations of 16 days, by a full inversion when there are enough of them and by a lower-quality magnitude inversion otherwise.
  - Both kinds are kept, so that cloudy weeks are not left out. A check keeps full inversions only, which the product's guide advises for scientific use.
- **Season.** A site's value for a year is the median of its observations from 1 July to 31 August, the weeks up to and around the August clipping. Two checks use August alone and the highest value from June to September, so the extraction covers June to September. A site-year with no observation in the season is missing.
- **Sensors.** Landsat 8 and 9 reflectance is converted to the Landsat 7 scale with the published coefficients of Roy et al. (2016, Table 2, ordinary least squares on surface reflectance), as in the release. Red becomes 0.0123 + 0.9372 times its value, and near infrared 0.0448 + 0.8339 times its value. Landsat 5 and 7 values are used as they are. The conversion is applied to the saved means, so it can be left out or replaced without a new extraction. The change of sensor falls in 2013, inside the decade that matters, so three checks guard against a step:
  - observations of two sensors at the same site within eight days of each other are compared directly, with and without the conversion;
  - the trends are repeated without the conversion, which Earth Engine's [guide to it](https://developers.google.com/earth-engine/tutorials/community/landsat-etm-to-oli-harmonization) calls unnecessary for the current Landsat collection;
  - the 2011–2020 trend is repeated with Landsat 7 alone, and set against MODIS, which is one product through the whole period. Landsat 7 has drifted to an earlier time of day since 2017 (Earth Engine catalog), which that check has to allow for.
- **Replication.** The release describes its indices as June to August means, and the file name of its site table says August. The table itself does not say which it holds.
  - MODIS values are extracted for the three windows this leaves open (June to August, July and August, August alone), as means and as medians, with and without the magnitude inversions, in a few years spread over the record.
  - Each version is compared with the release's values by correlation and mean absolute difference.
  - The closest version is then extracted for every year, and the step 1 greenness trend is recomputed from it.
- **Enough data.** The number of sites with a value in each year is reported before any greenness value is analysed.
  - For 2011–2020 a site needs 8 of the 10 years, as in step 1.
  - For longer periods a site needs 80% of the years.
  - The long record starts in the first year from which every year has a value at 70% of the sites or more.
- **Analysis.** Greenness is analysed like biomass in step 1: in logs, each site against its own average, with rain and summer temperature removed zone by zone. The results are the trend of the yearly mean with its 95% range, and the share of sites declining. For the long record, the standard version of the method is reported alongside: each site's greenness is regressed on its own rain, and a trend is fitted through the residuals (Evans & Geerken 2004).
- **Seeing the field decline.** As in step 1, the Landsat trend is set against the change expected if greenness had followed biomass, at its year-to-year rate and at its between-site rate. Both rates are estimated again for Landsat.
- **Standing in for the field.** The satellite record is read as a stand-in for field biomass before 2007 only in what it reproduces over 2007–2020: the ranking of good and bad years, and the 2011–2020 trend relative to the weather. What it fails to reproduce there is not inferred from it for earlier years.

### Order of work

Each stage saves its table to `data/processed/`, so later stages run without a connection. The Landsat extraction takes hours and runs as a script, not in a notebook.

1. Access to Earth Engine, and a test at one site.
2. The MODIS replication (question 1).
3. The Landsat extraction, with the counts of clear observations.
4. The sensor checks.
5. Trends and the comparison with biomass (questions 2 to 4).
6. Weather at each site's coordinates from ERA5-Land, as a check on the soum averages used so far.

## Known risks

- Single clippings are noisy, so declines may be detectable only for groups of sites.
- The main period is 10 years long and ends in 2020. Later years would need NAMEM's own records.
- Rain on the soum's summer range is not rain at the site. Within each zone it explains only 5 to 12% of a site's changes from year to year, so much noise remains for the trend tests.
- What rain leaves unexplained shares a pattern across the country. Averaged over all sites, it is above zero in 2011–2014 and below in most later years, lowest in 2017 and 2020. Most site trends are therefore negative (median −47% per decade). A run of good years followed by bad ones, from heat or other weather the rain data miss, would look the same as a lasting decline over 10 years. Separating the two is the main open question for steps 1 and 2.
- The causes of a decline, grazing or climate, are not part of the question. Claims about them stay modest.
