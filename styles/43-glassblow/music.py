# 43 吹制玻璃 · 配乐：炉火的低频底 + 拨弦低音的律动 + 钢件敲击；冷却后换成玻璃质的钟音和长垫，8.0 一声玻璃泛音收住
# 调式：A 多利亚。build.py 注入 synth.py 的函数。

def furnace(dur, vel=1.0):
    n = t2n(dur); t = np.arange(n) / SR
    y = lp(noise(n), 160) * .5 + svf_bp(noise(n), 420 + 80 * np.sin(2 * np.pi * .7 * t), .7) * .12
    return y * (.85 + .15 * np.sin(2 * np.pi * 3.1 * t)) * vel


def bassp(m, dur=.5, vel=1.0):
    return upright(m, dur) * vel


def anvil(vel=1.0):
    n = t2n(.5); t = np.arange(n) / SR
    y = np.zeros(n)
    for f, a, d in ((1530, 1., .12), (2410, .6, .08), (3790, .35, .05)):
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
    return (y + hp(noise(n), 3000) * np.exp(-t / .004)) * .22 * vel


def glassbell(m, dur=2.0, vel=1.0):
    n = t2n(dur); f = mtof(m); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 1.1) + .35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / .3) + .15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / .1)
    return y * (1 - np.exp(-t / .001)) * .18 * vel


A = {'A1': 33, 'A2': 45, 'C3': 48, 'D3': 50, 'E3': 52, 'G3': 55, 'A3': 57, 'C4': 60, 'D4': 62, 'E4': 64, 'F#4': 66, 'G4': 67, 'A4': 69,
     'B4': 71, 'C5': 72, 'D5': 74, 'E5': 76, 'G5': 79, 'A5': 81, 'B5': 83, 'E6': 88}


def mus(M, tb, name, root, tones, bi):
    if bi < 2:        # hot: the furnace, a walking bass, steel on the off-beats
        M.add('music', furnace(BAR * 1.05, 1.), tb, .55, 0, .1)
        walk = [['A2', 'A2', 'E3', 'G3'], ['D3', 'D3', 'A2', 'C3']][bi]
        for q, s in enumerate(walk): M.add('music', bassp(A[s], BEAT * .9, .9), tb + q * BEAT, .55, -.05)
        for q in range(4): M.add('drums', anvil(.5 if q % 2 else .35), tb + q * BEAT + BEAT / 2, .4, .3, .2)
        M.add('music', pad([A['A3'], A['E4'], A['G4']], BAR, 900), tb, .25, 0, .3)
    elif bi == 2:     # it cools: the bass drops out, glass begins to ring
        M.add('music', furnace(BAR * .7, .6), tb, .4, 0, .1)
        M.add('music', pad([A['A3'], A['E4'], A['B4'], A['F#4'] + 12], BAR * 1.05, 2600), tb, .4, 0, .5)
        for e, s in enumerate(['E5', None, 'B5', None, 'A5', None, 'E6', None]):
            if s: M.add('music', glassbell(A[s], 2.0, .8), tb + e * BEAT / 2, .4, -.3 + .15 * e, .55)
        M.add('music', bassp(A['A2'], BEAT * 1.8, .8), tb, .45)
    elif bi == 3:
        M.add('music', pad([A['D4'], A['A4'], A['E5'], A['F#4'] + 12], BAR * 1.05, 2600), tb, .4, 0, .5)
        for e, s in enumerate(['A5', None, None, 'G5', 'E5', None, 'D5', None]):
            if s: M.add('music', glassbell(A[s], 2.0, .75), tb + e * BEAT / 2, .38, .3 - .1 * e, .55)
        M.add('music', bassp(A['D3'], BEAT * 1.8, .7), tb, .4)
    else:             # 8.0: the vase rings
        M.add('music', pad([A['A3'], A['E4'], A['A4'], A['C5'] + 1, A['E5']], BAR, 2400), tb, .38, 0, .55)
        for k, m in enumerate((A['A4'], A['E5'], A['A5'])): M.add('music', glassbell(m, 3.0, .8), tb + k * .02, .4, -.2 + .2 * k, .6)
        M.add('music', bassp(A['A2'], BEAT * 2, .6), tb, .35)


# ---------- SFX ----------
def furnace_roar():
    n = t2n(1.6); t = np.arange(n) / SR
    return (lp(noise(n), 250) * .6 + svf_bp(noise(n), 700, .5) * .15) * np.clip(t / .3, 0, 1) * np.exp(-np.clip(t - .8, 0, None) / .4) * .9


def block_steam():
    """湿木勺碰到热料：一阵白汽的嘶声"""
    n = t2n(1.2); t = np.arange(n) / SR
    return hp(noise(n), 3000) * np.clip(t / .04, 0, 1) * np.exp(-t / .5) * .3 + bp(noise(n), 600, 2000) * np.exp(-t / .2) * .1


def blow_puff():
    """往吹管里吹一口气：气流声 + 料泡鼓起的低频"""
    n = t2n(.6); t = np.arange(n) / SR; u = t / .6
    y = svf_bp(noise(n), 500 + 300 * u, .6) * np.sin(np.pi * np.clip(u * 1.3, 0, 1)) * .35
    y += sine(70 + 25 * u, n) * np.sin(np.pi * u) * .3
    return y


def jacks_ring():
    n = t2n(1.0); t = np.arange(n) / SR
    y = np.zeros(n)
    for f, a, d in ((2840, 1., .25), (4130, .55, .15), (6020, .3, .08), (1490, .25, .35)):
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
    y += svf_bp(noise(n), 900, 1.) * np.exp(-t / .05) * .3       # the glass hissing on the steel
    return y * (1 - np.exp(-t / .001)) * .2


def flare_whoosh():
    return whoosh(.6, True, 300, 4000, .45)


def cool_hiss():
    """冷却：一阵嘶声由亮转暗，玻璃开始发出细小的咔声"""
    n = t2n(1.5); t = np.arange(n) / SR
    y = svf_bp(noise(n), 6000 * np.exp(-t / .5) + 800, .5) * np.exp(-t / .6) * .3
    cr = (np.random.default_rng(43).random(n) > .9995).astype(float)
    y += hp(cr, 3000) * np.clip((t - .3) / .5, 0, 1) * .6
    return y


def glass_ting():
    return glassbell(nm('E6'), 1.6, 1.) * 1.3


def glint_ring():
    n = t2n(2.4); y = np.zeros(n)
    for k, m in enumerate((nm('A6'), nm('E7'), nm('A7'))):
        b = glassbell(m, 2.2, .9); s0 = t2n(k * .07); y[s0:s0 + len(b)] += b[:n - s0]
    t = np.arange(n) / SR
    y += svf_bp(noise(n), 4000 + 3500 * np.clip(t / .6, 0, 1), .5) * np.sin(np.pi * np.clip(t / .7, 0, 1)) * .06
    return y


SFX_NEW = {'furnace_roar': furnace_roar, 'block_steam': block_steam, 'blow_puff': blow_puff, 'jacks_ring': jacks_ring,
           'flare_whoosh': flare_whoosh, 'cool_hiss': cool_hiss, 'glass_ting': glass_ting, 'glint_ring': glint_ring}

# AAC-safe: take the edge off near-impulse transients so the codec does not ring past the true-peak ceiling
SFX_NEW = {k: (lambda f=f: lp(f(), 11000)) for k, f in SFX_NEW.items()}
