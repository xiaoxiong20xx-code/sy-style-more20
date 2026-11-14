# 51 马赛克 · 配乐：拜占庭小教堂——低沉的人声持续音（共振峰滤出的「啊」）托着五度，乌德琴般的拨弦走弗里吉亚调式，
# 手鼓（达甫）轻轻打拍，指钹点在重拍；油灯走过时一串细碎的玻璃金光声；8.0 秒一声钟和合唱和弦落下，余音在穹顶里散开。
# 音效：tessera_set（石块压进湿灰泥）、eye_set（点睛）、gold_shimmer（金块闪光）、sponge_wipe（海绵擦墙）、chapel_chord（收尾钟声）
import numpy as np


def choir(ms, dur, vowel=(700, 1150, 2800), amp=1.0, att=0.5):
    """a soft vowel 'ah' from saw voices through three formants"""
    n = t2n(dur); t = np.arange(n) / SR
    y = np.zeros(n)
    for m in ms:
        for dv in (-0.006, 0.0, 0.007):
            f = mtof(m) * (1 + dv) * (1 + 0.003 * np.sin(2 * np.pi * (4.6 + dv * 100) * t))
            y += polyblep_saw(f, n)
    out = sum(bp(y, f0 * 0.85, f0 * 1.15) * g for f0, g in zip(vowel, (1.0, 0.5, 0.18)))
    return out * adsr(n, att, 0.3, 0.85, 0.8) * 0.06 * amp


def oud(m, dur=0.7, vel=1.0):
    y = ks(m, dur, 0.55, 0.995)
    return lp(y, 3500) * 0.5 * vel


def daf(acc=False):
    n = t2n(0.35); t = np.arange(n) / SR
    y = sine(85 + 40 * np.exp(-t / 0.03), n) * np.exp(-t / (0.16 if acc else 0.09))
    y += bp(noise(n), 800, 4000) * np.exp(-t / 0.02) * (0.35 if acc else 0.5)
    return y * (0.7 if acc else 0.45)


def zill():
    n = t2n(1.2); t = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in ((3150, .5, .5), (4720, .35, .3), (6890, .2, .18), (2240, .2, .6)))
    return y * (1 - np.exp(-t / 0.0006)) * 0.18


def bell_toll(m=45, dur=3.5):
    n = t2n(dur); t = np.arange(n) / SR; f = mtof(m)
    y = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d) for r, a, d in ((0.5, .5, 2.4), (1.0, 1.0, 1.8), (1.19, .45, 1.2), (1.5, .35, 1.0), (2.0, .4, .8), (2.52, .25, .5), (3.0, .15, .3)))
    return y * (1 - np.exp(-t / 0.001)) * 0.25


PHRY = {'E4': 64, 'F4': 65, 'G4': 67, 'A4': 69, 'Bb4': 70, 'C5': 72, 'D5': 74, 'E5': 76}
LINE = [
    ['A4', None, None, 'Bb4', 'A4', None, None, None],
    [None, None, 'C5', 'Bb4', 'A4', 'G4', 'A4', None],
    ['D5', None, 'C5', 'Bb4', 'C5', 'D5', 'E5', None],
    ['D5', 'C5', 'Bb4', None, 'A4', 'G4', 'F4', 'E4'],
    ['A4', None, None, None, None, None, None, None],
]


