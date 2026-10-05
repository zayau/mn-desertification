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

## Known risks

- Single clippings are noisy, so declines may be detectable only for groups of sites.
- The main period is 10 years long and ends in 2020. Later years would need NAMEM's own records.
- Rain on the soum's summer range is not rain at the site. Within each zone it explains only 5 to 12% of a site's changes from year to year, so much noise remains for the trend tests.
- What rain leaves unexplained shares a pattern across the country. Averaged over all sites, it is above zero in 2011–2014 and below in most later years, lowest in 2017 and 2020. Most site trends are therefore negative (median −47% per decade). A run of good years followed by bad ones, from heat or other weather the rain data miss, would look the same as a lasting decline over 10 years. Separating the two is the main open question for steps 1 and 2.
- The causes of a decline, grazing or climate, are not part of the question. Claims about them stay modest.
