# 48 扎染 · 配乐：云南白族院子里的日光——三弦/月琴式拨弦 + 竹笛 + 手鼓，五声音阶；
# 浸染段只有拨弦和笛子；钩子三拍各配一声太鼓和上行的钟琴；解绳四拍拨弦重音；8.0 布抖开时和弦落下。
# 音效：院子环境（courtyard：鸟、风）、入缸（plunge）、咕嘟（glug）、出水（lift_water）、滴落（drip）、
#       氧化三拍（air_bloom1/2/3）、绳子弹开（cord_snap）、布抖开（cloth_flap）
import numpy as np

PENT = ['A3', 'C4', 'D4', 'E4', 'G4', 'A4', 'C5', 'D5', 'E5', 'G5', 'A5', 'C6']


def pluck(m, dur=1.0, vel=1.0):          # bright, dry plucked lute
    y = ks(m, dur, 0.85, 0.9965)
    n = len(y); t = np.arange(n) / SR
    return (y + hp(noise(n), 3000) * np.exp(-t / 0.003) * 0.2) * 0.5 * vel


def dizi(m, dur, vel=1.0):
    n = t2n(dur); t = np.arange(n) / SR
    y = flute(m, dur) * 1.1
    y += bp(noise(n), mtof(m) * 1.5, mtof(m) * 4) * adsr(n, 0.05, 0.1, 0.6, 0.2) * 0.07
    return y * vel


def hand_drum(f=110):
    n = t2n(0.35); t = np.arange(n) / SR
    return (sine(f * (1 + 0.6 * np.exp(-t / 0.02)), n) * np.exp(-t / 0.12) + bp(noise(n), 400, 2500) * np.exp(-t / 0.015) * 0.3) * 0.6


FLUTE = {0: [('E5', 1.0), ('D5', 0.5), ('C5', 0.5)], 1: [('A4', 1.5), ('C5', 0.5)], 3: [('G5', 1.0), ('E5', 1.0)]}


def mus(M, tb, name, root, tones, bi):
    last = bi == 4
    pt = [nm(x) for x in PENT]
    if not last:
        # plucked lute: a lilting figure on the half beats
        fig = [0, 4, 2, 5, 3, 4, 2, 1] if bi % 2 == 0 else [5, 3, 4, 2, 4, 1, 2, 0]
        for e, k in enumerate(fig):
            M.add('music', pluck(pt[3 + k] + 12, 0.9, 0.9 if e % 2 == 0 else 0.65), tb + e * BEAT / 2, 0.36, -0.25 + 0.07 * e, 0.3)
        M.add('music', pluck(root, 1.6, 0.9), tb, 0.45, -0.1, 0.2)
        M.add('music', pluck(root + 7, 1.0, 0.7), tb + 2 * BEAT, 0.35, -0.1, 0.2)
        if bi in FLUTE:
            tt = tb
            for sN, d in FLUTE[bi]:
                M.add('music', dizi(nm(sN), BEAT * d * 2 * 1.02), tt, 0.32, 0.2, 0.5); tt += BEAT * d * 2
        M.add('drums', hand_drum(120), tb, 0.45, 0, 0.2)
        if bi >= 1: M.add('drums', hand_drum(160), tb + 2.5 * BEAT, 0.3, 0.1, 0.2)
        if bi in (2, 3):
            M.add('music', strings([x + 12 for x in tones], BAR * 1.02, 2000), tb, 0.25, 0, 0.6)
            for e in range(8): M.add('drums', shaker(), tb + e * BEAT / 2 + BEAT / 4, 0.07, 0.35)
        if bi == 2:      # the three beats of air
            for q in range(3): M.add('drums', taiko() * (0.7 + 0.15 * q), tb + q * BEAT, 0.5, 0, 0.4)
        if bi == 3:      # cords snapping on every beat
            for q in range(4): M.add('drums', hand_drum(140 + 20 * q), tb + q * BEAT, 0.35, 0, 0.2)
        return
    # 8.0: the cloth opens — chord rings out
    for j, m in enumerate(tones + [tones[0] + 12]):
        M.add('music', pluck(m + 12, 2.6, 0.9), tb + j * 0.03, 0.4, -0.25 + 0.15 * j, 0.5)
        M.add('music', bell(m + 24, 2.4, 0.6), tb + j * 0.05, 0.12, -0.3 + 0.2 * j, 0.6)
    M.add('music', dizi(tones[0] + 24, BAR * 0.9), tb + 0.02, 0.3, 0.2, 0.6)
    M.add('music', strings([x + 12 for x in tones], BAR * 0.95, 1800), tb, 0.25, 0, 0.6)
    M.add('drums', taiko(), tb, 0.55, 0, 0.4)


