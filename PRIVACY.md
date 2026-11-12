# Privacy Policy

**Photo Credits** is published by Firelands AI. Last updated: November 12, 2026.

## Summary

This plugin collects no personal data. Firelands AI receives nothing from it: no accounts, no analytics, no telemetry, no cookies, no tracking.

## What each part does with data

| Part | Where it runs | What it reads | What it stores | What it sends |
| --- | --- | --- | --- | --- |
| The skill (instructions for Claude) | In your Claude session | The website folder you point Claude to | Nothing of its own | Nothing |
| `scan_photos.py` | On your computer, or in Claude's code sandbox | File names and text files inside the website folder you name | Only `photo-credits.json`, and only when run with `--write` | Nothing. It makes no network requests |
| Photo Credits Editor | In your web browser | The pictures and `photo-credits.json` in the folder you choose | Unsaved work, in that browser's local storage on your computer | Nothing. Pictures and credits never leave your computer |
| `photo-credit.js` | On your website, in each visitor's browser | `photo-credits.json` from your own website | Nothing. It sets no cookies | Nothing. It contacts no server other than your own website |

## Information you put in a credits file

`photo-credits.json` holds what you type into it, such as a photographer's name, a source and a link. When you upload that file to your website it becomes public, because showing credits is its purpose. You decide what goes in it.

## Claude and Anthropic

When you use this plugin inside Claude, your conversation and any files you share with Claude are handled under your own agreement with Anthropic and Anthropic's privacy policy. This plugin does not change that and receives none of that data.

If you give Claude the address of a web page where a picture came from, Claude may read that page to find the author and license. That request is made by Claude at your direction, not by Firelands AI.

## Children

The plugin is a tool for people who run websites. It is not directed at children and collects no data from anyone.

## Changes

Changes to this policy are recorded in this file's history in the repository.

## Contact

support@firelandsai.com
