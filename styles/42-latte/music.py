# 42 咖啡拉花 — a daytime café: bossa nova at 120 BPM. Nylon guitar comping (Karplus-Strong strums), upright bass on
# 1 and 3, brushes and a soft rim, Rhodes underneath, a little vibraphone melody. Gentle while the milk goes in, the groove
# fills out for the stacks, busiest on the wrist wiggle (4.0), a turnaround over the top stacks, and a Dmaj9 strummed on
# the cut (8.0) that rings out over the overhead hold.
# (synth.py's functions are injected into this module by build.py)

_r = np.random.default_rng(4242)
E8 = BEAT / 2
S16 = BEAT / 4
# (bass root, chord voicing) per half bar
DMAJ9 = (38, [54, 57, 61, 64])
BM7 = (47, [57, 62, 66, 69])
EM9 = (40, [55, 59, 62, 66])
A13 = (45, [55, 61, 66, 69])
B7 = (47, [54, 57, 63, 66])
GMAJ7 = (43, [54, 59, 62, 66])
PROG42 = {0: (DMAJ9, BM7), 1: (EM9, A13), 2: (DMAJ9, B7), 3: (EM9, A13)}


def nylon(m, dur=1.0, bright=0.45):
    y = ks(m, dur, bright, 0.9965)
    n = len(y); t = np.arange(n) / SR
    y = y + 0.2 * bp(y, 150, 500)                       # the guitar body
    y += bp(noise(n), 2000, 6000) * np.exp(-t / 0.004) * 0.05
    return y * 0.8


def strum(M, t, ms, gain=0.32, down=True, dur=0.9):
    order = ms if down else ms[::-1]
    for j, m in enumerate(order):
        M.add('music', nylon(m, dur), t + j * 0.012, gain * (0.85 + 0.15 * _r.random()), -0.25 + 0.15 * j, 0.3)


def bass_u(m, dur):
    return upright(m, dur) * 0.9


def rim_soft():
    n = t2n(0.08); t = np.arange(n) / SR
    return (bp(noise(n), 1800, 5000) * np.exp(-t / 0.008) * 0.5 + sine(820, n) * np.exp(-t / 0.02) * 0.25)


def comp_bar(M, tb, bi, busy=False):
    (r1, c1), (r2, c2) = PROG42[bi]
    # bossa thumb: root on 1, fifth on 3 (pushed into the next chord)
    M.add('music', bass_u(r1, BEAT * 1.4), tb, 0.6)
    M.add('music', bass_u(r1 + 7, BEAT * 0.9), tb + 1.5 * BEAT, 0.42)
    M.add('music', bass_u(r2, BEAT * 1.4), tb + 2 * BEAT, 0.58)
    M.add('music', bass_u(r2 + 7, BEAT * 0.9), tb + 3.5 * BEAT, 0.4)
    # chord stabs on the bossa pattern (eighths 1, 3, 4, 6 of 8)
    for e in (1, 3):
        strum(M, tb + e * E8, c1, 0.28 if e == 1 else 0.24, e % 2 == 1, 0.5)
    for e in (4, 6):
        strum(M, tb + e * E8, c2, 0.27 if e == 4 else 0.23, e == 4, 0.5)
    # brushes: a swish on every eighth, soft rim on 2 and 4
    for e in range(8):
        M.add('drums', brush(0.2), tb + e * E8, 0.5 if e % 2 else 0.35, 0.15)
    for q in (1, 3):
        M.add('drums', rim_soft(), tb + q * BEAT, 0.35, -0.1, 0.15)
    if busy:
        for s in range(16):
            M.add('drums', shaker(), tb + s * S16, 0.22 if s % 2 else 0.12, 0.35)
    # Rhodes pad underneath
    M.add('music', sum(epiano(m, BAR) for m in c1) * 0.18, tb, 0.5, 0, 0.35)
    M.add('music', sum(epiano(m, BAR * 0.6) for m in c2) * 0.18, tb + 2 * BEAT, 0.45, 0, 0.35)


