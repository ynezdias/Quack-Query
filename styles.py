"""Responsive crimson campus identity using Streamlit's existing components."""

STYLES = """
<style>
:root { --accent: #a32638; --accent-dark: #801b2c; --text: #29252b; --muted: #6e6267; --border: #e6dbd8; --panel: #fff; }
html, body, [data-testid="stAppViewContainer"] { font-family: "Segoe UI", system-ui, -apple-system, sans-serif; color: var(--text); }
[data-testid="stAppViewContainer"] {
    background-color: #faf7f4;
    background-image: radial-gradient(ellipse at 95% 4%, #ecd0ce88, transparent 45%), radial-gradient(ellipse at 8% 90%, #f1e3d680, transparent 45%), radial-gradient(#a326380b .7px, transparent .7px);
    background-size: auto, auto, 18px 18px; background-attachment: fixed;
}
#MainMenu, footer { display: none; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { visibility: hidden; }
[data-testid="stExpandSidebarButton"] { visibility: visible; color: var(--accent); border-radius: 10px; background: #fff9; backdrop-filter: blur(12px); }
[data-testid="stMainBlockContainer"], [data-testid="stBottomBlockContainer"] { max-width: 1180px; margin-inline: auto; padding-inline: 48px; }
.stMain { overflow-anchor: none; }
[data-testid="stMainBlockContainer"] { padding-top: 48px; padding-bottom: 36px; }
[data-testid="stVerticalBlock"] { gap: 18px; }
[data-testid="stMarkdownContainer"] p { line-height: 1.7; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: var(--muted); line-height: 1.65; opacity: 1; }
h1, h2, h3 { letter-spacing: -.045em; color: var(--text); }
button, [data-testid="stWidgetLabel"] { font-weight: 600; }
.qq-brand { display: flex; align-items: center; gap: 12px; color: #fff; font-size: 25px; font-weight: 750; letter-spacing: -.8px; margin-bottom: 30px; }
.mobile-wordmark { display: none; }
.brand-duck { width: 48px; height: 48px; flex-shrink: 0; background: #ffffff09; border: 1px solid #ffffff16; border-radius: 14px; padding: 4px; }
.qq-brand span:not(.brand-duck) { display: block; color: #c7afb2; font-size: 8px; letter-spacing: 1.8px; margin-top: 5px; }
.brand-duck svg { width: 100%; height: 100%; }
.sidebar-label { font-size: 10px; letter-spacing: 2px; font-weight: 700; color: #c5acb0; margin-top: 18px; }
[data-testid="stSidebar"] { background: radial-gradient(ellipse at 0% 0%, #772c3e55, transparent 55%), linear-gradient(165deg, #272126, #19171b); border-right: 1px solid #51323c; color: #f6ecef; }
[data-testid="stSidebarUserContent"] { padding: 30px 22px; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"], [data-testid="stSidebar"] h3 { color: #f8edf0; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"], [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #c8b8bf; font-size: 12px; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background: #ffffff08; border-color: #66505a; border-radius: 12px; color: #fff; }
[data-testid="stSidebar"] [data-baseweb="select"] svg { fill: #e5ccd2; }
[data-testid="stSidebar"] [data-testid="stAlert"] { background: #ffffff08; border: 1px solid #ffffff12; color: #e3ced3; border-radius: 12px; padding: 12px; }
[data-testid="stSidebar"] [data-testid="stAlertContainer"] { background: transparent; padding: 0; }
[data-testid="stSidebar"] [data-testid="stAlert"] p { color: #e3ced3; font-size: 12px; line-height: 1.65; }
[data-testid="stSidebar"] [data-testid="stAlert"] svg { fill: #dda8b2; }
[data-testid="stSidebar"] .stButton > button { width: 100%; color: #eadde2; background: #ffffff06; border-color: #ffffff20; box-shadow: none; text-align: left; justify-content: flex-start; font-size: 13px; }
[data-testid="stSidebar"] .stButton > button:hover { background: #a3263833; border-color: #bf6374; color: #fff; }
[data-testid="stSidebar"] hr { border-color: #ffffff16; }
.qq-hero { display: grid; grid-template-columns: 1.1fr 1fr; gap: 26px; align-items: center; padding: 22px 0 36px; animation: qq-enter .65s ease-out both; }
.hero-kicker, .eyebrow { color: var(--accent); font-size: 10px; font-weight: 750; letter-spacing: 2px; }
.hero-kicker { display: flex; align-items: center; gap: 9px; margin-bottom: 22px; }
.hero-kicker > span, .corpus-chip i { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 0 4px #a3263810; }
.hero-copy h1 { font-size: clamp(38px, 4.3vw, 62px); font-weight: 750; line-height: 1.08; letter-spacing: -.06em; padding: 0; margin: 0 0 22px; }
.hero-copy h1 em { color: var(--accent); font-family: Georgia, "Times New Roman", serif; font-weight: 400; letter-spacing: -.055em; }
.hero-copy > p { color: var(--muted); max-width: 390px; font-size: 15px; line-height: 1.8; }
.hero-tags { display: flex; gap: 16px; flex-wrap: wrap; margin-top: 24px; color: #5c4c53; font-size: 11px; font-weight: 600; }
.hero-visual { position: relative; min-width: 0; padding: 32px 0 24px; }
.art-orbit { position: absolute; inset: -12px 0; border: 1px solid #a3263812; border-radius: 50%; transform: rotate(-12deg); pointer-events: none; }
.art-orbit::after { content: ""; position: absolute; inset: 18px -14px; border: 1px dashed #a3263817; border-radius: 50%; }
.campus-frame { position: relative; padding: 10px 10px 0; background: #fff9; border: 1px solid #fff; backdrop-filter: blur(14px); border-radius: 24px; box-shadow: 0 24px 55px #63313916; transform: rotate(-3deg); }
.campus-art { width: 100%; height: auto; display: block; border-radius: 16px; }
.art-caption { display: block; text-align: center; font-size: 7px; letter-spacing: 1.5px; color: #80686c; padding: 12px 0; }
.floating-note { position: absolute; top: 4px; right: -4px; display: flex; align-items: center; gap: 10px; padding: 12px 18px; background: #fffffff0; border: 1px solid #fff; box-shadow: 0 10px 32px #54242b13; border-radius: 14px; font-size: 11px; color: var(--muted); animation: qq-float 8s ease-in-out infinite; }
.floating-note strong { display: block; margin-top: 2px; color: var(--text); font-size: 12px; }
.note-icon { color: var(--accent); font-size: 25px; background: #a326380c; border-radius: 10px; padding: 4px 10px; }
.duck-sticker { position: absolute; width: 86px; height: 86px; bottom: 2px; left: -22px; padding: 5px; background: #fffaf1; border: 4px solid #fff; border-radius: 24px; box-shadow: 0 10px 24px #54242b18; transform: rotate(10deg); }
.duck-sticker svg { width: 100%; height: 100%; }
.workspace-status { display: flex; align-items: center; justify-content: space-between; gap: 14px; padding: 18px 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); font-size: 11px; color: var(--muted); }
.workspace-status b, .qq-footer b { color: #c5b6b9; padding: 0 8px; }
.corpus-chip { display: inline-flex; align-items: center; gap: 9px; border: 1px solid #e4cccc; border-radius: 100px; padding: 7px 12px; background: #fff9; color: #803747; font-size: 11px; font-weight: 600; white-space: nowrap; }
.start-heading { padding-top: 16px; }
.start-heading h2 { font-size: 27px; font-weight: 700; margin: 8px 0 4px; padding: 0; }
.start-heading p { color: var(--muted); font-size: 13px; margin: 0; }
.workspace-bar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; padding: 10px 0 22px; border-bottom: 1px solid var(--border); }
.workspace-bar h1 { font-size: 30px; margin: 7px 0 0; padding: 0; }
.stButton > button, .stDownloadButton > button, [data-testid="stLinkButton"] a { min-height: 44px; padding: 10px 16px; border: 1px solid var(--border); border-radius: 12px; background: #ffffffc9; color: var(--text); transition: background .2s ease, border-color .2s ease, box-shadow .2s ease, transform .2s ease; }
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stLinkButton"] a:hover { color: var(--accent); background: #fff; border-color: #bc7a85; box-shadow: 0 6px 20px #a326380c; transform: translateY(-2px); }
.stButton > button:active { transform: translateY(0); }
.stButton > button[kind="primary"] { color: #fff; background: var(--accent); border-color: var(--accent); }
.stButton > button[kind="primary"]:hover { background: var(--accent-dark); color: #fff; }
.st-key-starter_admissions button, .st-key-starter_tuition button, .st-key-starter_courses button { min-height: 88px; justify-content: flex-start; text-align: left; padding: 18px; border-radius: 16px; box-shadow: 0 4px 16px #54242b04; }
.st-key-starter_admissions button p, .st-key-starter_tuition button p, .st-key-starter_courses button p { font-size: 13px; font-weight: 600; }
button:focus-visible, a:focus-visible, summary:focus-visible { outline: 3px solid #b93850 !important; outline-offset: 4px; }
[data-testid="stBottom"] { background: linear-gradient(0deg, #faf7f4 65%, #faf7f400); }
[data-testid="stBottomBlockContainer"] { padding-top: 18px; padding-bottom: 22px; }
[data-testid="stChatInput"] { border-radius: 18px; border: 1px solid #d7babe; background: #fff; box-shadow: 0 12px 40px #63313910; transition: box-shadow .2s, border-color .2s; }
[data-testid="stChatInput"]:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px #a3263812, 0 12px 40px #63313910; }
[data-testid="stChatInput"] [data-baseweb="textarea"], [data-testid="stChatInput"] [data-baseweb="base-input"], [data-testid="stChatInput"] > div { background: #fff; }
[data-testid="stChatInput"] textarea { background: #fff; color: var(--text); caret-color: var(--accent); font-size: 14px; }
[data-testid="stChatInput"] textarea::placeholder { color: #776b72; }
[data-testid="stChatInputSubmitButton"] { color: #fff; background: var(--accent); border-radius: 10px; min-width: 40px; min-height: 40px; transition: background .2s; }
[data-testid="stChatInputSubmitButton"]:hover { background: var(--accent-dark); color: #fff; }
[data-testid="stChatMessage"] { padding: 24px; border: 1px solid var(--border); border-radius: 20px; background: #ffffffdf; box-shadow: 0 8px 30px #52232a06; gap: 16px; animation: qq-enter .35s ease-out both; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background: #f1e8e5; border-color: #e7d5d1; box-shadow: none; }
[data-testid="stChatMessageAvatarAssistant"] { background: #a3263812; color: var(--accent); }
[data-testid="stChatMessageAvatarUser"] { background: #65515a; color: #fff; }
[data-testid="stChatMessageContent"] { min-width: 0; overflow-wrap: anywhere; }
[data-testid="stExpander"] details { background: #fcfaf8; border: 1px solid #e5d9d6; border-radius: 14px; overflow: hidden; }
[data-testid="stExpander"] summary { padding: 14px 16px; }
[data-testid="stExpander"] summary:hover { color: var(--accent); background: #a3263805; }
[data-testid="stExpanderDetails"] { padding: 16px; }
[data-testid="stText"] { white-space: pre-wrap; overflow-wrap: anywhere; font-family: inherit; line-height: 1.75; color: #4d4148; font-size: 14px; }
.answer-label { font-size: 10px; color: var(--accent); letter-spacing: 1.8px; font-weight: 750; margin-bottom: 14px; }
[data-testid="stSpinner"] { padding: 20px; background: #fff9; border: 1px solid var(--border); border-radius: 16px; color: var(--accent); }
[data-testid="stAlert"] { border-radius: 14px; }
.qq-footer { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; padding: 20px 0; margin-top: 8px; border-top: 1px solid var(--border); color: #77676d; font-size: 10px; }
.qq-footer > span:first-child { font-size: 8px; letter-spacing: 1px; }
@keyframes qq-enter { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes qq-float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
@media (min-width: 1500px) { .hero-copy h1 { font-size: 64px; } }
@media (max-width: 1050px) {
    [data-testid="stMainBlockContainer"], [data-testid="stBottomBlockContainer"] { padding-inline: 28px; }
    .qq-hero { gap: 22px; } .hero-copy h1 { font-size: 42px; }
    .hero-tags { gap: 10px; font-size: 10px; }
    .workspace-status > span:last-child { max-width: 210px; text-align: right; }
}
@media (max-width: 760px) {
    [data-testid="stMainBlockContainer"] { padding: 52px 20px 24px; }
    [data-testid="stBottomBlockContainer"] { padding: 12px 16px 16px; }
    .qq-hero { grid-template-columns: 1fr; gap: 8px; padding-top: 0; padding-bottom: 18px; }
    .hero-copy h1 { font-size: clamp(40px, 8vw, 58px); }
    .hero-copy > p { max-width: 100%; }
    .mobile-wordmark { display: flex; align-items: center; gap: 12px; color: var(--accent); font-size: 18px; font-weight: 750; letter-spacing: -.6px; margin-bottom: 18px; }
    .mobile-wordmark span { color: var(--muted); font-size: 7px; letter-spacing: 1px; }
    .hero-visual { max-width: 300px; width: 72%; margin: 4px auto 0; padding: 20px 0 18px; }
    .hero-tags { margin-top: 18px; }
    .duck-sticker { width: 70px; height: 70px; }
    .workspace-status { flex-wrap: wrap; gap: 10px; }
    .workspace-status > span:last-child { max-width: none; text-align: left; }
    [data-testid="stChatMessage"] { padding: 16px; gap: 10px; }
    .workspace-bar h1 { font-size: 25px; }
    .qq-footer { margin-top: 0; }
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
    button:hover, a:hover { transform: none !important; }
}
</style>
"""
