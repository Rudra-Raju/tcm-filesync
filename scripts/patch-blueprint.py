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
    # Windows-only block:
    #   - icon         : path to TCM .ico for installer + Add/Remove Programs entry
    #   - executable   : tells Craft's NullsoftInstallerPackager to create a Start
    #                    Menu shortcut named "The Cloud Market" pointing at the
    #                    main exe. Without this, no shortcut is created and the
    #                    user cannot find the app after install.
    #   - registry_hook: raw NSIS injected into the install Section. Writes
    #                    HKCU\Software\Microsoft\Windows\CurrentVersion\Run so
    #                    nextcloud.exe auto-starts at every login (parity with
    #                    Dropbox / OneDrive). Tray icon always present, sync
    #                    daemon always running.
    #
    # The registry_hook value must arrive at Craft as a Python string whose
    # CONTENTS are literal NSIS code with single backslashes and embedded
    # double-quotes around the value. Build the value at patch-script runtime
    # then use repr() to embed it as a syntactically-correct Python literal.
    run_key_nsis = (
        r'WriteRegStr HKCU '
        r'"Software\Microsoft\Windows\CurrentVersion\Run" '
        r'"TheCloudMarket" '
        r'"$INSTDIR\bin\nextcloud.exe"'
    )
    icon_block = (
        '        if CraftCore.compiler.isWindows:\n'
        f'            self.defines["icon"] = r"{icon}"\n'
        '            self.defines["executable"] = "bin/nextcloud.exe"\n'
        f'            self.defines["registry_hook"] = {repr(run_key_nsis)}\n'
    )
    s = re.sub(
        r'(self\.defines\["productname"\][^\n]*\n)',
        lambda m: m.group(1) + icon_block,
        s,
    )

# Mac-only: drop a blacklist.txt next to the patched blueprint. Craft loads it
# automatically (the upstream blueprint already calls
# `self.blacklist_file.append(os.path.join(self.packageDir(), 'blacklist.txt'))`).
# Without this, Craft's mergeTree fails on a stray top-level `plugins/` directory
# whose entries collide with files already inside the .app bundle.
import os.path as _op
_blueprint_dir = _op.dirname(p)
_blacklist = _op.join(_blueprint_dir, "blacklist.txt")
_blacklist_patterns = [
    "# TCM additions: macdeployqt populates everything we need INSIDE",
    "# TheCloudMarket.app/Contents/{PlugIns,Frameworks,Resources}. Craft",
    "# also ships parallel top-level trees (Qt's regular install layout)",
    "# which collide on mergeTree because the inner names sometimes resolve",
    "# to a folder on one side and a file on the other (versioned framework",
    "# stubs vs flat dylibs, qmldir as both metadata file and dir, etc.).",
    "# Drop every redundant top-level tree on the archive root.",
    "# Each line is wrapped by Craft as ^...$ — use .* to match descendants.",
    # Confirmed-redundant trees (already mirrored inside the .app):
    r"plugins/.*",
    r"translations/.*",
    r"qml/.*",
    # Build-only artifacts that should never ship:
    r"mkspecs/.*",
    r"doc/.*",
    r"include/.*",
    r"libexec/.*",
    # NOTE: do NOT blacklist lib/, share/, or bin/ — Craft's library fixer
    # sources runtime dylibs from archive/lib/ to populate
    # TheCloudMarket.app/Contents/Frameworks/ at packaging time, and
    # archive/share/ feeds .app/Contents/Resources/ for some assets.
]
if not _op.exists(_blacklist) or "TCM additions" not in open(_blacklist, encoding="utf-8").read():
    with open(_blacklist, "w", encoding="utf-8") as f:
        f.write("\n".join(_blacklist_patterns) + "\n")

with open(p, "w", encoding="utf-8") as f:
    f.write(s)

print(f"Patched {p}")
print(f"Wrote   {_blacklist}")
if icon:
    print(f"  icon: {icon}")
