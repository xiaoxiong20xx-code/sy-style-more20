# 49 蓝晒 · 配乐：夏日午后——原声吉他拨弦 + 钟琴 + 轻沙锤；日晒延时段吉他加密，进水后（4.0）铺开柔和的弦乐，
# 水盘摇晃时钟琴像水光一样闪；8.0 提纸时和弦落下，余音到底。
# 音效：叶子落纸（leaf_land）、玻璃滑过（glass_slide）、玻璃轻敲（glass_tap）、阳光上扬（sun_swell）、
#       水漫进来（water_flood）、水盘轻晃（slosh）、湿纸出水（paper_lift）、水滴（drip）
import numpy as np


def guitar(m, dur=1.2, vel=1.0):
    return ks(m, dur, 0.55, 0.997) * 0.5 * vel


def glock(m, dur=1.0):
    n = t2n(dur); t = np.arange(n) / SR; f = mtof(m)
    return (sine(f, n) * np.exp(-t / 0.6) + 0.3 * sine(f * 2.76, n) * np.exp(-t / 0.15)) * (1 - np.exp(-t / 0.001)) * 0.22


def mus(M, tb, name, root, tones, bi):
    last = bi == 4
    if not last:
        # fingerpicked guitar: bass on the beat, chord tones in between
        pat = [0, 2, 1, 2, 0, 2, 1, 3] if bi < 2 else [0, 2, 1, 3, 0, 3, 1, 2]
        ch = [root, tones[0] + 12, tones[1] + 12, tones[2] + 12]
        for e, k in enumerate(pat):
            M.add('music', guitar(ch[k] + (0 if k else 12), 1.0, 0.9 if e % 2 == 0 else 0.6), tb + e * BEAT / 2, 0.38, -0.2 + 0.06 * e, 0.3)
        if bi == 1:      # the sun moving: sixteenth-note shimmer on top
            for s16 in range(16): M.add('music', guitar(tones[s16 % 3] + 24, 0.4, 0.4), tb + s16 * BEAT / 4, 0.14, 0.3, 0.3)
        if bi >= 2:      # in the water: soft strings and glints of glockenspiel
            M.add('music', strings([x + 12 for x in tones], BAR * 1.02, 2400), tb, 0.3, 0, 0.6)
            for e, m in enumerate([tones[2] + 24, tones[1] + 24, tones[0] + 36, tones[2] + 24]):
                M.add('music', glock(m, 1.4), tb + e * BEAT + BEAT / 2, 0.22, -0.3 + 0.2 * e, 0.6)
        M.add('drums', soft_kick(), tb, 0.45)
        for e in range(8): M.add('drums', shaker(), tb + e * BEAT / 2 + BEAT / 4, 0.06 if bi < 2 else 0.08, 0.35)
        if bi == 2: M.add('drums', crash(1.6) * 0.4, tb, 0.3, 0, 0.5)
        return
    for j, m in enumerate([root, tones[0] + 12, tones[1] + 12, tones[2] + 12, tones[0] + 24]):
        M.add('music', guitar(m, 2.8, 0.9), tb + j * 0.035, 0.38, -0.25 + 0.12 * j, 0.5)
    for j, m in enumerate(tones): M.add('music', glock(m + 24, 2.2), tb + 0.05 + j * 0.06, 0.18, -0.3 + 0.3 * j, 0.6)
    M.add('music', strings([x + 12 for x in tones], BAR * 0.95, 2000), tb, 0.26, 0, 0.6)


# ---------------- SFX ----------------
def leaf_land():
    n = t2n(0.25); t = np.arange(n) / SR
    return bp(noise(n), 400, 4000) * np.exp(-t / 0.03) * 0.35 + lp(noise(n), 300) * np.exp(-t / 0.02) * 0.2


def glass_slide():
    n = t2n(0.42); t = np.arange(n) / SR
    y = svf_bp(noise(n), 2500 + 2000 * (t / 0.42), 0.4) * np.sin(np.pi * t / 0.42) ** 1.2 * 0.25
    y += sine(3150, n) * 0.02 * np.sin(np.pi * t / 0.42)
    return y


def glass_tap():
    n = t2n(0.6); t = np.arange(n) / SR
    y = sum(sine(f, n) * np.exp(-t / d) * a for f, d, a in [(2840, 0.2, 0.3), (4170, 0.12, 0.2), (6320, 0.07, 0.12)])
    return y + hp(noise(n), 4000) * np.exp(-t / 0.003) * 0.2


def sun_swell():
    n = t2n(2.0); t = np.arange(n) / SR
    y = pad([nm('E5'), nm('A5'), nm('C6')], 2.0, 3000) * np.clip(t / 1.6, 0, 1) ** 2 * 0.8
    y += hp(noise(n), 5000) * np.clip(t / 2.0, 0, 1) ** 2 * 0.04
    return y


def water_flood():
    n = t2n(1.4); t = np.arange(n) / SR
    y = bp(noise(n), 300, 4500) * np.exp(-np.maximum(t - 0.15, 0) / 0.45) * np.clip(t / 0.06, 0, 1) * 0.45
    r = np.random.default_rng(9)
    for k in range(14):
        nn = t2n(0.04); tt = np.arange(nn) / SR; f = r.uniform(600, 1800)
        b = sine(f * (1 + tt / 0.04), nn) * np.exp(-tt / 0.015) * 0.08; i0 = t2n(r.uniform(0.05, 1.0)); y[i0:i0 + nn] += b[: n - i0]
    return y


def slosh():
    n = t2n(0.7); t = np.arange(n) / SR
    return svf_bp(noise(n), 500 + 900 * np.sin(np.pi * t / 0.7), 0.6) * np.sin(np.pi * t / 0.7) ** 2 * 0.3


def paper_lift():
    n = t2n(1.2); t = np.arange(n) / SR
    y = bp(noise(n), 800, 6000) * np.exp(-t / 0.3) * np.clip(t / 0.1, 0, 1) * 0.35        # water sheeting off
    r = np.random.default_rng(2)
    cr = (r.random(n) > 0.997).astype(float) * np.exp(-t / 0.25)                           # wet paper peeling from the tray
    y += hp(cr, 2000) * 0.4
    return y


def drip():
    n = t2n(0.25); t = np.arange(n) / SR
    f = 1700 * np.exp(-t / 0.018) + 800
    return sine(f, n) * np.exp(-t / 0.035) * 0.3 + hp(noise(n), 3000) * np.exp(-t / 0.003) * 0.12


SFX_NEW = {'leaf_land': leaf_land, 'glass_slide': glass_slide, 'glass_tap': glass_tap, 'sun_swell': sun_swell,
           'water_flood': water_flood, 'slosh': slosh, 'paper_lift': paper_lift, 'drip': drip}
