"""Generator module - generates CSVs per schema using Faker"""
import os, yaml, random, csv
from faker import Faker
from . import store, utils

def generate_dataset(schema_path, name, rows_override=None, outdir='datasets'):
    schema = yaml.safe_load(open(schema_path, 'r', encoding='utf8'))
    seed = schema.get('seed', None)
    fake = Faker()
    if seed:
        Faker.seed(seed)
        random.seed(seed)
    ds_dir = os.path.join(outdir, name)
    os.makedirs(ds_dir, exist_ok=True)
    tables = schema.get('tables', {})
    generated = {}
    for tname, tconf in tables.items():
        rows = rows_override or tconf.get('rows', 100)
        cols = tconf.get('columns', {})
        csv_path = os.path.join(ds_dir, f"{tname}.csv")
        with open(csv_path, 'w', newline='', encoding='utf8') as fh:
            writer = None
            for i in range(rows):
                out = {}
                for cname, cconf in cols.items():
                    ctype = cconf.get('type', 'string')
                    faker_call = cconf.get('faker')
                    val = None
                    if faker_call:
                    # basic faker provider
                        try:
                            if faker_call == 'random_int':
                                val = fake.random_int(min=1, max=100000)
                            elif faker_call == 'email':
                                val = fake.unique.email()
                            elif faker_call == 'name':
                                val = fake.name()
                            elif faker_call == 'date_between':
                                val = fake.date_between(start_date='-2y', end_date='today').isoformat()
                            elif faker_call == 'bothify':
                                val = fake.bothify(text='????-###')
                            elif faker_call == 'word':
                                val = fake.word()
                            elif faker_call == 'pyfloat':
                                val = round(random.uniform(1, 500), 2)
                            elif faker_call == 'random_element':

                                val = None
                            else:

                                provider = getattr(fake, faker_call, None)
                                if provider:
                                    val = provider()
                                else:
                                    val = ''
                        except Exception:
                            val = ''
                    else:
                        
                        if ctype == 'integer':
                            val = i+1
                        elif ctype == 'datetime':
                            val = fake.date_time_between(start_date='-2y', end_date='now').isoformat()
                        else:
                            val = fake.word()
                    out[cname] = val
                if writer is None:
                    writer = csv.DictWriter(fh, fieldnames=list(out.keys()))
                    writer.writeheader()
                writer.writerow(out)
        generated[tname] = csv_path

    for tname, tconf in tables.items():
        cols = tconf.get('columns', {})
        for cname, cconf in cols.items():
            if cconf.get('faker') == 'random_element':

                from_table = cconf.get('from')
                choices = []
                if from_table:
                    fpath = os.path.join(ds_dir, f"{from_table}.csv")
                    if os.path.exists(fpath):
                        import csv as _csv
                        with open(fpath, newline='', encoding='utf8') as fh:
                            rdr = _csv.DictReader(fh)
                            for r in rdr:

                                if 'id' in r and r['id'] != '':
                                    choices.append(r['id'])

                if not choices:
                    choices = list(range(1, 11))

                import csv as _csv, tempfile
                path = generated[tname]
                tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, newline='', encoding='utf8')
                with open(path, newline='', encoding='utf8') as inf:
                    rdr = _csv.DictReader(inf)
                    writer = _csv.DictWriter(tmp, fieldnames=rdr.fieldnames)
                    writer.writeheader()
                    import random as _random
                    for r in rdr:
                        if not r.get(cname):
                            r[cname] = _random.choice(choices)
                        writer.writerow(r)
                tmp.close()
                os.replace(tmp.name, path)
    # register dataset
    meta = {
        'name': name,
        'schema': os.path.abspath(schema_path),
        'generated': generated
    }
    store.register_dataset(name, meta, base_dir=outdir)
    print(f"[ok] dataset '{name}' generated at {ds_dir}")
