# 52 机械表芯 · 配乐：精密的钟表感——擒纵的「嘀/嗒」就是八分音符的踩镲（场景 cues 里每 0.25 秒一下，和擒纵轮跳格同一帧），
# 上面是羽管键琴般明亮的拨弦琶音（十六分音符）、拨奏低音和一层很薄的弦乐；钩子处低音脉冲加重；
# 8.0 秒止秒杆一碰，嘀嗒停住，一个钟声和和弦落下，余音散开。
# 音效：tick_hi / tick_lo（嘀 / 嗒）、macro_air（开头空气声）、focus_pull（拉焦）、train_glide（沿齿轮滑行）、stop_click（止秒）
import numpy as np


def hpsi(m, dur=0.45, vel=1.0):
    """harpsichord-like pluck: a bright Karplus-Strong with a quill click"""
    y = ks(m, dur, 1.0, 0.9975)
    n = len(y); t = np.arange(n) / SR
    y = y + 0.35 * hp(y, 3000)
    y[:t2n(0.004)] += hp(noise(t2n(0.004)), 4000) * 0.3
    return y * 0.32 * vel * (1 - np.exp(-t / 0.001))


def pizz(m, dur=0.5, vel=1.0):
    y = ks(m, dur, 0.3, 0.993)
    n = len(y); t = np.arange(n) / SR
    return lp(y, 1600) * np.exp(-t / 0.35) * 0.8 * vel


def strings(ms, dur, cut=2200):
    out = None
    for m in ms:
        n = t2n(dur); t = np.arange(n) / SR
        f = mtof(m) * (1 + 0.004 * np.sin(2 * np.pi * 5.2 * t))
        y = polyblep_saw(f, n) * 0.5 + polyblep_saw(f * 1.003, n) * 0.5
        y = lp(y, cut) * adsr(n, 0.35, 0.2, 0.85, 0.6)
        out = y if out is None else out + y
    return out * 0.10


def chime(m, dur=3.0):
    n = t2n(dur); t = np.arange(n) / SR; f = mtof(m)
    y = np.zeros(n)
    for r, a, d in ((1.0, 1.0, 1.6), (2.0, .4, .8), (2.76, .3, .5), (5.4, .15, .2), (8.9, .06, .08)):
        y += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d)
    return y * (1 - np.exp(-t / 0.0008)) * 0.22


ARP = {  # sixteenth-note broken chords per bar (A minor -> F -> C -> G -> A)
    0: None,
    1: [57, 60, 64, 69, 72, 69, 64, 60],
    2: [53, 57, 60, 65, 69, 65, 60, 57],
    3: [55, 59, 62, 67, 71, 67, 62, 59],
}
BASSL = [[45, None, None, None], [45, 45, 52, 45], [41, 41, 48, 41], [43, 43, 50, 47], [33, None, None, None]]


def mus(M, tb, name, root, tones, bi):
    # plucked bass on the beats
    for q, m in enumerate(BASSL[bi]):
        if m: M.add('music', pizz(m, 0.6, 1.0 if q == 0 else 0.7), tb + q * BEAT, 0.6, -0.15, 0.2)
    # the bed
    if bi in (1, 2, 3): M.add('music', strings([x + 12 for x in tones], BAR * 1.02), tb, 0.55, 0, 0.35)
    # harpsichord: sparse in bar 0, sixteenths through the middle
    if bi == 0:
        for e, m in enumerate([None, None, 76, None, 72, None, 69, 71]):
            if m: M.add('music', hpsi(m, 0.5, 0.8), tb + e * BEAT / 2, 0.45, 0.3, 0.3)
    elif bi in ARP:
        pat = ARP[bi]
        for s16 in range(16):
            m = pat[s16 % 8] + (12 if (bi == 2 and s16 >= 8) else 0)
            M.add('music', hpsi(m, 0.35, 1.0 if s16 % 4 == 0 else 0.7), tb + s16 * BEAT / 4, 0.42, -0.35 + 0.7 * (s16 % 2), 0.25)
    # a soft low pulse drives the hook (bar 2) and the climb out (bar 3)
    if bi in (2, 3):
        for q in range(4): M.add('drums', soft_kick(), tb + q * BEAT, 0.55); M.sidechain(tb + q * BEAT, 0.25)
    if bi == 4:   # stopped: a chime and the resolving chord, then only their ring
        M.add('music', chime(81, 3.0), tb, 0.6, 0.2, 0.6)
        M.add('music', chime(76, 3.0), tb + 0.03, 0.4, -0.2, 0.6)
        for j, m in enumerate([57, 64, 69, 72, 76]): M.add('music', hpsi(m, 1.6, 0.9), tb + j * 0.02, 0.45, -0.3 + 0.15 * j, 0.5)
        M.add('music', strings([57, 64, 69, 72], BAR * 0.9, 1800), tb, 0.5, 0, 0.5)


# ---------------- SFX ----------------
def _tick(fr, amp):
    n = t2n(0.06); t = np.arange(n) / SR
    y = hp(noise(n), 5000) * np.exp(-t / 0.0007) * 0.9
    for f, a, d in fr:
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
    return y * amp


def tick_hi():
    return _tick(((5200, .45, .006), (7400, .3, .004), (9600, .2, .0025), (1350, .12, .012)), 0.55)


def tick_lo():
    return _tick(((3900, .45, .007), (5600, .3, .005), (8100, .18, .003), (1050, .14, .014)), 0.55)


def macro_air():
    n = t2n(1.8); t = np.arange(n) / SR; u = t / 1.8
    return (lp(noise(n), 300) * 0.08 + bp(noise(n), 3000, 9000) * 0.012) * np.sin(np.pi * u) ** 1.5


def focus_pull():
    n = t2n(0.7); t = np.arange(n) / SR; u = t / 0.7
    return svf_bp(noise(n), 600 + 1800 * u, 0.5) * np.sin(np.pi * u) ** 2 * 0.25


def train_glide():
    n = t2n(1.8); t = np.arange(n) / SR; u = t / 1.8
    y = svf_bp(noise(n), 300 + 1500 * np.sin(np.pi * u), 0.55) * np.sin(np.pi * u) ** 1.5 * 0.35
    y += sine(110, n) * 0.05 * np.sin(np.pi * u)
    return y


def stop_click():
    n = t2n(0.8); t = np.arange(n) / SR
    y = hp(noise(n), 3000) * np.exp(-t / 0.002) * 0.8
    for f, a, d in ((2900, .35, .05), (4600, .25, .03), (6800, .15, .015), (780, .2, .04)):
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
    return y * 0.7


SFX_NEW = {'tick_hi': tick_hi, 'tick_lo': tick_lo, 'macro_air': macro_air, 'focus_pull': focus_pull, 'train_glide': train_glide, 'stop_click': stop_click}
