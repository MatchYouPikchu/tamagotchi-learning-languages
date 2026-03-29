"""Generate visual catalog of all pet designer options as an HTML page."""

import os
import base64
import io

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

import math
from pet import Pet
from drawing import PetDrawer, _inflate_triangle, BLACK, OUTLINE_WIDTH
from settings import PET_CAT, PET_DOG, DESIGN_THEMES

import drawing as drawing_module


# ---- Proposed improved fur styles (monkey-patched for preview only) ----

def _proposed_draw_fur_style(self, surface, fur_style, head_x, head_cy, head_r, s, colors):
    """PROPOSED improved fur drawing — for catalog preview only."""
    if not fur_style or fur_style == "short":
        return
    body_color = colors["body"]
    body_dark = colors["body_dark"]
    accent = colors.get("ear_inner", body_dark)

    if fur_style == "fluffy":
        puffs = []
        for i in range(5):
            angle = math.pi * 0.2 + (math.pi * 0.6) * i / 4
            cx_f = head_x + int(math.cos(angle) * head_r * 0.5)
            cy_f = head_cy - int(math.sin(angle) * head_r * 1.05)
            puffs.append((cx_f, cy_f, int(8 * s)))
        for i in range(3):
            angle = math.pi * 0.3 + (math.pi * 0.4) * i / 2
            cx_f = head_x + int(math.cos(angle) * head_r * 0.35)
            cy_f = head_cy - int(math.sin(angle) * head_r * 1.15)
            puffs.append((cx_f, cy_f, int(6 * s)))
        for cx_f, cy_f, r in puffs:
            pygame.draw.circle(surface, BLACK, (cx_f, cy_f), r + OUTLINE_WIDTH)
        for cx_f, cy_f, r in puffs:
            pygame.draw.circle(surface, body_color, (cx_f, cy_f), r)

    elif fur_style == "long":
        for side in [-1, 1]:
            pts = []
            start_x = head_x + side * int(5 * s)
            for t_step in range(12):
                t = t_step / 11
                px = start_x + side * int(t * 18 * s + math.sin(t * 2) * 4 * s)
                py = head_cy - head_r + int(t * head_r * 1.6)
                pts.append((int(px), int(py)))
            if len(pts) > 1:
                pygame.draw.lines(surface, BLACK, False, pts, int(5 * s) + OUTLINE_WIDTH * 2)
                pygame.draw.lines(surface, body_dark, False, pts, int(5 * s))
            pts2 = []
            start_x2 = head_x + side * int(2 * s)
            for t_step in range(9):
                t = t_step / 8
                px = start_x2 + side * int(t * 12 * s + math.sin(t * 1.5) * 3 * s)
                py = head_cy - head_r + int(2 * s) + int(t * head_r * 1.1)
                pts2.append((int(px), int(py)))
            if len(pts2) > 1:
                pygame.draw.lines(surface, BLACK, False, pts2, int(4 * s) + OUTLINE_WIDTH * 2)
                pygame.draw.lines(surface, body_dark, False, pts2, int(4 * s))
        tuft_pts = []
        for i in range(5):
            angle = math.pi * 0.25 + (math.pi * 0.5) * i / 4
            cx_f = head_x + int(math.cos(angle) * head_r * 0.4)
            cy_f = head_cy - int(math.sin(angle) * head_r * 1.05)
            tuft_pts.append((cx_f, cy_f))
        for cx_f, cy_f in tuft_pts:
            pygame.draw.circle(surface, BLACK, (cx_f, cy_f), int(5 * s) + OUTLINE_WIDTH)
        for cx_f, cy_f in tuft_pts:
            pygame.draw.circle(surface, body_dark, (cx_f, cy_f), int(5 * s))

    elif fur_style == "curly":
        curls = []
        for i in range(5):
            angle = math.pi * 0.18 + (math.pi * 0.64) * i / 4
            cx_f = head_x + int(math.cos(angle) * head_r * 0.55)
            cy_f = head_cy - int(math.sin(angle) * head_r * 0.95)
            curls.append((cx_f, cy_f, int(6 * s)))
        for i in range(4):
            angle = math.pi * 0.22 + (math.pi * 0.56) * i / 3
            cx_f = head_x + int(math.cos(angle) * head_r * 0.4)
            cy_f = head_cy - int(math.sin(angle) * head_r * 1.08)
            curls.append((cx_f, cy_f, int(5 * s)))
        for cx_f, cy_f, r in curls:
            pygame.draw.circle(surface, BLACK, (cx_f, cy_f), r + OUTLINE_WIDTH)
        for cx_f, cy_f, r in curls:
            pygame.draw.circle(surface, body_dark, (cx_f, cy_f), r)

    elif fur_style == "spiky":
        for i in range(5):
            angle = math.pi * 0.2 + (math.pi * 0.6) * i / 4
            base_x = head_x + int(math.cos(angle) * head_r * 0.5)
            base_y = head_cy - int(math.sin(angle) * head_r * 0.88)
            spike_h = int((12 + (i % 2) * 8) * s)
            hw = int(4 * s)
            tri = [
                (base_x - hw, base_y),
                (base_x + hw, base_y),
                (base_x, base_y - spike_h),
            ]
            pygame.draw.polygon(surface, BLACK, _inflate_triangle(tri, OUTLINE_WIDTH))
            pygame.draw.polygon(surface, body_dark, tri)

    elif fur_style == "mohawk":
        mohawk_pts = []
        for i in range(7):
            t = i / 6
            cy_f = head_cy - head_r + int((-6 + t * 18) * s)
            r = int((6 - abs(t - 0.35) * 6) * s)
            r = max(int(3 * s), r)
            mohawk_pts.append((head_x, cy_f, r))
        for cx_f, cy_f, r in mohawk_pts:
            pygame.draw.circle(surface, BLACK, (cx_f, cy_f), r + OUTLINE_WIDTH)
        for cx_f, cy_f, r in mohawk_pts:
            pygame.draw.circle(surface, accent, (cx_f, cy_f), r)


