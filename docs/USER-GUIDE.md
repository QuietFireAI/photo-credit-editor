# Photo Credits: User Guide

This guide covers everything in the plugin: the credits file, the editor, the site script, the scanner, and how Claude uses them.

- [The idea](#the-idea)
- [Install](#install)
- [Use it with Claude](#use-it-with-claude)
- [The credits file](#the-credits-file)
- [The editor](#the-editor)
- [Showing credits on your site](#showing-credits-on-your-site)
- [The scanner](#the-scanner)
- [Troubleshooting](#troubleshooting)
- [Limits](#limits)

## The idea

One file, `photo-credits.json`, sits in the top folder of your website and lists every picture with who made it and where it came from. Three tools work from that file:

- the **editor**, where you type the credits,
- the **site script**, which shows them to visitors,
- the **scanner**, which finds pictures that are missing from the file or still blank.

The skill tells Claude how to run all three for you, and never to make up a credit.

## Install

**In Claude (claude.ai or the desktop app):** open Customize, then Plugins, and add Photo Credits from the directory. Before it is listed there, choose Add, then Add marketplace, and enter `https://github.com/QuietFireAI/photo-credit-editor`.

**In Claude Code:**

```bash
claude plugin marketplace add QuietFireAI/photo-credit-editor
claude plugin install firelands-photo-credits@firelands-ai
```

**Without Claude:** the editor, the site script and the scanner are ordinary files in `skills/photo-credits/`. Download them and use them directly.

## Use it with Claude

Give Claude access to your website folder, then ask in plain words:

| You say | Claude does |
| --- | --- |
| "Which pictures on my site have no photo credit?" | Scans the folder and lists the pictures that are blank or missing from the file |
| "Set up photo credits for this site." | Creates `photo-credits.json` with an entry for every picture, then asks you for the credits |
| "The mill photo is by Jane Doe, from the County Historical Society, used with permission." | Writes exactly that into the entry |
| "This one came from this page: (address)" | Reads the page, shows you the author and license it found, and writes them after you confirm |
| "Add a photo credits page and captions." | Adds the site script and a credits list to your pages |
| "Check the photo credits before we launch." | Runs the check and lists anything still blank |
| "Give me the editor." | Hands you the editor file to fill in credits yourself |

Claude fills a field only from what you tell it or from a source page you point it to. Anything it does not know stays blank and is reported as blank.

## The credits file

```json
{
 "note": "Edit with the Photo Credits Editor. One entry per picture.",
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

| Field | Meaning |
| --- | --- |
| `file` | Path to the picture from the top folder of the site |
| `title` | What the picture shows. Used as the heading on the credits page |
| `credit` | The photographer or owner. A picture with a blank credit is not shown anywhere |
| `source` | Where the picture came from, such as a collection or website |
| `license` | The license or permission, such as "CC BY-SA 4.0", "Own work" or "Used with permission" |
| `link` | Address of the source page. Shown only if it starts with `http://` or `https://` |
| `skip` | Set to `true` for a picture that needs no credit, such as a logo or icon |

The file type is ignored when matching, so one entry for `mill.jpg` also covers `mill.webp`.

## The editor

`skills/photo-credits/assets/photo-credits-editor.html` is a single file. Open it in a web browser. It needs no internet connection and sends nothing anywhere.

1. Click **Choose site folder** and pick the top folder of your site, the one that holds the home page. The editor lists every picture with a preview. If the folder already has a `photo-credits.json`, it is loaded.
2. Fill in the fields. Tick **No credit needed** for logos, icons and graphics you made yourself.
3. Use **Needs a credit** to see only what is left.
4. Click **Download photo-credits.json** and put the file in the top folder of your site.

Other buttons: **Open photo-credits.json** loads an existing file without choosing a folder, and **Add a picture** adds an entry by hand.

Your browser will ask to confirm when you choose a folder. The files are read on your computer only. Unsaved work is kept in the browser, so closing the tab does not lose it.

## Showing credits on your site

Copy `skills/photo-credits/assets/photo-credit.js` into your site, then add one tag before `</body>` on each page that should show credits:

```html
<script src="js/photo-credit.js" defer
        data-manifest="photo-credits.json"
        data-list="#creditList"
        data-rotators=".slideshow"
        data-images="main img"></script>
```

For a credits page, add an empty element for the list:

```html
<div id="creditList"></div>
```

| Setting | What it does | Default |
| --- | --- | --- |
| `data-manifest` | Path to `photo-credits.json` from the page | `photo-credits.json` |
| `data-list` | Element to fill with the full credits list | `#creditList` |
| `data-rotators` | Slideshow boxes that get a caption for the slide on show | none |
| `data-active` | The slide on show inside a slideshow, such as `.active`. Leave out for fade slideshows | the most opaque slide |
| `data-images` | Ordinary pictures that get a credit line under them | none |
| `data-item-class` | Class on each entry in the credits list | `photo-credit-item` |
| `data-prefix` | Text before a caption | `Photo: ` |
| `data-empty` | Text shown when no picture has a credit yet | a short placeholder |
| `data-style` | `off` to skip the built-in caption styling | on |

Captions use the classes `photo-credit` and `photo-credit-inline`. The built-in styling has the lowest priority, so any rule in your own stylesheet overrides it.

A working example is in [`examples/sample-site`](../examples/sample-site).

## The scanner

`skills/photo-credits/scripts/scan_photos.py` needs Python 3 and nothing else.

```bash
python3 scan_photos.py SITE_FOLDER            # report only, changes nothing
python3 scan_photos.py SITE_FOLDER --write    # add a blank entry for each unlisted picture
python3 scan_photos.py SITE_FOLDER --check    # exit status 1 if any picture lacks a credit
python3 scan_photos.py SITE_FOLDER --json     # the report as JSON
```

| Option | Use |
| --- | --- |
| `--manifest PATH` | Use a credits file somewhere other than `SITE_FOLDER/photo-credits.json` |
| `--exclude GLOB` | Leave out pictures whose path matches, such as `--exclude "icons/*"`. Repeatable |
| `--min-kb N` | Leave out pictures smaller than N kilobytes |

With `--write`, existing entries are never changed or removed. New blank entries are added at the end.

It looks at `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif` and `.avif` files, and skips hidden folders and `node_modules`.

## Troubleshooting

- **Captions or the credits list do not appear when I open a page from my computer.** The site script loads `photo-credits.json` over the web, and browsers block that for pages opened straight from disk. Check on the live site or through a local web server.
- **Credits show on the home page but not on pages in subfolders.** Those pages need the path back to the file, for example `data-manifest="../photo-credits.json"`.
- **I uploaded a new `photo-credits.json` and the site still shows the old credits.** Browsers may keep the old copy for up to an hour. Reload the page with the cache cleared to see it sooner.
- **A slideshow shows no caption.** Set `data-rotators` to the slideshow's own selector. If slides move sideways instead of fading, also set `data-active` to the selector for the slide on show.
- **A picture has a credit in the file but shows none on the site.** Check that `file` is the path from the top folder of the site, that `credit` is not blank, and that "No credit needed" is not ticked.
- **The editor lists file paths that look wrong.** Choose the top folder of the site, not a folder inside it.
- **The scan says "no mention found" for a picture I know is used.** A script that builds file names in code is not detected. The picture still needs a credit.
- **The scan will not run.** It needs Python 3.

Still stuck? See [SUPPORT.md](../SUPPORT.md).

## Limits

- The plugin records credits. It does not check whether you are allowed to use a picture, and it is not legal advice.
- Slideshows that move slides sideways need `data-active`, because the script cannot see which slide is on show otherwise.
- Pictures loaded from another website, such as a photo service, are not in your site folder, so the scanner and the editor do not list them. You can add them by hand.
- SVG files and icons in `.ico` format are not treated as pictures.
