"""
Generates the animated SVGs for the profile README into assets/profile/.

    python3 scripts/profile/generate.py            # everything
    python3 scripts/profile/generate.py --streak   # streak only (run daily by .github/workflows/streak.yml)

Each asset is written as *-light.svg and *-dark.svg (GitHub Primer colours); the README
picks one with <picture>, which follows the viewer's GitHub theme. Only system fonts are
used, since GitHub's image proxy blocks web fonts, and motion stops under
prefers-reduced-motion. Streak data comes from the GitHub GraphQL contribution calendar,
using $GITHUB_TOKEN or, locally, `gh auth token`. Edit the CONTENT block and re-run.
"""

import datetime as dt
import json
import math
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parent.parent / "assets" / "profile"
USER = "shard-c6"

# ── CONTENT ──────────────────────────────────────────────────────────────────
NAME = "Shardul Chogale"
CHIPS = ["Open to GSoC 2027", "ML / data internships", "Mumbai, IN"]

ROADMAP = [  # (when, title, subtitle, state)  state: done | now | next
    ("2024", "B.Tech CE", "VIT Mumbai · 9.5 CGPA", "done"),
    ("2025", "Open source", "opensre · GreenGuard", "done"),
    ("2026", "Hackathons", "SIH lead · Amazon ML", "done"),
    ("NOW", "MOSIP Decode", "Conformance automation", "now"),
    ("2027", "GSoC", "+ ML / data internship", "next"),
    ("GOAL", "ML / Data Engineer", "systems, end to end", "next"),
]

LAYERS = [  # (layer, tools) — top of the stack to the bottom
    ("serve", ["FastAPI", "Express", "Next.js", "React", "WebSockets"]),
    ("learn", ["PyTorch", "fastai", "scikit-learn", "XGBoost", "River", "LSTM", "RAG", "RL"]),
    ("store", ["PostgreSQL", "PostGIS", "pgvector", "Supabase", "Redis"]),
    ("process", ["Python", "SQL", "pandas", "ETL/ELT", "Entity resolution"]),
    ("ship", ["AWS", "Azure", "Docker", "GitHub Actions", "Vercel"]),
    ("secure", ["Intrusion detection", "Wireshark", "MITRE ATT&amp;CK", "OpenID4VCI/VP"]),
]

# tool → (Simple Icons slug in mockups/icons, brand colour). Tools not listed get a neutral marker.
LOGOS = {
    "FastAPI": ("fastapi", "009688"), "Express": ("express", "0A0A0A"), "Next.js": ("nextdotjs", "000000"),
    "React": ("react", "61DAFB"), "PyTorch": ("pytorch", "EE4C2C"), "scikit-learn": ("scikitlearn", "F7931E"),
    "PostgreSQL": ("postgresql", "4169E1"), "Supabase": ("supabase", "3FCF8E"), "Redis": ("redis", "FF4438"),
    "Python": ("python", "3776AB"), "pandas": ("pandas", "150458"), "AWS": ("amazonwebservices", "FF9900"),
    "Azure": ("microsoftazure", "0078D4"), "Docker": ("docker", "2496ED"), "GitHub Actions": ("githubactions", "2088FF"),
    "Vercel": ("vercel", "000000"), "Wireshark": ("wireshark", "1679A7"), "OpenID4VCI/VP": ("openid", "F78C40"),
}

# ── THEME ────────────────────────────────────────────────────────────────────
ACCENTS = {  # (light, dark)
    "blue": ("#0969da", "#4493f8"),
    "amber": ("#bc4c00", "#f0883e"),
    "green": ("#1a7f37", "#3fb950"),
}
SANS = '-apple-system,BlinkMacSystemFont,&quot;Segoe UI&quot;,&quot;Noto Sans&quot;,Helvetica,Arial,sans-serif'
MONO = 'ui-monospace,SFMono-Regular,&quot;SF Mono&quot;,Menlo,Consolas,&quot;Liberation Mono&quot;,monospace'


PALETTES = {
    "light": "--ink:#1f2328;--muted:#59636e;--faint:#818b98;--line:#d1d9e0;--panel:#f6f8fa;--bg:#ffffff;--warn:#9a6700",
    "dark": "--ink:#f0f6fc;--muted:#9198a1;--faint:#656c76;--line:#3d444d;--panel:#151b23;--bg:#0d1117;--warn:#d29922",
}
MODE = "light"  # set by the writer loop at the bottom


