"""
ui/styles/theme.py
────────────────────────────────────────────────────────────────────────────
Accelerons Electric — Design System  [LIGHT BEIGE THEME]
"""

class Color:
    # ── Backgrounds ──────────────────────────────────────────────────────────
    BG_BASE     = "#FAF6EE"       # warm light beige — main background
    BG_PANEL    = "#F0EAD6"       # slightly darker beige for nav/panels
    BG_CARD     = "#FFFFFF"       # pure white cards
    BG_CARD2    = "#FDF9F3"       # soft beige secondary cards

    # ── Brand greens ─────────────────────────────────────────────────────────
    NEON_GREEN  = "#16A34A"       # primary green (readable on light)
    GREEN_DIM   = "#BBF7D0"
    GREEN_GLOW  = "#22C55E"
    GREEN_BAR   = "#22C55E"

    # ── Amber / warning ───────────────────────────────────────────────────────
    AMBER       = "#B45309"
    AMBER_DIM   = "#FDE68A"
    AMBER_GLOW  = "#F59E0B"
    AMBER_BAR   = "#F59E0B"

    # ── Red / critical ────────────────────────────────────────────────────────
    RED         = "#DC2626"
    RED_DIM     = "#FECACA"
    RED_GLOW    = "#EF4444"
    RED_BAR     = "#EF4444"

    # ── Structural ────────────────────────────────────────────────────────────
    SLATE       = "#64748B"
    BORDER      = "#D6C9A8"       # warm beige border
    BORDER_LIT  = "#1D4ED8"       # blue accent border
    BORDER_SEG  = "#3B82F6"

    # ── Text ──────────────────────────────────────────────────────────────────
    TEXT_PRI    = "#1C1917"       # near-black warm
    TEXT_SEC    = "#57534E"       # medium warm brown-grey
    TEXT_DIM    = "#A8A29E"       # dim placeholder

    # ── Accents ───────────────────────────────────────────────────────────────
    ACCENT_BLUE = "#1D4ED8"       # strong blue
    LOGO_ORANGE = "#EA580C"       # brand orange accent for logo
    WHITE       = "#FFFFFF"
    BLACK       = "#0F172A"

    # ── Timer/Stopwatch specific ──────────────────────────────────────────────
    TIMER_BG    = "#FFFFFF"
    TIMER_DIGIT = "#1C1917"
    TIMER_RUN   = "#16A34A"
    TIMER_STOP  = "#DC2626"
    TIMER_LAP   = "#1D4ED8"


class Font:
    FAMILY   = "Roboto, Inter, Segoe UI, Arial"
    MONO     = "Roboto Mono, Consolas, Courier New"
    SIZE_XS  = 9
    SIZE_SM  = 11
    SIZE_MD  = 13
    SIZE_LG  = 16
    SIZE_XL  = 22
    SIZE_2XL = 32
    SIZE_3XL = 48
    SIZE_4XL = 72
    SIZE_5XL = 96


