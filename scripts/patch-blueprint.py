#!/usr/bin/env python3
"""Patch the upstream nextcloud-client blueprint at runtime so the
build produces TCM-branded artifacts.

Two fixes:
  1. Prepend `import os` (upstream's createPackage uses os.path.join
     without importing os — the build dies with NameError).
  2. Rewrite defines so the installer wizard, install folder, and
     Add/Remove Programs entry all read "The Cloud Market" instead
     of "nextcloud" / "Nextcloud".

NSIS visual assets (welcome banner, installer icon) are NOT touched
here — those are overridden directly on disk before the package step
(see workflow step "Override NSIS+Craft branding assets"), which
sidesteps NSIS path-resolution quirks for absolute paths.

Usage:  python3 patch-blueprint.py /path/to/nextcloud-client.py
"""
import re
import sys

if len(sys.argv) != 2:
    print("usage: patch-blueprint.py <blueprint.py>", file=sys.stderr)
    sys.exit(2)

p = sys.argv[1]
with open(p, encoding="utf-8") as f:
    s = f.read()

if not re.search(r"(?m)^import os\b", s):
    s = "import os\n" + s

s = re.sub(
    r'self\.defines\["appname"\]\s*=\s*".+?"',
    'self.defines["appname"] = "thecloudmarket"',
    s,
)
s = re.sub(
    r'self\.defines\["company"\]\s*=\s*".+?"',
    'self.defines["company"] = "The Cloud Market"',
    s,
)
if "productname" not in s:
    s = re.sub(
        r'(self\.defines\["company"\][^\n]*\n)',
        r'\1        self.defines["productname"] = "The Cloud Market"\n',
        s,
    )

with open(p, "w", encoding="utf-8") as f:
    f.write(s)

print(f"Patched {p}")
