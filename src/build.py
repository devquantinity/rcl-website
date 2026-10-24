#!/usr/bin/env python3
"""Builds the Rhu Law Chambers pages from src/ into the site root.

Edit the files in src/pages and src/partials, then run:  python3 src/build.py

Every page is also built in Simplified Chinese into zh/. The Chinese text lives in
src/i18n/zh.json, keyed by the English text it replaces. If you change English copy,
the build lists the strings that need a Chinese version: add them to zh.json and build again.
"""
import html
import json
import os
import re
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(SRC, 'i18n'))
import segment  # noqa: E402

# The live address. rlchambers.com.my redirects here (set in Vercel), and so can rcl.gotka.com.
SITE = 'https://www.rlchambers.com.my'

TEMPLATE_CSS = ('<link crossorigin="anonymous" href="https://cdn.prod.website-files.com/69e49a695752288e8bdbb47e/css/'
                'juristiq-wcopilot.webflow.shared.4d9dc6430.css" integrity="sha384-TZ3GQw0qtkh9JnL83zpq0rNdgUbtZV68RRm'
                'zJrCJWegWSWPCCiVbKJ/SxBXTSCxv" rel="stylesheet" type="text/css" />')
FONT_FAMILIES = {
    'en': 'family=Playfair+Display:wght@400..700&amp;family=Roboto:wght@300..700',
    # Chinese headings get a matching serif; Chinese body text uses the system's own font (see rlc.css)
    'zh': 'family=Noto+Serif+SC:wght@400..700&amp;family=Playfair+Display:wght@400..700&amp;family=Roboto:wght@300..700',
}
DESCRIPTION = ('Rhu Law Chambers is a boutique law firm in Kuala Lumpur providing practical and commercially '
               'focused legal solutions to businesses, entrepreneurs, investors and cross-border clients.')
ZH_DESCRIPTION = ('Rhu Law Chambers 是一家立足吉隆坡的精品律师事务所，为企业、创业者、投资者及跨境客户提供务实且注重'
                  '商业实效的法律解决方案。')

PAGES = [
    dict(out='index.html', wf='69e49a695752288e8bdbb469', scripts='index.html', path='', cta=True,
         title='Rhu Law Chambers | Boutique Law Firm in Kuala Lumpur', desc=DESCRIPTION,
         zh_title='Rhu Law Chambers | 吉隆坡精品律师事务所', zh_desc=ZH_DESCRIPTION),
    dict(out='about-us.html', wf='69e49a695752288e8bdbb46a', scripts='about-us.html', path='about-us.html', cta=True,
         title='Our Vision & Purpose | Rhu Law Chambers',
         desc='Growing businesses, building relationships and creating lasting impact: the four purposes that guide '
              'Rhu Law Chambers, a boutique law firm in Kuala Lumpur.',
         zh_title='愿景与使命 | Rhu Law Chambers',
         zh_desc='助力企业成长、建立长久关系、创造深远影响：指引吉隆坡精品律师事务所 Rhu Law Chambers 的四大使命。'),
    dict(out='services.html', wf='69e49a695752288e8bdbb46b', scripts='services.html', path='services.html', cta=True,
         title='Areas of Expertise | Rhu Law Chambers',
         desc='Corporate and commercial matters, business structuring, investments, cross-border transactions, '
              'commercial agreements and dispute resolution. See all 17 areas of expertise.',
         zh_title='专业领域 | Rhu Law Chambers',
         zh_desc='公司及商业事务、业务架构、投资、跨境交易、商业协议及争议解决。查看全部 17 个专业领域。'),
    dict(out='our-team.html', wf='69e49a695752288e8bdbb46f', scripts='our-team.html', path='our-team.html', cta=True,
         title='Our Team | Rhu Law Chambers',
         desc='Meet the partners and consultants of Rhu Law Chambers, bringing legal, commercial and cross-border '
              'experience from Malaysia, Taiwan, Thailand and the United Kingdom.',
         zh_title='我们的团队 | Rhu Law Chambers',
         zh_desc='认识 Rhu Law Chambers 的合伙人与顾问。他们来自马来西亚、台湾、泰国及英国，为每一项事务带来法律、商业与跨境经验。'),
    dict(out='contact-us.html', wf='69e49a695752288e8bdbb473', scripts='contact-us.html', path='contact-us.html', cta=False,
         title='Make an Enquiry | Rhu Law Chambers',
         desc='Contact Rhu Law Chambers in Mid Valley City, Kuala Lumpur. Email enquiry@rlchambers.com.my or call '
              '+60 10-837 7531.',
         zh_title='立即咨询 | Rhu Law Chambers',
         zh_desc='联系位于吉隆坡谷中城的 Rhu Law Chambers。电邮 enquiry@rlchambers.com.my，或致电 +60 10-837 7531。'),
    # English only: a missing page anywhere on the site is answered with this one
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
    'telephone': '+60 10-837 7531',
    'address': {
        '@type': 'PostalAddress',
        'streetAddress': 'Level 27, Penthouse, Centrepoint North Tower, Lingkaran Syed Putra, Mid Valley City',
        'addressLocality': 'Kuala Lumpur',
        'postalCode': '59200',
        'addressCountry': 'MY',
    },
    'areaServed': 'Malaysia',
}

