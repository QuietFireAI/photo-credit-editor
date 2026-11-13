# Changelog

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
