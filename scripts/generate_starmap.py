#!/usr/bin/env python3
"""
Generate a Star Map SVG — GitHub contributions rendered as a constellation
with twinkling stars, nebula effects, and connecting lines.
"""

import random
import math
import hashlib

# --- Configuration ---
WIDTH = 900
HEIGHT = 500
NUM_BG_STARS = 120          # tiny background stars
NUM_CONSTELLATION_STARS = 18  # main "contribution" stars
NUM_NEBULA_BLOBS = 8        # soft nebula clouds
SEED = 42                   # for reproducibility

SKILLS = [
    "Python", "Kafka", "Spark", "Docker", "K8s",
    "FastAPI", "React", "AWS", "Azure", "GCP",
    "TensorFlow", "PostgreSQL", "MongoDB", "Git",
    "NumPy", "Pandas", "Hadoop", "Snowflake"
]

PROJECTS = [
    ("EVNet Sentinel", "🔋"),
    ("GreenGuard", "🌿"),
    ("PaperTrail", "📄"),
    ("dehelpers", "🤝"),
]

def generate_svg():
    random.seed(SEED)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">
  <defs>
    <!-- Nebula gradient -->
    <radialGradient id="nebula1" cx="30%" cy="40%" r="40%">
      <stop offset="0%" stop-color="#6366f1" stop-opacity="0.15"/>
      <stop offset="50%" stop-color="#8b5cf6" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="#0d1117" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="nebula2" cx="70%" cy="60%" r="35%">
      <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.12"/>
      <stop offset="50%" stop-color="#0891b2" stop-opacity="0.06"/>
      <stop offset="100%" stop-color="#0d1117" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="nebula3" cx="50%" cy="30%" r="30%">
      <stop offset="0%" stop-color="#ec4899" stop-opacity="0.1"/>
      <stop offset="50%" stop-color="#be185d" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="#0d1117" stop-opacity="0"/>
    </radialGradient>

    <!-- Star glow filter -->
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="glow-strong" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="nebula-blur" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="30"/>
    </filter>

    <style>
      @keyframes twinkle {{
        0%, 100% {{ opacity: 0.3; }}
        50% {{ opacity: 1; }}
      }}
      @keyframes twinkle-slow {{
        0%, 100% {{ opacity: 0.5; }}
        50% {{ opacity: 0.9; }}
      }}
      @keyframes pulse {{
        0%, 100% {{ r: 3; opacity: 0.8; }}
        50% {{ r: 4.5; opacity: 1; }}
      }}
      @keyframes drift {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-3px); }}
      }}
      .bg {{ fill: #0d1117; }}
      .bg-star {{
        fill: #ffffff;
        opacity: 0.4;
      }}
      .constellation-star {{
        fill: #39FF14;
        filter: url(#glow);
      }}
      .project-star {{
        fill: #00d9ff;
        filter: url(#glow-strong);
      }}
      .constellation-line {{
        stroke: #39FF14;
        stroke-width: 0.5;
        stroke-opacity: 0.25;
        stroke-dasharray: 4 4;
      }}
      .label {{
        font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
        font-size: 9px;
        fill: #8b949e;
        text-anchor: middle;
      }}
      .project-label {{
        font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
        font-size: 11px;
        fill: #00d9ff;
        font-weight: bold;
        text-anchor: middle;
      }}
      .title {{
        font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
        font-size: 11px;
        fill: #484f58;
        text-anchor: end;
        letter-spacing: 2px;
        text-transform: uppercase;
      }}
      .coord {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 7px;
        fill: #30363d;
        text-anchor: start;
      }}
    </style>
  </defs>

  <!-- Deep space background -->
  <rect width="100%" height="100%" class="bg"/>

  <!-- Nebula clouds -->
  <ellipse cx="{WIDTH*0.3}" cy="{HEIGHT*0.4}" rx="250" ry="180" fill="url(#nebula1)" filter="url(#nebula-blur)"/>
  <ellipse cx="{WIDTH*0.7}" cy="{HEIGHT*0.6}" rx="200" ry="150" fill="url(#nebula2)" filter="url(#nebula-blur)"/>
  <ellipse cx="{WIDTH*0.5}" cy="{HEIGHT*0.25}" rx="180" ry="120" fill="url(#nebula3)" filter="url(#nebula-blur)"/>
'''

    # --- Background stars (tiny twinkling dots) ---
    for i in range(NUM_BG_STARS):
        x = random.randint(5, WIDTH - 5)
        y = random.randint(5, HEIGHT - 5)
        r = random.uniform(0.3, 1.2)
        dur = random.uniform(2, 6)
        delay = random.uniform(0, 5)
        opacity = random.uniform(0.2, 0.7)
        svg += f'  <circle cx="{x}" cy="{y}" r="{r}" class="bg-star" style="animation: twinkle {dur}s {delay}s ease-in-out infinite; opacity: {opacity}"/>\n'

    # --- Constellation stars (skills) ---
    # Place them in a pleasing scattered pattern
    margin = 70
    constellation_points = []
    for i, skill in enumerate(SKILLS):
        attempts = 0
        while attempts < 100:
            x = random.randint(margin, WIDTH - margin)
            y = random.randint(margin + 20, HEIGHT - margin - 10)
            # Ensure minimum distance from other points
            too_close = False
            for px, py, _ in constellation_points:
                if math.sqrt((x - px)**2 + (y - py)**2) < 80:
                    too_close = True
                    break
            if not too_close:
                break
            attempts += 1
        constellation_points.append((x, y, skill))

    # --- Draw constellation lines (connect nearby stars) ---
    svg += '\n  <!-- Constellation Lines -->\n'
    connections = []
    for i in range(len(constellation_points)):
        distances = []
        for j in range(len(constellation_points)):
            if i != j:
                dx = constellation_points[i][0] - constellation_points[j][0]
                dy = constellation_points[i][1] - constellation_points[j][1]
                dist = math.sqrt(dx*dx + dy*dy)
                distances.append((dist, j))
        distances.sort()
        # Connect to 1-2 nearest neighbors
        for dist, j in distances[:2]:
            if dist < 300:
                pair = tuple(sorted([i, j]))
                if pair not in connections:
                    connections.append(pair)
                    x1, y1 = constellation_points[i][0], constellation_points[i][1]
                    x2, y2 = constellation_points[j][0], constellation_points[j][1]
                    svg += f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="constellation-line"/>\n'

    # --- Draw constellation stars with labels ---
    svg += '\n  <!-- Skill Stars -->\n'
    for i, (x, y, skill) in enumerate(constellation_points):
        r = random.uniform(2, 4)
        dur = random.uniform(3, 7)
        delay = random.uniform(0, 4)
        svg += f'  <circle cx="{x}" cy="{y}" r="{r}" class="constellation-star" style="animation: pulse {dur}s {delay}s ease-in-out infinite"/>\n'
        svg += f'  <text x="{x}" y="{y + 16}" class="label">{skill}</text>\n'

    # --- Project stars (bigger, brighter, cyan) ---
    svg += '\n  <!-- Project Stars -->\n'
    project_positions = [
        (WIDTH * 0.2, HEIGHT * 0.2),
        (WIDTH * 0.8, HEIGHT * 0.15),
        (WIDTH * 0.15, HEIGHT * 0.8),
        (WIDTH * 0.85, HEIGHT * 0.75),
    ]
    for i, ((name, emoji), (px, py)) in enumerate(zip(PROJECTS, project_positions)):
        dur = random.uniform(4, 8)
        delay = random.uniform(0, 3)
        svg += f'  <circle cx="{px}" cy="{py}" r="5" class="project-star" style="animation: pulse {dur}s {delay}s ease-in-out infinite"/>\n'
        svg += f'  <text x="{px}" y="{py - 12}" class="project-label">{emoji} {name}</text>\n'

    # --- Decorative grid coordinates (like a star chart) ---
    svg += '\n  <!-- Grid coordinates -->\n'
    for gx in range(0, WIDTH, 150):
        for gy in range(0, HEIGHT, 150):
            ra = f"{random.randint(0,23)}h{random.randint(0,59)}m"
            dec = f"+{random.randint(0,90)}°{random.randint(0,59)}'"
            svg += f'  <text x="{gx + 5}" y="{gy + 12}" class="coord">{ra} {dec}</text>\n'

    # --- Title overlay ---
    svg += f'''
  <!-- Title -->
  <text x="{WIDTH - 20}" y="25" class="title">shard-c6 · tech constellation</text>
  <text x="{WIDTH - 20}" y="40" class="title" style="font-size: 8px; fill: #30363d;">EPOCH {random.randint(2400000, 2500000)}.{random.randint(100,999)} · EQUINOX J2026.0</text>

</svg>'''

    with open("assets/starmap.svg", "w") as f:
        f.write(svg)

    print("Star Map SVG generated!")

if __name__ == "__main__":
    generate_svg()