GLOBE = ('<svg aria-hidden="true" class="rlc-lang-icon" fill="none" height="16" stroke="currentColor" '
         'stroke-width="1.5" viewBox="0 0 24 24" width="16"><circle cx="12" cy="12" r="9" />'
         '<path d="M3 12h18M12 3c2.4 2.5 3.6 5.5 3.6 9s-1.2 6.5-3.6 9c-2.4-2.5-3.6-5.5-3.6-9s1.2-6.5 3.6-9z" /></svg>')

with open(os.path.join(SRC, 'i18n', 'zh.json'), encoding='utf-8') as _fh:
    ZH = json.load(_fh)
MISSING = {}
USED = set()


def read(*parts):
    with open(os.path.join(SRC, *parts), encoding='utf-8') as fh:
        return fh.read()


def lang_switch(page, lang, menu=False):
    """The EN / 中文 link (in the header, or in the phone menu), pointing at the same page in the other language."""
    target = page['out'] if page['path'] is not None else 'index.html'
    if lang == 'en':
        href, code, title, label = f'zh/{target}', 'zh-Hans', '阅读中文版', '中文'
    else:
        href, code, title, label = f'../{target}', 'en', 'Read this page in English', 'English' if menu else 'EN'
    css = 'rlc-menu-lang' if menu else 'rlc-lang'
    return f'<a class="{css}" href="{href}" hreflang="{code}" lang="{code}" title="{title}">{GLOBE}<span>{label}</span></a>'


