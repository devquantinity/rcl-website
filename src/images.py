# Derived images for the site: team avatars, a tighter portrait crop, social preview.
from PIL import Image
import os
A = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')

# Seow Swang's portrait is full-length; crop to waist-up so it matches the others.
im = Image.open(f'{A}/team-seow-swang.jpg').convert('RGB')
im.crop((117, 0, 783, 833)).resize((720, 900), Image.LANCZOS).save(
    f'{A}/team-seow-swang-crop.jpg', quality=86, optimize=True, progressive=True)

# Square avatars centred on each face (face centre x, y, crop side) in 900x1125 coords.
spec = {'wen-rhu': (420, 265, 400), 'alexandra-yi': (462, 300, 420), 'seow-swang': (450, 215, 300),
        'june-lu': (450, 300, 420), 'shew-mee-ling': (392, 255, 410), 'teh-ping-ying': (478, 265, 410)}
for n, (cx, cy, s) in spec.items():
    im = Image.open(f'{A}/team-{n}.jpg').convert('RGB')
    x0 = max(0, cx - s // 2); y0 = max(0, cy - int(s * 0.45))
    im.crop((x0, y0, x0 + s, y0 + s)).resize((200, 200), Image.LANCZOS).save(
        f'{A}/avatar-{n}.jpg', quality=86, optimize=True)

# 1200x630 social preview: KL skyline, navy fade on the left, white logo.
W, H = 1200, 630
hero = Image.open(f'{A}/hero-kl.jpg').convert('RGB')
ww = int(1080 * W / H); x0 = hero.size[0] - ww
bg = hero.crop((x0, 0, x0 + ww, 1080)).resize((W, H), Image.LANCZOS)
mask = Image.new('L', (W, 1))
for x in range(W):
    t = x / W
    a = 1.0 if t < 0.30 else max(0.0, 1 - (t - 0.30) / 0.42)
    mask.putpixel((x, 0), int(255 * min(1, a * 0.97)))
bg = Image.composite(Image.new('RGB', (W, H), (42, 65, 115)), bg, mask.resize((W, H)))
logo = Image.open(f'{A}/rlc-logo-white.png').convert('RGBA')
lw = 560; lh = int(logo.size[1] * lw / logo.size[0])
logo = logo.resize((lw, lh), Image.LANCZOS)
bg = bg.convert('RGBA'); bg.alpha_composite(logo, (70, (H - lh) // 2))
bg.convert('RGB').save(f'{A}/og-image.jpg', quality=84, optimize=True, progressive=True)
print('done')
