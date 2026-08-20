import sys
import requests
from PIL import Image
from io import BytesIO

def get_avatar(username="shard-c6"):
    url = f"https://github.com/{username}.png"
    print(f"Fetching {url}")
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))

def to_ascii_svg(image, width=100, height=None, output_path="assets/avi-ascii.svg"):
    # ASCII chars sorted from darkest to lightest
    ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']

    # Resize image
    aspect_ratio = image.height / image.width
    # Adjust for character aspect ratio (characters are generally taller than they are wide)
    char_aspect_ratio = 2.0 
    
    if height is None:
        height = int((aspect_ratio * width) / char_aspect_ratio)
        
    image = image.resize((width, height)).convert("L")

    # Handle DeprecationWarning in Pillow 14
    try:
        pixels = image.get_flattened_data()
    except AttributeError:
        pixels = image.getdata()
        
    ascii_str = ""
    for pixel_val in pixels:
        # 0-255 mapped to 0-10
        idx = pixel_val // 25
        if idx >= len(ASCII_CHARS):
            idx = len(ASCII_CHARS) - 1
        ascii_str += ASCII_CHARS[idx]

    # Break string into lines
    ascii_str_len = len(ascii_str)
    ascii_img = ""
    for i in range(0, ascii_str_len, width):
        ascii_img += ascii_str[i:i+width] + "\n"

    # SVG generation
    font_size = 12
    line_height = 14
    svg_width = width * 7.2 + 40 # Add padding
    
    # Calculate height: macbook header (40px) + content + padding
    lines = ascii_img.split('\n')
    lines = [line for line in lines if line.strip()]
    content_height = len(lines) * line_height
    svg_height = content_height + 60 

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <style>
    .text {{
      font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', Courier, monospace;
      font-size: {font_size}px;
      font-weight: bold;
      fill: #39FF14; /* Neon Green */
      white-space: pre;
      opacity: 0;
      animation: type 0.1s forwards;
    }}
    .terminal-bg {{
      fill: #1E1E1E;
    }}
    .header-bg {{
      fill: #2D2D2D;
    }}
    .title {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 13px;
      fill: #A0A0A0;
      font-weight: 500;
    }}
    @keyframes type {{
      from {{ opacity: 0; transform: translateX(-5px); }}
      to {{ opacity: 1; transform: translateX(0); }}
    }}
'''
    
    # Generate animation delays for each line
    for i in range(len(lines)):
        delay = 0.5 + (i * 0.05) # Start after 0.5s, 50ms per line
        svg_content += f"    .line-{i} {{ animation-delay: {delay}s; }}\n"

    svg_content += '''  </style>
  
  <!-- Terminal Window -->
  <rect width="100%" height="100%" rx="10" class="terminal-bg" />
  
  <!-- MacBook Header -->
  <path d="M 0 10 C 0 4.477 4.477 0 10 0 L {w} 0 C {w_minus_10} 0 {w} 4.477 {w} 10 L {w} 30 L 0 30 Z" class="header-bg" />
  
  <!-- Window Buttons -->
  <circle cx="20" cy="15" r="6" fill="#FF5F56" />
  <circle cx="40" cy="15" r="6" fill="#FFBD2E" />
  <circle cx="60" cy="15" r="6" fill="#27C93F" />
  
  <!-- Title -->
  <text x="50%" y="20" text-anchor="middle" class="title">shard-c6@macbook:~</text>
  
  <!-- Command prompt before typing avatar -->
  <text x="20" y="55" class="text" style="fill: #00d9ff; animation-delay: 0.1s; opacity: 0; animation: type 0.1s forwards;">$ cat avatar.txt</text>
  
  <!-- ASCII Content -->
  <g transform="translate(20, 75)">
'''.replace("{w}", str(svg_width)).replace("{w_minus_10}", str(svg_width - 10))
    
    # Add each line
    for idx, line in enumerate(lines):
        y_pos = idx * line_height
        svg_content += f'    <text x="0" y="{y_pos}" class="text line-{idx}">{line}</text>\n'

    svg_content += '''  </g>
</svg>'''

    with open(output_path, "w") as f:
        f.write(svg_content)
    
    print(f"ASCII SVG generated at {output_path}")

if __name__ == "__main__":
    img = get_avatar()
    to_ascii_svg(img, width=60)
