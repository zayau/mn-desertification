# Findings

What the analysis has shown so far, step by step. The rules behind each result are in [design.md](design.md), and the checks of the data are in [data-checks.md](data-checks.md).

The notebooks in [../notebooks/](../notebooks/) reproduce every number here from the data. On 5 October 2026 they were checked against an earlier version of the analysis. The tables agree to rounding error, and the detection, permutation and robustness runs agree exactly.

## Field trends, 5 October 2026

NAMEM's August biomass at 1,250 sites with at least 8 of the 10 years 2011–2020, after the floor and the three flags. Two weather models were used.

- **Rain only,** as planned.
- **Rain and summer temperature,** added after the site trends showed a shared pattern. Both are reported.

### The weather effect

| | Rain only | Rain and summer temperature |
|---|---|---|
| Effect of rain (log10 biomass per log10 rain) | 1.07 to 1.25 | 0.70 to 1.04 |
| Effect of 1 °C warmer summer (log10) | — | −0.08 to −0.15, about 17 to 30% less biomass |
| Share of a site's year-to-year change explained | 5 to 12% | 8 to 15% |

Weather on the soum's summer grazing range explains little of what happens at a single site. Most of a site's year-to-year change remains, as measurement noise, local conditions and real change.

### A decline shared by the whole country

What the weather leaves unexplained, averaged over all sites, is above zero in 2011–2014 and below zero in most later years, lowest in 2017 and 2020. The national trend in it is −0.28 log10 per decade with rain only (about −48%) and −0.22 with temperature (about −40%).

- 22.7% of sites show a significant decline with rain only and 20.5% with temperature, where about 5% would by chance. 46 sites remain after controlling the false discovery rate (rain only).
- The order of the years is very unusual. When the same years are shuffled 1,000 times, the share of declining sites reaches the real value 3 times with rain only and never with temperature. With shuffled orders, 95% of results stay below 13% and 12%.

So the decline is not a chance ordering of ordinary good and bad years. Something systematic lowered biomass, relative to rain and summer temperature, across the country between 2011 and 2020.

Later analyses narrowed this. The robustness checks showed that the decline depends on starting in 2011. The comparison with satellite greenness showed that it lies in the three dry zones, and that with temperature in the model about half of it rests on the 2020 drought.

### What the method can detect

Declines of known size were added to shuffled data, 50 times, starting in 2012, 2014 or 2016 and reaching full size in 2020.

| Level | False alarms | 20% decline found | 40% decline found |
|---|---|---|---|
| Site | 5% | 8–9% | 15–17% |
| Soum, sites averaged | 5–6% | 9–11% | 20–22% |
| Zone, sites averaged | 6–7% | 22–23% | 49–51% |

No level finds a 20% decline 80% of the time, the rule set in the design. A decline the size seen between degraded and intact land elsewhere (10 to 20%, Wessels et al. 2012) cannot be told from noise at any level with these data. The shared national decline is detected because it is much larger.

### What this means

- **No map of degrading sites.** A map of site or soum trends from these data would mostly show noise. Individual sites should not be called degrading on this evidence.
- **The open question is the national decline.** It could be lasting productivity loss, weather the models miss (soil moisture, the severity of the 2020 Gobi drought, multi-year dry spells), or changes in how the clipping was done. Ten years of field data cannot separate these.
- **What can separate them:**
  - The satellite record of 1985–2025 (step 2), if it agrees with the field data where they overlap.
  - NAMEM's measurements after 2020, which would show whether the decline continued.
  - Weather at each site's coordinates instead of the soum average.

### First clues about the national decline, 5 October 2026

These were quick checks, both redone in the grazing analysis below.

- **Herds doubled over the same years.** The December census, summed over soums in the Purevjav et al. release, counts 35.9 million head in 2011 and 71.0 million in 2019 (67.1 million in 2020). Clipped August biomass is what still stands at the end of summer, so more animals eating would lower it even if the land produced as much as before. Whether NAMEM's plots are open to grazing is not yet known.
- **Satellite greenness at the same sites did not decline.** Redone properly in the grazing analysis below, which also asks whether greenness could have shown a decline of this size.