def style(accent, extra=""):
    acc = ACCENTS[accent][MODE == "dark"]
    return f"""<style>
svg{{{PALETTES[MODE]};--acc:{acc}}}
.ink{{fill:var(--ink)}}.muted{{fill:var(--muted)}}.faint{{fill:var(--faint)}}.acc{{fill:var(--acc)}}.warn{{fill:var(--warn)}}
.bg{{fill:var(--bg)}}.panel{{fill:var(--panel)}}.nofill{{fill:none}}
.s-line{{stroke:var(--line)}}.s-acc{{stroke:var(--acc)}}.s-faint{{stroke:var(--faint)}}.s-warn{{stroke:var(--warn)}}.s-ink{{stroke:var(--ink)}}.s-bg{{stroke:var(--bg)}}
.sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}
.pulse{{animation:pulse 2.4s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.2}}}}
.rise{{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) forwards}}
@keyframes rise{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
{extra}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;opacity:1!important}}.motion{{display:none}}}}
</style>"""


def svg(w, h, label, body, accent, extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}">\n<title>{label}</title>\n{style(accent, extra)}\n{body}\n</svg>\n')


def tw(text, size, k=0.55):
    """Rough rendered width of sans text."""
    return len(text) * size * k


def chips(x, y, items):
    out, cx = [], x
    for i, label in enumerate(items):
        dot = 20 if i == 0 else 0
        w = round(tw(label, 17, 0.54) + 34 + dot)
        out.append(f'<rect x="{cx}" y="{y}" width="{w}" height="38" rx="19" class="nofill s-line" stroke-width="1.5"/>')
        if i == 0:
            out.append(f'<circle cx="{cx + 22}" cy="{y + 19}" r="5" class="acc pulse"/>')
        out.append(f'<text x="{cx + 17 + dot}" y="{y + 25}" class="sans {"ink" if i == 0 else "muted"}" font-size="17">{label}</text>')
        cx += w + 12
    return "\n".join(out)


def intro(eyebrow, tagline, y0=64):
    lines = [
        f'<text x="2" y="{y0}" class="mono acc rise" font-size="16" letter-spacing="3">{eyebrow}</text>',
        f'<text x="0" y="{y0 + 74}" class="sans ink rise" font-size="62" font-weight="700" letter-spacing="-1.5" style="animation-delay:.1s">{NAME}</text>',
    ]
    for i, t in enumerate(tagline):
        lines.append(f'<text x="2" y="{y0 + 124 + i * 31}" class="sans muted rise" font-size="22" style="animation-delay:{.2 + i * .05:.2f}s">{t}</text>')
    lines.append(f'<g class="rise" style="animation-delay:.35s">{chips(2, y0 + 124 + len(tagline) * 31 + 14, CHIPS)}</g>')
    return "\n".join(lines)


# ── B · SIGNAL ───────────────────────────────────────────────────────────────
def hero_signal():
    W, H = 1200, 340
    px, py, pw, ph = 648, 14, 552, 312
    x0, x1, top, bot = px + 22, px + pw - 22, py + 80, py + ph - 52
    P = x1 - x0                      # one period = plot width; series scrolls by exactly P
    mid, amp = (top + bot) / 2 + 10, 34
    rnd = [((i * 7919) % 97) / 97 - .5 for i in range(200)]
    step, n = 6, round(P / 6)
    spikes = {round(n * .28): -1, round(n * .74): -1}
    ys = []
    for i in range(n):
        t = i / n * 2 * math.pi
        y = mid - amp * (.55 * math.sin(2 * t) + .3 * math.sin(5 * t + 1)) + rnd[i % 200] * 16
        if i in spikes:
            y = top + 8
        ys.append(y)
    pts = [(x0 + i * P / n, ys[i % n]) for i in range(2 * n + 1)]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    band_t, band_b = mid - amp - 14, mid + amp + 14
    marks = []
    for rep_ in range(2):
        for i in spikes:
            x, y = x0 + (i + rep_ * n) * P / n, top + 8
            marks.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" class="nofill s-acc" stroke-width="2"/>'
                         f'<text x="{x + 16:.1f}" y="{y + 5:.1f}" class="mono acc" font-size="14">anomaly</text>')
    extra = f""".scroll{{animation:scroll 14s linear infinite}}
@keyframes scroll{{to{{transform:translateX(-{P:.0f}px)}}}}"""
    grid = "".join(f'<line x1="{x0}" y1="{y:.0f}" x2="{x1}" y2="{y:.0f}" class="s-line" stroke-dasharray="2 6"/>' for y in (top, mid, bot))
    body = f"""
{intro("ML · DATA · NETWORK SECURITY", ["I build ML and data systems end to end —", "and the detectors that watch them."])}
<defs><clipPath id="plot"><rect x="{x0}" y="{py + 56}" width="{P}" height="{ph - 90}"/></clipPath></defs>
<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="16" class="panel s-line" stroke-width="1.5"/>
<text x="{px + 22}" y="{py + 34}" class="mono muted" font-size="15">traffic · distance-from-normal</text>
<circle cx="{px + pw - 96}" cy="{py + 29}" r="5" class="acc pulse"/>
<text x="{px + pw - 84}" y="{py + 34}" class="mono muted" font-size="15">live</text>
<line x1="{px}" y1="{py + 52}" x2="{px + pw}" y2="{py + 52}" class="s-line" stroke-width="1.5"/>
{grid}
<rect x="{x0}" y="{band_t:.0f}" width="{P}" height="{band_b - band_t:.0f}" class="bg" opacity=".9"/>
<text x="{x1 - 6}" y="{band_b - 8:.0f}" text-anchor="end" class="mono faint" font-size="12">normal</text>
<g clip-path="url(#plot)"><g class="scroll">
  <path d="{d}" class="nofill s-ink" stroke-width="2" stroke-linejoin="round" opacity=".8"/>
  {''.join(marks)}
</g></g>
<text x="{px + 22}" y="{py + ph - 20}" class="mono faint" font-size="13">LSTM world model · AUC 0.984 on unseen attacks</text>
"""
    return svg(W, H, f"{NAME} — ML, data engineering and network security", body, "amber", extra)


