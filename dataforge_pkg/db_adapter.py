"""DB adapter: create sqlite DB from dataset CSVs"""
import os, sqlite3, csv
from . import store

def create_sqlite_db_from_dataset(dataset, out_path, base_dir='datasets'):
    dd = os.path.join(base_dir, dataset)
    if not os.path.exists(dd):
        raise FileNotFoundError(f"dataset not found: {dd}")

    import glob
    csv_files = glob.glob(os.path.join(dd, '*.csv'))
    if not csv_files:
        raise FileNotFoundError('no csv files found in dataset folder')
    conn = sqlite3.connect(out_path)
    cur = conn.cursor()
    for cf in csv_files:
        table = os.path.splitext(os.path.basename(cf))[0]
        with open(cf, newline='', encoding='utf8') as fh:
            rdr = csv.DictReader(fh)
            cols = rdr.fieldnames
        # creating table
            col_defs = ', '.join(f'"{c}" TEXT' for c in cols)
            cur.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs});')
            # insert rows
            rows = []
            for r in rdr:
                rows.append([r.get(c) for c in cols])
            if rows:
                placeholders = ','.join(['?'] * len(cols))
                cur.executemany(f'INSERT INTO "{table}" ({",".join(cols)}) VALUES ({placeholders})', rows)
    conn.commit()
    conn.close()
    print(f"[ok] sqlite DB created at {out_path}")
