# 47 毛线编织 · 配乐：北欧冬日的暖——钢片琴 + 竖琴拨弦 + 低音提琴拨奏；
# 第 1 小节只有钢片琴陪着每一针；加速段竖琴琶音加密；延时段（4.0 起）加入沙锤、软鼓和弦乐铺底；8.0 和弦落下余音到底。
# 音效：木针相碰（knit_click）、线滑过针（yarn_slide）、越织越快的咔嗒（knit_roll）、延时的沙沙织物声（knit_timelapse）、
#       收针链（yarn_zip）、织片落桌（cloth_drop）
import numpy as np


def celesta(m, dur=1.4, vel=1.0):
    n = t2n(dur); t = np.arange(n) / SR; f = mtof(m)
    y = sine(f, n) * np.exp(-t / 0.9) + 0.45 * sine(2 * f, n) * np.exp(-t / 0.35) + 0.16 * sine(3.98 * f, n) * np.exp(-t / 0.12)
    y += hp(noise(n), 4000) * np.exp(-t / 0.004) * 0.06
    return y * (1 - np.exp(-t / 0.0015)) * 0.26 * vel


def harp(m, dur=1.6, vel=1.0):
    return ks(m, dur, 0.75, 0.9985) * 0.55 * vel


MEL = {'Am': ['E6', 'C6', 'A5', 'B5', 'C6', None, 'E6', 'D6'], 'F': ['C6', 'A5', 'F5', 'A5', 'C6', None, 'F6', 'E6'],
       'C': ['E6', 'G6', 'E6', 'C6', 'D6', 'E6', None, 'G5'], 'G': ['D6', 'B5', 'G5', 'B5', 'D6', None, 'G6', 'F#6']}


def mus(M, tb, name, root, tones, bi):
    last = bi == 4
    if bi == 0:      # the macro: a celesta note on each stitch (0.5, 1.0, 1.5) and on the downbeat
        for q, m in enumerate([tones[2] + 24, tones[0] + 24, tones[1] + 24, tones[2] + 24]):
            M.add('music', celesta(m, 1.8, 0.8 if q else 0.6), tb + q * BEAT, 0.45, -0.2 + 0.13 * q, 0.5)
        M.add('music', upright(root, BAR * 0.9), tb, 0.45)
        M.add('music', pad([x + 12 for x in tones], BAR, 1400), tb, 0.18, 0, 0.5)
        return
    if bi == 1:      # speeding up: harp arpeggio in eighths, then sixteenths
        for e in range(12):
            tt = e * BEAT / 2 if e < 6 else 3 * BEAT + (e - 6) * BEAT / 6
            m = (tones + [tones[0] + 12])[e % 4] + 12
            M.add('music', harp(m, 1.2, 0.8), tb + tt, 0.32, -0.3 + 0.1 * (e % 6), 0.35)
        M.add('music', upright(root, BAR * 0.9), tb, 0.45)
        M.add('music', pad([x + 12 for x in tones], BAR, 1600), tb, 0.22, 0, 0.5)
        for e in range(8): M.add('drums', shaker(), tb + e * BEAT / 2 + BEAT / 4, 0.05 + 0.01 * e, 0.3)
        return
    if not last:     # the time-lapse: tune on celesta, harp running, strings under, light kit
        for e, sN in enumerate(MEL[name]):
            if sN: M.add('music', celesta(nm(sN), 1.2, 0.9), tb + e * BEAT / 2, 0.42, 0.2, 0.45)
        for e in range(16):
            m = (tones + [tones[1] + 12])[e % 4] + 12
            M.add('music', harp(m, 0.9, 0.6), tb + e * BEAT / 4, 0.18, -0.35 + 0.05 * (e % 8), 0.3)
        for q in range(4): M.add('music', pizz(root - 12 + (7 if q % 2 else 0), 0.5), tb + q * BEAT, 0.55, -0.1, 0.2)
        M.add('music', strings([x + 12 for x in tones], BAR * 1.02, 2200), tb, 0.32, 0, 0.6)
        M.add('drums', soft_kick(), tb, 0.55); M.add('drums', soft_kick(), tb + 2 * BEAT, 0.45)
        for q in (1, 3): M.add('drums', snap(), tb + q * BEAT, 0.28, 0.15, 0.3)
        for s16 in range(16): M.add('drums', shaker(), tb + s16 * BEAT / 4, 0.1 if s16 % 2 else 0.06, 0.35)
        if bi == 2: M.add('drums', crash(1.4) * 0.5, tb, 0.3, 0, 0.5)
        return
    # 8.0: resolve, ring out to the end
    for j, m in enumerate(tones + [tones[0] + 12]):
        M.add('music', celesta(m + 24, 2.6, 0.9), tb + j * 0.035, 0.35, -0.3 + 0.2 * j, 0.6)
        M.add('music', harp(m + 12, 2.6, 0.8), tb + j * 0.05, 0.3, -0.25 + 0.15 * j, 0.5)
    M.add('music', strings([x + 12 for x in tones], BAR * 0.95, 1800), tb, 0.28, 0, 0.6)
    M.add('music', upright(root - 12, BAR * 0.8), tb, 0.5)


