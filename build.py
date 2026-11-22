#!/usr/bin/env python3
"""Builds the SWELTER $500 product test site: 5 pages, same product, different promise.

Run:  python3 build.py   -> writes docs/ (deploy that folder) and ads/ (ad creative HTML)
Edit VARIANTS below to change copy. Edit docs/assets/config.js for pixel id + form.
"""
import json, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "docs")
ADS = os.path.join(ROOT, "ads")

BASE_URL = "https://jamiedefiant.github.io/swelter"  # change when a custom domain is connected
PRICE = 49  # AUD, 30 sticks. Same on every page so the test reads the promise, not the price.
BUNDLES = [  # (boxes, total price, label)
    (1, 49, "1 box · 30 sticks"),
    (2, 88, "2 boxes · save 10%"),
    (3, 118, "3 boxes · save 20%"),
]

VARIANTS = [
    {
        "slug": "hydrate", "name": "SWELTER Daily", "tag": "DAILY", "line": "HYDRATION",
        "flavour": "Watermelon", "color": "#0A6CFF", "ink": "#ffffff", "bg": "#EAF3FF",
        "headline": "Built for 38° days.",
        "sub": "Zero-sugar electrolytes with 1000mg of sodium per stick. Tip it into 500ml of water and get back out there.",
        "bullets": ["1000mg sodium, 400mg potassium, 60mg magnesium", "Zero sugar, 10 calories", "Watermelon. Tastes like a drink, not a salt lick"],
        "for": ["Tradies on site in January", "Long runs before the sun's up", "Beach days and big nights"],
        "hook": "Water isn't enough when it's 38°.",
    },
    {
        "slug": "creatine", "name": "SWELTER + Creatine", "tag": "+ CREATINE", "line": "5G CREATINE",
        "flavour": "Mango", "color": "#FF4A1C", "ink": "#ffffff", "bg": "#FFF0EA",
        "headline": "Your electrolytes and your creatine. One stick.",
        "sub": "1000mg of sodium plus 5g of creatine monohydrate. Stop mixing two tubs every morning.",
        "bullets": ["5g creatine monohydrate in every stick", "1000mg sodium, 400mg potassium, zero sugar", "Mango. Dissolves clear, no gritty bottom"],
        "for": ["Gym before work", "Anyone already taking creatine", "Training through an Aussie summer"],
        "hook": "Stop mixing two tubs every morning.",
    },
    {
        "slug": "collagen", "name": "SWELTER + Collagen", "tag": "+ COLLAGEN", "line": "10G COLLAGEN",
        "flavour": "Pink Grapefruit", "color": "#F2508E", "ink": "#ffffff", "bg": "#FFEFF5",
        "headline": "The glass that does two jobs.",
        "sub": "Zero-sugar electrolytes plus 10g of marine collagen peptides. Your hydration and your collagen in one glass.",
        "bullets": ["10g marine collagen peptides per stick", "1000mg sodium, 400mg potassium, zero sugar", "Pink grapefruit. No fishy taste, ever"],
        "for": ["Already buying collagen separately", "Morning glass before coffee", "Summer, sun and salt water"],
        "hook": "Your collagen and your electrolytes, finally in one glass.",
    },
    {
        "slug": "focus", "name": "SWELTER + Caffeine", "tag": "+ CAFFEINE", "line": "100MG CAFFEINE",
        "flavour": "Lemon Lime", "color": "#B8E600", "ink": "#10210A", "bg": "#F6FFDD",
        "headline": "Swap the 3pm energy drink.",
        "sub": "Zero-sugar electrolytes plus 100mg of natural caffeine from green tea. The lift without the can of sugar.",
        "bullets": ["100mg natural caffeine from green tea", "1000mg sodium, 400mg potassium, zero sugar", "Lemon lime. Crisp, not syrupy"],
        "for": ["The 3pm slump", "Pre-training without the jitters of a pre-workout", "Hot days you still have to think on"],
        "hook": "The 3pm energy drink, minus the 50g of sugar.",
    },
    {
        "slug": "night", "name": "SWELTER Night", "tag": "NIGHT", "line": "MAGNESIUM",
        "flavour": "Mixed Berry", "color": "#5A3BD6", "ink": "#ffffff", "bg": "#EFEBFF",
        "headline": "The after-sun wind-down.",
        "sub": "Caffeine-free electrolytes with 300mg of magnesium glycinate. Made for the end of a long, hot day.",
        "bullets": ["300mg magnesium glycinate", "Electrolytes, zero sugar, zero caffeine", "Mixed berry. Easy to drink at night"],
        "for": ["After a day in the sun", "Post-training evenings", "Swapping the nightly wine"],
        "hook": "What you drink after a 38° day.",
    },
]

E = html.escape


def shade(hexcol, f):
    h = hexcol.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c * f))) for c in (r, g, b))


