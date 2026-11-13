# Contributing

Thanks for helping. Bug reports, fixes and ideas are welcome.

## Reporting a bug

Open an issue and say what you did, what you expected, and what happened. For editor or site problems, include your browser.

## Making a change

1. Fork the repository and create a branch.
2. Keep the plugin dependency-free: plain HTML, plain JavaScript, and Python standard library only.
3. Check your change:
   - `claude plugin validate .` passes.
   - `python3 skills/photo-credits/scripts/scan_photos.py examples/sample-site` reports 3 pictures: 1 complete, 1 incomplete, 1 with no credit.
   - Serve the repository with `python3 -m http.server` and open `/examples/sample-site/` to confirm captions and the credits page still work.
4. Add a line to `CHANGELOG.md`.
5. Open a pull request describing what changed and why.

## Rules that do not bend

- The skill never invents a credit, source, license or link.
- A lead is never written into the credits file without a person confirming it.
- Nothing in the plugin sends data anywhere.
- Text from the credits file is inserted into pages as plain text, never as HTML.

By contributing, you agree that your contribution is licensed under the MIT License.
