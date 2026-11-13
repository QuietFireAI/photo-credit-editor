---
name: photo-credits
description: Make sure every picture on a website has a proper credit. Use when the user wants to credit photographers, find which pictures have no credit or attribution, work out who made a picture or what license it is under, fix or complete image attributions, build a photo credits page, add "Photo by" captions, or check image credits before a launch.
---

# Photo credits

The goal is that **every picture on the site ends up with a proper credit**: who made it, where it came from, and the license or permission it is used under. Listing the pictures that already have one is not the job. The job is getting the rest there.

Everything is recorded in one file, `photo-credits.json`, in the top folder of the site.

This skill ships four files. Paths in the table are relative to this skill's folder. In commands, `${CLAUDE_SKILL_DIR}` stands for that folder; where it is not filled in for you, use the path to this skill's folder instead.

| File | What it is |
| --- | --- |
| `scripts/scan_photos.py` | Finds every picture, says which are complete, and gathers leads for the rest. Python 3, standard library only, no network. |
| `assets/photo-credits-editor.html` | A form the owner opens in a browser to fill in credits, with the same leads and completeness checks. Single file, works offline. |
| `assets/photo-credit.js` | The script the site loads to show captions and fill the credits page. |
| `assets/credits-page-snippet.html` | Markup to paste into a credits page. |

## The one rule

Never invent a credit, source, license or link. A wrong credit is worse than a blank one.

You may **propose** a value when you have evidence for it, and you must say what the evidence is. You may **write** a value only after the user confirms it, or when the user stated it themselves. Anything without evidence stays blank and is reported as blank.

A credit is not permission to use a picture. If the user asks whether they may use a picture, report what the source page says about its license and tell them to confirm with the owner when it is unclear. Do not give a legal opinion.

## What "proper" means

The scan and the editor apply the same rules:

| The entry has | Status |
| --- | --- |
| `"skip": true` (logo, icon, the owner's own graphic) | No credit needed |
| No credit | No credit |
| A credit, but no license or permission | Incomplete |
| A Creative Commons license without a link to the source page, or without a version number | Incomplete |
| A Creative Commons license of version 3.0 or earlier without a title | Incomplete |
| A credit and everything its license calls for | Complete |

The Creative Commons rows follow Creative Commons' own guidance: credit the author, link to the source, and name the license; a title is required for versions 3.0 and earlier. Typical values for `license` are `Own work`, `Used with permission`, `Public domain`, `CC0 1.0`, `CC BY 4.0`, `CC BY-SA 4.0`, or the name of a stock license.

## The file

```json
{
 "note": "Edit with the Photo Credit Editor. ...",
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
- `"skip": true` marks a picture that needs no credit.
- Keep any field you do not recognise. Never reorder or delete existing entries unless asked.

## Steps

### 1. Scan the site

Ask for the site folder only if you cannot find it. Then run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/scan_photos.py /path/to/site --json
```

This changes nothing. For every picture it gives a status, and for every picture that is not complete it gives **leads**:

- `inside_the_file`: author, copyright, credit line, title, source, license link and source link stored in the picture file itself.
- `on_the_page`: the alt text and caption where the picture is used.
- `file_name`: a picture site whose download naming the file name matches.

Useful options: `--exclude "icons/*"` (repeatable) and `--min-kb 5` leave out icons and tiny graphics. Leave out `--json` for a report the user can read.

"No mention found in site files" does not mean a picture is unused. A slideshow script that builds file names in code is not detected.

### 2. Add the missing entries

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/scan_photos.py /path/to/site --write
```

This adds a blank entry for each unlisted picture and creates the file if it does not exist. It never changes an existing entry and never writes a credit.

### 3. Work out the attribution for every picture that needs work

Do this for each picture with status no credit, not listed, or incomplete. Do not stop at reporting them.

1. **Read the leads.** An author stored inside the file is good evidence of who made it. It is not evidence of permission or license. Alt text and captions are weaker and often describe the subject, not the maker.
2. **Look at the picture** when you can open it. A visible watermark, signature or caption is evidence. Use what you see to write `title`. Do not identify people from their faces.
3. **Trace the source** when there is something to follow and you can reach the web:
   - A `source_link` or `license_link` from the file: open it.
   - A file name like `640px-Old_Mill.jpg`: this is how Wikimedia Commons names its thumbnails. Drop the size prefix and open `https://commons.wikimedia.org/wiki/File:Old_Mill.jpg`.
   - A file name that matches another picture site: search that site, or the web, using the distinctive words in the file name, alt text and caption.
   - On the source page, read the author, the title, the license with its version, and note the page address.
4. **Propose, with evidence.** Show the user a table with one row per picture: the file, each value you propose, and where each value came from ("stored in the file", "the Wikimedia Commons page at ...", "the caption on index.html"). Say plainly when a value is only a lead and not confirmed by a source page. Propose nothing you have no evidence for.
5. **Ask about the rest.** For pictures with no usable lead, ask the owner, a few pictures at a time, which of these applies:
   - They took it themselves: credit them, license `Own work`.
   - Someone gave it to them: who, and did that person agree to its use? License `Used with permission`.
   - It came from a website or collection: which one? Then trace it as in step 3.
   - They do not know.
6. **Write only what is confirmed.** Edit `photo-credits.json` with the values the user confirmed or stated. For logos, icons and the owner's own graphics, set `"skip": true`.
7. **Say what cannot be credited.** A picture whose origin nobody knows cannot be given a proper credit. Leave it blank, list it, and tell the user the options: find the source, replace the picture, or remove it. Do not fill it in to make the check pass.

The owner can also do all of this by hand: give them a copy of `assets/photo-credits-editor.html`. They choose the site folder, the editor shows the leads it finds inside each picture file with a button to use each one, and it marks every entry complete, incomplete or blank as they type.

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

On the credits page, a Creative Commons license is shown as a link to its license page, which is what those licenses ask for.

Captions use the classes `photo-credit` (slideshows) and `photo-credit-inline` (ordinary pictures). The built-in styling has the lowest priority, so any rule in the site's stylesheet overrides it.

Pictures are matched by path with the file type ignored, so a `.webp` copy on the page matches the `.jpg` entry in the file.

The script loads `photo-credits.json` with `fetch`, so captions do not appear when a page is opened straight from disk. Test through a local web server or on the live site.

### 5. Check before launch

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/scan_photos.py /path/to/site --check
```

Exit status 1 means at least one picture is still blank, unlisted or incomplete. Report the exact list. Do not say the site is fully credited unless this passes.

## Reporting back

State the counts from the scan. For each value you wrote, say where it came from. List every picture that still needs work and what is missing for each.
