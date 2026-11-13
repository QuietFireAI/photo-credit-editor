# Sample site

A three-picture website for trying the Photo Credit Editor and for checking changes to it. Each picture is in a different state on purpose:

| Picture | State | Why |
| --- | --- | --- |
| Hills at midday | Complete | Credit, source, license and link are all recorded |
| Hills at dusk | Credited but incomplete | It has a credit but no license or permission |
| Hills under a teal sky | No credit | The credit is blank, but the picture file carries an author and a copyright line inside it |

The three pictures were made for this example and are covered by the repository's MIT License. "Pat Example" is a made-up name stored in the third picture to show how leads work.

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

The scan reports 3 pictures found: 1 complete, 1 credited but incomplete, and 1 with no credit. For the last one it lists the author and copyright stored inside the file and the alt text from the page.

## Try the editor

Open `skills/photo-credits/assets/photo-credits-editor.html` in a browser, click **Choose site folder**, and pick this folder. The third picture shows a "Leads for this picture" box with the author stored in the file and a **Use as credit** button.

## Try it with Claude

With the plugin installed and this folder available to Claude, try:

1. "Which pictures in examples/sample-site still need a proper credit, and what can you find out about them?"
2. "Pat Example took the teal picture and said we can use it. The dusk picture is our own work."
3. "Check the photo credits in examples/sample-site before launch."

Expected: Claude reports one incomplete and one uncredited picture, shows the author it found inside the teal picture and asks you to confirm it, writes only what you confirm, and the last check then passes.
