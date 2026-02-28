"""Interactive SQL REPL using prompt_toolkit"""
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
import sqlite3, os
from tabulate import tabulate

HELP = """DataForge SQL REPL helpers:
  .tables           - list tables
  .schema <table>   - show CREATE for table
  .save <file>      - save last query to file
  .exit             - exit
You can run any SQL and it will show a preview (default 10 rows).
"""

def start_repl(db_uri, preview_rows=10):

    if not db_uri.startswith('sqlite:'):
        print('only sqlite supported in this prototype (use uri like sqlite:acme.db)')
        return
    path = db_uri.split(':',1)[1]
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    session = PromptSession(history=InMemoryHistory())
    last_query = None
    print(f"Connected to {path}. Type .help for helpers.")
    while True:
        try:
            text = session.prompt('dataforge-sql> ')
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        if not text.strip():
            continue
        if text.strip() == '.help':
            print(HELP)
            continue
        if text.strip() == '.tables':
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            rows = cur.fetchall()
            for r in rows:
                print('-', r[0])
            continue
        if text.strip().startswith('.schema'):
            parts = text.strip().split()
            if len(parts) >= 2:
                tbl = parts[1]
                cur.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tbl,))
                r = cur.fetchone()
                print(r[0] if r else f"no schema for {tbl}")
            continue
        if text.strip().startswith('.save'):
            parts = text.strip().split(maxsplit=1)
            if len(parts) == 2 and last_query:
                with open(parts[1], 'w', encoding='utf8') as fh:
                    fh.write(last_query)
                print('[ok] saved last query')
            else:
                print('usage: .save filename (and run a query first)')
            continue
        if text.strip() in ('.exit', '.quit'):
            break
        # run SQL
        try:
            cur.execute(text)
            if text.strip().lower().startswith('select') or cur.description:
                rows = cur.fetchmany(preview_rows)
                headers = [d[0] for d in cur.description] if cur.description else []
                print(tabulate(rows, headers=headers, tablefmt='pretty'))
            else:
                conn.commit()
                print('[ok] executed')
            last_query = text
        except Exception as e:
            print('error:', e)
    conn.close()
    print('bye')
