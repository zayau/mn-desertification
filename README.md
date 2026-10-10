# Mongolia desertification

A study of desertification in Mongolia's rangelands, measured as a loss of productivity beyond what the weather explains. It asks where the land lost productivity, whether satellites can see it, and whether it could have been predicted. The output will be a journal paper and a version for the web.

## Phases

| Phase | Work |
|---|---|
| 1. Frame | Definitions, questions, scope ([docs/scope.md](docs/scope.md)) |
| 2. Evidence base | Literature, official sources, datasets ([sources/](sources/)) |
| 3. Design | One question, study area, data, methods, validation ([docs/design.md](docs/design.md)) |
| 4. Analysis | Describe, explain, forecast |
| 5. Write-up | Draft, expert review, publication with code and data |

Evaluating solutions is outside this study. See the scope.

## Findings so far

These results are for NAMEM's August biomass at its monitoring sites over 2011–2020, after taking out what rain and summer temperature explain.

- **Biomass fell across many sites.** Nationally the decline is about 40% per decade with temperature in the weather model. It is concentrated in the desert, semi-desert steppe and steppe zones. Shuffled orders of the same years almost never produce it.
- **The decline rests on both ends of the decade.** At the start, values were high after the 2009–2010 dzud. At the end, the 2020 drought hit harder than the weather model predicts. Starting in 2007 reverses the decline. With temperature in the model, leaving out 2020 more than halves it.
- **The method cannot detect a 20% decline** at a single site, soum or zone, so the study draws no map of degrading sites.
- **Satellite greenness around the plots does not decline.** This holds when the greenness is extracted again from the MODIS archive.
- **Soums where herds grew more lost more biomass,** also without 2020. Grazing is the leading suspect, but the mechanism is open.

[docs/findings.md](docs/findings.md) gives the numbers, with their tests and caveats.

## Reproducing the analysis

The analysis runs on Python 3.10 or later. From the repository root:

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install -e ".[notebooks,dev]"
```

This installs the `mn_desertification` package in editable mode, with the notebook and test tools. Then download the data as [data/README.md](data/README.md) describes, and run the notebooks in order. Each one starts with what it reads and writes.

Notebook 5 extracts satellite data through Google Earth Engine. It needs the `satellite` extra, a Google Cloud project [registered for Earth Engine](https://developers.google.com/earth-engine/guides/access), and a sign-in on the computer:

```bash
.venv/bin/pip install -e ".[notebooks,dev,satellite]"
```

```bash
.venv/bin/earthengine authenticate
```

```bash
.venv/bin/earthengine set_project YOUR_PROJECT_ID
```

| Notebook | Content |
|---|---|
| [01-data](notebooks/01-data.ipynb) | Loads and checks the biomass, places each site in its soum and seasonal pasture, adds the weather, and flags likely recording errors |
| [02-weather-and-trends](notebooks/02-weather-and-trends.ipynb) | Takes out what the weather explains, then fits trends at every site and for the country |
| [03-detection-and-robustness](notebooks/03-detection-and-robustness.ipynb) | Tests what the method can detect, whether the order of years is unusual, and whether the results depend on the choices made |
| [04-grazing](notebooks/04-grazing.ipynb) | Compares satellite greenness, herds and seasonal pastures with the decline |
| [05-modis-replication](notebooks/05-modis-replication.ipynb) | Extracts MODIS greenness at the sites through Earth Engine, tests the extraction, compares it with the release's table and repeats the greenness trends |

Once the data are in place, the first four notebooks run in about a minute. Notebook 5 takes about 15 minutes on its first run and seconds after that, because it saves what it extracts. The unit tests need no data and no connection:

```bash
.venv/bin/pytest
```

## Where things are

| File | Content |
|---|---|
| [docs/scope.md](docs/scope.md) | Aim, definitions, questions, what is in and out of scope |
| [docs/design.md](docs/design.md) | The research question, data, steps and the rules set before the results |
| [docs/data-checks.md](docs/data-checks.md) | What the data hold and what the first checks showed |
| [docs/findings.md](docs/findings.md) | What the analysis has shown so far |
| [notebooks/](notebooks/) | The analysis, in numbered notebooks run in order |
| [src/mn_desertification/](src/mn_desertification/) | The analysis package: data readers, the rules, the weather model, the trend, detection and grazing tests, and the satellite extraction |
| [tests/](tests/) | Unit tests for the package, on small synthetic data |
| [sources/](sources/) | The evidence base: the evidence table, the bibliography, the data inventory and the search log |
| [scripts/](scripts/) | The literature search tool, and a first look at the biomass data |
| `data/` | The downloaded data and the tables the notebooks write. Git keeps only [data/README.md](data/README.md), which says how to get the data |
| [pyproject.toml](pyproject.toml) | Package metadata and dependencies |

## Data

The biomass comes from NAMEM's rangeland monitoring network, published with Purevjav et al. (2025) on Dryad under CC0, together with soum weather, livestock and map data. [data/README.md](data/README.md) explains how to download it and where to put it. Nothing under `data/` is kept in git.

## License

The code, including the code in the notebooks, is under the MIT License ([LICENSE](LICENSE)). The text and figures, in `docs/`, `sources/` and the notebooks' text and outputs, are under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The data are not part of this repository; their release is under CC0.
