#!/usr/bin/env python3
# Copyright 2026 QuietFireAI / Jeff Phillips. Licensed under the Apache License, Version 2.0.
# SPDX-License-Identifier: Apache-2.0
"""Check that every picture in a website folder has a proper credit, and gather leads for the ones that do not.

Usage:
    python3 scan_photos.py SITE_FOLDER                 report only, changes nothing
    python3 scan_photos.py SITE_FOLDER --write         also add a blank entry for every unlisted picture
    python3 scan_photos.py SITE_FOLDER --check         exit with status 1 unless every picture is complete
    python3 scan_photos.py SITE_FOLDER --json          print the report as JSON

Options:
    --manifest PATH    photo-credits.json location (default: SITE_FOLDER/photo-credits.json)
    --exclude GLOB     skip pictures whose path matches, e.g. --exclude "icons/*" (repeatable)
    --min-kb N         skip pictures smaller than N kilobytes (default 0: skip nothing)

For each picture the scan reports one status:
    complete     has a credit and everything its license calls for
    incomplete   has a credit, but something a proper attribution needs is missing
    no credit    listed, credit blank
    not listed   not in photo-credits.json yet
    no credit needed   marked "skip": true (logo, icon, own graphic)

For every picture that is not complete it also reports leads: facts that help find the right credit.
    inside the file   author, copyright and similar fields stored in the picture file itself
    on the page       alt text and captions where the picture is used
    file name         a name that matches how a known picture site names its downloads

Leads are evidence for a person to confirm. This script never writes a credit.

Standard library only. Reads files inside SITE_FOLDER. Writes one file, the manifest, and only with --write.
With --write, existing entries are never changed or removed: new blank entries are added at the end.
No network access.
"""
import argparse
import fnmatch
import json
import os
import posixpath
import re
import struct
import sys
import zlib
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import unquote

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
HTML_EXT = {".html", ".htm", ".php"}
TEXT_EXT = HTML_EXT | {
    ".css", ".scss", ".js", ".mjs", ".ts", ".jsx", ".tsx", ".vue", ".astro",
    ".svelte", ".json", ".xml", ".md", ".njk", ".liquid", ".hbs", ".ejs", ".twig", ".txt",
}
MAX_TEXT_BYTES = 2 * 1024 * 1024
MAX_IMAGE_BYTES = 40 * 1024 * 1024
NOTE = ("Edit with the Photo Credit Editor. One entry per picture. "
        "A picture with a blank credit stays off the credits page.")
FIELDS = ("file", "title", "credit", "source", "license", "link")
REF = re.compile(r"[^\s\"'()<>=,;\\?#]+\.(?:jpe?g|png|webp|gif|avif)", re.IGNORECASE)

# File names that match how a picture site names its downloads. A match is a lead, not proof.
NAME_HINTS = (
    (re.compile(r"^\d{2,4}px-", re.I), "Wikimedia Commons"),
    (re.compile(r"unsplash", re.I), "Unsplash"),
    (re.compile(r"pexels", re.I), "Pexels"),
    (re.compile(r"pixabay", re.I), "Pixabay"),
    (re.compile(r"istock", re.I), "iStock"),
    (re.compile(r"shutterstock", re.I), "Shutterstock"),
    (re.compile(r"gettyimages", re.I), "Getty Images"),
    (re.compile(r"adobestock", re.I), "Adobe Stock"),
    (re.compile(r"depositphotos", re.I), "Depositphotos"),
    (re.compile(r"dreamstime", re.I), "Dreamstime"),
    (re.compile(r"freepik", re.I), "Freepik"),
    (re.compile(r"flickr", re.I), "Flickr"),
)


# ---------------------------------------------------------------- facts stored inside a picture file

def _clean(value):
    if isinstance(value, bytes):
        try:
            value = value.decode("utf-8")
        except UnicodeDecodeError:
            value = value.decode("latin-1")
    value = re.sub(r"\s+", " ", str(value).replace("\x00", " ")).strip()
    return value[:300]


def _put(out, key, value):
    value = _clean(value)
    if value and key not in out:
        out[key] = value


EXIF_ASCII = {0x010E: "description", 0x013B: "artist", 0x8298: "copyright"}
EXIF_UTF16 = {0x9C9B: "title", 0x9C9D: "artist"}      # the fields Windows writes from a file's Properties