def mus(M, tb, name, root, tones, bi):
    # the drone: A and E held in the voices from the first frame to the bell (one long breath, no gaps at the bar lines);
    # a third voice joins for the gold
    if bi == 0: M.add('music', choir([45, 52], BAR * 4.15, amp=1.35, att=0.15), tb, 0.8, 0, 0.6)
    if bi == 2: M.add('music', choir([57], BAR * 2.1, amp=1.2, att=0.6), tb, 0.8, 0, 0.6)
    if bi == 4: M.add('music', choir([45, 52], BAR * 1.05, amp=1.0, att=0.3), tb, 0.8, 0, 0.6)
    # oud line
    for e, sN in enumerate(LINE[bi]):
        if sN: M.add('music', oud(PHRY[sN], 0.8, 1.0 if e % 2 == 0 else 0.8), tb + e * BEAT / 2, 0.5, 0.2 - 0.1 * (e % 3), 0.4)
    # frame drum and finger cymbals
    if bi == 0:                                                      # the frame drum already breathing under the first stones
        for q in (0, 2, 3): M.add('drums', daf(q != 3), tb + q * BEAT, 0.42 if q != 3 else 0.3, -0.2, 0.3)
    if 0 < bi < 4:
        for q, acc in ((0, True), (1.5, False), (2, True), (3, False), (3.5, False)): M.add('drums', daf(acc), tb + q * BEAT, 0.6 if acc else 0.4, -0.2, 0.3)
        M.add('drums', zill(), tb, 0.35, 0.35, 0.5)
    if bi == 4:
        M.add('music', choir([45, 52, 57, 61, 64], BAR, (750, 1200, 2900), 0.8), tb, 0.8, 0, 0.7)


# ---------------- SFX ----------------
def tessera_set():
    """a stone tessera pressed home into wet bedding: a dry tick, then a small wet give"""
    n = t2n(0.3); t = np.arange(n) / SR
    y = np.zeros(n)
    for f, a, d in ((2400, .35, .012), (3900, .22, .007), (1300, .2, .02)):
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
    y += hp(noise(n), 3000) * np.exp(-t / 0.002) * 0.5
    k = t2n(0.015); w = lp(noise(n - k), 900) * np.exp(-np.arange(n - k) / SR / 0.05) * 0.35
    y[k:] += w
    return y * 0.7


def eye_set():
    y = tessera_set()
    n = t2n(1.6); t = np.arange(n) / SR
    out = np.zeros(n); out[:len(y)] += y
    out += (np.sin(2 * np.pi * 1760 * t) * np.exp(-t / 0.5) + 0.4 * np.sin(2 * np.pi * 2640 * t) * np.exp(-t / 0.25)) * 0.12
    return out


def gold_shimmer():
    """the lamp passing: a cascade of tiny glassy glints, densest in the middle of the sweep"""
    dur = 2.2; out = np.zeros(t2n(dur + 0.6)); r = np.random.default_rng(51)
    pent = [76, 79, 81, 84, 86, 88, 91, 93]
    tt = 0.0
    while tt < dur:
        dens = np.sin(np.pi * tt / dur) ** 1.3
        m = pent[r.integers(len(pent))]
        n = t2n(0.5); t = np.arange(n) / SR
        y = (np.sin(2 * np.pi * mtof(m) * t) * np.exp(-t / 0.18) + 0.3 * np.sin(2 * np.pi * mtof(m) * 2.76 * t) * np.exp(-t / 0.05)) * 0.068 * (0.4 + 0.6 * dens)
        k = t2n(tt); out[k:k + n] += y[: len(out) - k]
        tt += 0.035 + 0.12 * (1 - dens) * r.random()
    return out


def sponge_wipe():
    n = t2n(0.8); t = np.arange(n) / SR; u = t / 0.8
    y = svf_bp(noise(n), 900 + 1500 * np.sin(np.pi * u), 0.5) * np.sin(np.pi * u) ** 1.2 * 0.5
    y *= 0.75 + 0.25 * np.sin(2 * np.pi * 31 * t)                   # the wet drag of the pores
    y += lp(noise(n), 400) * np.sin(np.pi * u) * 0.12
    return y


def chapel_chord():
    a = bell_toll(45, 3.5); b = bell_toll(57, 3.5)
    return (a + 0.5 * b) * 0.45


SFX_NEW = {'tessera_set': tessera_set, 'eye_set': eye_set, 'gold_shimmer': gold_shimmer, 'sponge_wipe': sponge_wipe, 'chapel_chord': chapel_chord}
