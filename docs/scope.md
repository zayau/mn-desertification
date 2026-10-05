# Scope

Phase 1 output. Draft of 3 October 2026, open to revision until the research design is fixed in phase 3.

## Aim

Forecast land degradation in Mongolia from satellite and climate records, and measure how much skill such a forecast has.

On 4 October 2026 this was narrowed to one question: where Mongolia's rangelands lost productivity between 2007 and 2020 beyond what rainfall explains, and whether it could have been predicted. See [design.md](design.md).

The study describes the change, explains it as far as the data allow, and then forecasts it. Evaluating and recommending solutions is outside this paper. The literature on actions is still collected, because the introduction and discussion of the paper need it and because it may become a second study.

The output is a paper submitted to a journal, with a version published on the project website.

## Definitions

| Term | Meaning used here | Source |
|---|---|---|
| Desertification | Land degradation in arid, semi-arid and dry sub-humid areas that results from various factors, including climatic variations and human activities | UNCCD, Article 1 |
| Drylands under the convention | Areas, other than polar and sub-polar regions, where the ratio of annual precipitation to potential evapotranspiration is between 0.05 and 0.65 | UNCCD, Article 1 |
| Land degradation | Reduction or loss of the biological or economic productivity and complexity of cropland, range, pasture, forest and woodland | UNCCD, as used for SDG indicator 15.3.1 |
| SDG indicator 15.3.1 | Proportion of land that is degraded over total land area. It combines three sub-indicators (land cover, land productivity, carbon stocks). Land counts as degraded if any one of them declines | SDG indicator metadata (UNCCD is the custodian agency) |
| Land degradation neutrality | No net loss of land-based natural capital against a baseline | Cowie et al. 2018 |
| State change and regime shift | A state change is a change in vegetation or soil that can reverse. A regime shift is a state change that persists | Bestelmeyer et al. 2015 |
| Dzud | Cold-season disaster with mass livestock mortality | Rao et al. 2015 |

Three distinctions matter for everything that follows.

- **Drought and degradation.** A drought lowers vegetation for a season or a few years. Degradation is a loss that persists after rainfall returns. A short satellite record cannot tell them apart.
- **Greenness and rangeland condition.** A vegetation index measures green cover. Rangeland condition also depends on which species grow there. Karnieli et al. (2013) found grazed plots that were greener than fenced ones because unpalatable plants had moved in.
- **Affected and severely degraded.** The national figure of land "affected by desertification" counts slight degradation. Field assessments put very severe degradation at a small share of the country (Jamsranjav et al. 2018).

Mongolian terms for searching local sources: цөлжилт (desertification), газрын доройтол (land degradation), бэлчээрийн доройтол (rangeland degradation), бэлчээрийн төлөв байдал (rangeland health), зуд (dzud).

## Questions for the evidence base

| Theme | Question |
|---|---|
| Trajectory | How much land is degraded, where, since when, and by which measure? |
| Causes | How much of the change comes from climate and how much from land use, and does the answer differ by ecological zone? |
| Effects | What does degradation change for water, dust, livestock and people? |
| Actions | What has been tried in Mongolia, and what is known about the results? |
| Measurement | Which indicators and datasets are valid where vegetation is sparse? |
| Forecasting | What has already been forecast, with which methods, and how was it validated? |
| Comparable drylands | What do longer-running programmes elsewhere show, especially in Inner Mongolia? |

The sources are in [../sources/evidence.csv](../sources/evidence.csv).

## In and out of scope

| In scope | Out of scope |
|---|---|
| Mongolia, with Inner Mongolia as a comparison where studies cover the whole plateau | Other drylands, except as method references |
| Rangeland, which is most of the country | Forest loss, cropland and urban land as separate topics |
| Satellite era, from the 1980s to the present | Paleoclimate, except as context for the length of the record |
| Describing, explaining and forecasting change | Evaluating or recommending interventions |
| Open data and open code | Data that cannot be shared or cited |

## Decisions for phase 3

These are set in the research design, after the core papers are read. The first answers are in [design.md](design.md): the target is productivity relative to rainfall, measured as August biomass at NAMEM's sites, and the horizon is a few years.

1. **Target.** What the model forecasts. Options include fractional vegetation cover, productivity relative to rainfall, a degradation class, or a field-based recovery class.
2. **Horizon.** One season, a few years, or decades under climate scenarios. Only the first two can be tested against observations.
3. **Area.** The whole country at coarse resolution, selected regions at fine resolution, or both.
4. **Ground truth.** Which field data are available to check the satellite target.
5. **Baselines.** The simple methods a vision model has to beat.