def _tiff(data, out):
    """Author, copyright and description from an EXIF block."""
    order = {b"II": "<", b"MM": ">"}.get(data[:2])
    if not order or len(data) < 8:
        return
    try:
        if struct.unpack(order + "H", data[2:4])[0] != 42:
            return
        start = struct.unpack(order + "I", data[4:8])[0]
        count = struct.unpack(order + "H", data[start:start + 2])[0]
        for i in range(min(count, 300)):
            entry = data[start + 2 + i * 12:start + 14 + i * 12]
            if len(entry) < 12:
                break
            tag, kind, n = struct.unpack(order + "HHI", entry[:8])
            if not 0 < n < 8000:
                continue
            if n <= 4:
                raw = entry[8:8 + n]
            else:
                at = struct.unpack(order + "I", entry[8:12])[0]
                raw = data[at:at + n]
            if tag in EXIF_ASCII and kind == 2:
                _put(out, EXIF_ASCII[tag], raw)
            elif tag in EXIF_UTF16 and kind == 1:
                _put(out, EXIF_UTF16[tag], raw.decode("utf-16-le", "ignore"))
    except struct.error:
        return


IPTC = {(2, 80): "artist", (2, 110): "credit", (2, 115): "source", (2, 116): "copyright",
        (2, 105): "title", (2, 5): "title", (2, 120): "description"}


def _iptc(data, out):
    i = 0
    while i + 5 <= len(data):
        if data[i] != 0x1C:
            i += 1
            continue
        record, dataset = data[i + 1], data[i + 2]
        length = struct.unpack(">H", data[i + 3:i + 5])[0]
        if length & 0x8000:
            break
        key = IPTC.get((record, dataset))
        if key:
            _put(out, key, data[i + 5:i + 5 + length])
        i += 5 + length


def _photoshop(data, out):
    """The IPTC block inside a JPEG's Photoshop segment."""
    i = 0
    while i + 12 <= len(data) and data[i:i + 4] == b"8BIM":
        resource = struct.unpack(">H", data[i + 4:i + 6])[0]
        name_size = 1 + data[i + 6]
        name_size += name_size % 2
        at = i + 6 + name_size
        if at + 4 > len(data):
            break
        size = struct.unpack(">I", data[at:at + 4])[0]
        body = data[at + 4:at + 4 + size]
        if resource == 0x0404:
            _iptc(body, out)
        i = at + 4 + size + (size % 2)


RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
XMP_FIELDS = {
    "{http://purl.org/dc/elements/1.1/}creator": "artist",
    "{http://purl.org/dc/elements/1.1/}rights": "copyright",
    "{http://purl.org/dc/elements/1.1/}title": "title",
    "{http://purl.org/dc/elements/1.1/}description": "description",
    "{http://purl.org/dc/elements/1.1/}source": "source",
    "{http://ns.adobe.com/photoshop/1.0/}Credit": "credit",
    "{http://ns.adobe.com/photoshop/1.0/}Source": "source",
    "{http://ns.adobe.com/xap/1.0/rights/}UsageTerms": "license",
    "{http://ns.adobe.com/xap/1.0/rights/}WebStatement": "license_link",
    "{http://creativecommons.org/ns#}license": "license_link",
    "{http://creativecommons.org/ns#}attributionName": "artist",
    "{http://creativecommons.org/ns#}attributionURL": "source_link",
}


def _xmp(packet, out):
    try:
        root = ET.fromstring(packet)
    except ET.ParseError:
        return
    for el in root.iter():
        for name, value in el.attrib.items():          # fields written as attributes
            if name in XMP_FIELDS:
                _put(out, XMP_FIELDS[name], value)
        key = XMP_FIELDS.get(el.tag)
        if not key:
            continue
        items = [li.text for li in el.iter(RDF + "li") if li.text and li.text.strip()]
        value = ", ".join(items) if items else (el.text or el.attrib.get(RDF + "resource", ""))
        _put(out, key, value)


def _xmp_anywhere(data, out):
    start = data.find(b"<x:xmpmeta")
    end = data.find(b"</x:xmpmeta>", start)
    if start != -1 and end != -1:
        _xmp(data[start:end + 12], out)


PNG_KEYS = {"author": "artist", "artist": "artist", "copyright": "copyright", "title": "title",
            "description": "description", "source": "source", "credit": "credit"}


