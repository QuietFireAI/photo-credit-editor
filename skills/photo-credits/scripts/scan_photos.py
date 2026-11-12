#!/usr/bin/env python3
"""Inventory the pictures in a website folder against its photo-credits.json.

Usage:
    python3 scan_photos.py SITE_FOLDER                 report only, changes nothing
    python3 scan_photos.py SITE_FOLDER --write         also add a blank entry for every unlisted picture
    python3 scan_photos.py SITE_FOLDER --check         exit with status 1 if any picture still lacks a credit
    python3 scan_photos.py SITE_FOLDER --json          print the report as JSON

Options:
    --manifest PATH    photo-credits.json location (default: SITE_FOLDER/photo-credits.json)
    --exclude GLOB     skip pictures whose path matches, e.g. --exclude "icons/*" (repeatable)
    --min-kb N         skip pictures smaller than N kilobytes (default 0: skip nothing)

Standard library only. Reads files inside SITE_FOLDER. Writes one file, the manifest, and only with --write.
With --write, existing entries are never changed or removed: new blank entries are added at the end.
No network access.
"""
import argparse
import fnmatch
import json
import os
import re
import sys
from urllib.parse import unquote

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
TEXT_EXT = {
    ".html", ".htm", ".php", ".css", ".scss", ".js", ".mjs", ".ts", ".jsx", ".tsx", ".vue", ".astro",
    ".svelte", ".json", ".xml", ".md", ".njk", ".liquid", ".hbs", ".ejs", ".twig", ".txt",
}
MAX_TEXT_BYTES = 2 * 1024 * 1024
NOTE = ("Edit with the Photo Credits Editor. One entry per picture. "
        "A picture with a blank credit stays off the credits page.")
FIELDS = ("file", "title", "credit", "source", "license", "link")
REF = re.compile(r"[^\s\"'()<>=,;:\\/?#]+\.(?:jpe?g|png|webp|gif|avif)", re.IGNORECASE)


def norm(path):
    """Compare paths the way the site script does: forward slashes, no leading ./ or /, lower case."""
    p = str(path or "").strip().replace("\\", "/")
    while p.startswith("./") or p.startswith("/"):
        p = p[2:] if p.startswith("./") else p[1:]
    return p.lower()