### Robustness, 5 October 2026

The weather model, the site trends and the tests were rerun with one analytical choice changed at a time, for both weather models. Results are in `data/processed/robustness.csv`, written by notebook 3.

**Rain only**

| Check | National trend (log10 per decade) | Same, % per decade | Sites declining | Shuffles reaching the observed share (of 1,000) | 20% decline found: site / soum / zone |
|---|---|---|---|---|---|
| Main analysis: 2011–2020, floor 0.1, flagged values out | −0.283 | −47.8 | 22.7% | 1 | 9 / 10 / 21% |
| Start in 2007 | +0.072 | +18.0 | 8.5% | 141 | 9 / 11 / 19% |
| Floor 0.05 c/ha | −0.292 | −48.9 | 23.0% | 1 | 9 / 10 / 21% |
| Floor 0.2 c/ha | −0.266 | −45.9 | 22.5% | 1 | 9 / 10 / 21% |
| Flagged values kept | −0.283 | −47.9 | 22.8% | 1 | 9 / 10 / 21% |
| Values above 30 c/ha removed | −0.281 | −47.7 | 22.8% | 1 | 9 / 10 / 21% |
| End in 2019, added later | −0.251 | −43.9 | 17.0% | 12 | 8 / 10 / 19% |

**Rain and summer temperature**

| Check | National trend (log10 per decade) | Same, % per decade | Sites declining | Shuffles reaching the observed share (of 1,000) | 20% decline found: site / soum / zone |
|---|---|---|---|---|---|
| Main analysis | −0.219 | −39.5 | 20.5% | 0 | 9 / 11 / 25% |
| Start in 2007 | +0.069 | +17.2 | 9.1% | 117 | 9 / 11 / 25% |
| Floor 0.05 c/ha | −0.228 | −40.9 | 20.8% | 0 | 9 / 11 / 25% |
| Floor 0.2 c/ha | −0.203 | −37.4 | 19.9% | 1 | 9 / 11 / 26% |
| Flagged values kept | −0.219 | −39.6 | 20.4% | 1 | 9 / 11 / 25% |
| Values above 30 c/ha removed | −0.218 | −39.5 | 20.3% | 1 | 9 / 11 / 26% |
| End in 2019, added later | −0.093 | −19.3 | 10.7% | 35 | 9 / 10 / 34% |

**How to read the tables**

- **National trend.** The least-squares slope, times ten, of the remainder averaged over all sites in each year. It is in log10 units: a value v means biomass relative to the weather changed by a factor of 10^v per decade, so −0.30 is a halving. The next column gives the same as 100 × (10^v − 1).
- **Sites declining.** The share of sites whose own remainder trend is negative with a one-sided p below 0.05, from an ordinary least-squares t-test. Sites need 8 of the 10 years 2011–2020 (1,250 sites), 7 of the 9 years 2011–2019 (1,250 sites) or 10 of the 14 years 2007–2020 (1,202 sites). With no trend, about 5% would pass.
- **Shuffles reaching the observed share.** The years were put in random order 1,000 times, with one order applied to all sites together, so years that were good or bad across the country stay together. The count is how many orders gave a share of declining sites at least as large as observed. Divided by 1,000 it is a one-sided permutation p-value: 1 means p ≈ 0.001 and 141 means p ≈ 0.14.
- **20% decline found.** A straight-line decline of 20% was added to data whose year order had been shuffled within each zone. The decline started in one of three years and reached full size in the last year. The column gives how often the test found it, averaged over 50 shuffles, for single sites, for soums (sites averaged) and for zones (sites averaged). With nothing added, the same procedure flags 5–7% of units in the detection test, so values close to that mean the decline goes unseen.
- **Shares and counts are not in logs.** Only the national trend is.
- The robustness checks use one random seed for every check, so their numbers differ slightly from the detection test's, for example 1 rather than 3 shuffles. Differences of that size are random variation.

**Results**