def mockup_svg(v, uid="m"):
    """Carton + stick pack render. Pure SVG so all five look like one real range."""
    c, ink, dark = v["color"], v["ink"], shade(v["color"], 0.72)
    return f'''<svg viewBox="0 0 600 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{E(v['name'])} box and stick pack">
<defs>
 <linearGradient id="{uid}g" x1="0" x2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#f1f1f1"/></linearGradient>
 <filter id="{uid}s" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>
</defs>
<ellipse cx="300" cy="528" rx="210" ry="26" fill="#000" opacity=".18" filter="url(#{uid}s)"/>
<polygon points="190,112 250,78 470,78 410,112" fill="{shade(c, 1.08) if v['slug']!='focus' else '#cff24d'}"/>
<polygon points="410,112 470,78 470,478 410,512" fill="{dark}"/>
<rect x="190" y="112" width="220" height="400" fill="url(#{uid}g)"/>
<rect x="190" y="112" width="220" height="118" fill="{c}"/>
<text x="300" y="170" text-anchor="middle" font-family="Archivo Black, Archivo, sans-serif" font-size="38" fill="{ink}" letter-spacing="1">SWELTER</text>
<text x="300" y="203" text-anchor="middle" font-family="Archivo, sans-serif" font-weight="700" font-size="12" fill="{ink}" letter-spacing="3">ELECTROLYTE DRINK MIX</text>
<circle cx="300" cy="290" r="34" fill="none" stroke="{c}" stroke-width="7"/>
<path d="M250 290 h-18 M368 290 h-18 M300 240 v-14 M264 254 l-10 -10 M336 254 l10 -10" stroke="{c}" stroke-width="7" stroke-linecap="round"/>
<text x="300" y="368" text-anchor="middle" font-family="Archivo Black, Archivo, sans-serif" font-size="{30 if len(v['tag'])>8 else 40}" fill="#111">{E(v['tag'])}</text>
<text x="300" y="398" text-anchor="middle" font-family="Archivo, sans-serif" font-weight="700" font-size="14" fill="#555" letter-spacing="2">{E(v['flavour'].upper())}</text>
<rect x="190" y="440" width="220" height="72" fill="{c}"/>
<text x="300" y="472" text-anchor="middle" font-family="Archivo, sans-serif" font-weight="800" font-size="14" fill="{ink}" letter-spacing="1.5">{E(v['line'])}</text>
<text x="300" y="494" text-anchor="middle" font-family="Archivo, sans-serif" font-weight="600" font-size="12" fill="{ink}" letter-spacing="1.5">30 STICKS · ZERO SUGAR</text>
<g transform="translate(-26 6) rotate(-14 150 380)">
 <rect x="112" y="250" width="72" height="270" rx="6" fill="{c}"/>
 <rect x="112" y="250" width="72" height="18" rx="4" fill="{dark}"/>
 <rect x="112" y="502" width="72" height="18" rx="4" fill="{dark}"/>
 <text x="0" y="0" transform="translate(158 386) rotate(-90)" text-anchor="middle" font-family="Archivo Black, Archivo, sans-serif" font-size="30" fill="{ink}">SWELTER</text>
 <text x="0" y="0" transform="translate(176 386) rotate(-90)" text-anchor="middle" font-family="Archivo, sans-serif" font-weight="700" font-size="10" fill="{ink}" letter-spacing="2">{E(v['tag'])}</text>
</g>
</svg>'''


