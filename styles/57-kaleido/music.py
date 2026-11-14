# 57 万花筒 — wonder in G major: a music box and a harp. Each beat-notch of the cell is a little harp arpeggio over a music-box
# melody; the oil-cell charge sounds like glass beads settling, muffled. Hook 4.0: the pull-back out of the eyepiece — the
# strings swell and a warm low note opens the room; 7.6 a harp glissando dives back in; 8.0 the last notch: a full chord rings.
# (synth.py's functions are injected into this module by build.py)

_r = np.random.default_rng(5757)
E8 = BEAT / 2
CH57 = {0: [55, 59, 62, 66], 1: [52, 55, 59, 62], 2: [48, 52, 55, 59], 3: [50, 54, 57, 60], 4: [43, 55, 59, 62, 66, 69]}
MEL57 = {0: [79, 78, 74, 71], 1: [76, 74, 71, 67], 2: [76, 79, 81, 83], 3: [81, 78, 74, 72]}


def musicbox(m, dur=1.2, amp=1.0):
    n = t2n(dur); t = np.arange(n) / SR; f = mtof(m)
    y = sine(f, n) * np.exp(-t / 0.6) + 0.4 * sine(f * 3.0, n) * np.exp(-t / 0.12) + 0.2 * sine(f * 5.2, n) * np.exp(-t / 0.05)
    return y * (1 - np.exp(-t / 0.0008)) * 0.3 * amp


def harp(m, dur=1.6):
    return ks(m, dur, 0.45, 0.998) * 0.6


def arp(M, t, ms, gain=0.22, step=0.045):
    for j, m in enumerate(ms):
        M.add('music', harp(m, 1.4), t + j * step, gain, -0.3 + 0.15 * j, 0.45)


def mus(M, tb, name, root, tones, bi):
    ch = CH57[bi]
    if bi < 4:
        for q, m in enumerate(MEL57[bi]):
            M.add('music', musicbox(m, 1.2), tb + q * BEAT, 0.32, 0.25, 0.5)
    if bi == 0:      # looking in: music box, a harp roll on each notch (0.5, 1.0, 1.5)
        M.add('music', pad([x + 12 for x in ch], BAR + 0.4, 1500, 0.008), tb, 0.3, 0, 0.5)
        for q in (1, 2, 3): arp(M, tb + q * BEAT, [x + 12 for x in ch])
    elif bi == 1:
        M.add('music', pad([x + 12 for x in ch], BAR + 0.4, 1500, 0.008), tb, 0.3, 0, 0.5)
        for q in range(4): arp(M, tb + q * BEAT, [x + 12 for x in ch], 0.2)
        M.add('music', sub(ch[0] - 12, BAR * 0.95), tb, 0.3)
    elif bi == 2:    # the pull-back: strings swell, a warm low note — the room opens
        M.add('music', strings([x + 12 for x in ch] + [ch[0]], BAR + 0.6, 2600), tb, 0.5, 0, 0.6)
        M.add('music', sub(ch[0] - 12, BAR), tb, 0.4)
        for j, m in enumerate([67, 71, 74, 79, 83, 86]):
            M.add('music', harp(m, 1.6), tb + j * 0.07, 0.2, -0.4 + 0.15 * j, 0.5)
    elif bi == 3:    # circling the instrument, and the harp glissando down into the eyepiece at 7.6
        M.add('music', strings([x + 12 for x in ch], BAR + 0.4, 2200), tb, 0.42, 0, 0.6)
        M.add('music', sub(ch[0] - 12, BAR * 0.95), tb, 0.32)
        for j, m in enumerate([93, 90, 86, 83, 81, 78, 74, 71, 69, 66]):
            M.add('music', harp(m, 1.0), tb + 1.6 + j * 0.035, 0.16, 0.4 - 0.08 * j, 0.5)
    else:            # 8.0: the last notch, the last flower — a full G chord, harp and music box together
        M.add('music', strings([x + 12 for x in ch[1:5]], BAR * 1.1, 2400), tb, 0.45, 0, 0.6)
        M.add('music', sub(43, BAR * 1.1), tb, 0.35)
        arp(M, tb, [55, 59, 62, 67, 71, 74, 79], 0.22, 0.03)
        M.add('music', musicbox(86, 2.2), tb + 0.05, 0.3, 0.2, 0.6)
        M.add('music', musicbox(83, 2.0), tb + BEAT, 0.22, -0.2, 0.6)


# ---------------- sound effects ----------------
def tumble():
    # glass pieces settling through oil: a few muffled clinks, a soft slosh
    n = t2n(0.6); t = np.arange(n) / SR
    y = lp(noise(n), 700) * np.sin(np.pi * np.clip(t / 0.6, 0, 1)) ** 2 * 0.12
    for j in range(5):
        k = t2n(0.03 + 0.09 * j + 0.03 * _r.random()); L = t2n(0.12); tt = np.arange(L) / SR
        f = 2800 + 2200 * _r.random()
        c = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 2.7 * tt)) * np.exp(-tt / 0.02) * 0.08
        y[k:k + L] += lp(c, 4500)[: max(0, min(L, n - k))]
    return y


def reveal_pull():
    n = t2n(1.4); t = np.arange(n) / SR
    y = svf_bp(noise(n), 300 + 1500 * (1 - np.exp(-t / 0.4)), 0.5) * np.sin(np.pi * np.clip(t / 1.4, 0, 1)) ** 1.5 * 0.3
    y += sine(110, n) * 0.08 * np.sin(np.pi * np.clip(t / 1.4, 0, 1))      # the brass tube's hollow resonance
    return y


def dive_in():
    n = t2n(0.5); t = np.arange(n) / SR
    return svf_bp(noise(n), 2500 - 1800 * (t / 0.5), 0.5) * np.sin(np.pi * np.clip(t / 0.5, 0, 1)) * 0.25


def tumble_last():
    return over(tumble() * 1.2, np.concatenate([np.zeros(t2n(0.12)), tumble() * 0.7]))


SFX_NEW = {'tumble': tumble, 'reveal_pull': reveal_pull, 'dive_in': dive_in, 'tumble_last': tumble_last}