- **The data choices do not matter.** The floor (0.05 to 0.2 c/ha), the flagged values and values above 30 c/ha change the national trend by at most 0.017 log10 per decade. They change the share of declining sites by at most 0.6 percentage points, and the shuffle count stays at 0 or 1 of 1,000.
- **The start year does.** Adding 2007–2010:
  - reverses the sign of the national trend, to about +18% per decade;
  - lowers the share of declining sites to 8.5–9.1%;
  - makes that share ordinary under shuffling (117–141 of 1,000, p ≈ 0.12–0.14).

  The decline belongs to the 2011–2020 window. It reflects high values in 2011–2014 relative to the later years, not a steady decline over the whole record.
- **So does the end year, once temperature is in the model.** This check was added after the comparison with satellite greenness showed how far below the weather models 2020 fell in the dry zones. Leaving out 2020:
  - with temperature, more than halves the national trend, to −0.093 log10 per decade, and lowers the share of declining sites to 10.7%. 35 of 1,000 shuffles reach that share (p ≈ 0.035);
  - with rain only, changes the trend less, to −0.251, with 17.0% of sites declining and 12 of 1,000 shuffles reaching it.
- **Sensitivity is low whatever the choices.** A 20% decline is found 8–9% of the time at sites, 10–11% at soums and 19–34% at zones, against false alarms of 5–7%. The limit comes from year-to-year variation that the weather models do not explain, not from the data choices.

**Interpretation**

Two explanations for the dependence on the start year fit the evidence, and they can both be true. The dependence on 2020 is taken up in the grazing analysis below.

- **A change in method.** The 2007–2010 values were measured before the standard method began in 2011 and include placeholder values ([data-checks.md](data-checks.md), check 2). A series that crosses 2011 may mix two methods.
- **Grazing after a dzud.** The years 2011–2014 followed the 2009–2010 dzud. By the census sums in the release, the national herd fell from 43.5 to 32.3 million head between 2009 and 2010, then doubled to 71.0 million by 2019. Light and then heavy grazing would raise and then lower the biomass left standing in August with no change in what the land produces. Satellite greenness at the same sites shows no decline over 2011–2020.

The grazing analysis below tests the second. Whether the plots are fenced, and whether the method changed, would bear on both. The release does not say.

## Is it grazing? 5 October 2026

### Satellite greenness at the same sites

The release holds five MODIS vegetation indices for every site, 2000–2024, in `vegi_plot_modis_aug.dta` (August values, going by the file name). They come from MODIS reflectance at 500 m resolution, taken within 100 m of each plot (Purevjav et al. 2025, supplementary text pp. S2 and S4). Greenness here is NDVI, analysed like biomass: in logs, each site against its own average, with rain and summer temperature removed zone by zone.

**Greenness did not decline**

| Series | Trend (log10 per decade) | 95% range | Same, % per decade | Sites tested | Sites declining |
|---|---|---|---|---|---|
| Clipped biomass, 2011–2020 | −0.219 | −0.403 to −0.034 | −39.5 | 1,250 | 20.5% |
| Greenness, 2011–2020 | +0.001 | −0.050 to +0.052 | +0.3 | 1,487 | 5.0% |
| Greenness, 2000–2024 | +0.033 | +0.021 to +0.044 | +7.9 | 1,486 | 0.7% |

- The trend is the least-squares slope through the yearly means of all sites, and the 95% range comes from that fit. The share of declining sites uses the site test above, with sites needing 8 of the 10 years, or 20 of the 25.
- 5.0% of sites have declining greenness, as many as chance alone gives. The other four indices agree, with 2011–2020 trends of +0.007 to +0.014 (EVI, SAVI, MSAVI, NIRv).
- Over 2000–2024 greenness rose, and 2011–2020 lies above the 2000s.
- The two series agree on good and bad years. Their yearly means correlate at 0.53 and have the same sign in 8 of the 10 years. Greenness moves far less. The standard deviation of its yearly means is 0.019 log10, against 0.095 for biomass.

**Could greenness have shown a decline this large?**

That depends on how closely greenness follows biomass, and the data give two answers.