# Monkey-patch for catalog preview
PetDrawer._draw_fur_style = _proposed_draw_fur_style

CELL_W = 120
CELL_H = 150
BG_COLOR = (35, 20, 65)

# Original drawing constants (pet renders at these coords on a 480x640 canvas)
ORIG_CX = drawing_module.PET_CENTER_X
ORIG_CY = drawing_module.PET_CENTER_Y


def render_pet(pet_type, appearance_overrides=None, label=""):
    """Render a single pet to a base64 PNG string."""
    # Render on full-size canvas so drawing code works unchanged
    full = pygame.Surface((480, 640))
    full.fill(BG_COLOR)

    drawer = PetDrawer()
    pet = Pet(pet_type)
    pet.appearance["body_color"] = [200, 170, 120] if pet_type == PET_CAT else [180, 150, 90]
    pet.appearance["accent_color"] = [255, 200, 100]

    if appearance_overrides:
        for k, v in appearance_overrides.items():
            pet.appearance[k] = v

    drawer.draw(full, pet)

    # Crop around the pet center
    crop_x = ORIG_CX - CELL_W // 2
    crop_y = ORIG_CY - CELL_H // 2 - 10
    cell = pygame.Surface((CELL_W, CELL_H))
    cell.blit(full, (0, 0), (crop_x, crop_y, CELL_W, CELL_H))

    # Convert to PNG base64
    buf = io.BytesIO()
    pygame.image.save(cell, buf, "catalog.png")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("ascii")
    return b64


def render_theme(theme_name, pet_type):
    """Render a theme preset."""
    theme = DESIGN_THEMES[theme_name]
    return render_pet(pet_type, theme)


def make_section(title, description, options, field_name, pet_types=None):
    """Generate HTML for one feature section."""
    if pet_types is None:
        pet_types = [PET_CAT, PET_DOG]

    html = f'<div class="section">\n'
    html += f'  <h2>{title}</h2>\n'
    html += f'  <p class="desc">{description}</p>\n'
    html += f'  <div class="grid">\n'

    for opt in options:
        label = str(opt) if opt is not None else "none (default)"
        for pt in pet_types:
            overrides = {field_name: opt}
            # For patterns, add a pattern_color
            if field_name == "pattern" and opt not in (None, "solid"):
                overrides["pattern_color"] = [160, 100, 60]
            b64 = render_pet(pt, overrides)
            pt_label = "cat" if pt == PET_CAT else "dog"
            html += f'    <div class="cell">\n'
            html += f'      <img src="data:image/png;base64,{b64}" />\n'
            html += f'      <div class="label">{label}</div>\n'
            html += f'      <div class="sublabel">{pt_label}</div>\n'
            html += f'    </div>\n'

    html += f'  </div>\n'
    html += f'</div>\n'
    return html


