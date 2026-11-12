---
name: photo-credits
description: Track and display photo credits for a website. Use when the user wants to credit photographers, build or update a photo credits page, add "Photo by" captions to a site, find which pictures on a site have no credit or attribution, or check image credits before a launch.
---

# Photo credits

Help the owner of a website record who made each picture on the site and where it came from, then show that on the site. Everything is driven by one file, `photo-credits.json`, kept in the top folder of the site.

This skill ships four files. Paths in the table are relative to this skill's folder. In commands, `${CLAUDE_SKILL_DIR}` stands for that folder; where it is not filled in for you, use the path to this skill's folder instead.

| File | What it is |
| --- | --- |
| `scripts/scan_photos.py` | Lists every picture in a site folder and compares it with `photo-credits.json`. Python 3, standard library only, no network. |
| `assets/photo-credits-editor.html` | A form the owner opens in a browser to fill in credits. Single file, works offline. |
| `assets/photo-credit.js` | The script the site loads to show captions and fill the credits page. |
| `assets/credits-page-snippet.html` | Markup to paste into a credits page. |

## The one rule

Never invent a credit, source, license or link. A wrong credit is worse than a blank one. Fill a field only from what the user tells you or from a source page the user points you to. If you read a source page, show the user what you found and get a yes before writing it. Leave everything else blank and report it as blank.

A credit line is not permission to use a picture. If the user asks whether they are allowed to use a picture, say you can report what the source page states about its license, and that they should confirm with the owner when it is unclear. Do not give a legal opinion.

## The file

```json
{
 "note": "Edit with the Photo Credits Editor. ...",
 "photos": [
  {
   "file": "images/gallery/mill.jpg",
   "title": "The old mill, 1912",
   "credit": "Jane Doe",
   "source": "County Historical Society",
   "license": "Used with permission",
   "link": "https://example.org/collection/mill"
  }
 ]
}
```

- `file` is the path from the top folder of the site.
- A picture with a blank `credit` is not shown anywhere.
- `"skip": true` marks a picture that needs no credit, such as a logo or icon. It counts as dealt with.
- Keep any field you do not recognise. Never reorder or delete existing entries unless asked.

## Steps

### 1. Find the site folder and scan it

Ask for the site folder only if you cannot find it. Then run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/scan_photos.py /path/to/site
```

This changes nothing. It reports how many pictures are credited, marked no credit needed, blank, not yet listed, and listed but missing from the folder, and names the pages that mention each one. Add `--json` if you want to work with the result.

Useful options: `--exclude "icons/*"` (repeatable) and `--min-kb 5` leave out icons and tiny graphics.

"No mention found in site files" does not mean a picture is unused. A slideshow script that builds file names in code will not be found by the scan. Do not tell the user a picture is unused on that basis alone.

### 2. Add the missing entries

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/scan_photos.py /path/to/site --write
```

This adds a blank entry for each unlisted picture and creates the file if it does not exist. Existing entries are never changed.

### 3. Fill in the credits

Tell the user how many pictures need a credit, then offer both ways of filling them in:

- **The user fills them in.** Give them a copy of `assets/photo-credits-editor.html`. They open it in a browser, choose the site folder to see every picture with a preview, type the credits, and download `photo-credits.json` into the top folder of the site.
- **You fill them in from what the user tells you.** Edit `photo-credits.json` directly. Go through the blank ones a few at a time and ask who made each. If the user gives a source page address, read that page for the author and license, show what you found, and write it only after they confirm.

For logos, icons and graphics the user made themselves, set `"skip": true` instead of leaving them blank.

### 4. Show credits on the site

Only do this when the user wants credits displayed. Read the site's pages first so the settings match its markup.

1. Copy `assets/photo-credit.js` into the site, for example to `js/photo-credit.js`.
2. Add the credits list to a page. Use `assets/credits-page-snippet.html` as the starting point and restyle it to match the site.
3. Add the script tag before `</body>` on each page that should show credits. Settings go on the tag:

| Setting | Use |
| --- | --- |
| `data-manifest` | Path to `photo-credits.json` from the page. Default `photo-credits.json`. Pages in subfolders need `../photo-credits.json`. |
| `data-list` | Element to fill with the full list. Default `#creditList`. |
| `data-rotators` | Selector for slideshow boxes. Each gets a small caption for the slide on show. |
| `data-active` | Selector for the slide on show inside a slideshow, such as `.active`. Leave out for fade slideshows, where the most opaque slide is used. |
| `data-images` | Selector for ordinary `<img>` pictures that should get a credit line under them. |
| `data-item-class` | Class for each entry in the list, to reuse the site's own card style. |
| `data-prefix` | Text before a caption. Default `Photo: `. |
| `data-style` | `off` to skip the built-in caption styling. |

Captions use the classes `photo-credit` (slideshows) and `photo-credit-inline` (ordinary pictures). The built-in styling has the lowest priority, so any rule in the site's stylesheet overrides it.

Pictures are matched by path with the file type ignored, so a `.webp` copy on the page matches the `.jpg` entry in the file.

The script loads `photo-credits.json` with `fetch`, so captions do not appear when a page is opened straight from disk. Test through a local web server or on the live site.

### 5. Check before launch

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/scan_photos.py /path/to/site --check
```

Exit status 1 means at least one picture still has no credit. Report the exact list. Do not say the site is fully credited unless this passes.

## Reporting back

State the counts from the scan, list what is still blank, and say plainly which fields you filled and where each value came from.
