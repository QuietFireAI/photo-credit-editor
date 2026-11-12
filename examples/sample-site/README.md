# Sample site

A three-picture website for trying the Photo Credits plugin and for checking changes to it. Two pictures have a credit. One, the town-park picture, is deliberately blank.

The three pictures were made for this example and are covered by the repository's MIT License.

## See it in a browser

From the top folder of the repository:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/examples/sample-site/`. The slideshow shows a credit caption for each slide, the first picture below it has a credit line, the second has none, and the credits page lists two pictures.

## Scan it

```bash
python3 skills/photo-credits/scripts/scan_photos.py examples/sample-site
```

The scan reports 3 pictures found, 2 credited, and 1 listed with the credit still blank.

## Try it with Claude

With the plugin installed and this folder available to Claude, try:

1. "Which pictures in examples/sample-site have no photo credit?"
2. "The town-park picture was taken by Pat Example and is used with permission. Add that credit."
3. "Check the photo credits in examples/sample-site before launch."

Expected: Claude names the town-park picture as the one blank picture, writes only the credit you gave it, and the last check then passes.