def make_themes_section():
    """Generate HTML for preset themes."""
    html = '<div class="section">\n'
    html += '  <h2>Preset Themes (offline, no LLM needed)</h2>\n'
    html += '  <p class="desc">Quick style presets users can tap. Each applies a coordinated set of colors + accessories.</p>\n'
    html += '  <div class="grid">\n'

    for name in DESIGN_THEMES:
        for pt in [PET_CAT, PET_DOG]:
            b64 = render_theme(name, pt)
            pt_label = "cat" if pt == PET_CAT else "dog"
            html += f'    <div class="cell">\n'
            html += f'      <img src="data:image/png;base64,{b64}" />\n'
            html += f'      <div class="label">{name}</div>\n'
            html += f'      <div class="sublabel">{pt_label}</div>\n'
            html += f'    </div>\n'

    html += '  </div>\n'
    html += '</div>\n'
    return html


def make_combo_section():
    """Show a few interesting combos."""
    combos = [
        ("Fluffy Princess", PET_CAT, {
            "body_color": [240, 180, 200], "accent_color": [255, 255, 255],
            "fur_style": "fluffy", "tail_style": "ribbon", "eye_style": "sparkly",
            "ear_style": "round", "hat": "flower", "special": "rosy_cheeks",
        }),
        ("Punk Rocker", PET_CAT, {
            "body_color": [60, 60, 70], "accent_color": [255, 50, 80],
            "fur_style": "mohawk", "tail_style": "short", "eye_style": "sleepy",
            "ear_style": "pointy", "collar": "bandana",
        }),
        ("Wise Scholar", PET_DOG, {
            "body_color": [140, 100, 60], "accent_color": [200, 180, 140],
            "fur_style": "curly", "tail_style": "long", "eye_style": "dot",
            "ear_style": "floppy", "glasses": "round", "hat": "tophat",
        }),
        ("Magical Fox", PET_CAT, {
            "body_color": [220, 120, 50], "accent_color": [255, 220, 100],
            "fur_style": "spiky", "tail_style": "fluffy", "eye_style": "big",
            "ear_style": "big", "special": "sparkle_eyes",
        }),
        ("Royal Pup", PET_DOG, {
            "body_color": [160, 50, 60], "accent_color": [255, 210, 80],
            "fur_style": "long", "tail_style": "ribbon", "eye_style": "sparkly",
            "ear_style": "round", "hat": "crown", "scarf": "gold",
        }),
        ("Sleepy Gentleman", PET_DOG, {
            "body_color": [80, 80, 100], "accent_color": [200, 200, 220],
            "fur_style": "short", "tail_style": "normal", "eye_style": "sleepy",
            "ear_style": "tiny", "hat": "tophat", "glasses": "monocle",
            "collar": "bowtie",
        }),
        ("Wild Kitty", PET_CAT, {
            "body_color": [100, 180, 80], "accent_color": [255, 255, 100],
            "fur_style": "spiky", "tail_style": "curly", "eye_style": "wink",
            "ear_style": "pointy", "pattern": "stripes", "pattern_color": [60, 120, 40],
        }),
        ("Cloud Puppy", PET_DOG, {
            "body_color": [230, 230, 245], "accent_color": [180, 200, 255],
            "fur_style": "fluffy", "tail_style": "fluffy", "eye_style": "big",
            "ear_style": "round", "special": "star_cheeks",
        }),
    ]

    html = '<div class="section">\n'
    html += '  <h2>Example Combos (what users can create)</h2>\n'
    html += '  <p class="desc">Combinations achieved via LLM text prompts or theme presets. These show the creative range.</p>\n'
    html += '  <div class="grid">\n'

    for name, pt, overrides in combos:
        b64 = render_pet(pt, overrides)
        pt_label = "cat" if pt == PET_CAT else "dog"
        html += f'    <div class="cell wide">\n'
        html += f'      <img src="data:image/png;base64,{b64}" />\n'
        html += f'      <div class="label">{name}</div>\n'
        html += f'      <div class="sublabel">{pt_label}</div>\n'
        html += f'    </div>\n'

    html += '  </div>\n'
    html += '</div>\n'
    return html


