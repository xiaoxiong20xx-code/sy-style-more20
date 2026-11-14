# 53 烙画 · 配乐：夜里的书桌——闷音的尼龙弦吉他分解和弦、拉奏低音、一层很轻的刷鼓，温暖安静；
# 烙笔的「嗞——」就是这首曲子的质感：落笔、长线、快速排线都按拍出现；8.0 秒提笔，吉他一个和弦加拉奏泛音收住。
# 音效：pen_hum（烙笔通电）、nib_touch（落笔）、burn_line / burn_short（烧线）、hatch_rush（快速排线）、burn_final（最后一笔）、pen_lift（提笔）
import numpy as np


def nylon(m, dur=0.9, vel=1.0):
    y = ks(m, dur, 0.28, 0.9955)
    n = len(y); t = np.arange(n) / SR
    return lp(y, 2600) * 0.55 * vel * (1 - np.exp(-t / 0.002))


def bowed(m, dur, cut=900):
    n = t2n(dur); t = np.arange(n) / SR
    f = mtof(m) * (1 + 0.004 * np.sin(2 * np.pi * 4.8 * t))
    y = polyblep_saw(f, n) * 0.6 + polyblep_saw(f * 1.002, n) * 0.4
    return lp(y, cut) * adsr(n, 0.35, 0.3, 0.85, 0.5) * 0.22


def brush_tap(acc=False):
    n = t2n(0.22); t = np.arange(n) / SR
    return bp(noise(n), 1500, 8000) * np.exp(-t / (0.06 if acc else 0.035)) * (0.25 if acc else 0.15)


ARPS = {  # finger-picked broken chords (eighths): Am7, Fmaj7, Cmaj9, G6, Am(add9)
    0: [45, 52, 57, 60, 64, 60, 57, 52],
    1: [45, 52, 57, 60, 64, 60, 57, 52],
    2: [41, 48, 52, 57, 60, 57, 52, 48],
    3: [43, 50, 55, 59, 64, 59, 55, 50],
    4: None,
}


def mus(M, tb, name, root, tones, bi):
    pat = ARPS[bi]
    if pat:
        for e, m in enumerate(pat):
            if bi == 0 and e < 2: continue
            M.add('music', nylon(m, 1.0, 1.0 if e % 4 == 0 else 0.7), tb + e * BEAT / 2, 0.55, -0.25 + 0.5 * (e % 2), 0.3)
        M.add('music', bowed(pat[0] - 12, BAR * 1.02), tb, 0.6, 0, 0.3)
    if 0 < bi < 4:
        for e in range(8): M.add('drums', brush_tap(e % 4 == 2), tb + e * BEAT / 2, 0.48, 0.3, 0.2)
        M.add('drums', soft_kick(), tb, 0.45); M.add('drums', soft_kick(), tb + 2 * BEAT, 0.35)
    if bi == 4:   # the pen lifts: one chord, a bowed harmonic, and they ring
        for j, m in enumerate([45, 52, 57, 59, 64, 69]): M.add('music', nylon(m, 2.4, 0.9), tb + j * 0.025, 0.85, -0.3 + 0.12 * j, 0.45)
        M.add('music', bowed(33, BAR * 0.95, 700), tb, 0.8, 0, 0.4)
        n = t2n(2.5); t = np.arange(n) / SR
        M.add('music', np.sin(2 * np.pi * mtof(81) * t) * adsr(n, 0.3, 0.3, 0.6, 1.0) * 0.07, tb, 0.6, 0.2, 0.6)


# ---------------- SFX ----------------
def _sizzle(dur, rate=1.0, amp=1.0):
    """a hot nib in basswood: a fine crackle over a soft hiss"""
    n = t2n(dur); t = np.arange(n) / SR
    r = np.random.default_rng(int(dur * 1000 + rate * 7))
    crack = np.zeros(n)
    for _ in range(int(dur * 260 * rate)):
        k = r.integers(n); m = min(n - k, t2n(0.002)); crack[k:k + m] += r.normal(0, 1, m) * np.exp(-np.arange(m) / SR / 0.0006)
    hiss = bp(noise(n), 3000, 9000) * 0.08
    env = np.clip(t / 0.02, 0, 1) * np.clip((dur - t) / 0.05, 0, 1)
    c = lp(hp(crack, 2000), 11000)                                   # keep the crackle off Nyquist: no inter-sample overs after AAC
    c = np.tanh(c * 2.0) / 2.0                                       # and round off the odd hot spark
    return (c * 0.35 + hiss) * env * amp


def pen_hum():
    n = t2n(0.8); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 100 * t) + 0.3 * np.sin(2 * np.pi * 200 * t)) * 0.045 * np.clip(t / 0.12, 0, 1) * np.clip((0.8 - t) / 0.3, 0, 1)


def nib_touch():
    n = t2n(0.12); t = np.arange(n) / SR
    y = bp(noise(n), 2000, 7000) * np.exp(-t / 0.01) * 0.5 + np.sin(2 * np.pi * 900 * t) * np.exp(-t / 0.008) * 0.15
    return y * 0.6


SFX_NEW = {
    'pen_hum': pen_hum, 'nib_touch': nib_touch,
    'burn_line': lambda: _sizzle(0.95, 1.0, 1.0), 'burn_short': lambda: _sizzle(0.48, 1.0, 0.9),
    'hatch_rush': lambda: _sizzle(1.0, 2.6, 0.75), 'burn_final': lambda: _sizzle(0.3, 0.7, 1.1),
    'pen_lift': lambda: nib_touch() * 0.6,
}
