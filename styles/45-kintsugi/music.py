# 45 金缮 · 配乐：尺八式长音 + 筝的拨弦 + 坐磬（rin）；碎片归位的咔声排在拍上，金漆流动时磬声和筝的轮指，8.0 一个筝的和弦收住
# 调式：D 都节（D Eb G A Bb）。build.py 注入 synth.py 的函数。

K = {'D3': 50, 'A3': 57, 'D4': 62, 'Eb4': 63, 'G4': 67, 'A4': 69, 'Bb4': 70, 'D5': 74, 'Eb5': 75, 'G5': 79, 'A5': 81}


def koto(m, dur=1.4, vel=1.0):
    y = ks(m, dur, .6, .9965)
    n = len(y); t = np.arange(n) / SR
    y = y + hp(y, 1500) * .3 * np.exp(-t / .05)
    return y * .5 * vel


def shaku(m, dur, vel=1.0):
    """尺八：气声很重的竹笛，起音有一点向上的滑音"""
    n = t2n(dur); t = np.arange(n) / SR
    bend = 1 - .03 * np.exp(-t / .12)
    vib = 1 + .006 * np.sin(2 * np.pi * 4.8 * t) * np.clip((t - .4) / .5, 0, 1)
    f = mtof(m) * bend * vib
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + .18 * np.sin(2 * ph) + .06 * np.sin(3 * ph)
    breath = svf_bp(noise(n), f * 1.5, .5) * .35 + bp(noise(n), 1500, 6000) * .05
    y = y * (.8 + .2 * np.sin(2 * np.pi * .7 * t)) + breath
    return y * adsr(n, .25, .4, .75, .6) * .28 * vel


def rin(m, dur=4.0, vel=1.0):
    """坐磬：铜钵的长鸣，带一点拍频"""
    n = t2n(dur); f = mtof(m); t = np.arange(n) / SR
    y = np.zeros(n)
    for r, a, d in ((1., 1., 2.6), (1.004, .8, 2.4), (2.71, .45, 1.2), (5.2, .2, .5), (8.6, .1, .25)):
        y += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d)
    return y * (1 - np.exp(-t / .002)) * .18 * vel


def mus(M, tb, name, root, tones, bi):
    if bi == 0:
        M.add('music', shaku(K['A4'], BAR * 1.1, .9), tb, .55, -.1, .55)
        M.add('music', koto(K['D4'], 1.8, .7), tb, .4, .2, .3)
    elif bi == 1:
        for e, s in enumerate(['D4', None, 'G4', None, 'A4', None, 'D5', None]):
            if s: M.add('music', koto(K[s], 1.4, .75), tb + e * BEAT / 2, .45, -.3 + .12 * e, .35)
        M.add('music', shaku(K['Bb4'], BAR * .6, .7), tb + BEAT * 1.5, .45, -.1, .5)
    elif bi == 2:     # the gold runs
        M.add('music', rin(K['A4'], 4.0, 1.), tb, .6, 0, .7)
        for k in range(16):
            s = ['D5', 'A4', 'G4', 'A4'][k % 4]
            M.add('music', koto(K[s], .9, .35 + .2 * (k % 4 == 0)), tb + k * BEAT / 4, .3, .25 * np.sin(k), .3)
        M.add('music', shaku(K['D5'], BAR, .6), tb + BEAT * 2, .4, -.1, .5)
    elif bi == 3:
        M.add('music', shaku(K['G4'], BEAT * 1.9, .8), tb, .5, -.1, .55)
        M.add('music', shaku(K['A4'], BEAT * 2.1, .8), tb + BEAT * 2, .5, -.1, .55)
        for e, s in enumerate(['D4', None, None, 'Eb4', None, None, 'G4', None]):
            if s: M.add('music', koto(K[s], 1.6, .6), tb + e * BEAT / 2, .4, .3, .35)
    else:             # 8.0: a last chord on the koto, the rin under it
        for k, m in enumerate((K['D3'], K['A3'], K['D4'], K['Eb4'], K['A4'])):
            M.add('music', koto(m, 2.2, .75), tb + k * .03, .5, -.3 + .15 * k, .45)
        M.add('music', rin(K['D5'], 3.0, .7), tb, .45, 0, .6)


# ---------- SFX ----------
def shard_click():
    """碎片合拢：瓷片相碰的清脆一咔 + 短促的瓷鸣"""
    n = t2n(.5); t = np.arange(n) / SR
    y = hp(noise(n), 3000) * np.exp(-t / .004) * .7
    for f, a, d in ((3150, .4, .08), (4870, .25, .05), (2210, .2, .12)):
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
    y += sine(180, n) * np.exp(-t / .02) * .25
    return y * .7


def bowl_ring():
    n = t2n(2.2); t = np.arange(n) / SR
    y = np.zeros(n)
    for f, a, d in ((880, 1., 1.), (1460, .5, .6), (2390, .3, .35)):
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
    return y * (1 - np.exp(-t / .003)) * .15


def gold_flow():
    """金漆流过裂缝：细细的液体声 + 一层金属的微光泛音"""
    n = t2n(1.4); t = np.arange(n) / SR; u = t / 1.4
    y = svf_bp(noise(n), 900 + 700 * np.sin(2 * np.pi * 7 * t) ** 2, .3) * .2 * np.sin(np.pi * u) ** .6
    for k, m in enumerate((nm('A6'), nm('D7'), nm('G7'), nm('A7'))):
        b = bell(m, .9, .3) * .06; s0 = t2n(.1 + k * .22); y[s0:s0 + len(b)] += b[:n - s0]
    return y


def gold_glint():
    n = t2n(1.2); t = np.arange(n) / SR; u = np.clip(t / .6, 0, 1)
    y = svf_bp(noise(n), 2500 + 4500 * u, .45) * np.sin(np.pi * u) * .12
    b = bell(nm('A7'), 1.0, .5) * .12; y[:len(b)] += b
    return y


def bowl_settle():
    """碗在麻布上落定：一声闷的轻响 + 碗身的余鸣"""
    n = t2n(2.3); t = np.arange(n) / SR
    y = sine(120 + 60 * np.exp(-t / .02), n) * np.exp(-t / .08) * .5 + lp(noise(n), 800) * np.exp(-t / .03) * .3
    r = bowl_ring(); y[:len(r)] += r * .7
    return y


SFX_NEW = {'shard_click': shard_click, 'bowl_ring': bowl_ring, 'gold_flow': gold_flow, 'gold_glint': gold_glint, 'bowl_settle': bowl_settle}

# AAC-safe: take the edge off near-impulse transients so the codec does not ring past the true-peak ceiling
SFX_NEW = {k: (lambda f=f: lp(f(), 11000)) for k, f in SFX_NEW.items()}