def roadmap():
    W, H = 1200, 196
    x0, x1, y = 110, 1090, 96
    step = (x1 - x0) / (len(ROADMAP) - 1)
    now_i = next(i for i, r in enumerate(ROADMAP) if r[3] == "now")
    now_x = x0 + now_i * step
    prog = now_x - x0
    extra = f""".draw{{stroke-dasharray:{prog:.0f};stroke-dashoffset:{prog:.0f};animation:draw 1.8s cubic-bezier(.6,0,.2,1) .2s forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}"""
    parts = [
        f'<line x1="{now_x:.0f}" y1="{y}" x2="{x1}" y2="{y}" class="s-faint" stroke-width="2" stroke-dasharray="3 7"/>',
        f'<line x1="{x0}" y1="{y}" x2="{now_x:.0f}" y2="{y}" class="s-line" stroke-width="2"/>',
        f'<line x1="{x0}" y1="{y}" x2="{now_x:.0f}" y2="{y}" class="s-acc draw" stroke-width="3" stroke-linecap="round"/>',
    ]
    for i, (when, title, sub, state) in enumerate(ROADMAP):
        x = x0 + i * step
        d = f"{.3 + i * .22:.2f}s"
        wc = "acc" if state == "now" else ("muted" if state == "done" else "faint")
        parts.append(f'<g class="rise" style="animation-delay:{d}">')
        parts.append(f'<text x="{x:.0f}" y="{y - 30}" text-anchor="middle" class="mono {wc}" font-size="15" letter-spacing="1.5">{when}</text>')
        if state == "done":
            parts.append(f'<circle cx="{x:.0f}" cy="{y}" r="8" class="acc"/>')
        elif state == "now":
            parts.append(f'<circle cx="{x:.0f}" cy="{y}" r="8" class="nofill s-acc" stroke-width="2"><animate attributeName="r" values="8;22" dur="2s" repeatCount="indefinite"/>'
                         f'<animate attributeName="opacity" values=".9;0" dur="2s" repeatCount="indefinite"/></circle>')
            parts.append(f'<circle cx="{x:.0f}" cy="{y}" r="9" class="acc"/><circle cx="{x:.0f}" cy="{y}" r="3.5" class="bg"/>')
        else:
            parts.append(f'<circle cx="{x:.0f}" cy="{y}" r="8" class="bg s-faint" stroke-width="2"/>')
        tc = "faint" if state == "next" else "ink"
        parts.append(f'<text x="{x:.0f}" y="{y + 46}" text-anchor="middle" class="sans {"ink" if state != "next" else "muted"}" font-size="19" font-weight="600">{title}</text>')
        parts.append(f'<text x="{x:.0f}" y="{y + 74}" text-anchor="middle" class="sans {"muted" if state != "next" else tc}" font-size="16">{sub}</text>')
        parts.append('</g>')
    return svg(W, H, "Roadmap: B.Tech at VIT Mumbai 2024, open source 2025, hackathons 2026, MOSIP Decode now, GSoC 2027, goal ML / Data Engineer",
               "\n".join(parts), "amber", extra)