def mus(M, tb, name, root, tones, bi):
    if bi == 0:      # the high pour: just guitar and a Rhodes chord, the bass enters on the bloom (1.0)
        (r1, c1), (r2, c2) = PROG42[0]
        strum(M, tb, c1, 0.3, True, 1.6)
        M.add('music', sum(epiano(m, BAR) for m in c1) * 0.18, tb, 0.5, 0, 0.4)
        for e in range(2, 8):
            M.add('drums', brush(0.2), tb + e * E8, 0.28 if e % 2 else 0.18, 0.15)
        M.add('music', bass_u(r2, BEAT * 1.4), tb + 2 * BEAT, 0.55)
        strum(M, tb + 4 * E8, c2, 0.26, True, 0.6); strum(M, tb + 6 * E8, c2, 0.22, False, 0.5)
        M.add('music', vibes(78, 1.4), tb + 2 * BEAT, 0.2, 0.3, 0.5)
    elif bi == 1:    # the stacks
        comp_bar(M, tb, 1)
        for k, (m, off) in enumerate([(76, 0), (74, 1.0), (73, 2.0), (71, 3.0)]):
            M.add('music', vibes(m, 1.0), tb + off * BEAT, 0.2, 0.3, 0.5)
    elif bi == 2:    # the wiggle: busy, shaker sixteenths, a vibes run
        comp_bar(M, tb, 2, busy=True)
        for s, m in enumerate([74, 76, 78, 81, 78, 76, 74, 73]):
            M.add('music', vibes(m, 0.6), tb + s * E8, 0.18, 0.3 if s % 2 else -0.2, 0.45)
    elif bi == 3:    # the top stacks and the cut: turnaround
        comp_bar(M, tb, 3)
        M.add('music', vibes(76, 0.9), tb + BEAT, 0.18, 0.3, 0.5)
        M.add('music', vibes(73, 1.4), tb + 3 * BEAT, 0.2, 0.3, 0.5)
    else:            # 8.0: the tulip is done — a Dmaj9 strummed slowly, low D, vibes on top, rings out
        M.add('music', bass_u(38, BAR * 1.2), tb, 0.6)
        strum(M, tb, [45, 50, 54, 57, 61, 64, 69], 0.3, True, 2.6)
        M.add('music', sum(epiano(m, BAR * 1.2) for m in [54, 57, 61, 64]) * 0.18, tb, 0.5, 0, 0.5)
        M.add('music', vibes(81, 2.2), tb + 0.02, 0.22, 0.3, 0.6)
        M.add('music', vibes(76, 2.0), tb + BEAT * 0.5, 0.16, -0.3, 0.6)


# ---------------- sound effects ----------------
def milk_pour(dur=1.05):
    # a thin stream from height into liquid: a bright splashy hiss with small bubbly gurgles
    n = t2n(dur); t = np.arange(n) / SR
    env = np.clip(t / 0.08, 0, 1) * np.clip((dur - t) / 0.12, 0, 1)
    y = bp(noise(n), 1200, 5200) * 0.22 * (0.8 + 0.2 * np.sin(2 * np.pi * 13 * t))
    for k in _r.integers(0, n - 2400, 18):
        L = 2400; tt = np.arange(L) / SR
        y[k:k + L] += np.sin(2 * np.pi * (380 + 500 * _r.random()) * tt * (1 + tt * 6)) * np.exp(-tt / 0.012) * 0.12
    return y * env


def foam_bloom():
    n = t2n(0.6); t = np.arange(n) / SR
    y = sine(150 * np.exp(-t / 0.09) + 70, n) * np.exp(-t / 0.12) * 0.4
    y += lp(noise(n), 1600) * np.sin(np.pi * np.clip(t / 0.6, 0, 1)) ** 2 * 0.2
    return y


def foam_push():
    # a soft liquid swell: the jug dips, foam rolls forward
    n = t2n(0.38); t = np.arange(n) / SR
    y = svf_bp(noise(n), 500 + 900 * (t / 0.38), 0.6) * np.sin(np.pi * np.clip(t / 0.38, 0, 1)) * 0.3
    y += sine(110 + 40 * (t / 0.38), n) * np.exp(-t / 0.08) * 0.18
    return y


def foam_wiggle():
    n = t2n(1.0); t = np.arange(n) / SR
    y = svf_bp(noise(n), 700 + 400 * np.sin(2 * np.pi * 6 * t), 0.5) * 0.3
    y *= (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 3 * t))) * np.clip(t / 0.05, 0, 1) * np.clip((1.0 - t) / 0.1, 0, 1)
    return y


def foam_cut():
    n = t2n(0.55); t = np.arange(n) / SR
    y = bp(noise(n), 2500, 8000) * 0.16 * (1 - t / 0.55) ** 0.5
    return y * np.clip(t / 0.03, 0, 1)


def last_drip():
    return np.concatenate([np.zeros(t2n(0.04)), sfx_drip() * 0.9])


SFX_NEW = {'milk_pour': milk_pour, 'foam_bloom': foam_bloom, 'foam_push': foam_push, 'foam_wiggle': foam_wiggle,
           'foam_cut': foam_cut, 'last_drip': last_drip}
