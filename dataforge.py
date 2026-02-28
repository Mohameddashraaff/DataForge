#!/usr/bin/env python3
"""DataForge CLI - entrypoint
Run `python dataforge.py --help` for commands.
"""
import argparse, sys, os
from dataforge_pkg import generator, store, db_adapter, importer, sql_repl

def main():
    ap = argparse.ArgumentParser(prog='dataforge')
    sub = ap.add_subparsers(dest='cmd')

    # gen
    g = sub.add_parser('gen', help='generate dataset from schema')
    g.add_argument('--schema', required=True)
    g.add_argument('--name', required=True)
    g.add_argument('--rows', type=int, default=None, help='default rows override')
    g.add_argument('--outdir', default='datasets')

    # db create
    d = sub.add_parser('db')
    dsub = d.add_subparsers(dest='dbcmd')
    create = dsub.add_parser('create', help='create DB from dataset')
    create.add_argument('--dataset', required=True)
    create.add_argument('--out', required=True)
    create.add_argument('--type', choices=['sqlite'], default='sqlite')

    # attach-file
    a = sub.add_parser('attach-file', help='attach external file to dataset')
    a.add_argument('--dataset', required=True)
    a.add_argument('--file', required=True)
    a.add_argument('--name', required=True)

    files = sub.add_parser('files', help='manage files')
    files.add_argument('action', choices=['list'], nargs='?')

    # import
    imp = sub.add_parser('import', help='import attached file using mapping')
    imp.add_argument('--dataset', required=True)
    imp.add_argument('--map', required=True)
    imp.add_argument('--db', required=False, help='target DB (sqlite:xxx.db) optional')
    imp.add_argument('--strategy', choices=['append','overwrite','skip','merge'], default='merge')

    imp_rb = sub.add_parser('import-rollback', help='rollback last import (simple)')
    imp_rb.add_argument('--dataset', required=True)
    imp_rb.add_argument('--last', type=int, default=1)

    # sql
    sql = sub.add_parser('sql', help='start interactive SQL REPL')
    sql.add_argument('--db', required=True, help='sqlite:path or sqlite::memory:')
    sql.add_argument('--preview', type=int, default=10)

    args = ap.parse_args()

    if args.cmd == 'gen':
        generator.generate_dataset(args.schema, args.name, rows_override=args.rows, outdir=args.outdir)
    elif args.cmd == 'db' and args.dbcmd == 'create':
        db_adapter.create_sqlite_db_from_dataset(args.dataset, args.out)
    elif args.cmd == 'attach-file':
        store.attach_file(args.dataset, args.file, args.name)
    elif args.cmd == 'files':
        if args.action == 'list':
            store.list_files()
    elif args.cmd == 'import':
        importer.run_import(dataset=args.dataset, map_path=args.map, db_path=args.db, strategy=args.strategy)
    elif args.cmd == 'import-rollback':
        importer.rollback(dataset=args.dataset, last=args.last)
    elif args.cmd == 'sql':
        sql_repl.start_repl(args.db, preview_rows=args.preview)
    else:
        ap.print_help()

if __name__ == '__main__':
    main()