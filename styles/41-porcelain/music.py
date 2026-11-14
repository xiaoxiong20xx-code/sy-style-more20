# 41 青花瓷 · 配乐：古琴式拨弦 + 编钟 + 低弦长音；窑火处一记大鼓和锣，成瓷后编钟旋律，8.0 一声瓷器清鸣收住
# 调式：D 宫五声（D E F# A B）。build.py 会把 synth.py 的函数注入本模块：np, SR, BEAT, BAR, t2n, mtof, nm, sine, noise, lp, hp, bp, ks, bell, pad, adsr ...

P = {'D3': 50, 'A3': 57, 'D4': 62, 'E4': 64, 'F#4': 66, 'A4': 69, 'B4': 71, 'D5': 74, 'E5': 76, 'F#5': 78, 'A5': 81, 'B5': 83, 'D6': 86}


def qin(m, dur=1.6, vel=1.0):
    """古琴式拨弦：Karplus-Strong + 木质腔体共鸣 + 轻微滑音"""
    y = ks(m, dur, 0.32, 0.9975)
    n = len(y); t = np.arange(n) / SR
    y = y + bp(y, 180, 900) * 0.35
    return y * (1 - 0.15 * np.exp(-t / 0.05)) * 0.55 * vel


def zhong(m, dur=3.0, vel=1.0):
    """编钟：两音钟的非谐波分音，青铜的长尾"""
    n = t2n(dur); f = mtof(m); t = np.arange(n) / SR
    y = np.zeros(n)
    for r, a, d in ((1.0, 1.0, 1.6), (2.4, .45, .7), (2.95, .3, .5), (4.1, .2, .3), (5.9, .12, .15), (1.003, .5, 1.3)):
        y += a * np.sin(2 * np.pi * f * r * t + r * 3) * np.exp(-t / d)
    y += bp(noise(n), f, min(f * 8, 16000)) * np.exp(-t / .01) * .4
    return y * (1 - np.exp(-t / .0015)) * .22 * vel


def drone(ms, dur, vel=1.0):
    n = t2n(dur); t = np.arange(n) / SR
    y = np.zeros(n)
    for m in ms:
        for d in (-.004, 0, .005):
            y += polyblep_saw(mtof(m) * (1 + d) * (1 + .002 * np.sin(2 * np.pi * 4.6 * t + m)), n)
    y = lp(y / (3 * len(ms)), 1100)
    return y * adsr(n, .6, .3, .85, .7) * .3 * vel


def bangzi():
    n = t2n(.15); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1850 * t) * np.exp(-t / .02) + bp(noise(n), 1500, 6000) * np.exp(-t / .006) * .6) * .45


def dagu(vel=1.0):
    n = t2n(1.6); t = np.arange(n) / SR
    y = sine(52 + 40 * np.exp(-t / .06), n) * np.exp(-t / .55) + lp(noise(n), 300) * np.exp(-t / .08) * .5
    return np.tanh(y * 1.3) * .8 * vel


def gong(dur=3.2):
    n = t2n(dur); t = np.arange(n) / SR
    y = np.zeros(n)
    for f, a, d in ((150, 1., 2.2), (227, .6, 1.6), (312, .45, 1.2), (468, .3, .9), (690, .2, .6)):
        y += a * np.sin(2 * np.pi * f * t * (1 + .01 * np.exp(-t / .4))) * np.exp(-t / d)
    y += bp(noise(n), 300, 3000) * np.exp(-t / .05) * .5
    return y * .3


LINES = [
    ['A4', None, 'D5', None, 'E5', None, None, 'A4'],
    ['F#5', None, 'E5', 'D5', 'B4', None, 'A4', None],
    [None, None, None, None, None, None, None, None],
    ['D5', None, None, 'E5', 'F#5', None, 'A5', None],
    [None, None, None, None, None, None, None, None],
]