- **From year to year,** greenness changes by 0.10 log10 per log10 of biomass. At that rate the biomass decline would lower greenness by 0.023 per decade, which lies inside the observed range. Ten years of greenness could not have shown it.
- **Between sites,** greenness changes by 0.60 log10 per log10 of biomass. If a lasting loss moved greenness as the differences between sites do, greenness would have fallen by 0.131 per decade, far outside the observed range.
- **The relation between sites is curved.**
  - It is steep between 1 and 4 c/ha (slope 0.8).
  - Below 1 c/ha it is flat (0.2), where greenness is close to that of bare ground (mean NDVI 0.13).
  - Above 4 c/ha it is also flat (0.3), where greenness levels off.

**Where the decline is**

All values are in log10 per decade. The last two columns give the change in greenness expected if it followed biomass at that zone's year-to-year or between-site rate.

| Zone | Sites | Biomass trend | Greenness trend | Greenness 95% range | Expected, year to year | Expected, between sites |
|---|---|---|---|---|---|---|
| Desert | 112 | −0.412 | −0.014 | −0.056 to +0.029 | −0.029 | −0.011 |
| Semi-desert steppe | 323 | −0.434 | −0.008 | −0.052 to +0.036 | −0.023 | −0.165 |
| Steppe | 627 | −0.233 | −0.005 | −0.068 to +0.057 | −0.028 | −0.094 |
| Forest steppe | 374 | +0.011 | +0.024 | −0.040 to +0.088 | +0.002 | +0.002 |
| Mountain taiga | 49 | −0.024 | +0.006 | −0.020 to +0.032 | −0.002 | −0.002 |

- The biomass decline is in the three dry zones. Forest steppe and mountain taiga show none.
- In the steppe and the semi-desert steppe, a decline at the between-site rate falls outside the greenness range, so it would have shown. A decline at the year-to-year rate would not.
- In the desert, greenness barely differs between sites with more or less biomass, so it cannot test the decline there.

**How much rests on 2020**

The 2020 drought in the south ([data-checks.md](data-checks.md), check 3) left biomass far below what the weather models predict. The mean remainder in 2020 is −0.36 in the desert, −0.35 in the semi-desert steppe and −0.20 in the steppe, against −0.06 and −0.08 in the two northern zones. With the model refitted without 2020:

- **The national trend more than halves with temperature.** It goes from −0.219 to −0.093 per decade, with a 95% range of −0.309 to +0.123. No zone's range then excludes zero. The semi-desert steppe comes closest, at −0.217 (−0.464 to +0.031).
- **It changes less with rain only,** from −0.283 to −0.251.
- **The order of years stays unusual, but less so.** Shuffles reach the observed share of declining sites 12 times in 1,000 with rain only and 35 times with temperature, against 1 and 0 with 2020 included (robustness tables above).

**What it means**

- **No sign of a large loss of green cover.** Greenness around the plots did not fall over 2011–2020, in any zone or index. That rules out a large loss of green cover around the plots in the steppe and semi-desert steppe.
- **What remains possible.** Greenness cannot rule out a smaller loss, or a loss confined to the plots. Nor can it rule out a shift towards unpalatable plants, which can lower biomass while keeping greenness up. On six fence-line pairs in the Mongolian steppe, grazed sides had less than half the biomass of fenced ones (59 against 129 g/m²) but higher EVI (0.28 against 0.22). The unpalatable plants that had moved in reflect more near-infrared light, and the palatable grasses yellow by mid-summer (Karnieli et al. 2013). In the desert, greenness cannot test the decline at all.
- **The decline rests on both ends of the decade.** At the start, values were high in 2011–2012, after the 2009–2010 dzud. At the end, the 2020 drought hit the dry zones harder than the weather models predict. The start fits the grazing explanation. The end points to weather the models capture poorly.
- **Next.** The herd and pasture analyses below test the grazing part.

### Herds

**Data.** Herd size per soum comes from the December census in the release, in sheep units: horse 7, cattle 6, camel 5, sheep 1, goat 0.9 (Purevjav et al. 2025, supplement Table S3). The release's soum table, `wrk_soum.dta`, labels its census columns in two ways:

- **Head-count columns** (`cen_*`) carry the calendar year of the census.
- **Sheep-unit columns** (`su_cen_*`) hold the census of the December before each summer. They equal the previous year's head counts, weighted, to within 1e-7.

The second fits the release's year, which runs from September to August. Here "herd before summer t" is `su_cen_total` of year t. The national herd before each summer, in million sheep units:

| | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Million sheep units | 68.4 | 53.9 | 59.3 | 67.2 | 74.7 | 86.3 | 93.8 | 102.8 | 110.8 | 110.7 | 119.0 |

**Tests.** These were set before they were run. Each soum's sites are averaged.

- **Herd growth.** log10 of the herd before summer 2020 over the herd before summer 2011. The median soum grew 2.2-fold, and the middle half grew 1.8- to 2.7-fold.
- **Dzud loss.** log10 of the herd before summer 2010 over the herd before summer 2011, which is December 2009 against December 2010.
- **Responses.** For biomass and for greenness, each with rain and temperature removed:
  - the trend of the soum's yearly mean remainder;
  - the bump, the mean of 2011–2013 minus the mean of 2016–2020.
- **Model.** Each response is regressed on its driver, with one baseline per zone. Soums need 8 of the 10 years, and 7 soums with no herd recorded drop out.
- **Clustered errors.** The 95% ranges and p-values let soums in the same aimag move together (21 aimags), because neighbouring soums share weather and herders. Clustering was added after a first run with ordinary errors.
- **Without 2020.** Everything is repeated with the weather model refitted on 2011–2019, herd growth up to the herd before summer 2019, and the bump measured against 2016–2019.

| Period | Response | Driver | Soums | Slope | 95% range | p |
|---|---|---|---|---|---|---|
| 2011–2020 | Biomass trend | Herd growth | 317 | −0.654 | −1.048 to −0.260 | 0.001 |
| 2011–2020 | Biomass bump | Dzud loss | 317 | +0.251 | −0.162 to +0.664 | 0.23 |
| 2011–2020 | Greenness trend | Herd growth | 322 | −0.003 | −0.082 to +0.076 | 0.94 |
| 2011–2020 | Greenness bump | Dzud loss | 322 | −0.017 | −0.074 to +0.040 | 0.56 |
| 2011–2019 | Biomass trend | Herd growth | 317 | −0.372 | −0.720 to −0.025 | 0.036 |
| 2011–2019 | Biomass bump | Dzud loss | 317 | +0.132 | −0.276 to +0.540 | 0.53 |
| 2011–2019 | Greenness trend | Herd growth | 322 | +0.038 | −0.034 to +0.111 | 0.30 |
| 2011–2019 | Greenness bump | Dzud loss | 322 | −0.026 | −0.083 to +0.030 | 0.36 |

Trends are in log10 per decade per log10 of herd change. Bumps are in log10 per log10 of herd change.

**Results**

- **Where herds grew more, biomass fell more, within zones.** Compare a soum at the lower quartile of herd growth (1.8-fold) with one at the upper quartile (2.7-fold). Their biomass trends differ by about 0.115 log10 per decade, about 23%. Without 2020 the slope is a little over half as large, and its range still excludes zero.
- **The dzud test finds nothing clear.** Soums that lost more animals in the 2009–2010 dzud had a larger bump in 2011–2013, but the range includes zero. With ordinary errors the same test gives p = 0.024. That gap shows how much neighbouring soums move together.
- **Dzud loss and herd growth go together** (correlation 0.67), because soums that lost more animals rebuilt more. In an extra check with both drivers in one model (ordinary errors), the biomass trend follows herd growth (−0.651) and not dzud loss (−0.005).
- **Greenness follows neither.**
- **The gap opens late.** Split the soums into thirds by herd growth, and compare each soum with its zone's mean that year.
  - The fastest-growing third tracks the slowest until 2016.
  - In the 2017 drought it is far above (+0.114 against −0.090).
  - In 2018, 2019 and 2020 it falls below (−0.049, −0.065 and −0.075 against +0.031, +0.044 and +0.054). Herds before those summers were the largest of the decade.