def icon_path(slug):
    return re.search(r' d="([^"]+)"', (HERE / "icons" / f"{slug}.svg").read_text()).group(1)


def brand_fill(hex_):
    """Brand colour, unless it would vanish against the current background."""
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lum = .2126 * r + .7152 * g + .0722 * b
    if (MODE == "dark" and lum < .12) or (MODE == "light" and lum > .75):
        return 'class="ink"'
    return f'style="fill:#{hex_}"'


# ── DATA ─────────────────────────────────────────────────────────────────────
def fetch_days(user=USER):
    token = os.environ.get("GITHUB_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
    q = ('{user(login:"%s"){contributionsCollection{contributionCalendar{'
         'weeks{contributionDays{date contributionCount}}}}}}' % user)
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": q}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": user})
    weeks = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(dt.date.fromisoformat(d["date"]), d["contributionCount"]) for w in weeks for d in w["contributionDays"]]


def stats(days):
    counts = [c for _, c in days]
    # Today may still be empty; that shouldn't break the streak yet.
    tail = counts[:-1] if counts[-1] == 0 else counts
    cur = 0
    for c in reversed(tail):
        if not c:
            break
        cur += 1
    best = run = 0
    for c in counts:
        run = run + 1 if c else 0
        best = max(best, run)
    peak_i = max(range(len(counts)), key=counts.__getitem__)
    return {
        "total": sum(counts), "current": cur, "longest": best,
        "active": sum(1 for c in counts if c), "peak": counts[peak_i], "peak_date": days[peak_i][0],
        "updated": days[-1][0],
    }


def fmt(n):
    return f"{n:,}"


def num_block(x, y, label, value, unit, delay):
    return (f'<g class="rise" style="animation-delay:{delay:.2f}s">'
            f'<text x="{x}" y="{y}" class="mono muted" font-size="14" letter-spacing="2">{label}</text>'
            f'<text x="{x}" y="{y + 48}" class="sans ink" font-size="44" font-weight="700" letter-spacing="-1">{value}'
            f'<tspan class="sans muted" font-size="18" font-weight="400" dx="8">{unit}</tspan></text></g>')


# ── STREAK · 1 · WAVEFORM ────────────────────────────────────────────────────
def streak_waveform(days, s):
    W, H = 1200, 360
    span = days[-182:]
    x0, x1, top, bot = 40, W - 40, 170, 316
    mx = max(c for _, c in span) ** .5 or 1
    pts = [(x0 + i * (x1 - x0) / (len(span) - 1), bot - (c ** .5) / mx * (bot - top)) for i, (_, c) in enumerate(span)]
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = line + f" L{x1},{bot} L{x0},{bot} Z"
    length = sum(((pts[i][0] - pts[i - 1][0]) ** 2 + (pts[i][1] - pts[i - 1][1]) ** 2) ** .5 for i in range(1, len(pts)))
    k = max(range(len(span)), key=lambda i: span[i][1])
    px, py = pts[k]
    sx = pts[max(0, len(span) - 1 - s["current"])][0] if s["current"] < len(span) else x0
    extra = f""".wave{{stroke-dasharray:{length:.0f};stroke-dashoffset:{length:.0f};animation:draw 2.6s cubic-bezier(.5,0,.2,1) .3s forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.fill{{opacity:0;animation:fadein 1s ease 2.4s forwards}}@keyframes fadein{{to{{opacity:1}}}}"""
    body = f"""
<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--acc);stop-opacity:.28"/><stop offset="1" style="stop-color:var(--acc);stop-opacity:0"/></linearGradient></defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" class="panel s-line" stroke-width="1.5"/>
<text x="40" y="44" class="mono muted" font-size="15">contributions · last 26 weeks</text>
<circle cx="{W - 54 - len(f"updated {s['updated']:%d %b}") * 9}" cy="39" r="5" class="acc pulse"/>
<text x="{W - 40}" y="44" text-anchor="end" class="mono muted" font-size="15">updated {s["updated"]:%d %b}</text>
{num_block(40, 88, "CURRENT STREAK", s["current"], "days", .1)}
{num_block(340, 88, "LONGEST", s["longest"], "days", .2)}
{num_block(600, 88, "PAST YEAR", fmt(s["total"]), "contributions", .3)}
{num_block(960, 88, "ACTIVE DAYS", s["active"], f"/ {len(days)}", .4)}
<rect x="{sx:.1f}" y="{top - 14}" width="{x1 - sx:.1f}" height="{bot - top + 14}" class="bg" opacity=".7"/>
<line x1="{sx:.1f}" y1="{top - 14}" x2="{sx:.1f}" y2="{bot}" class="s-acc" stroke-dasharray="3 5"/>
<text x="{sx + 8:.1f}" y="{top}" class="mono acc" font-size="13">streak →</text>
<line x1="{x0}" y1="{bot}" x2="{x1}" y2="{bot}" class="s-line" stroke-width="1.5"/>
<path d="{area}" fill="url(#g)" class="fill"/>
<path d="{line}" class="nofill s-acc wave" stroke-width="2" stroke-linejoin="round"/>
<g class="fill"><circle cx="{px:.1f}" cy="{py:.1f}" r="9" class="nofill s-acc" stroke-width="2"/>
<text x="{px + (14 if px < W - 220 else -14):.1f}" y="{py + 5:.1f}" text-anchor="{"start" if px < W - 220 else "end"}" class="mono acc" font-size="13">peak {span[k][1]} · {span[k][0]:%d %b}</text></g>
<g class="fill"><circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="5" class="acc"><animate attributeName="r" values="5;9;5" dur="2s" repeatCount="indefinite"/></circle></g>
"""
    return svg(W, H, f"Contributions: {s['current']}-day current streak, longest {s['longest']}, {fmt(s['total'])} in the past year", body, "amber", extra)


