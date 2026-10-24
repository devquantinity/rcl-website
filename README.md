# rcl-website

Website for Rhu Law Chambers, deployed on Vercel at https://www.rlchambers.com.my (rlchambers.com.my redirects there; rcl.gotka.com was the working address).

## Editing pages

`index.html`, `about-us.html`, `services.html`, `our-team.html`, `contact-us.html` and `404.html` are generated. Edit the sources in `src/`, then rebuild:

    python3 src/build.py

- `src/pages/` - page content
- `src/partials/` - header, footer and the enquiry banner shared by every page
- `src/scripts/` - each page's template scripts (leave as they are)
- `assets/rlc.css`, `assets/rlc.js` - site styles and behaviour
- The site's address is `SITE` in `src/build.py`: canonical links, share previews and the enquiry form's return page use it.

## Chinese version

The build also writes a Simplified Chinese copy of every page (except 404) to `zh/`, with an EN / 中文 switch in the header and the phone menu.

- The Chinese text is in `src/i18n/zh.json`, keyed by the English text it replaces. Edit a Chinese line there and rebuild.
- If you change English copy, the build stops and lists the strings that need a Chinese version. Add them to `zh.json` and build again.
- Long Chinese headings only break at punctuation or where `zh.json` has a `<wbr />`.
- Chinese page titles and descriptions are the `zh_title` / `zh_desc` fields in `src/build.py`.

## Enquiry form

The form on `contact-us.html` is relayed by FormSubmit to enquiry@rlchambers.com.my. The first enquiry sent from the live site triggers an activation email to that inbox; click "Activate Form" once and later enquiries arrive normally.
