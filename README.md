# Photo Credits

Keep track of who made every picture on a website, and show it.

Most small sites collect pictures from many places: a local photographer, a historical society, Wikimedia Commons, a stock library, a neighbour's phone. Months later nobody remembers which came from where. This plugin gives Claude a simple, repeatable way to sort that out, and gives the site owner a form they can use without Claude.

## What it does

- **Finds every picture** in a site folder and reports which have a credit, which are blank, and which pages use them.
- **Keeps one record**, `photo-credits.json`, in the top folder of the site: file, what it shows, credit, source, license or permission, and a link to the source page.
- **Gives the owner an editor**: a single web page that opens in a browser, shows a preview of each picture, and saves the record. It works offline.
- **Shows credits on the site**: a small caption on slideshows and pictures, and a full credits page, both driven by the same record.
- **Checks before launch** that no picture is left without a credit.

Claude never makes up a credit. A field is filled only from what you tell it or from a source page you point it to, and it asks before writing.

## How to use it

Ask Claude things like:

- "Which pictures on my site have no photo credit?"
- "Set up photo credits for this site."
- "Add a photo credits page."
- "Check the photo credits before we launch."

To fill in credits yourself, ask Claude for the Photo Credits Editor, open it in a browser, choose your site folder, type the credits, and download `photo-credits.json` into the top folder of your site.

## What is inside

| File | Purpose |
| --- | --- |
| `skills/photo-credits/SKILL.md` | The steps Claude follows |
| `skills/photo-credits/scripts/scan_photos.py` | Lists the pictures in a site folder and compares them with the record |
| `skills/photo-credits/assets/photo-credits-editor.html` | The editor |
| `skills/photo-credits/assets/photo-credit.js` | The script a site loads to show credits |
| `skills/photo-credits/assets/credits-page-snippet.html` | Starting markup for a credits page |

## What it runs, reads and sends

- `scan_photos.py` is Python 3 with the standard library only. It reads files inside the site folder you name. It writes one file, `photo-credits.json`, and only when run with `--write`, where it adds blank entries and never changes existing ones. It makes no network requests.
- The editor runs entirely in your browser. Pictures and credits stay on your computer. It keeps unsaved work in the browser's local storage so a closed tab does not lose it.
- `photo-credit.js` runs on your website and loads `photo-credits.json` from that same website. It contacts no other server and sets no cookies.
- If you give Claude the address of a source page, Claude may read that page to find the author and license. That is the only time anything is fetched, and it is at your request.

The plugin has no hooks, no MCP servers, no dependencies to install, and collects no data.

## Troubleshooting

- **Captions or the credits list do not appear when I open a page from my computer.** The site script loads `photo-credits.json` over the web, and browsers block that for pages opened straight from disk. Check on the live site or through a local web server.
- **Credits show on the home page but not on pages in subfolders.** Those pages need the path back to the file, for example `data-manifest="../photo-credits.json"` on the script tag.
- **I uploaded a new `photo-credits.json` and the site still shows the old credits.** Browsers may keep the old copy for up to an hour. Reload the page with the cache cleared to see it sooner.
- **A slideshow shows no caption.** Set `data-rotators` to the slideshow's own selector. If slides move sideways instead of fading, also set `data-active` to the selector for the slide on show, such as `.active`.
- **A picture has a credit in the file but shows none on the site.** Check that `file` is the path from the top folder of the site, that `credit` is not blank, and that "No credit needed" is not ticked.
- **The editor lists file paths that look wrong.** Choose the top folder of the site, the one that holds the home page, not a folder inside it.
- **The scan says "no mention found" for a picture I know is used.** A script that builds file names in code is not detected. The picture still needs a credit.
- **The scan will not run.** It needs Python 3. Nothing else has to be installed.

## A note on permission

A credit line says who made a picture. It is not permission to use it. This plugin records what you know; it does not decide whether you are allowed to publish a picture. When in doubt, ask the owner.

## Support

Questions or problems: support@firelandsai.com

## License

MIT. Copyright Firelands AI. See `LICENSE`.
