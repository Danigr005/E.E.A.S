#!/usr/bin/env python3
"""Merge one or more CWCDT profiles into a Claude Code settings.json.

Idempotent and non-destructive: unrelated keys stay untouched; objects merge recursively,
lists are unions (existing order first), scalars take the profile value. With several
--managed files, later ones win over earlier ones. Keys starting with "_" are comments.
"""
import argparse
import json
import os
import tempfile
from pathlib import Path

MASTER = Path(__file__).resolve().parent.parent


def expand(value):
    """Copy of value with {{MASTER}}/{{HOME}} replaced and comment keys removed."""
    if isinstance(value, str):
        return value.replace("{{MASTER}}", str(MASTER)).replace("{{HOME}}", str(Path.home()))
    if isinstance(value, list):
        return [expand(item) for item in value]
    if isinstance(value, dict):
        return {key: expand(item) for key, item in value.items() if not key.startswith("_")}
    return value


def merge(base, patch):
    """New object: objects merge recursively, lists are unions, scalars take patch."""
    if isinstance(base, dict) and isinstance(patch, dict):
        return {**base, **{key: merge(base[key], val) if key in base else val for key, val in patch.items()}}
    if isinstance(base, list) and isinstance(patch, list):
        return base + [item for item in patch if item not in base]
    return patch


def changes(old, new, path=""):
    """Dotted paths whose value differs between old and new (lists summarised)."""
    if isinstance(old, dict) and isinstance(new, dict):
        for key in sorted(set(old) | set(new)):
            yield from changes(old.get(key), new.get(key), f"{path}.{key}" if path else key)
    elif old != new:
        if isinstance(old, list) and isinstance(new, list):
            yield f"{path} (+{len([item for item in new if item not in old])} entries)"
        else:
            yield path


def write_atomic(target: Path, payload: str) -> None:
    mode = target.stat().st_mode & 0o777 if target.exists() else 0o600
    fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=".settings-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.chmod(tmp, mode)
        os.replace(tmp, target)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=str(Path.home() / ".claude" / "settings.json"))
    parser.add_argument("--managed", action="append", help="profile JSON (repeatable); default: profiles/default.json")
    parser.add_argument("--dry-run", action="store_true", help="show what would change")
    parser.add_argument("--check", action="store_true", help="like --dry-run, but exit 1 if anything is missing")
    args = parser.parse_args()

    target = Path(args.target)
    current = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
    managed = {}
    for name in args.managed or [str(MASTER / "profiles" / "default.json")]:
        managed = merge(managed, expand(json.loads(Path(name).read_text(encoding="utf-8"))))
    merged = merge(current, managed)

    diff = list(changes(current, merged))
    if not diff:
        print("  ok      settings.json already contains the managed settings")
        return 0
    preview = args.dry_run or args.check
    for item in diff:
        print(f"  {'[dry-run] ' if preview else ''}set     {item}")
    if args.check:
        return 1
    if args.dry_run:
        return 0

    payload = json.dumps(merged, indent=2, ensure_ascii=False) + "\n"
    json.loads(payload)  # must round-trip before touching the real file
    write_atomic(target, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
