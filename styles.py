"""QuackQuery presentation; spacing uses an eight-pixel scale."""

STYLES = """
<style>
:root {
    --accent: #8baafa;
    --text: #e8edf7;
    --muted: #a5b2c8;
    --border: #303e55;
    --panel: #192233;
}
html, body, [data-testid="stAppViewContainer"] {
    font-family: "Segoe UI", Arial, sans-serif;
    font-weight: 400;
    color: var(--text);
    background: #0b1020;
}
/* Midnight observatory: light pools, orbital arcs, and a fine drafting grid.
   CSS-only decoration keeps the page light and never intercepts clicks. */
[data-testid="stAppViewContainer"] {
    background-color: #0b1020;
    background-image:
        radial-gradient(ellipse at 52% 42%, rgba(11, 16, 32, 0.78), transparent 72%),
        radial-gradient(ellipse at 88% 16%, transparent 0 31%, rgba(139, 170, 250, 0.13) 31.1% 31.2%, transparent 31.3% 39%, rgba(139, 170, 250, 0.08) 39.1% 39.2%, transparent 39.3%),
        radial-gradient(ellipse at 12% 8%, rgba(105, 133, 234, 0.28), transparent 48%),
        radial-gradient(ellipse at 94% 65%, rgba(95, 119, 205, 0.22), transparent 48%),
        radial-gradient(ellipse at 42% 112%, rgba(109, 132, 232, 0.18), transparent 52%),
        linear-gradient(rgba(160, 182, 239, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(160, 182, 239, 0.035) 1px, transparent 1px),
        linear-gradient(155deg, #10192f, #0b1020 55%, #131b32);
    background-size: auto, auto, auto, auto, auto, 64px 64px, 64px 64px, auto;
    background-attachment: fixed;
}
[data-testid="stMainBlockContainer"] {
    min-height: 80vh;
}
[data-testid="stMainBlockContainer"] h1 {
    color: #eef3ff;
    text-shadow: 0 8px 32px rgba(139, 170, 250, 0.24);
}
[data-testid="stMainBlockContainer"] h1::after {
    content: "";
    display: block;
    width: 64px;
    height: 2px;
    margin-top: 16px;
    background: linear-gradient(90deg, var(--accent), rgba(139, 170, 250, 0));
    box-shadow: 0 0 16px rgba(139, 170, 250, 0.32);
}
#MainMenu, footer { display: none; }
[data-testid="stHeader"] { visibility: hidden; background: transparent; }
/* Keep Streamlit's sidebar reopen control available when the header is hidden. */
[data-testid="stExpandSidebarButton"] {
    visibility: visible;
    position: fixed;
    top: 16px;
    left: 16px;
    z-index: 1000;
}
[data-testid="stMainBlockContainer"],
[data-testid="stBottomBlockContainer"] {
    width: 100%;
    max-width: 900px;
    margin-inline: auto;
    padding: 32px;
}
[data-testid="stBottom"] { background: transparent; }
[data-testid="stVerticalBlock"] { gap: 16px; }
h1, h2, h3, h4, h5, h6, strong, b,
[data-testid="stWidgetLabel"], button {
    font-weight: 600 !important;
}
h1 {
    font-size: clamp(2rem, 5vw, 3rem);
    letter-spacing: -0.04em;
    padding-block: 8px !important;
}
[data-testid="stCaptionContainer"] {
    color: var(--muted);
    line-height: 1.6;
}
[data-testid="stSidebar"] {
    background:
        radial-gradient(ellipse at 0% 0%, rgba(105, 133, 234, 0.14), transparent 65%),
        linear-gradient(180deg, rgba(17, 25, 45, 0.97), rgba(10, 16, 30, 0.98));
    border-right: 1px solid rgba(139, 170, 250, 0.18);
    box-shadow: 8px 0 32px rgba(0, 0, 0, 0.16);
}
[data-testid="stSidebarUserContent"] { padding: 32px 24px; }
.stTextInput input,
[data-testid="stChatInput"] textarea {
    color: var(--text);
    caret-color: var(--accent);
    padding: 16px;
    font-weight: 400;
}
.stTextInput input::placeholder,
[data-testid="stChatInput"] textarea::placeholder { color: var(--muted); }
.stTextInput [data-baseweb="input"],
[data-testid="stChatInput"] {
    background: rgba(22, 32, 53, 0.96);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.24);
    border: 1px solid rgba(139, 170, 250, 0.3);
    border-radius: 10px;
    transition: all 0.2s ease;
}
.stTextInput [data-baseweb="input"]:hover,
.stTextInput [data-baseweb="input"]:focus-within,
[data-testid="stChatInput"]:hover,
[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 16px rgba(139, 170, 250, 0.16);
}
.stButton > button,
.stDownloadButton > button,
[data-testid="stLinkButton"] a {
    min-height: 40px;
    padding: 8px 24px;
    border: 1px solid var(--accent);
    border-radius: 10px;
    background: var(--accent);
    color: #101521;
    font-weight: 600;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.16);
    transition: all 0.2s ease;
}
.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stLinkButton"] a:hover {
    background: #a1bafa;
    color: #101521;
    border-color: var(--accent);
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28);
}
.stButton > button:active,
.stDownloadButton > button:active,
[data-testid="stLinkButton"] a:active {
    transform: translateY(0);
    box-shadow: none;
}
button:focus-visible, a:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 4px;
}
[data-testid="stChatInputSubmitButton"] {
    color: var(--accent);
    border-radius: 8px;
    transition: all 0.2s ease;
}
[data-testid="stChatInputSubmitButton"]:hover {
    background: #303e55;
    transform: translateY(-1px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.16);
}
[data-testid="stChatInputSubmitButton"]:active { transform: translateY(0); }
[data-testid="stChatMessage"] {
    background: linear-gradient(135deg, rgba(31, 43, 68, 0.94), rgba(17, 26, 45, 0.96));
    border: 1px solid rgba(139, 170, 250, 0.2);
    border-radius: 16px;
    padding: 24px;
    gap: 16px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(218, 229, 255, 0.05);
}
[data-testid="stChatMessageContent"] { min-width: 0; }
[data-testid="stMarkdownContainer"] p { line-height: 1.7; }
[data-testid="stExpander"] details {
    background: #121b2b;
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
}
[data-testid="stExpander"] summary { padding: 16px; }
[data-testid="stExpander"] summary:hover { color: var(--accent); }
[data-testid="stExpanderDetails"] { padding: 16px; }
[data-testid="stText"] {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    line-height: 1.7;
    color: var(--text);
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    width: 100%;
    justify-content: flex-start;
    text-align: left;
    background: transparent;
    color: var(--text);
    border-color: var(--border);
    box-shadow: none;
    padding: 8px 16px;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background: var(--panel);
    border-color: var(--accent);
}
@media (max-width: 640px) {
    [data-testid="stAppViewContainer"] { background-attachment: scroll; }
    [data-testid="stMainBlockContainer"] { padding: 48px 16px 24px; }
    [data-testid="stBottomBlockContainer"] { padding: 16px; }
    [data-testid="stChatMessage"] { padding: 16px; gap: 8px; }
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { transition: none !important; transform: none !important; }
}
</style>
"""