**What it means**

- **The link fits grazing.** Herd growth and biomass decline go together across soums, as grazing would produce, and the link holds within zones and without 2020.
- **Other explanations fit too.** The link is a correlation across soums, not proof.
  - Herds may grow faster where pasture was good early on, and early highs pull a soum's trend down.
  - The fastest-growing soums lie mostly in the dry zones, where the 2020 drought fell hardest. Zone baselines remove only part of that, and the slope halves without 2020.
  - Herds are counted in the soum where they are registered, and they cross soum borders.
- **Greenness doesn't follow, again.** With the greenness comparison, the herd-linked decline shows in the clipped biomass but not in the greenness around the plots. That fits causes that act on clipped biomass more than on greenness: grazing around the plots, a shift towards unpalatable plants, or a change in clipping. It does not fit a broad loss of green cover.
- **Next.** The pasture analysis asks whether the decline is stronger on summer pastures, which are grazed before the August clipping.

### Seasonal pastures

**Data.** The release's seasonal pasture map comes from the land agency's 2021 State Land Report (Purevjav et al. 2025, supplement p. S3). Winter-spring ranges are used December to May, and summer-fall ranges June to November. The map file holds 16 areas:

- six winter-spring areas, plus winter camps and spring camps;
- six summer-fall areas;
- an inter-soum otor and soum reserve area;
- unused pasture.

Each area is drawn as many outlines, 251,865 in all, of which 184,876 are holes. A site is in an area when it lies inside an odd number of that area's outlines. This agrees with outline direction for every site: outer outlines run clockwise and holes counterclockwise.

- 755 sites are on winter-spring ranges, including 6 in the camp areas, and 498 on summer-fall ranges.
- 235 lie outside all 16 areas, probably on land the map treats as non-pasture. The supplement says that includes protected areas and uninhabitable desert.
- No site is in the reserve or unused areas, and none is in two areas.

The classification is in `data/processed/sites.csv`, column `pasture`, written by notebook 1.

**Tests.** These were set before they were run. They use site trends from the rain and temperature model, for sites with 8 of the 10 years. Each test has one baseline per zone and errors clustered by aimag, and leaves out sites outside the map. Everything is repeated without 2020.

| Period | Test | Sites | Estimate | 95% range | p |
|---|---|---|---|---|---|
| 2011–2020 | Trend, summer-fall minus winter-spring | 1,067 | −0.097 | −0.198 to +0.004 | 0.059 |
| 2011–2020 | Herd link on winter-spring sites | 1,065 | −0.770 | −1.182 to −0.358 | <0.001 |
| 2011–2020 | Herd link, summer-fall minus winter-spring | 1,065 | +0.263 | −0.299 to +0.826 | 0.36 |
| 2011–2019 | Trend, summer-fall minus winter-spring | 1,067 | −0.088 | −0.207 to +0.030 | 0.15 |
| 2011–2019 | Herd link on winter-spring sites | 1,065 | −0.471 | −0.849 to −0.092 | 0.015 |
| 2011–2019 | Herd link, summer-fall minus winter-spring | 1,065 | +0.376 | −0.141 to +0.893 | 0.15 |

Mean site trend by zone and pasture type, 2011–2020, in log10 per decade:

| Zone | Summer-fall | Winter-spring | Outside the map |
|---|---|---|---|
| Desert | −0.608 | −0.441 | −0.309 |
| Semi-desert steppe | −0.602 | −0.458 | −0.314 |
| Steppe | −0.309 | −0.203 | −0.132 |
| Forest steppe | −0.006 | +0.010 | +0.062 |
| Mountain taiga | −0.116 | +0.052 | −0.061 |

**Results**

- **Summer-fall sites declined most.** They declined more than winter-spring sites in every zone, by 0.097 log10 per decade on average (about 20%), and sites outside the map declined least in the dry zones.
  - Compared with their zone each year, summer-fall sites drift from +0.043 in 2011 to −0.042 in 2020, while winter-spring sites stay close to their zone.
  - The difference points the way grazing before the clipping predicts, but its range includes zero (p = 0.06, and 0.15 without 2020).
