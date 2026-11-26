# Photo Credit Editor

Audit website photos and export the attribution updates you approve.

Most small sites collect pictures from many places: a local photographer, a historical society, Wikimedia Commons, a stock library, a neighbour's phone. Months later nobody remembers which came from where, and pictures go out with no credit or the wrong one. This plugin works through a site picture by picture until each one has a proper attribution, or is clearly marked as one that cannot be credited yet.

## What it does

- **Audits a folder you authorize.** The editor separates likely photos, ambiguous assets and exclusions using page references, dimensions and file context.
- **Shows the current state.** Review a thumbnail, embedded author and rights metadata, recorded attribution and any visible credit found in static site files.
- **Exports your selection.** Download a Markdown audit or preview and download a merged `photo-credits.json`. When only embedded metadata needs updating, download a JPEG copy with standard XMP attribution fields.
- **Works out the attribution.** With your approval, Claude can follow leads to source pages and show you the evidence for each proposed credit. Site files change only when you ask to apply the result.
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

Open [Photo Credit Editor](skills/photo-credits/assets/photo-credits-editor.html) in a desktop browser. Choose a site folder or a local checkout of a repository you can read, authorize the scan, and review its thumbnails and credit fields. Select one, several, or all photos in view. Review the export, then add the downloaded artifacts to your project.

The **V2 preview** panel previews and exports self-contained inline credit banners for complete selected credits. The preview is available in this release.

Try the [three-picture sample walkthrough](examples/sample-site/README.md) to see a complete credit, an incomplete credit, and an uncredited photo with embedded author metadata.

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
- The editor runs entirely in your browser. It inspects photos and static HTML or CSS in the folder you authorize and uploads nothing. A download leaves the chosen files intact. Unsaved work stays in the browser's local storage.
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

Apache License 2.0. Copyright 2026 QuietFireAI / Jeff Phillips. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
