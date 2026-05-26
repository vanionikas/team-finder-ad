import io
import random
import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

AVATAR_COLORS = [
    '#4A90D9', '#6B7280', '#10B981', '#F59E0B',
    '#8B5CF6', '#EC4899', '#14B8A6', '#F97316',
]
AVATAR_SIZE = 200
AVATAR_FONT_SIZE = 90

FONT_PATH = settings.BASE_DIR / 'static' / 'fonts' / 'Neue_Haas_Grotesk_Display_Pro_75_Bold.otf'


def generate_user_avatar(letter: str) -> ContentFile:
    letter = (letter or '?').upper()
    bg_color = random.choice(AVATAR_COLORS)

    img = Image.new('RGB', (AVATAR_SIZE, AVATAR_SIZE), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(str(FONT_PATH), size=AVATAR_FONT_SIZE)
    except (IOError, OSError):
        font = ImageFont.load_default(size=AVATAR_FONT_SIZE)

    bbox = draw.textbbox((0, 0), letter, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (AVATAR_SIZE - tw) / 2 - bbox[0]
    y = (AVATAR_SIZE - th) / 2 - bbox[1]
    draw.text((x, y), letter, fill='white', font=font)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return ContentFile(buf.read(), name=f'gen_{uuid.uuid4().hex[:8]}.png')