- **Winter-spring sites declined too,** by two-thirds to three-quarters as much as summer-fall sites in the dry zones.
- **The herd link is not stronger on summer-fall sites.** It is clear on winter-spring sites (−0.770). Summer-fall sites differ by +0.263, which if anything weakens the link there.
- **An exploratory check, not set in advance.** Sites outside the map declined less than winter-spring sites (+0.073, 95% range −0.010 to +0.156, p = 0.09).

**What it means**

- **The decline is not confined to land grazed in the summer before the clipping,** and the herd link is strongest on winter-spring ranges. Grazing in the months before the clipping is not the whole story.
- **Winter-spring ranges are not a clean control.**
  - They are grazed until the end of May, after growth has begun. The weather model already counts spring as part of the growing season.
  - Herders do not always keep to the map, least of all as herds grow.
  - Records of each site's seasonal use would show which ranges the plots are on in practice.
- **Lasting effects of grazing would fit.** A shift towards unpalatable plants, for example, would fit a decline and a herd link on winter-spring ranges. These data cannot show plant composition.

### In short

- **Where and when.** The decline in clipped biomass relative to weather over 2011–2020 lies in the three dry zones. With temperature in the model, about half of it rests on the 2020 drought.
- **Not seen by satellite.** Greenness around the plots shows neither the decline nor the herd link.
- **Linked to herds.** Within zones, soums where herds grew more lost more biomass, also without 2020. The link is strongest on winter-spring ranges, not on the summer-fall ranges grazed before the clipping.
- **Grazing is the leading suspect, but the mechanism is open.** The evidence does not single out animals eating the grass before the August clipping. Longer-lasting effects of more animals fit as well, and so do grazing outside the mapped seasons or factors that go with herd growth. A change in the clipping method is not ruled out.
- **What can decide.** NAMEM's plant groups, seasonal use and records after 2020 can tell these apart.

## The satellite check

### MODIS greenness, extracted again, 10 October 2026

The greenness comparison above used the release's table of MODIS values at the sites. Here the same greenness was extracted from the MODIS archive (MCD43A4, 500 m) through Google Earth Engine, under the rules that [design.md](design.md) sets for the satellite check. Notebook 5 has the code and the numbers.

**The extraction**

- **The rule.** A site's value for a year is the median of 1 July to 31 August in each pixel, averaged within 100 m of the plot.
- **It matches a value worked out by hand.** At site 63 in 2015, whose circle lies inside one pixel, the extraction returns the median of the daily series (NDVI 0.6255).
- **Most circles reach into a neighbouring pixel.** Earth Engine weighs the pixels by their share of the circle, which it measures in steps of about 1/256 of a pixel. At site 1 the plot's own pixel carries 61.5% of the weight, and the four pixels around the plot span 0.09 in NDVI.
- **There is no shortage of data.** Every site has a value in every year from 2000 to 2024, and the median site has 58 to 62 days behind it.

**Against the release's table**

The release describes its indices as June to August means, and the file name of its site table says August. Twelve versions were extracted in three test years (2002, 2012 and 2022): three windows, each as a mean and as a median, with all values and with full inversions only. The six versions with all values:

| Window | Summary | Correlation with the release | Mean absolute gap | Mean gap |
|---|---|---|---|---|
| June to August | mean | 0.973 | 0.038 | −0.030 |
| June to August | median | 0.973 | 0.033 | −0.022 |
| July and August | mean | 0.987 | 0.019 | −0.007 |
| July and August | median | 0.989 | 0.017 | −0.002 |
| August | mean | 0.990 | 0.017 | 0.000 |
| August | median | 0.989 | 0.018 | +0.003 |

The gap is this extraction minus the release, in NDVI.

