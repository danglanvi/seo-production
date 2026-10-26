# Dữ liệu giả cho test font và ảnh của wp-pagespeed (fallback_faces, fa_subset, img_variants, img_display_width). Chỉ ghi trong thư mục tạm.
import os
import random
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def py(script, *argv, cwd=None, timeout=180):
    """Chạy script .py trong scripts/ bằng python3 (không -I, vì cần fontTools hoặc Pillow trong site-packages của người dùng)."""
    return subprocess.run(['python3', os.path.join(SCRIPTS, script)] + list(argv), capture_output=True, text=True, timeout=timeout, cwd=cwd)


def make_font(path, adv, asc=900, desc=-200, upem=1000, flavor=None, family='Test', license_text=None):
    """Font TTF rỗng nét vẽ. adv: {ký tự: bề rộng}. Cùng bộ glyph nên chỉ dùng để đo bề rộng và ghép cmap."""
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    order = ['.notdef'] + ['g%X' % ord(c) for c in adv]
    fb = FontBuilder(upem, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap({ord(c): 'g%X' % ord(c) for c in adv})
    empty = TTGlyphPen(None).glyph()
    fb.setupGlyf({g: empty for g in order})
    fb.setupHorizontalMetrics({'.notdef': (500, 0), **{'g%X' % ord(c): (w, 0) for c, w in adv.items()}})
    fb.setupHorizontalHeader(ascent=asc, descent=desc)
    names = {'familyName': family, 'styleName': 'Regular'}
    if license_text:
        names['licenseDescription'] = license_text
    fb.setupNameTable(names)
    fb.setupOS2(sTypoAscender=asc, sTypoDescender=desc, usWinAscent=asc, usWinDescent=-desc)
    fb.setupPost()
    if flavor:
        fb.font.flavor = flavor
    fb.save(path)
    return path


LATIN = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,:;!?-%&@#'
VIET = 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ'


def noise_image(path, size, seed=1, fmt=None, **save_kw):
    """Ảnh nhiễu (khó nén) để các cỡ ảnh khác nhau có dung lượng khác nhau rõ rệt."""
    from PIL import Image
    rnd = random.Random(seed)
    im = Image.new('RGB', size)
    im.putdata([(rnd.randrange(256), rnd.randrange(256), rnd.randrange(256)) for _ in range(size[0] * size[1])])
    im.save(path, fmt, **save_kw)
    return path


def flat_image(path, size, color=(30, 90, 200, 255), fmt=None, **save_kw):
    from PIL import Image
    Image.new('RGBA', size, color).save(path, fmt, **save_kw)
    return path
