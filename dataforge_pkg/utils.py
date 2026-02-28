"""Utility transforms and helpers"""
from datetime import datetime
def t_strip(v): return v.strip() if isinstance(v, str) else v
def t_lower(v): return v.lower() if isinstance(v, str) else v
def t_upper(v): return v.upper() if isinstance(v, str) else v
def t_titlecase(v): return v.title() if isinstance(v, str) else v
def t_int(v):
    try:
        return int(v) if v not in (None, '') else None
    except:
        return None
def t_float(v):
    try:
        return float(v) if v not in (None, '') else None
    except:
        return None
def t_iso_date(v):
    if not v:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(v, fmt).isoformat()
        except:
            pass
    return v

TRANSFORMS = {
    'strip': t_strip,
    'lower': t_lower,
    'upper': t_upper,
    'titlecase': t_titlecase,
    'int': t_int,
    'float': t_float,
    'iso_date': t_iso_date,
}
