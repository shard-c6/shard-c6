"""
Generates the animated SVGs for the three profile README mockups.

    python3 mockups/build.py

Every asset is written twice, `*-light.svg` and `*-dark.svg` (GitHub Primer
colours), and the READMEs pick one with <picture>, which follows the viewer's
GitHub theme rather than their OS theme. Only system fonts are used (GitHub's image proxy blocks
web fonts), and disables motion under `prefers-reduced-motion`.
Edit the CONTENT block below and re-run to update text everywhere.
"""

import math
from pathlib import Path

ROOT = Path(__file__).parent

# ── CONTENT ──────────────────────────────────────────────────────────────────
NAME = "Shardul Chogale"
CHIPS = ["Open to GSoC 2027", "ML / data internships", "Mumbai, IN"]

PROJECTS = [  # (name, one-liner ≤ 55 chars, tags, link)
    ("NetForecast", "SIH 2026 team lead · LSTM IDS flags unseen attacks", ["pytorch", "lstm", "fastapi"], "https://github.com/shard-c6"),
    ("Amazon ML Challenge", "Entity resolution on 7.6M records · F0.5 0.712 → 0.882", ["xgboost", "tf-idf", "aws"], "https://github.com/shard-c6"),
    ("GreenGuard", "NGO platform · RAG consultant + PostGIS matching", ["next.js", "pgvector", "postgis"], "https://github.com/shard-c6/GreenGuard"),
    ("opensre", "Open source · EKS tooling, dedup fix, test protocol", ["python", "pytest", "ruff"], "https://github.com/shard-c6/opensre"),
    ("EVNet Sentinel", "Reproduced an online IDS paper; found data leakage", ["river", "scikit-learn"], "https://github.com/shard-c6"),
    ("live-pong-rl", "Learns Pong from scratch at 365K frames/s, live", ["pytorch", "rl", "websockets"], "https://github.com/shard-c6"),
]

ROADMAP = [  # (when, title, subtitle, state)  state: done | now | next
    ("2024", "B.Tech CE", "VIT Mumbai · 9.5 CGPA", "done"),
    ("2025", "Open source", "opensre · GreenGuard", "done"),
    ("2026", "Hackathons", "SIH lead · Amazon ML", "done"),
    ("NOW", "MOSIP Decode", "Conformance automation", "now"),
    ("2027", "GSoC", "+ ML / data internship", "next"),
    ("GOAL", "ML / Data Engineer", "systems, end to end", "next"),
]

STATUS = [  # (job, description, state)  state: pass | run | queue
    ("sih-2026/netforecast", "Team lead · unseen-attack detection, AUC 0.984", "pass"),
    ("amazon-ml-2026", "Entity resolution · macro F0.5 0.882", "pass"),
    ("mosip-decode", "OpenID conformance automation", "run"),
    ("opensre", "Open-source contributions", "run"),
    ("gsoc-2027", "Researching orgs · drafting proposal", "queue"),
    ("internships", "ML / data engineering — let's talk", "queue"),
]

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
MODE = "light"  # set by the writer loop below


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


