"""
Option SVGs for mockup B · Signal: contribution streak (3 designs) and stack (2 designs).

    python3 mockups/signal_options.py            # everything
    python3 mockups/signal_options.py --streak   # streak SVGs only (what the daily workflow runs)

Streak data comes from the GitHub GraphQL contribution calendar. The token is read
from $GITHUB_TOKEN, falling back to `gh auth token` locally.
"""

import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.request

import build as B
from build import svg

USER = "shard-c6"
OUT = B.ROOT / "b-signal" / "assets"

# ── STACK CONTENT ────────────────────────────────────────────────────────────
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

MATRIX_PROJECTS = ["NetForecast", "Amazon ML", "GreenGuard", "opensre", "EVNet", "MOSIP", "pong-rl"]
MATRIX = [  # (tool, projects it shipped in) — from the 30-09-2026 resume
    ("Python", {"NetForecast", "Amazon ML", "opensre", "EVNet", "MOSIP", "pong-rl"}),
    ("PyTorch", {"NetForecast", "pong-rl"}),
    ("scikit-learn", {"EVNet"}),
    ("XGBoost", {"Amazon ML"}),
    ("River (online ML)", {"EVNet"}),
    ("FastAPI", {"NetForecast", "pong-rl"}),
    ("Next.js", {"GreenGuard", "EVNet"}),
    ("PostgreSQL / Supabase", {"GreenGuard"}),
    ("pgvector + PostGIS", {"GreenGuard"}),
    ("Docker", {"MOSIP"}),
    ("AWS (EC2, S3)", {"Amazon ML"}),
    ("GitHub Actions", {"GreenGuard"}),
    ("pytest + ruff", {"opensre"}),
    ("Wireshark / pcap", {"NetForecast"}),
]


def icon_path(slug):
    return re.search(r' d="([^"]+)"', (B.ROOT / "icons" / f"{slug}.svg").read_text()).group(1)


def brand_fill(hex_):
    """Brand colour, unless it would vanish against the current background."""
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lum = .2126 * r + .7152 * g + .0722 * b
    if (B.MODE == "dark" and lum < .12) or (B.MODE == "light" and lum > .75):
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


# ── STREAK · 2 · HEATMAP ─────────────────────────────────────────────────────
def streak_heatmap(days, s):
    W, H = 1200, 300
    cell, gap = 17, 4
    first = days[0][0]
    cols = (len(days) + first.isoweekday() % 7 + 6) // 7
    gx = (W - cols * (cell + gap) + gap) / 2
    gy = 96
    nz = sorted(c for _, c in days if c)
    q = [nz[int(len(nz) * f)] for f in (.25, .5, .75)] if nz else [1, 2, 3]
    level = lambda c: 0 if c == 0 else 1 + sum(c > t for t in q)
    op = {1: .3, 2: .5, 3: .75, 4: 1}
    extra = """.c{opacity:0;animation:pop .5s ease forwards}@keyframes pop{to{opacity:1}}"""
    cells, months, last_m, last_col = [], [], None, -9
    for i, (d, c) in enumerate(days):
        idx = i + first.isoweekday() % 7
        col, row = divmod(idx, 7)
        x, y = gx + col * (cell + gap), gy + row * (cell + gap)
        lv = level(c)
        cls = "panel s-line" if lv == 0 else "acc"
        o = f' fill-opacity="{op[lv]}"' if lv else ""
        cells.append(f'<rect x="{x:.1f}" y="{y}" width="{cell}" height="{cell}" rx="3.5" class="c {cls}"{o} style="animation-delay:{col * .025:.2f}s"/>')
        if row == 0 and d.month != last_m:
            if col - last_col < 3:  # a stub month at the edge: let the full month take the label
                months.pop()
            months.append(f'<text x="{x:.1f}" y="{gy - 10}" class="mono faint" font-size="13">{d:%b}</text>')
            last_m, last_col = d.month, col
    tcol, trow = divmod(len(days) - 1 + first.isoweekday() % 7, 7)
    tx, ty = gx + tcol * (cell + gap), gy + trow * (cell + gap)
    legend_x = W - gx - 5 * (cell + gap) - 40
    legend = "".join(
        f'<rect x="{legend_x + 40 + j * (cell - 4 + gap):.1f}" y="{H - 34}" width="{cell - 4}" height="{cell - 4}" rx="3" class="{"panel s-line" if j == 0 else "acc"}"'
        + (f' fill-opacity="{op[j]}"' if j else "") + "/>" for j in range(5))
    body = f"""
<text x="{gx:.1f}" y="40" class="sans ink" font-size="22" font-weight="600">{fmt(s["total"])} contributions<tspan class="sans muted" font-weight="400"> in the past year</tspan></text>
<text x="{W - gx:.1f}" y="40" text-anchor="end" class="mono muted" font-size="15"><tspan class="acc">●</tspan> {s["current"]}-day streak · longest {s["longest"]} · {s["active"]} active days</text>
{''.join(months)}
{''.join(cells)}
<rect x="{tx - 3:.1f}" y="{ty - 3}" width="{cell + 6}" height="{cell + 6}" rx="5" class="nofill s-acc" stroke-width="2"><animate attributeName="opacity" values="1;.2;1" dur="2s" repeatCount="indefinite"/></rect>
<text x="{gx:.1f}" y="{H - 22}" class="mono faint" font-size="13">updated {s["updated"]:%d %b %Y}</text>
<text x="{legend_x:.1f}" y="{H - 22}" class="mono faint" font-size="13">less</text>{legend}
<text x="{legend_x + 40 + 5 * (cell - 4 + gap) + 6:.1f}" y="{H - 22}" class="mono faint" font-size="13">more</text>
"""
    return svg(W, H, f"{fmt(s['total'])} contributions in the past year, {s['current']}-day streak", body, "amber", extra)


