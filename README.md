# rcl-website

Website for Rhu Law Chambers, deployed on Vercel (working address: rcl.gotka.com).

## Editing pages

`index.html`, `about-us.html`, `services.html`, `our-team.html`, `contact-us.html` and `404.html` are generated. Edit the sources in `src/`, then rebuild:

    python3 src/build.py

- `src/pages/` - page content
- `src/partials/` - header, footer and the enquiry banner shared by every page
- `src/scripts/` - each page's template scripts (leave as they are)
- `assets/rlc.css`, `assets/rlc.js` - site styles and behaviour
- When the site moves to rlchambers.com.my, change `SITE` in `src/build.py` and rebuild.

## Enquiry form

The form on `contact-us.html` is relayed by FormSubmit to enquiry@rlchambers.com.my. The first enquiry sent from the live site triggers an activation email to that inbox; click "Activate Form" once and later enquiries arrive normally.
