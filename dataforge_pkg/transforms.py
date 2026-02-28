"""Example custom transforms module.
You can add custom functions here and reference them in mapping YAML as:
transform:
  - custom: dataforge_pkg.transforms::normalize_phone
"""
def normalize_phone(v):
    if not v:
        return v
    s = ''.join(c for c in str(v) if c.isdigit())
    if len(s) == 10:
        return f"+1-{s[0:3]}-{s[3:6]}-{s[6:]}"
    return s
