"""Original code-native artwork and static markup for the QuackQuery interface."""
from html import escape

DUCK = """<svg viewBox="0 0 80 80" fill="none" aria-hidden="true">
<path d="M18 48c-7 0-11-5-11-5 0 18 12 28 29 28 15 0 27-8 27-21V38" fill="#F5C96B"/>
<circle cx="49" cy="31" r="18" fill="#FFE2A0"/><path d="m64 31 12 5-12 6" fill="#D97439"/>
<circle cx="54" cy="28" r="2.4" fill="#262329"/>
<path d="M27 49c0 9 10 13 20 8" stroke="#D9A34A" stroke-width="3" stroke-linecap="round"/>
<path d="m27 16 23-8 23 8-23 8-23-8Z" fill="#29262D"/>
<path d="M38 20v8c8 4 16 4 24 0v-8" fill="#39333E"/>
<path d="M72 17v14" stroke="#A32638" stroke-width="3" stroke-linecap="round"/>
</svg>"""

CAMPUS = """<svg class="campus-art" viewBox="0 0 540 330" fill="none" aria-hidden="true">
<defs><linearGradient id="campus-sky" x1="40" y1="0" x2="440" y2="330" gradientUnits="userSpaceOnUse"><stop stop-color="#F9EBE7"/><stop offset="1" stop-color="#E9D5CF"/></linearGradient>
<linearGradient id="campus-water" x1="0" y1="270" x2="540" y2="330" gradientUnits="userSpaceOnUse"><stop stop-color="#D9B7B1"/><stop offset="1" stop-color="#EEE2DD"/></linearGradient></defs>
<rect width="540" height="330" rx="24" fill="url(#campus-sky)"/>
<circle cx="420" cy="76" r="42" fill="#FFF8EC" opacity=".85"/>
<g fill="#B8918E" opacity=".4"><path d="M327 204V122h23v82M355 204V101h22v103M383 204V138h21v66M411 204V113h28v91M446 204V145h24v59M478 204V130h31v74"/><path d="M366 101V78h2v23M422 113V91h2v22"/></g>
<path d="M0 233c102-32 188-18 271-14s180-22 269-5v116H0V233Z" fill="url(#campus-water)"/>
<g stroke="#FDF5EF" stroke-width="2" opacity=".65"><path d="M311 251h131M350 270h160M280 293h117M407 308h100"/></g>
<path d="M0 237c102-21 176-10 260-6l20 26H0v-20Z" fill="#A09A83"/><path d="M15 235h244l17 14H0l15-14Z" fill="#D8C8AD"/>
<g stroke="#66333A" stroke-linejoin="round"><path d="M58 223V126h132v97" fill="#A4535B" stroke-width="2"/>
<path d="m48 126 76-45 76 45H48Z" fill="#68353E" stroke-width="2"/>
<path d="M113 220V86h45v134" fill="#B96A6C" stroke-width="2"/>
<path d="m107 88 29-36 29 36h-58Z" fill="#6C3740" stroke-width="2"/>
<path d="M126 55V36h19v19" fill="#AD6265" stroke-width="2"/><path d="M119 37h33l-16-21-17 21Z" fill="#68353E"/>
<path d="M185 222v-70h51v70" fill="#B76668" stroke-width="2"/><path d="m179 152 31-22 32 22h-63Z" fill="#733C44" stroke-width="2"/></g>
<g fill="#FFE8B6" stroke="#693C42" stroke-width="2"><path d="M128 113v-9a8 8 0 0 1 16 0v9h-16ZM128 143v-9a8 8 0 0 1 16 0v9h-16ZM128 173v-9a8 8 0 0 1 16 0v9h-16Z"/>
<path d="M73 153v-8a7 7 0 0 1 14 0v8H73ZM95 153v-8a7 7 0 0 1 14 0v8H95ZM73 185v-8a7 7 0 0 1 14 0v8H73ZM95 185v-8a7 7 0 0 1 14 0v8H95ZM167 153v-8a7 7 0 0 1 14 0v8h-14ZM167 185v-8a7 7 0 0 1 14 0v8h-14ZM201 180v-8a8 8 0 0 1 16 0v8h-16Z"/></g>
<path d="M126 223v-19a10 10 0 0 1 20 0v19" fill="#542F36"/><path d="M49 226h195" stroke="#6C4143" stroke-width="5" stroke-linecap="round"/>
<g fill="#68715C"><circle cx="29" cy="191" r="18"/><circle cx="43" cy="207" r="17"/><circle cx="262" cy="199" r="22"/><circle cx="277" cy="215" r="17"/></g>
<g stroke="#626553" stroke-width="4"><path d="M29 200v35M264 205v30"/></g>
<path d="m297 125 11-5 11 5M323 145l8-4 8 4" stroke="#8E6869" stroke-width="2" stroke-linecap="round"/>
</svg>"""

CORPUS_LABELS = {"synthetic": "Synthetic demo", "unverified": "Original documents", "verified": "Reviewed university sources"}


def brand_markup():
    return f'<div class="qq-brand"><span class="brand-duck">{DUCK}</span><div>QuackQuery<span>YOUR CAMPUS. CONNECTED.</span></div></div>'


def hero_markup(corpus, compact=False):
    label = escape(CORPUS_LABELS.get(corpus, corpus))
    if compact:
        return f'<div class="workspace-bar"><div><span class="eyebrow">THE QUACKQUERY WORKSPACE</span><h1>Ask. Discover. Understand.</h1></div><span class="corpus-chip"><i></i>{label}</span></div>'
    return f'''<div class="mobile-wordmark">QuackQuery<span>YOUR CAMPUS. CONNECTED.</span></div><section class="qq-hero">
<div class="hero-copy"><div class="hero-kicker"><span></span> BUILT FOR CURIOUS MINDS</div>
<h1>Your campus.<br>Your questions.<br><em>A clearer answer.</em></h1>
<p>From admissions to your next semester. Explore university documents with an AI study companion that brings the evidence with it.</p>
<div class="hero-tags"><span>⌕ &nbsp; Search by meaning</span><span>↗ &nbsp; Explore the evidence</span></div></div>
<div class="hero-visual"><div class="art-orbit"></div><div class="campus-frame">{CAMPUS}<span class="art-caption">HOBOKEN-INSPIRED · AN ORIGINAL ILLUSTRATION</span></div>
<div class="floating-note"><span class="note-icon">↗</span><div>Less searching.<strong>More discovering.</strong></div></div>
<div class="duck-sticker">{DUCK}</div></div></section>
<div class="workspace-status"><span class="corpus-chip"><i></i>{label}</span><span>University document intelligence <b> / </b> Evidence you can explore</span></div>'''


EMPTY_MARKUP = '<div class="start-heading"><span class="eyebrow">A GOOD QUESTION IS A GREAT START</span><h2>What’s on your mind?</h2><p>Try a starting point below, or write your own question.</p></div>'
FOOTER_MARKUP = '<div class="qq-footer"><span>QUACKQUERY <b> / </b> A LITTLE CURIOSITY GOES A LONG WAY.</span><span>Independent portfolio project · Not affiliated with Stevens</span></div>'
