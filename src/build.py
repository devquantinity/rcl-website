#!/usr/bin/env python3
"""Builds the Rhu Law Chambers pages from src/ into the site root.

Edit the files in src/pages and src/partials, then run:  python3 src/build.py
"""
import html
import json
import os
import re

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)

# Change to https://rlchambers.com.my when the domain is switched over.
SITE = 'https://rcl.gotka.com'

TEMPLATE_CSS = ('<link crossorigin="anonymous" href="https://cdn.prod.website-files.com/69e49a695752288e8bdbb47e/css/'
                'juristiq-wcopilot.webflow.shared.4d9dc6430.css" integrity="sha384-TZ3GQw0qtkh9JnL83zpq0rNdgUbtZV68RRm'
                'zJrCJWegWSWPCCiVbKJ/SxBXTSCxv" rel="stylesheet" type="text/css" />')
FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400..700&amp;'
         'family=Roboto:wght@300..700&amp;display=swap" rel="stylesheet" />')
DESCRIPTION = ('Rhu Law Chambers is a boutique law firm in Kuala Lumpur providing practical and commercially '
               'focused legal solutions to businesses, entrepreneurs, investors and cross-border clients.')

PAGES = [
    dict(out='index.html', wf='69e49a695752288e8bdbb469', scripts='index.html', path='', cta=True,
         title='Rhu Law Chambers | Boutique Law Firm in Kuala Lumpur', desc=DESCRIPTION),
    dict(out='about-us.html', wf='69e49a695752288e8bdbb46a', scripts='about-us.html', path='about-us.html', cta=True,
         title='Our Vision & Purpose | Rhu Law Chambers',
         desc='Growing businesses, building relationships and creating lasting impact: the four purposes that guide '
              'Rhu Law Chambers, a boutique law firm in Kuala Lumpur.'),
    dict(out='services.html', wf='69e49a695752288e8bdbb46b', scripts='services.html', path='services.html', cta=True,
         title='Areas of Expertise | Rhu Law Chambers',
         desc='Corporate and commercial matters, business structuring, investments, cross-border transactions, '
              'commercial agreements and dispute resolution. See all 17 areas of expertise.'),
    dict(out='our-team.html', wf='69e49a695752288e8bdbb46f', scripts='our-team.html', path='our-team.html', cta=True,
         title='Our Team | Rhu Law Chambers',
         desc='Meet the partners and consultants of Rhu Law Chambers, bringing legal, commercial and cross-border '
              'experience from Malaysia, Taiwan and the United Kingdom.'),
    dict(out='contact-us.html', wf='69e49a695752288e8bdbb473', scripts='contact-us.html', path='contact-us.html', cta=False,
         title='Make an Enquiry | Rhu Law Chambers',
         desc='Contact Rhu Law Chambers in Mid Valley City, Kuala Lumpur. Email enquiry@rlchambers.com.my or call '
              '+60 12-399 1241.'),
    dict(out='404.html', wf='69e49a695752288e8bdbb469', scripts='index.html', path=None, cta=False,
         title='Page Not Found | Rhu Law Chambers', desc=DESCRIPTION),
]

JSON_LD = {
    '@context': 'https://schema.org',
    '@type': 'LegalService',
    'name': 'Rhu Law Chambers',
    'alternateName': 'RLC',
    'description': DESCRIPTION,
    'url': SITE + '/',
    'logo': SITE + '/assets/rlc-logo-navy.png',
    'image': SITE + '/assets/og-image.jpg',
    'email': 'enquiry@rlchambers.com.my',
    'telephone': '+60 12-399 1241',
    'address': {
        '@type': 'PostalAddress',
        'streetAddress': 'Level 27, Penthouse, Centrepoint North Tower, Lingkaran Syed Putra, Mid Valley City',
        'addressLocality': 'Kuala Lumpur',
        'postalCode': '59200',
        'addressCountry': 'MY',
    },
    'areaServed': 'Malaysia',
}


def read(*parts):
    with open(os.path.join(SRC, *parts), encoding='utf-8') as fh:
        return fh.read()


