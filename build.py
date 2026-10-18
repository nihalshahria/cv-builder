"""Build CV flavors: merge cv/base.yaml with each cv/flavors/<name>.yaml and render with RenderCV.

Usage:
    .venv/bin/python build.py            # render every flavor
    .venv/bin/python build.py go web3    # render only the named flavors

Merge rules (flavor overrides base):
  - mappings merge recursively
  - a value of null removes that key (e.g. drop a whole section)
  - lists replace the base list, except lists of entries with a `company` key
    (experience), which are matched to base entries by `company` and merged
"""

import subprocess
import sys
from pathlib import Path

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "cv" / "base.yaml"
FLAVORS = ROOT / "cv" / "flavors"
BUILD = ROOT / ".build"
RENDERCV = ROOT / ".venv" / "bin" / "rendercv"

yaml = YAML()
yaml.width = 4096


def merge(base, overlay):
    if isinstance(base, dict) and isinstance(overlay, dict):
        for key, value in overlay.items():
            if value is None:
                base.pop(key, None)
            elif key in base:
                base[key] = merge(base[key], value)
            else:
                base[key] = value
        return base
    if isinstance(base, list) and isinstance(overlay, list) and overlay and all(
        isinstance(item, dict) and "company" in item for item in overlay
    ):
        by_company = {item.get("company"): item for item in base if isinstance(item, dict)}
        for item in overlay:
            if item["company"] not in by_company:
                sys.exit(f"error: no base entry with company {item['company']!r}")
            merge(by_company[item["company"]], item)
        return base
    return overlay


def build(name):
    flavor = yaml.load(FLAVORS / f"{name}.yaml") or {}
    doc = merge(yaml.load(BASE), flavor)

    pdf_path = doc.get("settings", {}).get("render_command", {}).pop("pdf_path", None)
    if not pdf_path:
        sys.exit(f"error: cv/flavors/{name}.yaml must set settings.render_command.pdf_path")

    out = BUILD / name
    out.mkdir(parents=True, exist_ok=True)
    merged = out / f"{name}.yaml"
    yaml.dump(doc, merged)

    print(f"→ {name}: {pdf_path}")
    subprocess.run(
        [
            str(RENDERCV), "render", str(merged), "--quiet",
            "--pdf-path", str(ROOT / pdf_path),
            "--typst-path", str(out / f"{name}.typ"),
            "--png-path", str(out / f"{name}.png"),
        ],
        check=True,
    )


def main():
    names = sys.argv[1:] or sorted(p.stem for p in FLAVORS.glob("*.yaml"))
    for name in names:
        if not (FLAVORS / f"{name}.yaml").exists():
            sys.exit(f"error: unknown flavor {name!r} (no cv/flavors/{name}.yaml)")
        build(name)


if __name__ == "__main__":
    main()
