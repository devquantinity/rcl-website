# rcl-website

Website for Rhu Law Chambers, deployed on Vercel at https://rlchambers.com.my (www.rlchambers.com.my redirects there; rcl.gotka.com was the working address).

## Editing pages

`index.html`, `about-us.html`, `services.html`, `our-team.html`, `contact-us.html` and `404.html` are generated. Edit the sources in `src/`, then rebuild:

    python3 src/build.py

- `src/pages/` - page content
- `src/partials/` - header, footer and the enquiry banner shared by every page
- `src/scripts/` - each page's template scripts (leave as they are)
- `assets/rlc.css`, `assets/rlc.js` - site styles and behaviour
- The site's address is `SITE` in `src/build.py`: canonical links, share previews, the sitemap and the enquiry form's return page use it.
- Page addresses have no `.html` (`/about-us`, `/zh/about-us`): `vercel.json` turns on Vercel's clean URLs, and old `.html` links redirect. In `src/` keep linking pages as `about-us.html`; the build rewrites the links.
- To preview the built site on your Mac, run `npx serve .` in this folder (opening the files directly no longer works, because links start with `/`).
- Files in `assets/` are cached by browsers for a year. The build adds `?v=…` to every asset link, so a changed file is picked up at once. Fonts and `og-image.jpg` have plain links: give a replacement a new file name.
- `assets/base.css` is the template's stylesheet (it used to load from Webflow's CDN). The fonts are in `assets/fonts/` (licence in `OFL.txt`).
- The build also writes `sitemap.xml` and `robots.txt`. Visits are counted by Vercel Web Analytics (Analytics tab on Vercel).

## Chinese version

The build also writes a Simplified Chinese copy of every page (except 404) to `zh/`, with an EN / 中文 switch in the header and the phone menu.

- The Chinese text is in `src/i18n/zh.json`, keyed by the English text it replaces. Edit a Chinese line there and rebuild.
- If you change English copy, the build stops and lists the strings that need a Chinese version. Add them to `zh.json` and build again.
- Long Chinese headings only break at punctuation or where `zh.json` has a `<wbr />`.
- Chinese page titles and descriptions are the `zh_title` / `zh_desc` fields in `src/build.py`.

## Enquiry form

The form on `contact-us.html` is sent through Web3Forms (free plan, 250 enquiries a month), which emails each enquiry to the address set on the form in the Web3Forms dashboard (dev@quantinity.com account). The access key in the form is public by design. If Web3Forms does not answer within 12 seconds, or refuses the enquiry, the visitor is offered the same enquiry as a ready-to-send email to enquiry@rlchambers.com.my, so nothing is lost. FormSubmit, used until November 2026, went down in late October 2026.
