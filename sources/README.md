# Sources

The evidence base behind the study.

| File | Content |
|---|---|
| [evidence.csv](evidence.csv) | One row per source, 165 in all, with region, period, data and method, finding and a note |
| [references.bib](references.bib) | BibTeX for every source, with fields taken from Crossref and DataCite |
| [datasets.md](datasets.md) | Data that could serve the study, with access, coverage and notes |
| [search-log.tsv](search-log.tsv) | Every OpenAlex query, with its date, year filter, sort order and hit counts |

## How the sources were found

This is a scoping search, not a systematic review.

- **Papers** came from OpenAlex queries, run with [../scripts/openalex.py](../scripts/openalex.py) and logged in [search-log.tsv](search-log.tsv). Others were added by DOI, from reference lists and from earlier knowledge of the field.
- **Official material** came from web searches.
- **Bibliographic fields** come from Crossref and DataCite. Abstracts that OpenAlex does not hold came from Semantic Scholar, Europe PMC and publisher pages.
- **Choice.** Sources were chosen by judgment from the top results of each query, with no second screener. A source was kept if it was one of these:
  - a study of Mongolia or the Mongolian Plateau on one of the themes in [../docs/scope.md](../docs/scope.md);
  - a review;
  - a paper that represents a distinct position in a dispute;
  - a method paper that later studies rely on;
  - an evaluation of restoration programmes in northern China;
  - a forecasting or projection study.

**Known limits.**

- OpenAlex matches only the title when it holds no abstract, so papers from some publishers are missed.
- Sorting by citations favours older papers.
- The word "mongolia" also matches Inner Mongolia.
- Results change as the index grows.
- Mongolian-language and Russian-language literature is largely absent.

## Reading the evidence table

| Column | Meaning |
|---|---|
| `theme` | framing, ecology, drivers, trajectory, climate, effects, actions, comparable, measurement, forecasting, validation |
| `finding` | What the source reports, in our words |
| `note` | Our comment, such as a caveat or where an open copy is |
| `access` | open or paywalled, as listed by OpenAlex |
| `checked` | How much of the source was read. `abstract`, `full text`, `excerpt`, or `metadata` when only the title and bibliographic record were seen |
| `core` | `yes` for the eighteen sources to read first |

A finding marked `abstract` reflects the abstract only. Read the paper before citing a number from it.

## Searching for more literature

```bash
python3 scripts/openalex.py search 'mongolia AND dzud' --n 30 --sort cited
```

The query matches titles and abstracts and accepts AND, OR, NOT and quoted phrases. Each run adds a line to the search log and stores the records with abstracts under `sources/search/`, which git ignores.

```bash
python3 scripts/openalex.py show 10.1111/gcb.12365
```

This prints a stored record with its abstract.