def natural(text):
    """Sort photo2 before photo10."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", text)]


def walk(site):
    images, texts = [], []
    for root, dirs, files in os.walk(site):
        dirs[:] = sorted((d for d in dirs if not d.startswith(".") and d != "node_modules"), key=natural)
        for name in sorted(files, key=natural):
            if name.startswith("."):
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, site).replace(os.sep, "/")
            ext = os.path.splitext(name)[1].lower()
            if ext in IMAGE_EXT:
                images.append((rel, full))
            elif ext in TEXT_EXT:
                texts.append((rel, full))
    return images, texts


def find_references(texts, manifest_abs):
    """Map each picture file name (lower case) to the site files that mention it."""
    refs = {}
    for rel, full in texts:
        if os.path.abspath(full) == manifest_abs:
            continue
        try:
            if os.path.getsize(full) > MAX_TEXT_BYTES:
                continue
            with open(full, "r", encoding="utf-8", errors="ignore") as fh:
                body = fh.read()
        except OSError:
            continue
        for hit in set(REF.findall(body)):
            name = unquote(hit).lower()
            refs.setdefault(name, set()).add(rel)
            # The site script ignores the file type, so photo2.webp on a page counts for photo2.jpg.
            refs.setdefault(os.path.splitext(name)[0] + ".*", set()).add(rel)
    return refs


def load_manifest(path):
    if not os.path.exists(path):
        return {"note": NOTE, "photos": []}, False
    with open(path, "r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
    if isinstance(data, list):
        data = {"note": NOTE, "photos": data}
    if not isinstance(data, dict) or not isinstance(data.get("photos"), list):
        raise ValueError('expected an object with a "photos" list')
    data["photos"] = [p for p in data["photos"] if isinstance(p, dict)]
    return data, True


def main():
    ap = argparse.ArgumentParser(description="Inventory a website folder's pictures against photo-credits.json.")
    ap.add_argument("site")
    ap.add_argument("--manifest")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--min-kb", type=float, default=0)
    args = ap.parse_args()

    site = os.path.abspath(args.site)
    if not os.path.isdir(site):
        print("Not a folder: %s" % args.site, file=sys.stderr)
        return 2
    manifest_path = os.path.abspath(args.manifest) if args.manifest else os.path.join(site, "photo-credits.json")

    try:
        manifest, existed = load_manifest(manifest_path)
    except (ValueError, OSError) as exc:
        print("Could not read %s: %s" % (manifest_path, exc), file=sys.stderr)
        return 2

    images, texts = walk(site)
    refs = find_references(texts, manifest_path)

    excluded = 0
    kept = []
    for rel, full in images:
        if any(fnmatch.fnmatch(rel.lower(), g.lower()) for g in args.exclude):
            excluded += 1
            continue
        try:
            size = os.path.getsize(full)
        except OSError:
            size = 0
        if args.min_kb and size < args.min_kb * 1024:
            excluded += 1
            continue
        kept.append((rel, size))

    # The site script ignores the file type, so mill.webp and mill.jpg are one picture with one credit.
    def stem(key):
        return os.path.splitext(key)[0]

    all_on_disk = {stem(norm(rel)) for rel, _ in images}
    listed = {}
    for p in manifest["photos"]:
        k = stem(norm(p.get("file")))
        if k and k not in listed:
            listed[k] = p

    files_found = len(kept)
    groups = {}
    for rel, size in kept:
        groups.setdefault(stem(norm(rel)), []).append((rel, size))
    kept = []
    for k, members in groups.items():
        entry = listed.get(k)
        named = [m for m in members if entry and norm(m[0]) == norm(entry.get("file"))]
        kept.append((named or members)[0])

    def used_on(rel):
        name = os.path.basename(rel).lower()
        return sorted(refs.get(name) or refs.get(os.path.splitext(name)[0] + ".*", ()))

    credited, skipped, blank, unlisted = [], [], [], []
    for rel, size in kept:
        entry = listed.get(stem(norm(rel)))
        row = {"file": rel, "kb": round(size / 1024, 1), "used_on": used_on(rel)}
        if entry is None:
            unlisted.append(row)
        elif entry.get("skip"):
            skipped.append(row)
        elif str(entry.get("credit") or "").strip():
            credited.append(row)
        else:
            blank.append(row)
    missing = [p.get("file") for k, p in listed.items() if k not in all_on_disk]

    added = 0
    if args.write:
        for row in unlisted:
            manifest["photos"].append({f: (row["file"] if f == "file" else "") for f in FIELDS})
            added += 1
        if added or not existed:
            manifest.setdefault("note", NOTE)
            ordered = {"note": manifest["note"]}
            ordered.update({k: v for k, v in manifest.items() if k not in ("note", "photos")})
            ordered["photos"] = manifest["photos"]
            with open(manifest_path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(ordered, fh, indent=1, ensure_ascii=False)
                fh.write("\n")
        blank.extend(unlisted)
        unlisted = []

    need = len(blank) + len(unlisted)
    report = {
        "site": site,
        "manifest": manifest_path,
        "manifest_existed": existed,
        "pictures_found": len(kept),
        "picture_files_found": files_found,
        "excluded": excluded,
        "credited": credited,
        "no_credit_needed": skipped,
        "listed_but_blank": blank,
        "not_listed": unlisted,
        "listed_but_file_missing": missing,
        "entries_added": added,
        "need_a_credit": need,
    }

    if args.as_json:
        print(json.dumps(report, indent=1, ensure_ascii=False))
    else:
        print("Photo credits scan: %s" % site)
        print("Manifest: %s%s" % (manifest_path, "" if existed else "  (did not exist)"))
        print()
        notes = []
        if files_found != len(kept):
            notes.append("%d files; the same picture in two file types counts once" % files_found)
        if excluded:
            notes.append("%d more excluded" % excluded)
        print("%5d pictures found%s" % (len(kept), (" (%s)" % "; ".join(notes)) if notes else ""))
        print("%5d credited" % len(credited))
        print("%5d marked no credit needed" % len(skipped))
        print("%5d listed, credit still blank" % len(blank))
        print("%5d not in photo-credits.json yet" % len(unlisted))
        print("%5d listed, but the file is not in the folder" % len(missing))
        if added:
            print("\nAdded %d blank entries to the manifest." % added)

        def show(title, rows):
            if not rows:
                return
            print("\n%s" % title)
            for r in rows:
                where = ", ".join(r["used_on"][:4]) + (" ..." if len(r["used_on"]) > 4 else "")
                print("  %s%s" % (r["file"], ("   used on: " + where) if where else "   no mention found in site files"))

        show("Credit still blank:", blank)
        show("Not in photo-credits.json yet (run again with --write to add them):", unlisted)
        if missing:
            print("\nListed, but the file is not in the folder:")
            for f in missing:
                print("  %s" % f)
        if blank or unlisted:
            print("\n'No mention found' means no page, stylesheet or script names that file. "
                  "A script that builds file names in code can still load it.")
        print("\n%s" % ("Every picture has a credit or is marked no credit needed." if not need
                        else "%d pictures still need a credit." % need))

    return 1 if (args.check and need) else 0


if __name__ == "__main__":
    sys.exit(main())