# ── STREAK · 3 · COUNTERS ────────────────────────────────────────────────────
def streak_counters(days, s):
    W, H = 1200, 220
    last = [c for _, c in days[-30:]]
    mx = max(last) ** .5 or 1
    bx, bw, bg, base, bh = 640, 14, 4.2, 168, 104
    bars = []
    for i, c in enumerate(last):
        h = max(3, (c ** .5) / mx * bh)
        x = bx + i * (bw + bg)
        bars.append(f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{bw}" height="{h:.1f}" rx="2" class="acc" fill-opacity="{.35 + .65 * (i / 29):.2f}">'
                    f'<animate attributeName="height" from="0" to="{h:.1f}" begin="{.2 + i * .03:.2f}s" dur=".6s" fill="freeze" calcMode="spline" keySplines=".2 .7 .2 1"/>'
                    f'<animate attributeName="y" from="{base}" to="{base - h:.1f}" begin="{.2 + i * .03:.2f}s" dur=".6s" fill="freeze" calcMode="spline" keySplines=".2 .7 .2 1"/></rect>')
    body = f"""
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" class="panel s-line" stroke-width="1.5"/>
{num_block(40, 62, "CURRENT STREAK", s["current"], "days", .1)}
{num_block(40, 150, "PAST YEAR", fmt(s["total"]), "contributions", .2)}
{num_block(340, 62, "LONGEST", s["longest"], "days", .3)}
{num_block(340, 150, "BEST DAY", s["peak"], f'{s["peak_date"]:%d %b}', .4)}
<line x1="600" y1="30" x2="600" y2="{H - 30}" class="s-line" stroke-width="1.5"/>
<text x="{bx}" y="50" class="mono muted" font-size="14" letter-spacing="2">LAST 30 DAYS</text>
<circle cx="{W - 48}" cy="45" r="5" class="acc pulse"/>
{''.join(bars)}
<line x1="{bx}" y1="{base}" x2="{bx + 30 * (bw + bg) - bg:.0f}" y2="{base}" class="s-line" stroke-width="1.5"/>
<text x="{bx}" y="{base + 26}" class="mono faint" font-size="13">{days[-30][0]:%d %b}</text>
<text x="{bx + 30 * (bw + bg) - bg:.0f}" y="{base + 26}" text-anchor="end" class="mono faint" font-size="13">today</text>
"""
    return svg(W, H, f"{s['current']}-day streak, longest {s['longest']}, {fmt(s['total'])} contributions in the past year", body, "amber", extra="")


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


# ── STACK · 2 · EVIDENCE MATRIX ──────────────────────────────────────────────
def stack_matrix():
    rh, top, lx, cx0, cw = 34, 84, 28, 270, 120
    W = cx0 + cw * len(MATRIX_PROJECTS) + 60
    H = top + len(MATRIX) * rh + 30
    parts = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" class="panel s-line" stroke-width="1.5"/>',
             f'<text x="{lx}" y="40" class="mono muted" font-size="15">stack × shipped projects</text>',
             f'<text x="{W - 28}" y="40" text-anchor="end" class="mono faint" font-size="15">uses</text>']
    for j, p in enumerate(MATRIX_PROJECTS):
        parts.append(f'<text x="{cx0 + j * cw + cw / 2}" y="{top - 14}" text-anchor="middle" class="sans ink" font-size="15" font-weight="600">{p}</text>')
    for i, (tool, used) in enumerate(MATRIX):
        y = top + i * rh + rh / 2
        if i % 2 == 0:
            parts.append(f'<rect x="12" y="{y - rh / 2}" width="{W - 24}" height="{rh}" rx="6" class="bg" opacity=".6"/>')
        parts.append(f'<text x="{lx}" y="{y + 6}" class="sans ink" font-size="17">{tool}</text>')
        for j, p in enumerate(MATRIX_PROJECTS):
            x = cx0 + j * cw + cw / 2
            if p in used:
                parts.append(f'<circle cx="{x}" cy="{y}" r="7" class="acc rise" style="animation-delay:{.2 + j * .12 + i * .02:.2f}s"/>')
            else:
                parts.append(f'<circle cx="{x}" cy="{y}" r="2" class="faint"/>')
        parts.append(f'<text x="{W - 28}" y="{y + 6}" text-anchor="end" class="mono muted" font-size="15">{len(used)}</text>')
    return svg(W, H, "Stack used per project: " + "; ".join(f"{t}: {', '.join(sorted(u))}" for t, u in MATRIX),
               "\n".join(parts), "amber")


# ── WRITE ────────────────────────────────────────────────────────────────────
def write(name, content):
    p = OUT / f"{name}-{B.MODE}.svg"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", p.relative_to(B.ROOT.parent))


if __name__ == "__main__":
    days = fetch_days()
    s = stats(days)
    for B.MODE in ("light", "dark"):
        write("streak-waveform", streak_waveform(days, s))
        write("streak-heatmap", streak_heatmap(days, s))
        write("streak-counters", streak_counters(days, s))
        if "--streak" not in sys.argv:
            write("stack-layers", stack_layers())
            write("stack-matrix", stack_matrix())