# ---------------- SFX ----------------
def knit_click():
    n = t2n(0.12); t = np.arange(n) / SR
    y = bp(noise(n), 1500, 6000) * np.exp(-t / 0.006) * 0.55
    y += sine(2150, n) * np.exp(-t / 0.018) * 0.22 + sine(3320, n) * np.exp(-t / 0.01) * 0.12
    k = t2n(0.022); y2 = bp(noise(n), 2000, 7000) * np.exp(-t / 0.004) * 0.3   # the second needle answering
    y[k:] += y2[: n - k]
    return y


def yarn_slide():
    n = t2n(0.32); t = np.arange(n) / SR
    am = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 23 * t))
    return svf_bp(noise(n), 900 + 2400 * (t / 0.32), 0.6) * am * np.sin(np.pi * t / 0.32) ** 1.4 * 0.35


def knit_roll():
    out = np.zeros(t2n(2.1))
    p = 1.2; tt = []
    for j in range(1, 150):      # same ramp as the knitting: 2 → 160 stitches a second
        a, b = 0.0, 2.0
        for _ in range(30):
            m = (a + b) / 2; N = 2 * m + 162 * 2 * (m / 2) ** (p + 1) / (p + 1)
            a, b = (m, b) if N < j else (a, m)
        tt.append((a + b) / 2)
    for i, t0 in enumerate(tt):
        c = knit_click() * (0.75 - 0.45 * t0 / 2) * (0.7 + 0.3 * ((i * 7) % 5) / 4)
        k = t2n(t0); out[k:k + len(c)] += c[: len(out) - k]
    return out * 0.8


def knit_timelapse():
    n = t2n(3.8); t = np.arange(n) / SR
    rows = 0.6 + 0.4 * np.abs(np.sin(np.pi * t / 0.25))                 # a row every half beat
    y = bp(noise(n), 1800, 7000) * rows * 0.22 + lp(noise(n), 900) * 0.08
    r = np.random.default_rng(7)
    clicks = (r.random(n) > 0.9965).astype(float); y += hp(clicks, 1500) * 0.35
    return y * np.clip(t / 0.2, 0, 1) * np.clip((3.8 - t) / 0.3, 0, 1)


def yarn_zip():
    n = t2n(0.32); t = np.arange(n) / SR
    am = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 60 * t))
    return svf_bp(noise(n), 1200 + 5000 * (t / 0.32) ** 1.4, 0.5) * am * np.sin(np.pi * t / 0.32) * 0.5


def cloth_drop():
    n = t2n(0.6); t = np.arange(n) / SR
    y = sine(85 + 30 * np.exp(-t / 0.04), n) * np.exp(-t / 0.12) * 0.7
    y += lp(noise(n), 1500) * np.exp(-t / 0.05) * 0.4 + bp(noise(n), 300, 2500) * np.exp(-t / 0.15) * 0.15
    return y


SFX_NEW = {'knit_click': knit_click, 'yarn_slide': yarn_slide, 'knit_roll': knit_roll, 'knit_timelapse': knit_timelapse,
           'yarn_zip': yarn_zip, 'cloth_drop': cloth_drop}
