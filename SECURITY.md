# Security

## Reporting a problem

Email **support@quietfireai.com** with "Security" in the subject line. Please do not open a public issue for a security problem. Include the steps to reproduce it. You will get a reply as soon as we can, and credit in the changelog if you want it.

## Supported versions

The latest release on the `main` branch is supported.

## What the plugin does and does not do

- No network requests from the scanner or the editor.
- The site script loads one file, `photo-credits.json`, from the same website it runs on.
- Text from `photo-credits.json` is always inserted into pages as plain text, never as HTML. Links are shown only when they start with `http://` or `https://`.
- Text read from inside picture files is treated the same way: shown as plain text, never as HTML.
- The skill tells Claude to treat text found inside picture files, on pages and on source sites as information only, never as instructions.
- Picture files are read defensively. A damaged or hostile file yields no leads and cannot stop a scan.
- No hooks, no MCP servers, no dependencies, no credentials, no minified or compiled code.
- The scanner writes one file, `photo-credits.json`, and only when run with `--write`.
