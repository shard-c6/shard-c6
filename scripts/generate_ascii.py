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
    # Estimate sizes based on standard monospace font
    font_size = 12
    line_height = 14
    svg_width = width * 7.2  # Approx character width
    svg_height = height * line_height + 20

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <style>
    .text {{
      font-family: 'Courier New', Courier, monospace;
      font-size: {font_size}px;
      font-weight: bold;
      fill: #00d9ff;
      white-space: pre;
    }}
    rect {{
      fill: #0d1117;
    }}
  </style>
  <rect width="100%" height="100%" rx="10"/>
'''
    
    # Add each line as a tspan or text element
    lines = ascii_img.split('\n')
    for idx, line in enumerate(lines):
        if not line.strip():
            continue
        y_pos = 20 + (idx * line_height)
        svg_content += f'  <text x="10" y="{y_pos}" class="text">{line}</text>\n'

    svg_content += '</svg>'

    with open(output_path, "w") as f:
        f.write(svg_content)
    
    print(f"ASCII SVG generated at {output_path}")

if __name__ == "__main__":
    img = get_avatar()
    to_ascii_svg(img, width=60)