def _png(data, out):
    i = 8
    while i + 8 <= len(data):
        size = struct.unpack(">I", data[i:i + 4])[0]
        kind = data[i + 4:i + 8]
        body = data[i + 8:i + 8 + size]
        i += 12 + size
        try:
            if kind == b"tEXt":
                key, _, text = body.partition(b"\x00")
                text = text.decode("latin-1")
            elif kind == b"zTXt":
                key, _, rest = body.partition(b"\x00")
                text = zlib.decompress(rest[1:]).decode("latin-1")
            elif kind == b"iTXt":
                key, _, rest = body.partition(b"\x00")
                packed = rest[0:1] == b"\x01"
                rest = rest[2:]
                _, _, rest = rest.partition(b"\x00")       # language tag
                _, _, text = rest.partition(b"\x00")       # translated keyword
                text = (zlib.decompress(text) if packed else text).decode("utf-8", "ignore")
            elif kind == b"eXIf":
                _tiff(body, out)
                continue
            else:
                continue
        except (zlib.error, ValueError):
            continue
        key = key.decode("latin-1")
        if key == "XML:com.adobe.xmp":
            _xmp(text.encode("utf-8"), out)
        elif key.lower() in PNG_KEYS:
            _put(out, PNG_KEYS[key.lower()], text)


