# Changelog

## 1.3.0 - 2026-11-26

- Authorize a local folder scan and review likely photos, ambiguous assets, and exclusions with thumbnails and reasons.
- Check embedded metadata, manifest attribution, and visible credit in static site files separately. Review responsive alternatives and filter the results by what is missing.
- Export one photo, selected photos, or all results in view. The Markdown audit includes unresolved items. The merged manifest previews selected changes and preserves unselected records.
- Download a JPEG copy with updated author, credit, and rights fields in standard XMP. The original photo stays in place.
- V2 preview adds bottom-overlay and below-photo credit banners with responsive previews and portable HTML export.
- Harden scanner file access and manifest writes, cap PNG metadata expansion, scan image references in linear time, escape terminal controls in the CLI report, and keep the site renderer's manifest fetch on the same origin.

## 1.2.0 - 2026-11-18

- Editor: click a preview to see the picture larger. Each preview shows the picture's size in pixels.
- Editor and scanner: pictures smaller than 100 pixels on their longest side (icons, spacers, tracking pixels) are set aside instead of listed. They are always counted and shown, with a way to add them back, and the limit can be changed or turned off. Pictures already in the credits file are never set aside.
- New `show` field: show a credit on the picture and the credits page (the default), on the credits page only, or nowhere. The editor has a choice for it, the site script follows it, and a Creative Commons picture set to show nowhere counts as incomplete.
- Fixed, editor: changing the size limit and then clicking elsewhere no longer rebuilds the list under the click.

## 1.1.0 - 2026-11-12

The plugin now works to get every picture a proper credit, instead of only listing which have one.

- Plugin named `photo-credit-editor` (shown as Photo Credit Editor), published by QuietFireAI.
- Licensed under the Apache License 2.0, matching the other QuietFireAI open-source repositories.
- Leads: the scanner and the editor read the author, copyright, credit line, title, source and license stored inside JPEG, PNG and WebP files, the alt text and captions on the pages that use a picture, and file names that match how picture sites name their downloads.
- Completeness: an entry is complete only when it has a credit and what its license calls for. Creative Commons entries need a source link and a version, and a title for versions 3.0 and earlier.
- Skill: Claude now works out an attribution for each picture that needs one, proposes it with the evidence, and writes only what the user confirms.
- Editor: a leads box with a Use button per lead, a status line per picture, a preview of how the credit reads, and a Needs work filter.
- Site script: Creative Commons licenses on the credits page link to their license pages.
- Scanner: `--check` now fails on incomplete credits as well as blank ones.
- Fixed, editor: choosing a site folder while the browser still held unsaved work from an earlier visit skipped the folder's own `photo-credits.json` and mixed the two lists. The editor now reads the folder's file and asks which list to use.
- Fixed, editor: opening a file or clearing the list asks before replacing work, and Remove offers Undo.
- Fixed, site script: a picture whose address is swapped in after the page loads now gets the right caption, and loses it if it changes to an uncredited picture.
- Changed, site script: captions follow page changes instead of rechecking every one to two seconds.
- Fixed, scanner: two pictures with the same file name in different folders no longer share each other's pages, alt text or captions.
- Fixed: singular and plural wording in the scanner and the editor.
- Sample site: picture files renamed to match what they show.

## 1.0.0 - 2026-11-12

First release.

- Skill `photo-credits`, `scan_photos.py`, the editor, `photo-credit.js`, and a sample site.