def mus(M, tb, name, root, tones, bi):
    if bi < 2:
        M.add('music', drone([P['D3'], P['A3']], BAR * 1.05, .8 + .2 * bi), tb, .5, 0, .3)
        for e, s in enumerate(LINES[bi]):
            if s: M.add('music', qin(P[s], 1.8, .9 if e % 2 == 0 else .7), tb + e * BEAT / 2, .6, -.25 + .1 * (e % 5), .35)
        if bi == 1:
            for q in range(4): M.add('drums', bangzi(), tb + q * BEAT, .32 if q % 2 == 0 else .22, .35, .2)
    elif bi == 2:     # the kiln
        M.add('drums', dagu(1.), tb, .9, 0, .4)
        M.add('music', gong(3.2), tb, .55, -.1, .6)
        M.add('music', drone([P['D3'], P['A3'], P['D4'], P['F#4']], BAR * 1.05, 1.0), tb, .55, 0, .4)
        M.add('music', zhong(P['D5'], 3.0, .8), tb + BEAT, .5, .2, .6)
        for q in (2, 2.5, 3): M.add('drums', dagu(.35), tb + q * BEAT, .45, 0, .3)
    elif bi == 3:     # finished: the bells sing over the strings
        M.add('music', drone([P['D3'], P['A3'], P['F#4']], BAR * 1.05, .9), tb, .5, 0, .4)
        for e, s in enumerate(LINES[3]):
            if s: M.add('music', zhong(P[s], 2.6, .8), tb + e * BEAT / 2, .45, -.2 + .1 * e, .55)
        M.add('music', qin(P['A4'], 1.8, .6), tb + 3 * BEAT, .45, .3, .35)
    else:             # 8.0: one last chord, left to ring
        M.add('music', drone([P['D3'], P['A3'], P['D4'], P['F#4'], P['A4']], BAR * 1.0, .8), tb, .45, 0, .5)
        for k, m in enumerate((P['D4'], P['A4'], P['D5'], P['F#5'])):
            M.add('music', zhong(m, 3.2, .8 - .1 * k), tb + k * .012, .5, -.3 + .2 * k, .6)


# ---------- SFX ----------
def brush_touch():
    """毛笔落在素坯上：细毛擦过粗坯的沙沙声"""
    n = t2n(.5); t = np.arange(n) / SR
    y = bp(noise(n), 2500, 9000) * np.exp(-t / .12) * np.clip(t / .015, 0, 1) * .35
    y += lp(noise(n), 400) * np.exp(-t / .02) * .1
    return y


def brush_wash():
    n = t2n(.6); t = np.arange(n) / SR; u = t / .6
    return svf_bp(noise(n), 1800 + 1500 * u, .7) * np.sin(np.pi * u) ** .8 * .3


def wheel_spin():
    """转台一拨飞转：铸铁轴承的呼呼声，转速升高"""
    n = t2n(.9); t = np.arange(n) / SR
    rot = 2 + 18 * np.clip(t / .2, 0, 1)
    ph = 2 * np.pi * np.cumsum(rot * 6) / SR
    y = np.sin(ph) * .12 + svf_bp(noise(n), 300 + 600 * np.clip(t / .3, 0, 1), .8) * .25
    y += lp(noise(n), 150) * .15
    return y * np.clip(t / .03, 0, 1) * np.exp(-np.clip(t - .5, 0, None) / .2)


def kiln_roar():
    """窑火一亮：低沉的火焰轰鸣 + 燃烧爆裂声"""
    n = t2n(1.8); t = np.arange(n) / SR
    y = lp(noise(n), 220) * (1 - np.exp(-t / .03)) * np.exp(-t / .9) * 1.4
    y += svf_bp(noise(n), 500 + 1500 * np.exp(-t / .3), .5) * np.exp(-t / .5) * .4
    cr = (np.random.default_rng(41).random(n) > .9993).astype(float)
    y += hp(cr, 2000) * np.exp(-t / .8) * 1.2
    y += sine(42 + 30 * np.exp(-t / .08), n) * np.exp(-t / .6) * .7
    return np.tanh(y) * .8


def glaze_ping():
    n = t2n(1.6); t = np.arange(n) / SR
    y = np.zeros(n)
    for f, a, d in ((2637, 1., .6), (4190, .5, .3), (6310, .25, .15), (1318, .2, .8)):
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
    return y * (1 - np.exp(-t / .001)) * .18


def porcelain_ring():
    """收尾：瓷器被轻弹的清鸣 + 编钟"""
    n = t2n(2.6); t = np.arange(n) / SR
    y = np.zeros(n)
    for f, a, d in ((1760, 1., 1.4), (2785, .55, .8), (4420, .3, .45), (6200, .15, .25)):
        y += a * np.sin(2 * np.pi * f * t + f) * np.exp(-t / d)
    y = y * (1 - np.exp(-t / .001)) * .2
    z = zhong(nm('D5'), 2.6, .6); y[:len(z)] += z * .6
    return y


SFX_NEW = {'brush_touch': brush_touch, 'brush_wash': brush_wash, 'wheel_spin': wheel_spin, 'kiln_roar': kiln_roar,
           'glaze_ping': glaze_ping, 'porcelain_ring': porcelain_ring}

# AAC-safe: take the edge off near-impulse transients so the codec does not ring past the true-peak ceiling
SFX_NEW = {k: (lambda f=f: lp(f(), 11000)) for k, f in SFX_NEW.items()}
