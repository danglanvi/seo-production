# python3 webp_gen.py <src_root> <out_root> <workers>
# Tạo <file>.webp cạnh từng JPG/PNG (trong cây out_root). Giữ ICC, xoay theo EXIF, PNG có ngưỡng PSNR 34 dB, chỉ giữ khi nhỏ hơn ít nhất 10%.
# Chạy trên bản sao của uploads/ hoặc thư mục ảnh theme. Script ghi đè <file>.webp đã có: backup các file đó trước. Log: <out_root>/_webp_log.tsv.
import os, sys, subprocess, math, tempfile, json
from multiprocessing import Pool
from PIL import Image, ImageChops, ImageStat, ImageOps

SRC, OUT, NW = sys.argv[1], sys.argv[2], int(sys.argv[3])


def psnr(a, b):
    a = a.convert('RGBA'); b = b.convert('RGBA')
    bg = Image.new('RGBA', a.size, (255, 255, 255, 255))
    a = Image.alpha_composite(bg, a).convert('RGB'); b = Image.alpha_composite(bg, b).convert('RGB')
    st = ImageStat.Stat(ImageChops.difference(a, b))
    mse = sum(v * v for v in st.rms) / 3
    return 99.0 if mse == 0 else 10 * math.log10(255 * 255 / mse)


def cwebp(args, src, dst):
    r = subprocess.run(['cwebp', '-quiet', '-metadata', 'icc'] + args + [src, '-o', dst], capture_output=True)
    return r.returncode == 0 and os.path.exists(dst)


def work(rel):
    src = os.path.join(SRC, rel); dst = os.path.join(OUT, rel + '.webp')
    try:
        s0 = os.path.getsize(src)
        if s0 < 1024:
            return (rel, 'skip-tiny', s0, 0)
        im = Image.open(src)
        if im.mode == 'CMYK':
            return (rel, 'skip-cmyk', s0, 0)
        if getattr(im, 'is_animated', False) and im.n_frames > 1:
            return (rel, 'skip-anim', s0, 0)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        ext = rel.lower().rsplit('.', 1)[-1]
        orient = 1
        try:
            orient = im.getexif().get(0x0112, 1)
        except Exception:
            pass
        srcfile = src; tmp = None
        if orient not in (1, None):
            # cwebp bỏ qua EXIF orientation: xoay trước rồi mới mã hoá
            t = ImageOps.exif_transpose(im)
            fd, tmp = tempfile.mkstemp(suffix='.png'); os.close(fd)
            t.save(tmp, 'PNG', icc_profile=im.info.get('icc_profile'))
            srcfile = tmp
        if ext in ('jpg', 'jpeg'):
            ok = cwebp(['-q', '80', '-m', '4', '-sharp_yuv'], srcfile, dst)
            how = 'q80'
        else:
            ok = cwebp(['-q', '85', '-alpha_q', '90', '-m', '4', '-sharp_yuv'], srcfile, dst)
            how = 'q85'
            if ok:
                im.load(); w = Image.open(dst); w.load()
                ref = ImageOps.exif_transpose(im) if orient not in (1, None) else im
                if psnr(ref, w) < 34:
                    ok = cwebp(['-near_lossless', '60', '-m', '4'], srcfile, dst); how = 'nl60'
                    if ok:
                        w = Image.open(dst); w.load()
                        if psnr(ref, w) < 34:
                            ok = False; how = 'psnr-fail'
        if tmp:
            os.remove(tmp)
        if not ok:
            if os.path.exists(dst): os.remove(dst)
            return (rel, 'fail-' + how, s0, 0)
        s1 = os.path.getsize(dst)
        if s1 > 0.9 * s0:
            os.remove(dst)
            return (rel, 'skip-bigger', s0, s1)
        return (rel, 'ok-' + how, s0, s1)
    except Exception as e:
        if os.path.exists(dst): os.remove(dst)
        return (rel, 'err-' + type(e).__name__, 0, 0)


if __name__ == '__main__':
    files = []
    for root, _, fs in os.walk(SRC):
        for f in fs:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                files.append(os.path.relpath(os.path.join(root, f), SRC))
    files.sort()
    print('files', len(files), flush=True)
    stats = {}; tot0 = tot1 = 0; n = 0
    with Pool(NW) as p, open(os.path.join(OUT, '_webp_log.tsv'), 'w') as log:
        for rel, st, s0, s1 in p.imap_unordered(work, files, chunksize=32):
            k = st.split('-')[0] if not st.startswith('ok') else 'ok'
            stats[st] = stats.get(st, 0) + 1
            log.write(f'{rel}\t{st}\t{s0}\t{s1}\n')
            if st.startswith('ok'):
                tot0 += s0; tot1 += s1
            n += 1
            if n % 5000 == 0:
                print(n, json.dumps(stats), flush=True)
    print('DONE', json.dumps(stats), f'ok bytes {tot0/1048576:.0f}MB -> {tot1/1048576:.0f}MB', flush=True)