def build(page, lang='en'):
    zh = lang == 'zh'
    esc = lambda s: html.escape(s, quote=True)
    title = esc(page['zh_title'] if zh else page['title'])
    desc = esc(page['zh_desc'] if zh else page['desc'])
    meta = [
        '<meta charset="utf-8" />',
        '<meta content="width=device-width, initial-scale=1" name="viewport" />',
        f'<title>{title}</title>',
        f'<meta content="{desc}" name="description" />',
    ]
    if page['path'] is None:
        meta.append('<meta content="noindex" name="robots" />')
    else:
        en_url, zh_url = f"{SITE}/{page['path']}", f"{SITE}/zh/{page['path']}"
        url = zh_url if zh else en_url
        meta += [
            f'<link href="{url}" rel="canonical" />',
            f'<meta content="{url}" property="og:url" />',
            f'<link href="{en_url}" hreflang="en" rel="alternate" />',
            f'<link href="{zh_url}" hreflang="zh-Hans" rel="alternate" />',
            f'<link href="{en_url}" hreflang="x-default" rel="alternate" />',
        ]
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
        meta.append('<link as="image" fetchpriority="high" href="assets/hero-city.jpg" imagesizes="(max-width: 479px) 100vw, 75vw" imagesrcset="assets/hero-city-960.jpg 960w, assets/hero-city.jpg 1920w" rel="preload" />')
    ld = dict(JSON_LD, description=ZH_DESCRIPTION, url=SITE + '/zh/') if zh else JSON_LD
    meta += [
        TEMPLATE_CSS,
        f'<link href="https://fonts.googleapis.com/css2?{FONT_FAMILIES[lang]}&amp;display=swap" rel="stylesheet" />',
        '<link href="assets/rlc.css" rel="stylesheet" />',
        '<script>!function(o,c){var n=c.documentElement,t=" w-mod-";n.className+=t+"js",("ontouchstart"in o'
        '||o.DocumentTouch&&c instanceof DocumentTouch)&&(n.className+=t+"touch")}(window,document);</script>',
        '<link href="assets/rlc-mark.png" rel="icon" type="image/png" />',
        '<link href="assets/rlc-mark.png" rel="apple-touch-icon" />',
        '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>',
    ]

    nav = read('partials', 'nav.html')
    nav = re.sub(r'\{\{cur:([^}]+)\}\}',
                 lambda m: ' w--current" aria-current="page' if m.group(1) == page['out'] else '', nav)
    body = read('pages', page['out'])
    body = body.replace('{{cta}}', read('partials', 'cta.html') if page['cta'] else '')
    content = '\n'.join([nav.rstrip(), body.rstrip(), read('partials', 'footer.html').rstrip()])
    if zh:
        # links back into the site from the form relay stay on the Chinese pages
        content = re.sub(r'\{\{site\}\}/(?=[\w-]+\.html)', '{{site}}/zh/', content)
        content = content.replace('name="_subject" type="hidden" value="Website enquiry"',
                                  'name="_subject" type="hidden" value="Website enquiry (Chinese site)"')
        # the embedded map shows its own labels in Chinese too
        content = content.replace('&amp;output=embed"', '&amp;output=embed&amp;hl=zh-CN"')
        USED.update(segment.strings(content))
        missing = []
        content = segment.translate(content, ZH, missing)
        if missing:
            MISSING[page['out']] = missing
    content = content.replace('<!--rlc-lang-->', lang_switch(page, lang))
    content = content.replace('<!--rlc-lang-menu-->', lang_switch(page, lang, menu=True))

    doc = '\n'.join([
        '<!doctype html>',
        f'<html data-wf-domain="www.rlchambers.com.my" data-wf-page="{page["wf"]}" data-wf-site="69e49a695752288e8bdbb47e" '
        f'lang="{"zh-Hans" if zh else "en"}">',
        '<head>',
        '\n'.join(meta),
        '</head>',
        '<body>',
        content,
        read('scripts', page['scripts']).rstrip(),
        '<script src="assets/rlc.js"></script>',
        '</body>',
        '</html>',
        '',
    ])
    doc = doc.replace('{{site}}', SITE)
    if zh:
        # the Chinese pages sit one folder down; page links stay relative so they stay in Chinese
        doc = re.sub(r'(?<=[\s"\'(,])assets/', '../assets/', doc)
    if page['path'] is None:
        # 404.html is served for any missing path, so make every local URL root-relative.
        doc = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|#|/|data:)([^"]+)"', r'\1="/\2"', doc)
    leftover = re.findall(r'\{\{[^}]*\}\}', doc)
    assert not leftover, (page['out'], leftover)
    out_dir = os.path.join(ROOT, 'zh') if zh else ROOT
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, page['out']), 'w', encoding='utf-8') as fh:
        fh.write(doc)
    return len(doc)


if __name__ == '__main__':
    for p in PAGES:
        print(f"{p['out']:<19} {build(p):>7,} bytes")
    for p in PAGES:
        if p['path'] is not None:
            print(f"{'zh/' + p['out']:<19} {build(p, 'zh'):>7,} bytes")
    unused = [k for k in ZH if k not in USED]
    if unused:
        print(f'\n{len(unused)} entries in src/i18n/zh.json are no longer used on any page:')
        for k in unused:
            print('  -', k[:100])
    if MISSING:
        print('\nMissing Chinese translations. Add these English strings to src/i18n/zh.json, then build again:')
        for out, keys in MISSING.items():
            for k in dict.fromkeys(keys):
                print(f'  [{out}] {k}')
        sys.exit(1)
