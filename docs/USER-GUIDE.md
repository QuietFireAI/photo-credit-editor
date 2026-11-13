# Photo Credit Editor: User Guide

This guide covers everything in the plugin: how it finds the right credit for a picture, what a proper credit needs, the credits file, the editor, the site script, the scanner, and how Claude uses them.

- [The idea](#the-idea)
- [Install](#install)
- [Use it with Claude](#use-it-with-claude)
- [Leads](#leads)
- [What a proper credit needs](#what-a-proper-credit-needs)
- [The credits file](#the-credits-file)
- [The editor](#the-editor)
- [Showing credits on your site](#showing-credits-on-your-site)
- [The scanner](#the-scanner)
- [Troubleshooting](#troubleshooting)
- [Limits](#limits)

## The idea

The aim is that every picture on your site ends up with a proper credit: who made it, where it came from, and the license or permission you use it under.

One file, `photo-credits.json`, sits in the top folder of your website and holds that for every picture. Three tools work from it:

- the **scanner**, which finds every picture, says which are complete, and gathers leads for the rest,
- the **editor**, where you fill in credits with those leads in front of you,
- the **site script**, which shows the credits to visitors.

The skill tells Claude how to use all three to get each picture to a proper credit, and never to make one up.

## Install

**In Claude (claude.ai or the desktop app):** open Customize, then Plugins, and add Photo Credit Editor from the directory. Before it is listed there, choose Add, then Add marketplace, and enter `https://github.com/QuietFireAI/photo-credit-editor`.

**In Claude Code:**

```bash
claude plugin marketplace add QuietFireAI/photo-credit-editor
claude plugin install photo-credit-editor@firelands-ai
```

**Without Claude:** the editor, the site script and the scanner are ordinary files in `skills/photo-credits/`. Download them and use them directly.

## Use it with Claude

Give Claude access to your website folder, then ask in plain words:

| You say | Claude does |
| --- | --- |
| "Which pictures on my site still need a proper credit?" | Scans the folder, lists the pictures that are blank or incomplete, and shows the leads it found for each |
| "Work out the credits for these." | Follows the leads to source pages where it can, then shows a table of proposed credits with the evidence for each value, for you to confirm |
| "The mill photo is by Jane Doe, from the County Historical Society, used with permission." | Writes exactly that into the entry |
| "This one came from this page: (address)" | Reads the page, shows you the author and license it found, and writes them after you confirm |
| "Add a photo credits page and captions." | Adds the site script and a credits list to your pages |
| "Check the photo credits before we launch." | Runs the check and lists anything still blank or incomplete |
| "Give me the editor." | Hands you the editor file to fill in credits yourself |

Claude writes a value only when you stated it or confirmed it. For a picture nobody can trace, it says so and leaves it blank, and tells you the options: find the source, replace the picture, or remove it.

## Leads

A lead is a fact that helps find the right credit. The scanner and the editor both gather three kinds:

| Lead | Where it comes from | How much to trust it |
| --- | --- | --- |
| Inside the file | Author, copyright, credit line, title, source, license link and source link that cameras, phones and editing programs store in a picture file | Good evidence of who made the picture. Not evidence that you may use it |
| On the page | The alt text and caption where the picture is used on your site | Weak. It often describes the subject, not the maker |
| File name | A name that matches how a picture site names its downloads, such as a size prefix like `640px-` used by Wikimedia Commons, or a site's name in the file name | A pointer to where to look. Not proof |

Leads are never written into the credits file automatically. In the editor each one has a **Use** button. With Claude, each one appears as evidence beside a proposed value.

Many pictures carry nothing inside the file, because websites and messaging apps often remove it. For those, you have to say where the picture came from.

## What a proper credit needs

| The entry has | Status |
| --- | --- |
| "No credit needed" ticked (logo, icon, your own graphic) | No credit needed |
| No credit | No credit |
| A credit, but no license or permission | Incomplete |
| A Creative Commons license without a link to the source page, or without a version number | Incomplete |
| A Creative Commons license of version 3.0 or earlier without a title | Incomplete |
| A credit and everything its license calls for | Complete |

The Creative Commons rows follow [Creative Commons' guidance on attribution](https://wiki.creativecommons.org/wiki/Recommended_practices_for_attribution): credit the author, link to the source, and name the license, with the title required for versions 3.0 and earlier.

Common values for the license field:

| You | Write |
| --- | --- |
| Took the picture yourself | `Own work` |
| Were given it by its owner, who agreed to its use | `Used with permission` |
| Know it is out of copyright | `Public domain` |
| Found it under a Creative Commons license | The license with its version, such as `CC BY-SA 4.0` |
| Bought or downloaded it from a stock library | The name of that library's license |

## The credits file

```json
{
 "note": "Edit with the Photo Credit Editor. One entry per picture.",
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
| `license` | The license or permission |
| `link` | Address of the source page. Shown only if it starts with `http://` or `https://` |
| `skip` | Set to `true` for a picture that needs no credit, such as a logo or icon |

The file type is ignored when matching, so one entry for `mill.jpg` also covers `mill.webp`.

## The editor

`skills/photo-credits/assets/photo-credits-editor.html` is a single file. Open it in a web browser. It needs no internet connection and uploads nothing.

1. Click **Choose site folder** and pick the top folder of your site, the one that holds the home page. The editor lists every picture with a preview. If the folder already has a `photo-credits.json`, it is loaded. If the editor is already holding a different list, such as unsaved work from an earlier visit, it asks which one you want before changing anything.
2. The editor reads each picture file that still needs work. Where it finds an author, copyright, title or license, a **Leads for this picture** box appears with a **Use** button beside each. Use a lead only if you know it is right.
3. Fill in the rest. Under each picture the editor says **Complete**, **No credit yet**, or **Incomplete** with what is missing, and shows how the credit will read.
4. Tick **No credit needed** for logos, icons and graphics you made yourself.
5. Use **Needs work** to see only what is left.
6. Click **Download photo-credits.json** and put the file in the top folder of your site.

Other buttons: **Open photo-credits.json** loads an existing file without choosing a folder, and asks first if that would replace a list you are working on. **Add a picture** adds an entry by hand. **Remove** takes an entry out and offers **Undo**.

Your browser will ask to confirm when you choose a folder. The files are read on your computer only. Unsaved work is kept in the browser, so closing the tab does not lose it; the editor tells you when it has picked up work from an earlier visit.

Choosing a folder needs a desktop browser: Chrome, Edge, Firefox or Safari. Support on phones and tablets varies by browser and version, and where a browser cannot choose a folder the editor says so and switches that button off. You can still open and edit a `photo-credits.json` there, without previews or leads.

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

On the credits page each entry shows its title, the credit and source, the license, and a link to the source page. A Creative Commons license is shown as a link to its license page.

Captions use the classes `photo-credit` and `photo-credit-inline`. The built-in styling has the lowest priority, so any rule in your own stylesheet overrides it.

The script updates captions when the page changes, so pictures that load late and slides that change are followed without checking on a clock. The one exception is a slideshow run purely by a CSS animation, which it checks once a second while the page is on show.

A working example is in [`examples/sample-site`](../examples/sample-site).

## The scanner

`skills/photo-credits/scripts/scan_photos.py` needs Python 3 and nothing else.

```bash
python3 scan_photos.py SITE_FOLDER            # report only, changes nothing
python3 scan_photos.py SITE_FOLDER --write    # add a blank entry for each unlisted picture
python3 scan_photos.py SITE_FOLDER --check    # exit status 1 unless every picture is complete
python3 scan_photos.py SITE_FOLDER --json     # the report as JSON, leads included
```

| Option | Use |
| --- | --- |
| `--manifest PATH` | Use a credits file somewhere other than `SITE_FOLDER/photo-credits.json` |
| `--exclude GLOB` | Leave out pictures whose path matches, such as `--exclude "icons/*"`. Repeatable |
| `--min-kb N` | Leave out pictures smaller than N kilobytes |

The report gives a status for every picture and, for each one that is not complete, what is missing and the leads it found. With `--write`, existing entries are never changed or removed, and no credit is ever written from a lead.

It looks at `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif` and `.avif` files, and skips hidden folders and `node_modules`.

## Troubleshooting

- **A picture is marked incomplete.** It has a credit but lacks something its license calls for. The scan and the editor both say what is missing.
- **No leads were found.** The picture file carries no author or copyright inside it and its name matches no known site. Say where it came from, or ask whoever supplied it.
- **A lead looks wrong.** Do not use it. Information stored in a file can be out of date or belong to an editing program. It is evidence, not proof.
- **Captions or the credits list do not appear when I open a page from my computer.** The site script loads `photo-credits.json` over the web, and browsers block that for pages opened straight from disk. Check on the live site or through a local web server.
- **Credits show on the home page but not on pages in subfolders.** Those pages need the path back to the file, for example `data-manifest="../photo-credits.json"`.
- **I uploaded a new `photo-credits.json` and the site still shows the old credits.** Browsers may keep the old copy for up to an hour. Reload the page with the cache cleared to see it sooner.
- **A slideshow shows no caption.** Set `data-rotators` to the slideshow's own selector. If slides move sideways instead of fading, also set `data-active` to the selector for the slide on show.
- **A picture has a credit in the file but shows none on the site.** Check that `file` is the path from the top folder of the site, that `credit` is not blank, and that "No credit needed" is not ticked.
- **The editor lists file paths that look wrong.** Choose the top folder of the site, not a folder inside it.
- **The editor opened with pictures I did not expect.** It picked up unsaved work from an earlier visit in the same browser, and says so at the top. Choose your site folder and pick "Use the file in the folder", or click "Start over with an empty list".
- **The scan says "no mention found" for a picture I know is used.** A script that builds file names in code is not detected. The picture still needs a credit.
- **The scan will not run.** It needs Python 3.

Still stuck? See [SUPPORT.md](../SUPPORT.md).

## Limits

- The plugin finds, completes and records credits. It does not check whether you are allowed to use a picture, and it is not legal advice.
- It cannot recognise a picture by its content. Finding the source of a picture that has no leads needs either your knowledge or a search by image, which the plugin does not do itself.
- The completeness rules know Creative Commons licenses. For any other license, an entry counts as complete once it has a credit and a license or permission; check that license's own terms for anything more it asks for.
- Slideshows that move slides sideways need `data-active`, because the script cannot see which slide is on show otherwise.
- Pictures loaded from another website are not in your site folder, so the scanner and the editor do not list them. You can add them by hand.
- The editor's folder chooser needs a desktop browser. It is not dependable on phones and tablets.
- When a script or stylesheet names a picture by file name alone and two folders hold a picture with that name, the scan lists that file under both. Alt text and captions are only ever attached to the one picture a page address clearly points at.
- SVG files and icons in `.ico` format are not treated as pictures.
