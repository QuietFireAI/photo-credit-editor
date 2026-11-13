# Photo Credit Editor

Make sure every picture on a website carries a proper credit.

Most small sites collect pictures from many places: a local photographer, a historical society, Wikimedia Commons, a stock library, a neighbour's phone. Months later nobody remembers which came from where, and pictures go out with no credit or the wrong one. This plugin works through a site picture by picture until each one has a proper attribution, or is clearly marked as one that cannot be credited yet.

## What it does

- **Finds every picture** in a site folder and sorts them: complete, credited but incomplete, no credit.
- **Gathers leads for the ones that need work.** It reads the author, copyright, title and license stored inside each picture file, the alt text and captions on the pages that use it, and file names that match how picture sites name their downloads.
- **Works out the attribution.** Claude follows the leads to the source page where it can, then shows you what it proposes for each picture and the evidence behind each value. Nothing is written until you confirm it.
- **Knows what a proper credit needs.** A credit plus the license or permission. A Creative Commons picture also needs a link to its source page and the license version, and versions 3.0 and earlier need the title.
- **Gives you an editor** you can use without Claude: a single web page that shows each picture, the leads found inside the file with a button to use them, and what is still missing.
- **Shows credits on the site**: a caption on slideshows and pictures, and a credits page where Creative Commons licenses link to their license pages.
- **Checks before launch** that no picture is left blank or incomplete.

Claude never makes up a credit. It proposes only what it has evidence for, tells you where the evidence came from, and leaves the rest blank.

## Install

In Claude, open Customize, then Plugins, and add Photo Credit Editor. To install straight from this repository instead, choose Add, then Add marketplace, and enter this repository's address.

In Claude Code:

```bash
claude plugin marketplace add QuietFireAI/photo-credit-editor
claude plugin install photo-credit-editor@quietfireai
```

## How to use it

Give Claude access to your website folder and ask things like:

- "Which pictures on my site still need a proper credit, and what can you find out about them?"
- "Set up photo credits for this site."
- "The mill photo is by Jane Doe, from the County Historical Society, used with permission."
- "Add a photo credits page and captions."
- "Check the photo credits before we launch."

To do it yourself, ask Claude for the Photo Credit Editor, open it in a browser, choose your site folder, fill in the credits, and download `photo-credits.json` into the top folder of your site.

A three-picture sample site for trying all of this is in [`examples/sample-site`](examples/sample-site).

## Documentation

| Document | What it covers |
| --- | --- |
| [User Guide](docs/USER-GUIDE.md) | Leads, what a proper credit needs, the credits file, the editor, the site script, the scanner, troubleshooting and limits |
| [Support](SUPPORT.md) | How to get help |
| [Privacy Policy](PRIVACY.md) | What data the plugin handles: none is collected |
| [Terms of Use](TERMS.md) | License, warranty and your responsibilities |
| [Security](SECURITY.md) | How to report a security problem |
| [Changelog](CHANGELOG.md) | What changed in each release |
| [Contributing](CONTRIBUTING.md) | How to propose a change |

## What is inside

| File | Purpose |
| --- | --- |
| `skills/photo-credits/SKILL.md` | The steps Claude follows |
| `skills/photo-credits/scripts/scan_photos.py` | Finds every picture, checks each credit, and gathers leads |
| `skills/photo-credits/assets/photo-credits-editor.html` | The editor |
| `skills/photo-credits/assets/photo-credit.js` | The script a site loads to show credits |
| `skills/photo-credits/assets/credits-page-snippet.html` | Starting markup for a credits page |
| `examples/sample-site/` | A small site for trying the plugin |

## What it runs, reads and sends

- `scan_photos.py` is Python 3 with the standard library only. It reads files inside the site folder you name, including the information stored inside picture files. It writes one file, `photo-credits.json`, and only when run with `--write`, where it adds blank entries and never changes existing ones. It makes no network requests.
- The editor runs entirely in your browser. It reads the pictures in the folder you choose, on your computer, and uploads nothing. It keeps unsaved work in the browser's local storage so a closed tab does not lose it. The one link it offers, for a file named like a Wikimedia Commons download, opens that site only if you click it.
- `photo-credit.js` runs on your website and loads `photo-credits.json` from that same website. It contacts no other server and sets no cookies.
- When Claude traces a picture to its source, Claude reads the source page or searches the web, in your conversation and at your request.

The plugin has no hooks, no MCP servers, no dependencies to install, and collects no data.

## Troubleshooting

- **A picture is marked incomplete.** It has a credit but is missing something its license calls for. The scan and the editor both say what.
- **No leads were found for a picture.** Many pictures carry nothing inside the file, and websites often strip it. You will need to say where the picture came from.
- **Captions or the credits list do not appear when I open a page from my computer.** Browsers block the site script from loading `photo-credits.json` for pages opened straight from disk. Check on the live site or through a local web server.
- **Credits show on the home page but not on pages in subfolders.** Those pages need the path back to the file, for example `data-manifest="../photo-credits.json"` on the script tag.

The [User Guide](docs/USER-GUIDE.md#troubleshooting) has the full list.

## A note on permission

A credit line says who made a picture. It is not permission to use it. This plugin records and completes credits; it does not decide whether you are allowed to publish a picture. When in doubt, ask the owner.

## Support

Questions or problems: support@quietfireai.com, or see [SUPPORT.md](SUPPORT.md).

## License

MIT. Copyright QuietFireAI. See [LICENSE](LICENSE).