# ---------------- SFX ----------------
def courtyard():
    n = t2n(10.0); t = np.arange(n) / SR
    wind = lp(noise(n), 700) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t + 1) ** 2) * 0.12
    y = wind
    r = np.random.default_rng(48)
    for k in range(9):           # a few birds in the trees
        t0 = r.uniform(0.2, 9.2); m = r.uniform(2600, 4200)
        for c in range(r.integers(2, 5)):
            nn = t2n(0.07); tt = np.arange(nn) / SR
            ch = sine(m * (1 + 0.25 * np.sin(np.pi * tt / 0.07)), nn) * np.sin(np.pi * tt / 0.07) ** 2 * 0.09
            i0 = t2n(t0 + c * 0.11); y[i0:i0 + nn] += ch[: n - i0]
    return y * np.clip(t / 0.5, 0, 1)


def plunge():
    n = t2n(0.9); t = np.arange(n) / SR
    y = sine(70 + 60 * np.exp(-t / 0.05), n) * np.exp(-t / 0.18) * 0.6
    y += bp(noise(n), 300, 3000) * np.exp(-t / 0.12) * 0.5
    r = np.random.default_rng(3)
    for k in range(10):
        nn = t2n(0.05); tt = np.arange(nn) / SR; f = r.uniform(400, 1200)
        b = sine(f * (1 + 2 * tt / 0.05), nn) * np.exp(-tt / 0.02) * 0.12; i0 = t2n(r.uniform(0.05, 0.6)); y[i0:i0 + nn] += b[: n - i0]
    return y


def glug():
    y = np.zeros(t2n(0.8)); r = np.random.default_rng(5)
    for k in range(6):
        nn = t2n(0.06); tt = np.arange(nn) / SR; f = r.uniform(250, 600)
        b = sine(f * (1 + 1.5 * tt / 0.06), nn) * np.exp(-tt / 0.025) * 0.25; i0 = t2n(k * 0.11 + r.uniform(0, 0.04)); y[i0:i0 + nn] += b[: len(y) - i0]
    return y


def lift_water():
    n = t2n(1.6); t = np.arange(n) / SR
    y = bp(noise(n), 500, 5000) * np.exp(-t / 0.35) * 0.5 * np.clip(t / 0.05, 0, 1)
    y += lp(noise(n), 400) * np.exp(-t / 0.2) * 0.3
    return y


def drip():
    n = t2n(0.25); t = np.arange(n) / SR
    f = 1500 * np.exp(-t / 0.02) + 700
    return sine(f, n) * np.exp(-t / 0.04) * 0.35 + hp(noise(n), 3000) * np.exp(-t / 0.003) * 0.15


def _bloom(m):
    n = t2n(1.0); t = np.arange(n) / SR
    y = svf_bp(noise(n), 600 + 2500 * np.sin(np.pi * t / 1.0) ** 2, 0.7) * np.sin(np.pi * np.clip(t / 0.7, 0, 1)) ** 2 * 0.3
    y[: t2n(1.0)] += bell(nm(m), 1.0, 0.5)[: n] * 0.25
    return y


def cord_snap():
    n = t2n(0.4); t = np.arange(n) / SR
    y = ks(nm('E5'), 0.4, 0.9, 0.99)[:n] * 0.5
    y += hp(noise(n), 2500) * np.exp(-t / 0.006) * 0.4
    y += bp(noise(n), 1000, 5000) * np.exp(-t / 0.06) * 0.15
    return y


def cloth_flap():
    n = t2n(0.6); t = np.arange(n) / SR
    am = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 34 * t))
    y = bp(noise(n), 200, 3500) * am * np.exp(-t / 0.12) * 0.7
    y += sine(90, n) * np.exp(-t / 0.08) * 0.35
    return y


SFX_NEW = {'courtyard': courtyard, 'plunge': plunge, 'glug': glug, 'lift_water': lift_water, 'drip': drip,
           'air_bloom1': lambda: _bloom('E6'), 'air_bloom2': lambda: _bloom('G6'), 'air_bloom3': lambda: _bloom('A6'),
           'cord_snap': cord_snap, 'cloth_flap': cloth_flap}
