# 59 冰雕 · 配乐：雪夜。钢片琴（celesta）+ 玻璃琴式的长音 + 冷色弦乐垫 + 风；凿击声排在拍上，底座灯亮时一个大的上扬和弦，8.0 一声极轻的铃音收住
# 调式：E 利底亚（E F# G# A# B C# D#）。build.py 注入 synth.py 的函数。

E = {'E2': 40, 'B2': 47, 'E3': 52, 'B3': 59, 'E4': 64, 'F#4': 66, 'G#4': 68, 'A#4': 70, 'B4': 71, 'C#5': 73, 'D#5': 75, 'E5': 76,
     'F#5': 78, 'G#5': 80, 'B5': 83, 'D#6': 87, 'E6': 88, 'F#6': 90, 'G#6': 92, 'B6': 95}


def celesta(m, dur=1.4, vel=1.0):
    n = t2n(dur); f = mtof(m); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / .7) + .3 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / .1) + .12 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / .3)
    return y * (1 - np.exp(-t / .001)) * .2 * vel


def harmonica(m, dur, vel=1.0):
    """玻璃琴：纯净的正弦长音，慢起，带轻微的抖动"""
    n = t2n(dur); t = np.arange(n) / SR; f = mtof(m) * (1 + .002 * np.sin(2 * np.pi * 5 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + .08 * np.sin(3 * ph)
    return y * adsr(n, .35, .3, .85, .7) * .14 * vel


def wind(dur):
    n = t2n(dur); t = np.arange(n) / SR
    return svf_bp(noise(n), 500 + 300 * np.sin(2 * np.pi * .3 * t) ** 2, .4) * .08


def coldpad(ms, dur, vel=1.0):
    return pad(ms, dur, 2200, .008) * .7 * vel


def mus(M, tb, name, root, tones, bi):
    M.add('music', wind(BAR * 1.05), tb, .5, 0, .2)
    if bi < 2:
        M.add('music', coldpad([E['E3'], E['B3'], E['F#4'], E['G#4']], BAR * 1.05), tb, .35, 0, .5)
        line = [['B5', None, 'G#5', None, 'E5', None, 'F#5', None], ['G#5', None, 'D#6', None, 'B5', None, 'A#4' if False else 'C#5', None]][bi]
        for e, s in enumerate(line):
            if s: M.add('music', celesta(E[s], 1.4, .8), tb + e * BEAT / 2, .4, -.3 + .1 * e, .55)
    elif bi == 2:     # the plinth light: a wide, lifting chord
        M.add('music', coldpad([E['E3'], E['B3'], E['E4'], E['G#4'], E['A#4'], E['D#5']], BAR * 1.05, 1.2), tb, .5, 0, .6)
        M.add('music', sub(E['E2'], BAR * .9), tb, .4)
        for k, m in enumerate((E['E5'], E['G#5'], E['B5'], E['D#6'], E['F#6'])):
            M.add('music', celesta(m, 1.8, .7), tb + k * BEAT / 4, .35, -.4 + .2 * k, .6)
        M.add('music', harmonica(E['B4'], BAR, .9), tb + BEAT, .4, .1, .6)
    elif bi == 3:
        M.add('music', coldpad([E['C#5'] - 12, E['G#4'], E['B4'], E['E5']], BAR * 1.05), tb, .4, 0, .55)
        M.add('music', harmonica(E['G#5'], BEAT * 1.9, .9), tb, .4, -.1, .6)
        M.add('music', harmonica(E['F#5'], BEAT * 2.1, .9), tb + BEAT * 2, .4, .1, .6)
        for e, s in enumerate([None, 'E6', None, None, None, 'D#6', None, 'B5']):
            if s: M.add('music', celesta(E[s], 1.4, .6), tb + e * BEAT / 2, .3, .3, .55)
    else:
        M.add('music', coldpad([E['E3'], E['B3'], E['E4'], E['G#4'], E['B4']], BAR, .9), tb, .4, 0, .6)
        M.add('music', harmonica(E['E5'], BAR, .8), tb, .35, 0, .6)


# ---------- SFX ----------
def ice_chisel():
    """冰凿：钢刃刮过冰面 + 冰块剥落的脆裂 + 冰屑叮当"""
    n = t2n(.9); t = np.arange(n) / SR
    y = svf_bp(noise(n), 3500 - 1500 * np.clip(t / .15, 0, 1), .6) * np.exp(-t / .08) * .4
    y += hp(noise(n), 2000) * np.exp(-t / .006) * .6
    y += sine(110 + 60 * np.exp(-t / .02), n) * np.exp(-t / .05) * .3
    rng = np.random.default_rng(59)
    for k in range(6):
        s0 = t2n(.05 + rng.random() * .4); b = celesta(int(96 + rng.integers(0, 8)), .3, .25)
        y[s0:s0 + len(b)] += b[:n - s0]
    return y * .8


def ice_glow():
    """底座灯亮：低频涌起，一层冰晶般的泛音"""
    n = t2n(2.4); t = np.arange(n) / SR
    y = sine(41.2, n) * np.clip(t / .15, 0, 1) * np.exp(-t / 1.2) * .5
    y += svf_bp(noise(n), 2000 + 5500 * np.clip(t / .5, 0, 1), .5) * np.exp(-t / .6) * .12
    for k, m in enumerate((nm('E6'), nm('B6'), nm('E7'))):
        b = celesta(m, 1.8, .7); s0 = t2n(.04 * k); y[s0:s0 + len(b)] += b[:n - s0]
    return y


def ice_shimmer():
    return sparkle() * 1.2


def flake_chime():
    """一片雪花落在喙尖：极轻的一声高音铃"""
    n = t2n(2.2); y = np.zeros(n)
    for k, m in enumerate((nm('E7'), nm('B7'))):
        b = celesta(m, 2.0, .6 - .2 * k); s0 = t2n(k * .09); y[s0:s0 + len(b)] += b[:n - s0]
    return y


SFX_NEW = {'ice_chisel': ice_chisel, 'ice_glow': ice_glow, 'ice_shimmer': ice_shimmer, 'flake_chime': flake_chime}

# AAC-safe: take the edge off near-impulse transients so the codec does not ring past the true-peak ceiling
SFX_NEW = {k: (lambda f=f: lp(f(), 11000)) for k, f in SFX_NEW.items()}
