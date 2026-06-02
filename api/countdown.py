from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
import io
import os

# Placeholder: 24 hour countdown from a fixed start time
# This will be made dynamic per subscriber later
HOURS = 24

def make_tile(draw, digit, x, y, tile_w, tile_h, font):
    padding = 4
    draw.rounded_rectangle(
        [x, y, x + tile_w, y + tile_h],
        radius=6,
        fill=(30, 30, 30)
    )
    bbox = draw.textbbox((0, 0), digit, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    tx = x + (tile_w - text_w) / 2
    ty = y + (tile_h - text_h) / 2 - bbox[1]
    draw.text((tx, ty), digit, fill=(255, 255, 255), font=font)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        total_seconds = HOURS * 3600

        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'DMSans-VariableFont_opsz,wght.ttf')
        try:
            font_digit = ImageFont.truetype(font_path, size=36)
            font_digit.set_variation_by_axes([36, 700])
            font_label = ImageFont.truetype(font_path, size=12)
            font_label.set_variation_by_axes([12, 400])
        except:
            font_digit = ImageFont.load_default()
            font_label = font_digit

        tile_w = 64
        tile_h = 64
        gap = 12
        colon_w = 20
        label_h = 20
        padding_x = 40
        img_w = 600
        img_h = tile_h + label_h + 20

        frames = []
        for i in range(10):
            secs = max(0, total_seconds - i)
            s = secs % 60
            m = (secs // 60) % 60
            h = secs // 3600

            img = Image.new("RGB", (img_w, img_h), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)

            # Calculate total width for centering
            total_w = (tile_w * 3) + (colon_w * 2) + (gap * 4)
            start_x = (img_w - total_w) / 2
            tile_y = 10

            units = [
                (f"{h:02d}", "Hours"),
                (f"{m:02d}", "Minutes"),
                (f"{s:02d}", "Seconds"),
            ]

            x = start_x
            for idx, (digits, label) in enumerate(units):
                # Draw tile
                make_tile(draw, digits, x, tile_y, tile_w, tile_h, font_digit)

                # Draw label
                lbbox = draw.textbbox((0, 0), label, font=font_label)
                lw = lbbox[2] - lbbox[0]
                lx = x + (tile_w - lw) / 2
                draw.text((lx, tile_y + tile_h + 4), label, fill=(100, 100, 100), font=font_label)

                x += tile_w + gap

                # Draw colon between tiles
                if idx < 2:
                    cbbox = draw.textbbox((0, 0), ":", font=font_digit)
                    cw = cbbox[2] - cbbox[0]
                    ch = cbbox[3] - cbbox[1]
                    cx = x + (colon_w - cw) / 2
                    cy = tile_y + (tile_h - ch) / 2 - cbbox[1]
                    draw.text((cx, cy), ":", fill=(30, 30, 30), font=font_digit)
                    x += colon_w + gap

            frames.append(img)

        buf = io.BytesIO()
        frames[0].save(
            buf,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=1000,
            optimize=False
        )
        buf.seek(0)
        gif_data = buf.read()

        self.send_response(200)
        self.send_header('Content-Type', 'image/gif')
        self.send_header('Cache-Control', 'public, max-age=60, s-maxage=60')
        self.end_headers()
        self.wfile.write(gif_data)
