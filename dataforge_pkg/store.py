"""Dataset registry and attachment management"""
import os, yaml, shutil, hashlib, json

BASE = 'datasets'

def _ds_dir(name, base_dir=BASE):
    return os.path.join(base_dir, name)

def register_dataset(name, meta, base_dir=BASE):
    dd = _ds_dir(name, base_dir)
    os.makedirs(dd, exist_ok=True)
    meta_path = os.path.join(dd, 'meta.yml')
    with open(meta_path, 'w', encoding='utf8') as fh:
        yaml.safe_dump(meta, fh)

def attach_file(dataset, path, name, base_dir=BASE):
    dd = _ds_dir(dataset, base_dir)
    if not os.path.exists(dd):
        raise FileNotFoundError(f"dataset not found: {dd}")
    att_dir = os.path.join(dd, 'attachments')
    os.makedirs(att_dir, exist_ok=True)

    dest = os.path.join(att_dir, name + os.path.splitext(path)[1])
    shutil.copy2(path, dest)

    reg = _load_registry(dd)
    reg['attachments'][name] = {
        'path': os.path.relpath(dest, dd),
    }
    _save_registry(dd, reg)
    print(f"[ok] attached {path} as {name} into dataset {dataset}")

def list_files(base_dir=BASE):
    for name in os.listdir(base_dir):
        dd = os.path.join(base_dir, name)
        meta = _load_registry(dd)
        print(f"Dataset: {name}")
        for k,v in meta.get('attachments', {}).items():
            print('  ', k, '->', v.get('path'))

def _load_registry(dd):
    regp = os.path.join(dd, 'registry.yml')
    if not os.path.exists(regp):
        return {'attachments': {}}
    with open(regp, 'r', encoding='utf8') as fh:
        return yaml.safe_load(fh) or {'attachments': {}}

def _save_registry(dd, reg):
    regp = os.path.join(dd, 'registry.yml')
    with open(regp, 'w', encoding='utf8') as fh:
        yaml.safe_dump(reg, fh)