MASTER_QSS = f"""
/* ── Global ── */
* {{
    font-family: {Font.FAMILY};
    color: {Color.TEXT_PRI};
}}
QMainWindow, QWidget {{
    background-color: {Color.BG_BASE};
}}
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: {Color.BG_PANEL};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {Color.BORDER};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {Color.ACCENT_BLUE};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ── Cards ── */
QFrame#card {{
    background: {Color.BG_CARD};
    border: 1.5px solid {Color.BORDER};
    border-radius: 12px;
}}
QFrame#card_lit {{
    background: {Color.BG_CARD};
    border: 2px solid {Color.BORDER_LIT};
    border-radius: 12px;
}}
QFrame#card_seg {{
    background: {Color.BG_CARD};
    border: 2px solid {Color.BORDER_SEG};
    border-radius: 10px;
}}
QFrame#card_timer {{
    background: {Color.BG_CARD};
    border: 2px solid {Color.BORDER};
    border-radius: 16px;
}}

/* ── Progress bars ── */
QProgressBar {{
    background: {Color.BG_PANEL};
    border: none;
    border-radius: 5px;
    text-align: center;
    color: {Color.TEXT_PRI};
    font-family: {Font.MONO};
    font-size: {Font.SIZE_XS}px;
    font-weight: 700;
}}
QProgressBar::chunk {{
    border-radius: 5px;
    background: {Color.GREEN_BAR};
}}

/* ── Buttons — primary ── */
QPushButton#btn_primary {{
    background: {Color.NEON_GREEN};
    color: {Color.WHITE};
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: {Font.SIZE_MD}px;
    font-weight: 700;
    letter-spacing: 1px;
}}
QPushButton#btn_primary:hover  {{ background: {Color.GREEN_GLOW}; }}
QPushButton#btn_primary:pressed {{ background: {Color.NEON_GREEN}; }}

/* ── Buttons — timer control ── */
QPushButton#btn_start {{
    background: {Color.TIMER_RUN};
    color: {Color.WHITE};
    border: none;
    border-radius: 12px;
    font-size: {Font.SIZE_LG}px;
    font-weight: 800;
    letter-spacing: 1px;
}}
QPushButton#btn_start:hover  {{ background: {Color.GREEN_GLOW}; }}

QPushButton#btn_stop {{
    background: {Color.TIMER_STOP};
    color: {Color.WHITE};
    border: none;
    border-radius: 12px;
    font-size: {Font.SIZE_LG}px;
    font-weight: 800;
    letter-spacing: 1px;
}}
QPushButton#btn_stop:hover  {{ background: {Color.RED_GLOW}; }}

QPushButton#btn_lap {{
    background: {Color.TIMER_LAP};
    color: {Color.WHITE};
    border: none;
    border-radius: 12px;
    font-size: {Font.SIZE_LG}px;
    font-weight: 800;
    letter-spacing: 1px;
}}
QPushButton#btn_lap:hover  {{ background: #3B82F6; }}

QPushButton#btn_reset {{
    background: {Color.BG_PANEL};
    color: {Color.TEXT_SEC};
    border: 1.5px solid {Color.BORDER};
    border-radius: 12px;
    font-size: {Font.SIZE_LG}px;
    font-weight: 800;
}}
QPushButton#btn_reset:hover  {{ background: {Color.BORDER}; }}

/* ── Pill buttons ── */
QPushButton#btn_pill {{
    background: {Color.BG_PANEL};
    color: {Color.TEXT_SEC};
    border: 1px solid {Color.BORDER};
    border-radius: 14px;
    padding: 5px 14px;
    font-size: {Font.SIZE_SM}px;
    font-weight: 600;
}}
QPushButton#btn_pill:checked {{
    background: {Color.ACCENT_BLUE};
    color: {Color.WHITE};
    border: 1px solid {Color.ACCENT_BLUE};
}}
QPushButton#btn_pill:hover:!checked {{
    border: 1px solid {Color.ACCENT_BLUE};
    color: {Color.ACCENT_BLUE};
}}

QPushButton#btn_download {{
    background: {Color.BG_CARD2};
    color: {Color.ACCENT_BLUE};
    border: 1px solid {Color.BORDER};
    border-radius: 8px;
    padding: 5px 12px;
    font-size: {Font.SIZE_SM}px;
    font-weight: 600;
}}
QPushButton#btn_download:hover {{
    background: {Color.ACCENT_BLUE};
    color: {Color.WHITE};
}}

/* ── Nav bar ── */
QWidget#nav_bar {{
    background: {Color.BG_CARD};
    border-top: 1.5px solid {Color.BORDER};
}}
QPushButton#nav_btn {{
    background: transparent;
    border: none;
    color: {Color.TEXT_DIM};
    font-size: {Font.SIZE_XS}px;
    padding: 6px 4px 4px 4px;
}}
QPushButton#nav_btn:checked {{
    color: {Color.ACCENT_BLUE};
    font-weight: 700;
}}

/* ── Page headers ── */
QLabel#page_header {{
    color: {Color.TEXT_PRI};
    font-size: {Font.SIZE_LG}px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}
QLabel#brand {{
    color: {Color.ACCENT_BLUE};
    font-size: {Font.SIZE_MD}px;
    font-weight: 900;
    letter-spacing: 3px;
}}
"""