def generate_html():
    body = ""

    # Intro
    body += '<div class="intro">\n'
    body += '  <h1>Tamagotchi Pet Designer — Visual Catalog</h1>\n'
    body += '  <p>Complete reference of all appearance options available in the pet designer.<br/>'
    body += '  Users can customize pets via <strong>preset theme chips</strong> (offline) or '
    body += '  <strong>free text descriptions</strong> (LLM-powered, requires API key).</p>\n'
    body += '  <div class="how-it-works">\n'
    body += '    <h3>How Users Design Pets</h3>\n'
    body += '    <table class="info-table">\n'
    body += '      <tr><th>Method</th><th>How</th><th>Requires</th></tr>\n'
    body += '      <tr><td>Theme Chips</td><td>Click one of 6 preset buttons (Magical, Sporty, Cool, Cute, Silly, Royal)</td><td>Nothing — always available</td></tr>\n'
    body += '      <tr><td>LLM Text</td><td>Type a description like "a fluffy pink princess cat" and press Enter</td><td>ANTHROPIC_API_KEY env var</td></tr>\n'
    body += '      <tr><td>Iterative</td><td>After LLM generates, type follow-up ("now add a hat") — conversation builds</td><td>ANTHROPIC_API_KEY</td></tr>\n'
    body += '      <tr><td>Reset</td><td>Click Reset to clear all customization back to defaults</td><td>Nothing</td></tr>\n'
    body += '    </table>\n'
    body += '    <p class="note">Users do NOT pick individual options from dropdowns — they either use presets or describe in natural language. '
    body += '    The LLM maps descriptions to the schema below.</p>\n'
    body += '  </div>\n'
    body += '</div>\n'

    # Schema overview
    body += '<div class="section schema">\n'
    body += '  <h2>Appearance Schema (what LLM can set)</h2>\n'
    body += '  <table class="schema-table">\n'
    body += '    <tr><th>Field</th><th>Options</th><th>Category</th></tr>\n'
    body += '    <tr><td>body_color</td><td>Any [R, G, B]</td><td>Colors</td></tr>\n'
    body += '    <tr><td>accent_color</td><td>Any [R, G, B]</td><td>Colors</td></tr>\n'
    body += '    <tr><td>pattern</td><td>solid, spots, stripes</td><td>Colors</td></tr>\n'
    body += '    <tr><td>pattern_color</td><td>Any [R, G, B] or null</td><td>Colors</td></tr>\n'
    body += '    <tr class="new"><td>fur_style ✨</td><td>null, short, fluffy, long, curly, spiky, mohawk</td><td>New Feature</td></tr>\n'
    body += '    <tr class="new"><td>tail_style ✨</td><td>null, normal, fluffy, curly, short, long, ribbon</td><td>New Feature</td></tr>\n'
    body += '    <tr class="new"><td>eye_style ✨</td><td>null, normal, big, sleepy, sparkly, wink, dot</td><td>New Feature</td></tr>\n'
    body += '    <tr class="new"><td>ear_style ✨</td><td>null, normal, floppy, pointy, round, tiny, big</td><td>New Feature</td></tr>\n'
    body += '    <tr><td>hat</td><td>null, beret, crown, tophat, flower, bow, helmet, propeller</td><td>Accessories</td></tr>\n'
    body += '    <tr><td>glasses</td><td>null, round, cat_eye, sunglasses, monocle</td><td>Accessories</td></tr>\n'
    body += '    <tr><td>scarf</td><td>null, red, blue, rainbow, gold</td><td>Accessories</td></tr>\n'
    body += '    <tr><td>collar</td><td>null, bell, bowtie, bandana, tag</td><td>Accessories</td></tr>\n'
    body += '    <tr><td>special</td><td>null, sparkle_eyes, freckles, star_cheeks, rosy_cheeks</td><td>Effects</td></tr>\n'
    body += '  </table>\n'
    body += '</div>\n'

    # New features sections
    body += make_section(
        "fur_style — Hair/Fur on Head (NEW)",
        "Controls tufts, hair, or fur on top of the pet's head. Drawn after head fill, before ears and hats.",
        [None, "short", "fluffy", "long", "curly", "spiky", "mohawk"],
        "fur_style",
    )

    body += make_section(
        "tail_style — Tail Shape (NEW)",
        "Modifies the tail shape and size. 'short'/'long' scale the tail. 'ribbon' adds a bow at the tip using accent_color.",
        [None, "normal", "fluffy", "curly", "short", "long", "ribbon"],
        "tail_style",
    )

    body += make_section(
        "eye_style — Resting Eye Look (NEW)",
        "Sets the default eye appearance during idle. Action expressions (eating, sleeping, sick) still override these. "
        "'big' enlarges eyes 1.3x. 'sleepy' half-closes them. 'sparkly' adds extra highlight dots. 'wink' closes right eye. 'dot' uses tiny solid dots.",
        [None, "normal", "big", "sleepy", "sparkly", "wink", "dot"],
        "eye_style",
    )

    body += make_section(
        "ear_style — Ear Shape Override (NEW)",
        "Overrides the default ear shape per species. 'floppy' gives cats dog-style ears. 'pointy' gives dogs cat-style ears. "
        "'round' gives bear-style circular ears. 'tiny'/'big' scale the default ears.",
        [None, "normal", "floppy", "pointy", "round", "tiny", "big"],
        "ear_style",
    )

    # Existing accessory sections
    body += make_section(
        "hat — Head Accessories",
        "Drawn on top of everything else. Each hat has unique geometry.",
        [None, "beret", "crown", "tophat", "flower", "bow", "helmet", "propeller"],
        "hat",
    )

    body += make_section(
        "glasses — Eyewear",
        "Drawn over the eyes. Each type has a distinct frame shape.",
        [None, "round", "cat_eye", "sunglasses", "monocle"],
        "glasses",
    )

    body += make_section(
        "scarf — Neck Scarves",
        "Drawn at neck level between body and face.",
        [None, "red", "blue", "rainbow", "gold"],
        "scarf",
    )

    body += make_section(
        "collar — Neck Collars",
        "Drawn below the scarf, at the upper body.",
        [None, "bell", "bowtie", "bandana", "tag"],
        "collar",
    )

    body += make_section(
        "special — Special Effects",
        "Face effects drawn on top of features.",
        [None, "sparkle_eyes", "freckles", "star_cheeks", "rosy_cheeks"],
        "special",
    )

    body += make_section(
        "pattern — Body Patterns",
        "Overlay pattern on the body polygon. Requires pattern_color for non-solid.",
        ["solid", "spots", "stripes"],
        "pattern",
        pet_types=[PET_CAT],
    )

    # Theme presets
    body += make_themes_section()

    # Combos
    body += make_combo_section()

    # Full HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tamagotchi Pet Designer — Visual Catalog</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #1a0f30;
    color: #e0dce8;
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }}
  h1 {{ color: #ffdc64; font-size: 28px; margin-bottom: 8px; }}
  h2 {{ color: #c8b8f0; font-size: 20px; margin-bottom: 6px; border-bottom: 1px solid #3a2860; padding-bottom: 6px; }}
  h3 {{ color: #a898d0; font-size: 16px; margin: 12px 0 6px; }}
  .intro {{ background: #241848; border-radius: 12px; padding: 20px; margin-bottom: 24px; }}
  .intro p {{ color: #b0a8c8; line-height: 1.5; }}
  .how-it-works {{ background: #1e1240; border-radius: 8px; padding: 14px; margin-top: 14px; }}
  .info-table {{ width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 14px; }}
  .info-table th {{ text-align: left; color: #a898d0; padding: 6px 10px; border-bottom: 1px solid #3a2860; }}
  .info-table td {{ padding: 6px 10px; border-bottom: 1px solid #2a1850; }}
  .note {{ color: #90889c; font-size: 13px; margin-top: 8px; font-style: italic; }}
  .section {{ background: #201440; border-radius: 10px; padding: 16px; margin-bottom: 20px; }}
  .schema {{ }}
  .schema-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  .schema-table th {{ text-align: left; color: #a898d0; padding: 6px 8px; border-bottom: 1px solid #3a2860; }}
  .schema-table td {{ padding: 5px 8px; border-bottom: 1px solid #2a1850; font-size: 13px; }}
  .schema-table tr.new {{ background: #2a1860; }}
  .schema-table tr.new td:first-child {{ color: #ffdc64; font-weight: bold; }}
  .desc {{ color: #908898; font-size: 13px; margin-bottom: 10px; line-height: 1.4; }}
  .grid {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }}
  .cell {{
    text-align: center;
    background: #18102e;
    border-radius: 8px;
    padding: 4px;
    width: 128px;
  }}
  .cell.wide {{
    width: 140px;
  }}
  .cell img {{
    width: 120px;
    height: 140px;
    image-rendering: pixelated;
    border-radius: 6px;
  }}
  .label {{
    font-size: 12px;
    color: #d0c8e0;
    font-weight: 600;
    margin-top: 2px;
  }}
  .sublabel {{
    font-size: 10px;
    color: #706880;
  }}
</style>
</head>
<body>
{body}
</body>
</html>"""

    return html


if __name__ == "__main__":
    print("Generating catalog...")
    html = generate_html()
    out_path = os.path.join(os.path.dirname(__file__), "pet_designer_catalog.html")
    with open(out_path, "w") as f:
        f.write(html)
    print(f"Written to {out_path}")
    print(f"File size: {len(html) // 1024} KB")
