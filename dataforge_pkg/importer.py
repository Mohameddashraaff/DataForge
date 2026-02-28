"""Importer: map attached files into DB using YAML mapping"""
import os, yaml, sqlite3, csv, json
from . import store, utils
import pandas as pd

def run_import(dataset, map_path, db_path=None, strategy='merge', base_dir='datasets'):
    dd = os.path.join(base_dir, dataset)
    if not os.path.exists(dd):
        raise FileNotFoundError('dataset not found')
    reg = store._load_registry(dd)
    mapping = yaml.safe_load(open(map_path, 'r', encoding='utf8'))
    file_key = mapping.get('file')
    attachment = reg.get('attachments', {}).get(file_key)
    if not attachment:
        raise FileNotFoundError(f'attached file not found: {file_key}')
    file_rel = attachment['path']
    file_path = os.path.join(dd, file_rel)
    fmt = mapping.get('format') or os.path.splitext(file_path)[1].lstrip('.').lower()

    if fmt in ('csv','txt'):
        df = pd.read_csv(file_path)
    elif fmt in ('xlsx','xls'):
        df = pd.read_excel(file_path)
    elif fmt in ('json','ndjson'):

        try:
            df = pd.read_json(file_path, lines=True)
        except Exception:
            df = pd.read_json(file_path)
    else:
        raise ValueError('unsupported file format: ' + fmt)

    if db_path is None:

        db_path = os.path.join(dd, f"{dataset}.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    tgt_table = mapping['table']
    mappings = mapping.get('mappings', {})
    pk = mapping.get('pk')
    imported_count = 0

    cols = list(mappings.keys())
    col_defs = ', '.join(f'"{c}" TEXT' for c in cols)
    cur.execute(f'CREATE TABLE IF NOT EXISTS "{tgt_table}" ({col_defs});')
    conn.commit()

    for _, row in df.iterrows():
        out = {}
        for tgt_col, spec in mappings.items():
            if isinstance(spec, dict):
                src_col = spec.get('column')
                transforms = spec.get('transform')
            else:
                src_col = spec
                transforms = None
            raw = None
            if src_col in row:
                raw = row[src_col]

            val = raw
            if transforms:
                if isinstance(transforms, str):
                    transforms = [transforms]
                for t in transforms:
                    func = utils.TRANSFORMS.get(t)
                    if func:
                        val = func(val)
            out[tgt_col] = val

        cols_list = list(out.keys())
        placeholders = ','.join(['?'] * len(cols_list))
        vals = [out[c] for c in cols_list]
        if pk and strategy == 'overwrite':
            sql = f"INSERT INTO {tgt_table} ({','.join(cols_list)}) VALUES ({placeholders}) ON CONFLICT({pk}) DO UPDATE SET " + ",".join(f"{c}=excluded.{c}" for c in cols_list)
            cur.execute(sql, vals)
        elif pk and strategy == 'skip':
            sql = f"INSERT OR IGNORE INTO {tgt_table} ({','.join(cols_list)}) VALUES ({placeholders})"
            cur.execute(sql, vals)
        else:
            sql = f"INSERT INTO {tgt_table} ({','.join(cols_list)}) VALUES ({placeholders})"
            cur.execute(sql, vals)
        imported_count += 1
    conn.commit()
    conn.close()
    print(f"[ok] imported {imported_count} rows into {tgt_table} (db={db_path})")

    logs = os.path.join(dd, 'imports.log')
    with open(logs, 'a', encoding='utf8') as fh:
        fh.write(json.dumps({'map': os.path.abspath(map_path), 'file': os.path.abspath(file_path), 'rows': imported_count}) + "\n")

def rollback(dataset, last=1, base_dir='datasets'):
    dd = os.path.join(base_dir, dataset)
    logs = os.path.join(dd, 'imports.log')
    if not os.path.exists(logs):
        print('[warn] no import logs found')
        return
    with open(logs, 'r', encoding='utf8') as fh:
        lines = fh.readlines()
    if not lines:
        print('[warn] no imports found')
        return
    to_remove = lines[-last:]
    remaining = lines[:-last]
    open(logs, 'w', encoding='utf8').write(''.join(remaining))
    print(f"[ok] rolled back last {last} import log entries (note: this simple rollback only removes the log)")