- **The release's site table is a late-summer value,** close to an August mean. The June to August versions lie 0.02 to 0.03 below it.
- **It could not be reproduced exactly.** The closest versions differ from it by 0.017 NDVI on average. Keeping full inversions only changes the gap by less than 0.001. The cause of the remaining difference was not found.
- **Over all 25 years** the August mean correlates at 0.985 with the release's table (mean absolute gap 0.021), and the July and August median at 0.986 (0.019).

**The greenness trends again**

The greenness analysis above was repeated with each version: in logs, each site against its own average, with rain and summer temperature removed zone by zone.

| Version | Period | Trend, log10 per decade | 95% range | Sites tested | Sites declining |
|---|---|---|---|---|---|
| Release's table | 2011–2020 | +0.001 | −0.050 to +0.052 | 1,487 | 5.0% |
| Extracted, August mean | 2011–2020 | +0.021 | −0.041 to +0.084 | 1,488 | 2.3% |
| Extracted, July and August median | 2011–2020 | −0.007 | −0.057 to +0.043 | 1,488 | 5.0% |
| Release's table | 2000–2024 | +0.033 | +0.021 to +0.044 | 1,486 | 0.7% |
| Extracted, August mean | 2000–2024 | +0.037 | +0.025 to +0.050 | 1,488 | 0.3% |
| Extracted, July and August median | 2000–2024 | +0.033 | +0.020 to +0.045 | 1,488 | 0.5% |

- **The result holds.** In every version greenness is flat over 2011–2020, with a range that spans zero and no more sites declining than chance gives, and it rises over 2000–2024.
- **The yearly means agree in part.** Those of the extracted versions correlate at 0.83 and 0.84 with the release's over 2011–2020.
- **So the finding does not depend on how the release built its table.** MODIS greenness at 500 m around the plots did not decline while clipped biomass did.

### Landsat at the sites, 11 October 2026

Landsat reflectance was extracted at every site for every overpass from June to September, 1984 to 2024, from Landsat 5, 7, 8 and 9. The rules of [design.md](design.md) changed before this extraction: a site now gets one observation per overpass, the mean red and near-infrared reflectance of the clear pixels within 100 m, and the season is summarised afterwards. Notebook 6 has the counts below. No greenness value was looked at for them.

**What was extracted**

- **1.2 million rows,** each one site, one circle (100 m or the 50 m check) and one overpass. Landsat 5 and Landsat 7 each give about 4,000 overpasses, Landsat 8 about 2,300 and Landsat 9 about 600.
- **The saved rows equal a fresh request** for one site and month.
- **Landsat 7 stands apart.** At least half of the circle is clear in 81% of its observations, against 96 to 97% for the other sensors. Its scenes have striped gaps after May 2003.

**Enough data**

An observation counts when it falls between 1 July and 31 August and at least half of the 100 m circle is clear. A site has a value in a year when it has at least one such observation.

| Years | Sites with a value, of 1,488 |
|---|---|
| 1984, 1985 | 0 and 4 |
| 1986 to 1988 | 738 to 861 (50 to 58%) |
| 1989, 1990 | 1,152 and 1,243 (77% and 84%) |
| 1991 to 1999 | 1,286 to 1,467 (86 to 99%) |
| 2000 to 2024 | 1,411 to 1,488 (95 to 100%) |

- **The long record starts in 1989,** the first year from which every year has a value at 70% of the sites. That is eleven years before MODIS.
- **Every site has enough years.** All 1,488 sites have a value in at least 8 of the 10 years 2011–2020, and 1,391 in all ten. Field biomass had 1,250 such sites. All 1,488 also have at least 80% of the years from 1989 to 2024.
- **2012 is the thinnest year since 2000,** with 1,411 sites and a median of 2 observations per site. Landsat 7 was the only sensor that summer.
- **The sensors change inside the decade.** Landsat 5 ends in 2011, Landsat 7 runs through, and Landsat 8 starts in 2013. Landsat 7 alone gives 1,468 sites at least 8 of the 10 years.
- **The stricter checks cost little.** Requiring 90% of the circle to be clear leaves 54,179 of 54,450 site-years, and the 50 m circle leaves as many as the 100 m one.