# ── A · PIPELINE ─────────────────────────────────────────────────────────────
def hero_pipeline():
    W, H = 1200, 340
    px, py, pw, ph = 648, 14, 552, 312
    nw, nh = 112, 48
    cols = [px + 20 + i * 133 for i in range(4)]
    r1, r2 = py + 90, py + 196
    nodes = [  # label, x, y
        ("Records", cols[0], r1), ("ETL", cols[1], r1), ("Postgres", cols[2], r1), ("Model", cols[3], r1),
        ("pcap", cols[0], r2), ("FastAPI", cols[2], r2), ("Dashboard", cols[3], r2),
    ]
    c = lambda x, y: (x + nw // 2, y + nh // 2)
    s2, kf, sp, dl = (c(*n[1:]) for n in nodes[:4])
    se, fe, da = (c(*n[1:]) for n in nodes[4:])
    mid = (r1 + nh + r2) // 2
    paths = [
        (f"M{s2[0]},{s2[1]} H{dl[0]}", 4.2, 3),
        (f"M{se[0]},{se[1]} H{kf[0]} V{kf[1]} H{dl[0]}", 4.2, 2),
        (f"M{dl[0]},{dl[1]} V{da[1]}", 1.6, 1),
        (f"M{dl[0]},{dl[1]} V{mid} H{fe[0]} V{fe[1]}", 2.2, 1),
    ]
    edges, packets = [], []
    for i, (d, dur, n) in enumerate(paths):
        edges.append(f'<path d="{d}" class="nofill s-line" stroke-width="2"/>')
        for k in range(n):
            begin = i * 0.7 + k * dur / n
            packets.append(
                f'<circle r="4.5" class="acc" opacity="0"><set attributeName="opacity" to="1" begin="{begin:.2f}s"/>'
                f'<animateMotion dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite" path="{d}"/></circle>')
    boxes = []
    for i, (label, x, y) in enumerate(nodes):
        boxes.append(
            f'<g class="rise" style="animation-delay:{.4 + i * .06:.2f}s"><rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="10" class="bg s-line" stroke-width="1.5"/>'
            f'<text x="{x + nw / 2}" y="{y + 30}" text-anchor="middle" class="sans ink" font-size="16" font-weight="600">{label}</text></g>')
    stages = ["ingest", "transform", "store", "learn"]
    stage_lbl = "".join(
        f'<text x="{cols[i] + nw / 2}" y="{r1 - 16}" text-anchor="middle" class="mono faint" font-size="13">{s}</text>' for i, s in enumerate(stages))
    body = f"""
{intro("ML · DATA ENGINEERING", ["I build ML and data systems end to end —", "from messy raw data to models in production."])}
<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="16" class="panel s-line" stroke-width="1.5"/>
<text x="{px + 22}" y="{py + 34}" class="mono muted" font-size="15">pipeline.dag</text>
<circle cx="{px + pw - 96}" cy="{py + 29}" r="5" class="acc pulse"/>
<text x="{px + pw - 84}" y="{py + 34}" class="mono muted" font-size="15">running</text>
<line x1="{px}" y1="{py + 52}" x2="{px + pw}" y2="{py + 52}" class="s-line" stroke-width="1.5"/>
{stage_lbl}
{''.join(edges)}
<g class="motion">{''.join(packets)}</g>
{''.join(boxes)}
<text x="{px + 22}" y="{py + ph - 20}" class="mono faint" font-size="13">ETL/ELT · PostgreSQL · PyTorch · FastAPI</text>
"""
    return svg(W, H, f"{NAME} — ML and data engineer building systems end to end", body, "blue")


def card(name, desc, tags, i):
    W, H = 560, 168
    pills, x = [], 28
    for t in tags:
        w = round(len(t) * 8.4 + 22)
        pills.append(f'<rect x="{x}" y="118" width="{w}" height="28" rx="14" class="panel s-line"/>'
                     f'<text x="{x + 11}" y="137" class="mono muted" font-size="14">{t}</text>')
        x += w + 8
    body = f"""
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" class="bg s-line" stroke-width="1.5"/>
<rect x="1" y="24" width="3" height="40" rx="1.5" class="acc"><animate attributeName="height" from="0" to="40" dur=".9s" begin="{i * .15:.2f}s" fill="freeze" calcMode="spline" keySplines=".2 .7 .2 1"/></rect>
<text x="28" y="54" class="sans ink" font-size="24" font-weight="600">{name}</text>
<text x="{W - 28}" y="54" text-anchor="end" class="sans faint" font-size="22">↗</text>
<text x="28" y="90" class="sans muted" font-size="18">{desc}</text>
{''.join(pills)}
"""
    return svg(W, H, f"{name}: {desc}", body, "blue")


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


# ── C · TERMINAL ─────────────────────────────────────────────────────────────
def hero_terminal():
    W, H = 1200, 392
    fs, cw, lh = 21, 21 * 0.6, 35
    tx, ty = 40, 106
    lines = [
        ("cmd", "whoami"),
        ("out", f"{NAME} — ML &amp; data engineer · CE @ VIT Mumbai"),
        ("cmd", "cat profile.yaml"),
        ("kv", ("role:", "ML / Data Engineer")),
        ("kv", ("focus:", "ML systems · data pipelines · network security")),
        ("kv", ("stack:", "python, sql, pytorch, postgres, fastapi, aws")),
        ("kv", ("open_to:", "gsoc-2027, ml-data-internships")),
    ]
    t, out, defs = 0.5, [], []
    for i, (kind, val) in enumerate(lines):
        y = ty + i * lh
        if kind == "cmd":
            text = f'<tspan class="acc">$</tspan> {val}'
            n = len(val) + 2
            vals = ";".join(f"{(k + 2) * cw:.1f}" for k in range(n - 1)) + f";{W}"
            anim = f'<animate attributeName="width" values="{vals}" begin="{t:.2f}s" dur="{len(val) * .07:.2f}s" fill="freeze" calcMode="discrete"/>'
            t += len(val) * .07 + .35
        else:
            text = (f'<tspan class="muted">{val[0]:<9}</tspan>{val[1]}' if kind == "kv" else val).replace("  ", "  ")
            if kind == "kv":
                text = f'<tspan class="muted" xml:space="preserve">{val[0].ljust(9)}</tspan>{val[1]}'
            anim = f'<animate attributeName="width" values="0;{W}" begin="{t:.2f}s" dur=".01s" fill="freeze"/>'
            t += .12 if kind == "kv" else .3
        defs.append(f'<clipPath id="l{i}"><rect x="{tx - 4}" y="{y - fs}" width="0" height="{lh}">{anim}</rect></clipPath>')
        out.append(f'<text x="{tx}" y="{y}" class="mono ink" font-size="{fs}" clip-path="url(#l{i})" xml:space="preserve">{text}</text>')
    yl = ty + len(lines) * lh
    t += .2
    out.append(f'<g opacity="0"><animate attributeName="opacity" to="1" begin="{t:.2f}s" dur=".01s" fill="freeze"/>'
               f'<text x="{tx}" y="{yl}" class="mono acc" font-size="{fs}">$</text>'
               f'<rect x="{tx + 2 * cw:.1f}" y="{yl - fs + 3}" width="{cw:.1f}" height="{fs + 2}" class="ink pulse" style="animation-duration:1.1s"/></g>')
    body = f"""
<defs>{''.join(defs)}</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" class="bg s-line" stroke-width="1.5"/>
<path d="M1,15 a14,14 0 0 1 14,-14 H{W - 15} a14,14 0 0 1 14,14 V50 H1 Z" class="panel"/>
<line x1="1" y1="50" x2="{W - 1}" y2="50" class="s-line" stroke-width="1.5"/>
{''.join(f'<circle cx="{28 + k * 22}" cy="26" r="6" class="nofill s-faint" stroke-width="1.5"/>' for k in range(3))}
<text x="{W / 2}" y="31" text-anchor="middle" class="mono muted" font-size="15">~/shardul — zsh</text>
{''.join(out)}
"""
    return svg(W, H, f"Terminal: {NAME}, ML and data engineer. Open to GSoC 2027 and ML / data engineering internships.", body, "green")


def status_board():
    W, rh, top = 1200, 58, 70
    H = top + len(STATUS) * rh + 14
    extra = """.spin{transform-box:fill-box;transform-origin:center;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.bar{animation:bar 2.2s cubic-bezier(.6,0,.4,1) infinite}
@keyframes bar{from{transform:translateX(-70px)}to{transform:translateX(190px)}}"""
    running = sum(s == "run" for *_, s in STATUS)
    passed = sum(s == "pass" for *_, s in STATUS)
    rows = [
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" class="bg s-line" stroke-width="1.5"/>',
        f'<text x="28" y="40" class="mono ink" font-size="17" font-weight="600">currently.yml</text>',
        f'<text x="{W - 28}" y="40" text-anchor="end" class="mono muted" font-size="15">{passed} passing · {running} running · {len(STATUS) - passed - running} queued</text>',
        f'<line x1="1" y1="{top - 8}" x2="{W - 1}" y2="{top - 8}" class="s-line" stroke-width="1.5"/>',
    ]
    for i, (job, desc, state) in enumerate(STATUS):
        y = top + i * rh
        cy = y + rh / 2 - 4
        g = [f'<g class="rise" style="animation-delay:{.15 + i * .12:.2f}s">']
        if i:
            g.append(f'<line x1="28" y1="{y - 4}" x2="{W - 28}" y2="{y - 4}" class="s-line"/>')
        if state == "pass":
            g.append(f'<circle cx="42" cy="{cy}" r="11" class="acc"/><path d="M36.5,{cy} l4,4 l7,-8" class="nofill s-bg" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
            st, sc = "passing", "acc"
        elif state == "run":
            g.append(f'<circle cx="42" cy="{cy}" r="10" class="nofill s-line" stroke-width="2.4"/>'
                     f'<path d="M42,{cy - 10} a10,10 0 0 1 10,10" class="nofill s-warn spin" stroke-width="2.4" stroke-linecap="round"/>')
            st, sc = "running", "warn"
            g.append(f'<clipPath id="b{i}"><rect x="900" y="{cy - 3}" width="140" height="6" rx="3"/></clipPath>'
                     f'<rect x="900" y="{cy - 3}" width="140" height="6" rx="3" class="panel s-line"/>'
                     f'<g clip-path="url(#b{i})"><rect x="900" y="{cy - 3}" width="70" height="6" rx="3" class="warn bar" style="animation-delay:{i * .3:.1f}s"/></g>')
        else:
            g.append(f'<circle cx="42" cy="{cy}" r="10" class="nofill s-faint" stroke-width="2" stroke-dasharray="3 3.3"/>')
            st, sc = "queued", "faint"
        g.append(f'<text x="72" y="{cy + 6}" class="mono ink" font-size="17">{job}</text>')
        g.append(f'<text x="380" y="{cy + 6}" class="sans muted" font-size="17">{desc}</text>')
        g.append(f'<text x="{W - 28}" y="{cy + 6}" text-anchor="end" class="mono {sc}" font-size="15">{st}</text>')
        g.append('</g>')
        rows.append("".join(g))
    return svg(W, H, "Currently: " + "; ".join(f"{j} ({s})" for j, _, s in STATUS), "\n".join(rows), "green", extra)


# ── WRITE ────────────────────────────────────────────────────────────────────
def write(rel, content):
    p = ROOT / rel.replace(".svg", f"-{MODE}.svg")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", p.relative_to(ROOT.parent))


def build():
    write("a-pipeline/assets/hero.svg", hero_pipeline())
    for i, (n, d, t, _) in enumerate(PROJECTS):
        write(f"a-pipeline/assets/card-{n.lower().replace(' ', '-')}.svg", card(n, d, t, i))
    write("b-signal/assets/hero.svg", hero_signal())
    write("b-signal/assets/roadmap.svg", roadmap())
    write("c-terminal/assets/hero.svg", hero_terminal())
    write("c-terminal/assets/currently.svg", status_board())


if __name__ == "__main__":
    for MODE in ("light", "dark"):
        build()
