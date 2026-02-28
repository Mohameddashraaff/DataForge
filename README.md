# DataForge CLI (local-first generator + importer + SQL REPL)

This is the local-first CLI tool that:
- Generates synthetic datasets from a schema (YAML).
- Attaches external files (CSV/JSON/Excel).
- Imports/mapping data from attached files into the dataset using YAML mapping configs.
- Creates a local SQLite DB populated from generated CSVs and imported data.
- Provides an interactive SQL REPL with preview, basic helpers, and query saving/export.

**Important Note:** This distribution contains the source code only. You must install Python dependencies to run it.

## Installation

``
git clone https://github.com/Mohameddashraaff/DataForge.git
``

``
cd DataForge
``

## Quick start

1. Create a Python virtualenv and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. See `examples/` for sample schema, mappings and sample CSVs.

3. Generate a dataset:
```bash
python dataforge.py gen --schema examples/schema_ecom.yml --name acme --rows 100
```

4. Create a SQLite DB from the generated dataset:
```bash
python dataforge.py db create --dataset acme --out acme.db
```

5. Attach an external CSV and import it (use provided sample mapping):
```bash
python dataforge.py attach-file --dataset acme --file examples/incoming/customers_partial.csv --name customers_csv
python dataforge.py import --dataset acme --map examples/maps/customers-map.yml --db acme.db --strategy merge
```

6. Start the interactive SQL REPL:
```bash
python dataforge.py sql --db sqlite:acme.db --preview 10
```

## Files
- `dataforge.py` — CLI entrypoint.
- `dataforge_pkg/` — core modules: generator, store, db_adapter, importer, sql_repl, utils.
- `examples/` — sample schema, mappings, CSVs.