def page(v):
    bundles = "".join(
        f'''<label class="bundle"><input type="radio" name="bundle" value="{n}" data-price="{p}" {"checked" if n == 1 else ""}>
<span class="b-main">{E(lbl)}</span><span class="b-price">${p}</span>{'<span class="b-flag">Most popular</span>' if n == 2 else ''}</label>'''
        for n, p, lbl in BUNDLES)
    bullets = "".join(f"<li>{E(b)}</li>" for b in v["bullets"])
    who = "".join(f"<li>{E(b)}</li>" for b in v["for"])
    return f'''<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(v['name'])} · {E(v['headline'])}</title>
<meta name="description" content="{E(v['sub'])}">
<meta property="og:title" content="{E(v['name'])}"><meta property="og:description" content="{E(v['headline'])}">
<meta property="og:image" content="{BASE_URL}/assets/{v['slug']}.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Archivo:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/style.css">
<style>:root{{--c:{v['color']};--ink:{v['ink']};--bg:{v['bg']};--dark:{shade(v['color'],0.72)}}}</style>
<script src="../assets/config.js"></script>
<script>window.VARIANT={json.dumps({"slug": v["slug"], "name": v["name"], "price": PRICE})};</script>
<script defer src="../assets/app.js"></script>
</head>
<body>
<div class="bar">Free shipping on 2+ boxes · Australia-wide</div>
<header class="top"><a class="logo" href="./">SWELTER</a><button class="cart-btn" data-open-cart aria-label="Open cart">Cart <span class="cart-count">0</span></button></header>

<main>
<section class="hero">
 <div class="hero-art">{mockup_svg(v)}</div>
 <div class="hero-copy">
  <p class="eyebrow">{E(v['name'])} · {E(v['flavour'])}</p>
  <h1>{E(v['headline'])}</h1>
  <p class="sub">{E(v['sub'])}</p>
  <ul class="ticks">{bullets}</ul>
  <form class="buy" data-buy>
   <fieldset class="bundles"><legend>Choose your pack</legend>{bundles}</fieldset>
   <div class="qty-row"><span>Quantity</span><div class="stepper"><button type="button" data-step="-1" aria-label="Less">−</button><output data-qty>1</output><button type="button" data-step="1" aria-label="More">+</button></div></div>
   <button class="cta" type="submit">Add to cart · <span data-total>${PRICE}</span></button>
   <p class="fine">30 sticks per box · 1 stick in 500ml water</p>
  </form>
 </div>
</section>

<section class="band">
 <div><b>1000mg</b><span>sodium per stick</span></div>
 <div><b>0g</b><span>sugar</span></div>
 <div><b>30</b><span>sticks a box</span></div>
 <div><b>$1.63</b><span>a glass</span></div>
</section>

<section class="two">
 <div><h2>Made for</h2><ul class="list">{who}</ul></div>
 <div><h2>How to use</h2><ol class="list"><li>Tear a stick.</li><li>Tip it into 500ml of cold water.</li><li>Shake or stir for 10 seconds.</li></ol></div>
</section>

<section class="faq">
 <h2>Questions</h2>
 <details><summary>When does it ship?</summary><p>Our first production run ships from January 2027. Order now to lock in launch pricing.</p></details>
 <details><summary>Is it really zero sugar?</summary><p>Yes. Sweetened with stevia and monk fruit. 10 calories a stick.</p></details>
 <details><summary>How much do I drink?</summary><p>One stick a day for most people. Two on very hot days or long sessions.</p></details>
 <details><summary>Can I cancel?</summary><p>Yes, any time before your order ships, no questions asked.</p></details>
</section>
</main>

<footer class="foot"><span>© 2026 SWELTER</span><a href="../privacy/">Privacy</a></footer>

<div class="sticky" data-sticky><button class="cta" data-sticky-add>Add to cart · <span data-total>${PRICE}</span></button></div>

<aside class="drawer" data-drawer aria-hidden="true">
 <div class="drawer-in">
  <div class="drawer-head"><h3>Your cart</h3><button data-close aria-label="Close">×</button></div>
  <div data-lines></div>
  <div class="drawer-foot"><div class="row"><span>Subtotal</span><b data-subtotal>$0</b></div><p class="fine" data-ship></p><button class="cta" data-checkout>Checkout</button></div>
 </div>
</aside>

<div class="modal" data-modal aria-hidden="true">
 <div class="modal-in">
  <button class="x" data-close aria-label="Close">×</button>
  <div data-step-reserve>
   <p class="eyebrow">You're early</p>
   <h3>We're not shipping yet, so we haven't charged you anything.</h3>
   <p>{E(v['name'])} launches in January. Reserve this order now and get <b>30% off</b> when it ships. We'll email you before anything is charged.</p>
   <p class="summary" data-summary></p>
   <form data-reserve><input type="email" required placeholder="Your email" autocomplete="email" aria-label="Email"><button class="cta" type="submit">Reserve my order</button></form>
   <p class="fine">We only email you about SWELTER. Unsubscribe any time.</p>
  </div>
  <div data-step-done hidden>
   <p class="eyebrow">Reserved</p>
   <h3>You're on the list.</h3>
   <p>We'll email you first when {E(v['name'])} ships, with your 30% off.</p>
  </div>
 </div>
</div>
</body>
</html>'''


def ad(v, fmt):
    w, h = (1080, 1350) if fmt == "feed" else (1080, 1920)
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Archivo:wght@500;700;800&display=swap" rel="stylesheet">
<style>
html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden}}
body{{background:{v['bg']};font-family:Archivo,sans-serif;color:#111;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
h1{{font-family:'Archivo Black';font-size:{88 if fmt=='feed' else 104}px;line-height:.98;letter-spacing:-1px;text-align:center;margin:0 70px}}
.art{{width:{820 if fmt=='feed' else 900}px;margin-top:-10px}}
.pill{{background:{v['color']};color:{v['ink']};font-weight:800;font-size:34px;padding:18px 34px;border-radius:999px;margin-top:-30px;letter-spacing:.5px}}
</style></head><body>
<h1>{E(v['hook'])}</h1>
<div class="art">{mockup_svg(v, 'a')}</div>
<div class="pill">{E(v['name'])} · ${PRICE} for 30</div>
</body></html>'''


def main():
    os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)
    os.makedirs(ADS, exist_ok=True)
    for v in VARIANTS:
        d = os.path.join(SITE, v["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(page(v))
        open(os.path.join(SITE, "assets", v["slug"] + ".svg"), "w").write(mockup_svg(v))
        for fmt in ("feed", "story"):
            open(os.path.join(ADS, f"{v['slug']}-{fmt}.html"), "w").write(ad(v, fmt))
    json.dump(VARIANTS, open(os.path.join(ROOT, "variants.json"), "w"), indent=1)
    print("built", [v["slug"] for v in VARIANTS])


if __name__ == "__main__":
    main()