def _jpeg(data, out):
    i = 2
    while i + 4 <= len(data) and data[i] == 0xFF:
        marker = data[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        if marker == 0xDA:                                 # picture data starts: no more metadata
            break
        size = struct.unpack(">H", data[i + 2:i + 4])[0]
        body = data[i + 4:i + 2 + size]
        if marker == 0xE1 and body[:6] == b"Exif\x00\x00":
            _tiff(body[6:], out)
        elif marker == 0xE1 and body[:29] == b"http://ns.adobe.com/xap/1.0/\x00":
            _xmp(body[29:], out)
        elif marker == 0xED and body[:14] == b"Photoshop 3.0\x00":
            _photoshop(body[14:], out)
        i += 2 + size


def _webp(data, out):
    i = 12
    while i + 8 <= len(data):
        kind = data[i:i + 4]
        size = struct.unpack("<I", data[i + 4:i + 8])[0]
        body = data[i + 8:i + 8 + size]
        if kind == b"EXIF":
            _tiff(body[6:] if body[:6] == b"Exif\x00\x00" else body, out)
        elif kind == b"XMP ":
            _xmp(body, out)
        i += 8 + size + (size % 2)


def read_embedded(path):
    """Author, copyright, title and similar facts stored inside a picture file. Empty when there are none."""
    out = {}
    try:
        if os.path.getsize(path) > MAX_IMAGE_BYTES:
            return out
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError:
        return out
    try:
        if data[:2] == b"\xff\xd8":
            _jpeg(data, out)
        elif data[:8] == b"\x89PNG\r\n\x1a\n":
            _png(data, out)
        elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            _webp(data, out)
        if not out:
            _xmp_anywhere(data, out)                       # GIF, AVIF and anything unusual
    except (struct.error, IndexError, ValueError):
        pass
    return out


def name_hints(rel):
    base = os.path.basename(rel)
    return [site for pattern, site in NAME_HINTS if pattern.search(base)]


# ---------------------------------------------------------------- what the pages say about a picture

class _Page(HTMLParser):
    """Collects the alt text, title and figure caption of each picture on a page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found = []            # (file name, alt, caption)
        self._figure = None        # pictures seen inside the open <figure>
        self._caption = None       # text collected inside the open <figcaption>
        self._captions = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "figure":
            self._figure, self._captions = [], []
        elif tag == "figcaption":
            self._caption = []
        elif tag == "img":
            name = (a.get("src") or a.get("data-src") or "").split("?")[0].split("#")[0].strip()
            if name:
                alt = _clean(a.get("alt") or a.get("title") or "")
                if self._figure is not None:
                    self._figure.append((name, alt))
                else:
                    self.found.append((name, alt, ""))

    def handle_endtag(self, tag):
        if tag == "figcaption" and self._caption is not None:
            self._captions.append(_clean(" ".join(self._caption)))
            self._caption = None
        elif tag == "figure" and self._figure is not None:
            caption = " ".join(c for c in self._captions if c)
            self.found.extend((name, alt, caption) for name, alt in self._figure)
            self._figure = None

    def handle_data(self, data):
        if self._caption is not None:
            self._caption.append(data)

    def close(self):
        if self._figure:
            self.found.extend((name, alt, "") for name, alt in self._figure)
        super().close()


def norm(path):
    """Compare paths the way the site script does: forward slashes, no leading ./ or /, lower case."""
    p = str(path or "").strip().replace("\\", "/")
    while p.startswith("./") or p.startswith("/"):
        p = p[2:] if p.startswith("./") else p[1:]
    return p.lower()


def stem(key):
    """The site script ignores the file type, so mill.webp and mill.jpg are one picture with one credit."""
    return os.path.splitext(key)[0]


def count(n, word, width=0):
    return "%*d %s%s" % (width, n, word, "" if n == 1 else "s")


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


class Pictures:
    """Works out which picture an address written in a page, stylesheet or script points at."""

    def __init__(self, images):
        self.by_path = {}                                  # path without file type -> same
        self.by_name = {}                                  # file name without type -> paths
        for rel, _ in images:
            key = stem(norm(rel))
            self.by_path[key] = key
            self.by_name.setdefault(posixpath.basename(key), set()).add(key)

    def find(self, address, written_in, sure_only=False):
        """The pictures an address may mean. With sure_only, an address that fits several pictures fits none."""
        a = unquote(address).replace("\\", "/")
        a = re.sub(r"^(?:[a-z][a-z0-9+.-]*:)?//[^/]*", "", a, flags=re.I)      # drop the site name, if any
        tail = re.sub(r"^(?:\.\.?/)+", "", a.lstrip("/"))
        tries = [a.lstrip("/")] if a.startswith("/") else [posixpath.join(posixpath.dirname(written_in), a), tail]
        for t in tries:                                    # 1. the exact path, from the file or from the site's top folder
            key = stem(norm(posixpath.normpath(t)))
            if key in self.by_path:
                return [key]
        key = stem(norm(posixpath.normpath(tail)))
        if "/" in key:                                     # 2. the end of a path
            hits = [k for k in self.by_path if k.endswith("/" + key)]
        else:                                              # 3. a bare file name
            hits = sorted(self.by_name.get(key, ()))
        if len(hits) == 1 or (hits and not sure_only):
            return hits
        return []


def read_site_text(texts, manifest_abs, pictures):
    """Which site files mention each picture, and what the pages say about it."""
    refs, context = {}, {}
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
            for key in pictures.find(hit, rel):
                refs.setdefault(key, set()).add(rel)
        if os.path.splitext(rel)[1].lower() in HTML_EXT:
            page = _Page()
            try:
                page.feed(body)
                page.close()
            except Exception:                              # a badly broken page must not stop the scan
                continue
            for address, alt, caption in page.found:
                if not (alt or caption):
                    continue
                item = {"page": rel}
                if alt:
                    item["alt"] = alt
                if caption:
                    item["caption"] = caption
                # Alt text and captions are leads, so they go only to the one picture the address surely means.
                for key in pictures.find(address, rel, sure_only=True):
                    bucket = context.setdefault(key, [])
                    if item not in bucket:
                        bucket.append(item)
    return refs, context


# ---------------------------------------------------------------- what a proper attribution needs

def license_family(text):
    t = str(text or "").lower()
    if not t.strip():
        return ""
    if re.search(r"\bcc0\b|public domain|no known copyright", t):
        return "public domain"
    if re.search(r"\bcc[ -]?by\b|creative commons", t):
        return "creative commons"
    return "other"


def problems(entry):
    """What a credited entry still lacks. An empty list means the attribution is complete.

    Creative Commons rules follow the Creative Commons guidance on attribution: credit the author,
    link to the source, and name the license. A title is required for versions 3.0 and earlier.
    """
    out = []
    lic = str(entry.get("license") or "").strip()
    link = str(entry.get("link") or "").strip()
    family = license_family(lic)
    if not lic:
        out.append("no license or permission recorded")
    if family == "creative commons":
        if not re.match(r"https?://", link, re.I):
            out.append("a Creative Commons license needs a link to the source page")
        version = re.search(r"(\d)\.\d", lic)
        if not version:
            out.append("the license version is missing, for example 4.0")
        elif int(version.group(1)) <= 3 and not str(entry.get("title") or "").strip():
            out.append("Creative Commons versions 3.0 and earlier need the title of the work")
    return out


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
    ap = argparse.ArgumentParser(
        description="Check that every picture in a website folder has a proper credit, and gather leads.")
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
    refs, context = read_site_text(texts, manifest_path, Pictures(images))
    full_path = dict(images)

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
        return sorted(refs.get(stem(norm(rel)), ()))

    def leads(rel):
        found = {}
        embedded = read_embedded(full_path[rel])
        if embedded:
            found["inside_the_file"] = embedded
        on_page = context.get(stem(norm(rel)))
        if on_page:
            found["on_the_page"] = on_page
        hints = name_hints(rel)
        if hints:
            found["file_name"] = hints
        return found

    complete, incomplete, skipped, blank, unlisted = [], [], [], [], []
    for rel, size in kept:
        entry = listed.get(stem(norm(rel)))
        row = {"file": rel, "kb": round(size / 1024, 1), "used_on": used_on(rel)}
        if entry is not None and entry.get("skip"):
            skipped.append(row)
            continue
        credit = str(entry.get("credit") or "").strip() if entry is not None else ""
        if credit:
            missing = problems(entry)
            if not missing:
                complete.append(row)
                continue
            row["credit"] = credit
            row["missing"] = missing
            row["leads"] = leads(rel)
            incomplete.append(row)
        else:
            row["leads"] = leads(rel)
            (unlisted if entry is None else blank).append(row)
    missing_files = [p.get("file") for k, p in listed.items() if k not in all_on_disk]

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

    need = len(incomplete) + len(blank) + len(unlisted)
    report = {
        "site": site,
        "manifest": manifest_path,
        "manifest_existed": existed,
        "pictures_found": len(kept),
        "picture_files_found": files_found,
        "excluded": excluded,
        "complete": complete,
        "incomplete": incomplete,
        "no_credit_needed": skipped,
        "no_credit": blank,
        "not_listed": unlisted,
        "listed_but_file_missing": missing_files,
        "entries_added": added,
        "need_work": need,
    }

    if args.as_json:
        print(json.dumps(report, indent=1, ensure_ascii=False))
        return 1 if (args.check and need) else 0

    print("Photo credit scan: %s" % site)
    print("Manifest: %s%s" % (manifest_path, "" if existed else "  (did not exist)"))
    print()
    notes = []
    if files_found != len(kept):
        notes.append("%s; the same picture in two file types counts once" % count(files_found, "file"))
    if excluded:
        notes.append("%d more excluded" % excluded)
    print("%s found%s" % (count(len(kept), "picture", 5), (" (%s)" % "; ".join(notes)) if notes else ""))
    print("%5d complete" % len(complete))
    print("%5d credited but incomplete" % len(incomplete))
    print("%5d no credit" % len(blank))
    print("%5d not in photo-credits.json yet" % len(unlisted))
    print("%5d marked no credit needed" % len(skipped))
    print("%5d listed, but the file is not in the folder" % len(missing_files))
    if added:
        print("\nAdded %s to the manifest." % count(added, "blank entry").replace("entrys", "entries"))

    def show(title, rows):
        if not rows:
            return
        print("\n%s" % title)
        for r in rows:
            print("  %s" % r["file"])
            if r.get("credit"):
                print("      credit: %s" % r["credit"])
            for m in r.get("missing", ()):
                print("      missing: %s" % m)
            where = ", ".join(r["used_on"][:4]) + (" ..." if len(r["used_on"]) > 4 else "")
            print("      used on: %s" % (where or "no mention found in site files"))
            found = r.get("leads", {})
            inside = found.get("inside_the_file")
            if inside:
                print("      inside the file: %s" % "; ".join('%s "%s"' % (k.replace("_", " "), v)
                                                              for k, v in inside.items()))
            for item in found.get("on_the_page", ())[:3]:
                parts = ['%s "%s"' % (k, item[k]) for k in ("alt", "caption") if k in item]
                print("      on the page (%s): %s" % (item["page"], "; ".join(parts)))
            for site_name in found.get("file_name", ()):
                print("      file name: matches how %s names its files" % site_name)
            if not found:
                print("      no leads found")

    show("Credited but incomplete:", incomplete)
    show("No credit:", blank)
    show("Not in photo-credits.json yet (run again with --write to add them):", unlisted)
    if missing_files:
        print("\nListed, but the file is not in the folder:")
        for f in missing_files:
            print("  %s" % f)
    if need:
        print("\nLeads are evidence to confirm, not credits. 'No mention found' means no page, stylesheet or "
              "script names that file; a script that builds file names in code can still load it.")
    print("\n%s" % ("Every picture has a complete credit or is marked no credit needed." if not need
                    else "%s still %s work." % (count(need, "picture"), "needs" if need == 1 else "need")))

    return 1 if (args.check and need) else 0


if __name__ == "__main__":
    sys.exit(main())
