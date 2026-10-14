# Redline & Rotors

A minimalist independent automotive and watch journal. Free hosting with GitHub Pages, mobile-friendly editing with Pages CMS.

## Initial setup (one time)

1. Create a free GitHub account at https://github.com and create a **public** repository named `redline-rotors` (or another name).
2. Upload **all files and folders from this ZIP**, including hidden `.pages.yml` and `.github/`. GitHub's browser uploader can accept files, but uploading nested folders from an iPhone is cumbersome; using a computer for the one-time upload is easier. You can also use a GitHub repository import tool if available.
3. In repository **Settings → Pages → Build and deployment**, select **GitHub Actions**.
4. Open **Actions** and allow workflows if GitHub asks. The `Publish Redline & Rotors` workflow builds and deploys the site automatically when changes are saved to `main`.
5. Visit `https://YOUR-USERNAME.github.io/redline-rotors/` only if using a project repository — NOTE: this site's internal links assume the domain root, so **recommended:** name your repository `YOUR-USERNAME.github.io` instead. Then the website is `https://YOUR-USERNAME.github.io/` and all links work immediately. Alternatively, use a custom domain and update your Pages settings.
6. Open https://app.pagescms.org/, sign in with GitHub, grant access to your repository, and open it. The Articles and Homepage settings editors should appear.
7. On iPhone, use Pages CMS in Safari to upload images, edit homepage and publish stories. Saving creates a GitHub commit and triggers automatic redeployment (usually a few minutes).

**Important:** GitHub Pages sites from public repositories are publicly accessible. Don't upload private images or unpublished personal information. GitHub repository storage and GitHub Pages usage limits apply. Uploaded images count toward your repository size. Compress photos before uploading, preferably to JPG/WebP at about 1600–2000 px wide.

## Content management

- **Articles:** Title, date, category, summary, cover image, publish toggle, rich-text body.
- **Homepage settings:** headline, introductory text, hero image, feature text, feature link.
- **About:** editable rich-text page.

## Design

Warm off-white paper, ink-black typography, muted red accents, bold editorial hierarchy, responsive photo-led layouts. Placeholder panels deliberately contain **no stock or AI-generated car photos**. Add your own images through the editor.

## Local preview / build

```bash
pip install -r requirements.txt
python build.py
python -m http.server 8000 --directory _site
```

For local preview, root-relative links work when served from the local server root.