def build(page):
    esc = lambda s: html.escape(s, quote=True)
    title, desc = esc(page['title']), esc(page['desc'])
    meta = [
        '<meta charset="utf-8" />',
        '<meta content="width=device-width, initial-scale=1" name="viewport" />',
        f'<title>{title}</title>',
        f'<meta content="{desc}" name="description" />',
    ]
    if page['path'] is None:
        meta.append('<meta content="noindex" name="robots" />')
    else:
        url = f"{SITE}/{page['path']}"
        meta += [f'<link href="{url}" rel="canonical" />', f'<meta content="{url}" property="og:url" />']
    meta += [
        f'<meta content="{title}" property="og:title" />',
        f'<meta content="{desc}" property="og:description" />',
        f'<meta content="{SITE}/assets/og-image.jpg" property="og:image" />',
        '<meta content="1200" property="og:image:width" />',
        '<meta content="630" property="og:image:height" />',
        '<meta content="Rhu Law Chambers" property="og:site_name" />',
        '<meta content="website" property="og:type" />',
        '<meta content="summary_large_image" name="twitter:card" />',
        f'<meta content="{title}" name="twitter:title" />',
        f'<meta content="{desc}" name="twitter:description" />',
        f'<meta content="{SITE}/assets/og-image.jpg" name="twitter:image" />',
        '<meta content="#2a4173" name="theme-color" />',
        '<link crossorigin="anonymous" href="https://cdn.prod.website-files.com" rel="preconnect" />',
        '<link href="https://fonts.googleapis.com" rel="preconnect" />',
        '<link crossorigin="anonymous" href="https://fonts.gstatic.com" rel="preconnect" />',
    ]
    if page['out'] == 'index.html':
        meta.append('<link as="image" fetchpriority="high" href="assets/hero-kl.jpg" imagesizes="(max-width: 479px) 100vw, 75vw" imagesrcset="assets/hero-kl-960.jpg 960w, assets/hero-kl.jpg 1920w" rel="preload" />')
    meta += [
        TEMPLATE_CSS,
        FONTS,
        '<link href="assets/rlc.css" rel="stylesheet" />',
        '<script>!function(o,c){var n=c.documentElement,t=" w-mod-";n.className+=t+"js",("ontouchstart"in o'
        '||o.DocumentTouch&&c instanceof DocumentTouch)&&(n.className+=t+"touch")}(window,document);</script>',
        '<link href="assets/rlc-mark.png" rel="icon" type="image/png" />',
        '<link href="assets/rlc-mark.png" rel="apple-touch-icon" />',
        '<script type="application/ld+json">' + json.dumps(JSON_LD, ensure_ascii=False) + '</script>',
    ]

    nav = read('partials', 'nav.html')
    nav = re.sub(r'\{\{cur:([^}]+)\}\}',
                 lambda m: ' w--current" aria-current="page' if m.group(1) == page['out'] else '', nav)
    body = read('pages', page['out'])
    body = body.replace('{{cta}}', read('partials', 'cta.html') if page['cta'] else '')

    doc = '\n'.join([
        '<!doctype html>',
        f'<html data-wf-domain="rcl.gotka.com" data-wf-page="{page["wf"]}" data-wf-site="69e49a695752288e8bdbb47e" lang="en">',
        '<head>',
        '\n'.join(meta),
        '</head>',
        '<body>',
        nav.rstrip(),
        body.rstrip(),
        read('partials', 'footer.html').rstrip(),
        read('scripts', page['scripts']).rstrip(),
        '<script src="assets/rlc.js"></script>',
        '</body>',
        '</html>',
        '',
    ])
    doc = doc.replace('{{site}}', SITE)
    if page['path'] is None:
        # 404.html is served for any missing path, so make every local URL root-relative.
        doc = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|#|/|data:)([^"]+)"', r'\1="/\2"', doc)
    leftover = re.findall(r'\{\{[^}]*\}\}', doc)
    assert not leftover, (page['out'], leftover)
    with open(os.path.join(ROOT, page['out']), 'w', encoding='utf-8') as fh:
        fh.write(doc)
    return len(doc)


if __name__ == '__main__':
    for p in PAGES:
        print(f"{p['out']:<16} {build(p):>7,} bytes")
