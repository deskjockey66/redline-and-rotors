# Redline & Rotors

First-person automotive and watch ownership journal. Hosted free on GitHub Pages at https://deskjockey66.github.io/redline-and-rotors/.

## Publish from an iPhone

Open https://app.pagescms.org/ in Safari, sign in with GitHub and authorize this repository once. Select `deskjockey66/redline-and-rotors`, branch `main`. Articles has a visual editor and photograph picker; Homepage controls the cover. Save to commit changes and trigger the existing GitHub Pages workflow. Turn off “Publish this article” to keep a draft out of the site. Upload photographs you own or have permission to use and fill in the photographer/licence credit.

## Development

Install `requirements.txt`, then run `python build.py`. Output is `_site`. `SITE_BASE_PATH` defaults to `/redline-and-rotors`; set it to an empty string for a local root preview or a custom domain. The GitHub Actions publishing workflow is preserved.

Photo sources and licences are documented in `content/credits.md`, published at `/credits/`. Included editorial pieces are design appreciations, not claimed road tests or ownership experiences.

<!-- Latest Pages CMS content: deploy from main. -->
