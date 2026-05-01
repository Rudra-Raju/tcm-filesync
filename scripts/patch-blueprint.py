#!/usr/bin/env python3
"""Patch the upstream nextcloud-client blueprint at runtime so the
build produces TCM-branded artifacts.

Three fixes:
  1. Prepend `import os` (upstream's createPackage uses os.path.join
     without importing os — the build dies with NameError).
  2. Rewrite defines so the installer wizard, install folder, and
     Add/Remove Programs entry all read "The Cloud Market" instead
     of "nextcloud" / "Nextcloud".
  3. (Optional, Windows only) Override defines["icon"] with an
     absolute path to our TCM .ico so the NSIS wrapper uses the
     TCM icon instead of Craft's default orange craft.ico.

Usage:
  patch-blueprint.py <blueprint.py>
  patch-blueprint.py <blueprint.py> <icon.ico>
"""
import re
import sys

if len(sys.argv) not in (2, 3):
    print("usage: patch-blueprint.py <blueprint.py> [icon.ico]", file=sys.stderr)
    sys.exit(2)

p = sys.argv[1]
icon = sys.argv[2] if len(sys.argv) == 3 else None

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

if icon and 'self.defines["icon"]' not in s:
    icon_block = (
        '        if CraftCore.compiler.isWindows:\n'
        f'            self.defines["icon"] = r"{icon}"\n'
    )
    s = re.sub(
        r'(self\.defines\["productname"\][^\n]*\n)',
        lambda m: m.group(1) + icon_block,
        s,
    )

with open(p, "w", encoding="utf-8") as f:
    f.write(s)

print(f"Patched {p}")
if icon:
    print(f"  icon: {icon}")
