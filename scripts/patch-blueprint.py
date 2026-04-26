#!/usr/bin/env python3
"""Patch the upstream nextcloud-client blueprint at runtime so the
build produces TCM-branded artifacts.

Three fixes:
  1. Prepend `import os` (upstream's createPackage uses os.path.join
     without importing os — the build dies with NameError).
  2. Rewrite defines so the installer wizard, install folder, and
     Add/Remove Programs entry all read "The Cloud Market" instead
     of "nextcloud" / "Nextcloud".
  3. Override Craft NSIS installer assets (Windows only) — point
     MUI_WELCOMEFINISHPAGE_BITMAP, MUI_HEADERIMAGE_BITMAP, and
     MUI_ICON at our TCM-branded files. Without this, NSIS falls
     back to its stock 2003 modern-wizard.bmp and KDE craft.ico.

Usage:
  patch-blueprint.py <blueprint.py>
      Minimal patch (defines only — no NSIS asset override).

  patch-blueprint.py <blueprint.py> <welcome.bmp> <header.bmp> <icon.ico>
      Full patch including NSIS asset override paths (used on Windows).
"""
import re
import sys

if len(sys.argv) not in (2, 5):
    print("usage: patch-blueprint.py <blueprint.py> [welcome.bmp header.bmp icon.ico]",
          file=sys.stderr)
    sys.exit(2)

p = sys.argv[1]
nsis_assets = None
if len(sys.argv) == 5:
    welcome, header, icon = sys.argv[2:5]
    # NSIS prefers forward slashes in path strings.
    welcome_n = welcome.replace("\\", "/")
    header_n = header.replace("\\", "/")
    icon_n = icon.replace("\\", "/")
    nsis_assets = (welcome_n, header_n, icon_n)

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

if nsis_assets:
    welcome_n, header_n, icon_n = nsis_assets
    nsis_block = (
        '        if CraftCore.compiler.isWindows:\n'
        f'            self.defines["icon"] = r"{icon_n}"\n'
        '            self.defines["nsis_include"] = (\n'
        f'                \'!define MUI_WELCOMEFINISHPAGE_BITMAP "{welcome_n}"\\n\'\n'
        f'                \'!define MUI_UNWELCOMEFINISHPAGE_BITMAP "{welcome_n}"\\n\'\n'
        '                \'!define MUI_HEADERIMAGE\\n\'\n'
        f'                \'!define MUI_HEADERIMAGE_BITMAP "{header_n}"\\n\'\n'
        f'                \'!define MUI_HEADERIMAGE_UNBITMAP "{header_n}"\\n\'\n'
        '            )\n'
    )

    # IMPORTANT: pass replacement as a callable. re.sub's string-replacement
    # interprets backslash escapes (e.g. "\n" → newline) which would mangle
    # the literal "\n" sequences we need to keep inside nsis_block.
    if "MUI_WELCOMEFINISHPAGE_BITMAP" not in s:
        s = re.sub(
            r'(self\.defines\["productname"\][^\n]*\n)',
            lambda m: m.group(1) + nsis_block,
            s,
        )

with open(p, "w", encoding="utf-8") as f:
    f.write(s)

print(f"Patched {p}")
if nsis_assets:
    print(f"  welcome: {nsis_assets[0]}")
    print(f"  header:  {nsis_assets[1]}")
    print(f"  icon:    {nsis_assets[2]}")
