#!/usr/bin/env python3
"""Search the OpenAlex scholarly index and keep a log of every search.

Usage:
  python3 scripts/openalex.py search '<query>' [--n 25] [--from-year 1990] [--sort relevance|cited|recent]
  python3 scripts/openalex.py doi [--brief] <doi> [<doi> ...]
  python3 scripts/openalex.py show <doi-or-title-fragment> [...]

`search` matches the query against titles and abstracts. It supports AND, OR,
NOT and quoted phrases. Each run appends one row to sources/search-log.tsv and
stores the records, with abstracts, in sources/search/pool.jsonl.
`doi` fetches single works by DOI and stores them in the same pool.
`show` prints stored records, including the abstract, without a new request.
"""

import argparse
import datetime
import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
POOL = ROOT / "sources" / "search" / "pool.jsonl"
LOG = ROOT / "sources" / "search-log.tsv"
API = "https://api.openalex.org/works"
FIELDS = ",".join(
    [
        "id",
        "doi",
        "title",
        "publication_year",
        "publication_date",
        "type",
        "cited_by_count",
        "authorships",
        "primary_location",
        "open_access",
        "biblio",
        "abstract_inverted_index",
    ]
)


def get(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=40) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise
    return None


def abstract_text(inverted_index):
    if not inverted_index:
        return ""
    positions = []
    for word, places in inverted_index.items():
        positions.extend((place, word) for place in places)
    return " ".join(word for _, word in sorted(positions))


def simplify(work):
    location = work.get("primary_location") or {}
    source = location.get("source") or {}
    biblio = work.get("biblio") or {}
    access = work.get("open_access") or {}
    return {
        "id": (work.get("id") or "").rsplit("/", 1)[-1],
        "doi": (work.get("doi") or "").replace("https://doi.org/", ""),
        "title": work.get("title") or "",
        "year": work.get("publication_year"),
        "date": work.get("publication_date"),
        "type": work.get("type"),
        "cited_by": work.get("cited_by_count"),
        "authors": [
            (authorship.get("author") or {}).get("display_name") or ""
            for authorship in work.get("authorships") or []
        ],
        "venue": source.get("display_name") or "",
        "volume": biblio.get("volume"),
        "issue": biblio.get("issue"),
        "first_page": biblio.get("first_page"),
        "last_page": biblio.get("last_page"),
        "is_oa": access.get("is_oa"),
        "oa_url": access.get("oa_url"),
        "abstract": abstract_text(work.get("abstract_inverted_index")),
    }


def load_pool():
    records = {}
    if POOL.exists():
        for line in POOL.read_text().splitlines():
            if line.strip():
                record = json.loads(line)
                records[record["id"]] = record
    return records


def save_pool(records):
    POOL.parent.mkdir(parents=True, exist_ok=True)
    with POOL.open("w") as handle:
        for record in records.values():
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def short_author(record):
    authors = record["authors"]
    if not authors:
        return "?"
    family = authors[0].split()[-1]
    return family if len(authors) == 1 else f"{family}+{len(authors) - 1}"


def line(record):
    access = "OA" if record["is_oa"] else "--"
    return (
        f"{record['year']} c{record['cited_by']:<5} {access} {short_author(record)}: "
        f"{record['title'][:150]} [{record['venue'][:40]}] {record['doi']}"
    )


def search(args):
    filters = [f"title_and_abstract.search:{args.query}"]
    if args.from_year:
        filters.append(f"from_publication_date:{args.from_year}-01-01")
    params = {
        "filter": ",".join(filters),
        "per-page": str(min(args.n, 200)),
        "select": FIELDS,
    }
    if args.sort == "cited":
        params["sort"] = "cited_by_count:desc"
    elif args.sort == "recent":
        params["sort"] = "publication_date:desc"
    data = get(API + "?" + urllib.parse.urlencode(params))
    total = data["meta"]["count"]
    records = [simplify(work) for work in data["results"]]

    pool = load_pool()
    new = 0
    for record in records:
        if record["id"] not in pool:
            new += 1
        record["queries"] = sorted(
            set(pool.get(record["id"], {}).get("queries", []) + [args.query])
        )
        pool[record["id"]] = record
    save_pool(pool)

    if not LOG.exists():
        LOG.write_text("date\tquery\tfrom_year\tsort\ttotal_hits\tretrieved\tnew_to_pool\n")
    with LOG.open("a") as handle:
        handle.write(
            f"{datetime.date.today().isoformat()}\t{args.query}\t{args.from_year or ''}\t"
            f"{args.sort}\t{total}\t{len(records)}\t{new}\n"
        )

    print(f"# {args.query}  (hits {total}, shown {len(records)}, new {new})")
    for record in records:
        print(line(record))


def doi(args):
    pool = load_pool()
    for value in args.dois:
        value = value.replace("https://doi.org/", "")
        try:
            work = get(f"{API}/doi:{urllib.parse.quote(value, safe='/')}?select={FIELDS}")
        except urllib.error.HTTPError as error:
            print(f"NOT FOUND {value} ({error.code})")
            continue
        record = simplify(work)
        record["queries"] = pool.get(record["id"], {}).get("queries", [])
        pool[record["id"]] = record
        if args.brief:
            print(line(record))
        else:
            print_full(record)
    save_pool(pool)


def print_full(record):
    pages = "-".join(str(page) for page in (record["first_page"], record["last_page"]) if page)
    print(f"## {record['title']}")
    print(f"{'; '.join(record['authors'][:12])}{' et al.' if len(record['authors']) > 12 else ''}")
    print(
        f"{record['venue']} {record['year']} vol {record['volume']} issue {record['issue']} "
        f"pp {pages} | doi {record['doi']} | cited {record['cited_by']} | "
        f"OA {record['is_oa']} {record['oa_url'] or ''}"
    )
    print(record["abstract"] or "(no abstract in OpenAlex)")
    print()


def show(args):
    pool = load_pool()
    for fragment in args.fragments:
        needle = fragment.lower()
        matches = [
            record
            for record in pool.values()
            if needle in record["doi"].lower() or needle in record["title"].lower()
        ]
        if not matches:
            print(f"NOT IN POOL {fragment}\n")
        for record in matches[:3]:
            print_full(record)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    search_parser = commands.add_parser("search")
    search_parser.add_argument("query")
    search_parser.add_argument("--n", type=int, default=25)
    search_parser.add_argument("--from-year", type=int)
    search_parser.add_argument("--sort", choices=["relevance", "cited", "recent"], default="relevance")
    search_parser.set_defaults(run=search)

    doi_parser = commands.add_parser("doi")
    doi_parser.add_argument("dois", nargs="+")
    doi_parser.add_argument("--brief", action="store_true")
    doi_parser.set_defaults(run=doi)

    show_parser = commands.add_parser("show")
    show_parser.add_argument("fragments", nargs="+")
    show_parser.set_defaults(run=show)

    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    sys.exit(main())