# ── STACK · 1 · LAYERS ───────────────────────────────────────────────────────
def stack_layers():
    W, rh, top = 1200, 70, 24
    H = top + len(LAYERS) * rh + 16
    lx, px = 180, 214
    parts = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" class="panel s-line" stroke-width="1.5"/>',
             f'<line x1="{lx - 40}" y1="{top + rh / 2}" x2="{lx - 40}" y2="{top + (len(LAYERS) - .5) * rh}" class="s-line" stroke-width="2"/>']
    d = f"M{lx - 40},{top + rh / 2} V{top + (len(LAYERS) - .5) * rh}"
    for i, (layer, tools) in enumerate(LAYERS):
        y = top + i * rh
        cy = y + rh / 2
        g = [f'<g class="rise" style="animation-delay:{.1 + i * .1:.2f}s">']
        if i:
            g.append(f'<line x1="{lx}" y1="{y}" x2="{W - 28}" y2="{y}" class="s-line" stroke-dasharray="2 6"/>')
        g.append(f'<circle cx="{lx - 40}" cy="{cy}" r="6" class="bg s-acc" stroke-width="2"/>')
        g.append(f'<text x="28" y="{cy + 5}" class="mono acc" font-size="15" letter-spacing="2">{layer.upper()}</text>')
        x = px
        for t in tools:
            w = round(len(t.replace("&amp;", "&")) * 9 + 56)
            g.append(f'<rect x="{x}" y="{cy - 19}" width="{w}" height="38" rx="9" class="bg s-line" stroke-width="1.5"/>')
            if t in LOGOS:
                slug, hex_ = LOGOS[t]
                g.append(f'<path d="{icon_path(slug)}" transform="translate({x + 13},{cy - 10}) scale({20 / 24:.4f})" {brand_fill(hex_)}/>')
            else:
                g.append(f'<rect x="{x + 18}" y="{cy - 5}" width="10" height="10" rx="2.5" class="nofill s-faint" stroke-width="1.5" transform="rotate(45 {x + 23} {cy})"/>')
            g.append(f'<text x="{x + 42}" y="{cy + 6}" class="sans ink" font-size="17">{t}</text>')
            x += w + 10
        g.append("</g>")
        parts.append("".join(g))
    parts.append(f'<g class="motion"><circle r="6" class="acc" opacity="0"><set attributeName="opacity" to="1" begin=".8s"/>'
                 f'<animateMotion dur="4s" begin=".8s" repeatCount="indefinite" path="{d}" keyPoints="0;1;1" keyTimes="0;.85;1" calcMode="linear"/></circle></g>')
    return svg(W, H, "Stack by layer: " + "; ".join(f"{l}: {', '.join(t)}" for l, t in LAYERS).replace("&amp;", "and"),
               "\n".join(parts), "amber")


# ── WRITE ────────────────────────────────────────────────────────────────────
def write(name, content):
    p = OUT / f"{name}-{MODE}.svg"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", p.relative_to(OUT.parent.parent))


if __name__ == "__main__":
    days = fetch_days()
    s = stats(days)
    for MODE in ("light", "dark"):
        write("streak", streak_waveform(days, s))
        if "--streak" not in sys.argv:
            write("hero", hero_signal())
            write("roadmap", roadmap())
            write("stack", stack_layers())
