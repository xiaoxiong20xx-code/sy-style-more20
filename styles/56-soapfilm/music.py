# 56 肥皂泡 — a sunny garden: light and airy. Celesta (bright FM bells), kalimba-like marimba plucks, a soft pad, a gentle
# pulse (soft kick on 1 and 3, a shaker) that only arrives once the bubble floats. Hook 4.0: the two bubbles kiss and the
# pad opens, a bell glissando for the new wall. 8.0: one bubble pops — a bright chord and a sparkle, then it rings out.
# (synth.py's functions are injected into this module by build.py)

_r = np.random.default_rng(5656)
E8 = BEAT / 2
# E major colours: Emaj9, C#m9, Amaj9 / B6, G#m7 / C#m7, Emaj9
CH56 = {0: [52, 56, 59, 63, 66], 1: [49, 52, 56, 59, 63], 2: [45, 49, 52, 56, 59], 3: [44, 47, 51, 54, 59], 4: [40, 52, 56, 59, 63, 66]}
ROOT56 = {0: 40, 1: 37, 2: 45, 3: 44, 4: 40}


def celesta(m, dur=1.4, amp=1.0):
    return bell(m, dur, 0.55) * 0.5 * amp


def kalimba(m, dur=0.8):
    n = t2n(dur); t = np.arange(n) / SR; f = mtof(m)
    y = sine(f, n) * np.exp(-t / 0.35) + 0.3 * sine(f * 5.4, n) * np.exp(-t / 0.03) + 0.12 * sine(f * 2.0, n) * np.exp(-t / 0.15)
    return y * (1 - np.exp(-t / 0.0015)) * 0.45


def mus(M, tb, name, root, tones, bi):
    ch = CH56[bi]
    if bi < 4:
        M.add('music', pad([x + 12 for x in ch[:4]], BAR + 0.5, 1800 if bi != 2 else 2600, 0.01), tb, 0.38 if bi != 2 else 0.5, 0, 0.5)
    if bi == 0:      # the film in the ring: celesta arpeggio, no beat yet
        for e, k in enumerate([0, 2, 4, 3, 1, 3, 2, 4]):
            M.add('music', celesta(ch[k] + 12, 1.6, 0.9 if e % 2 == 0 else 0.7), tb + e * E8, 0.32, -0.3 + 0.08 * e, 0.55)
    elif bi == 1:    # the bubble floats free: the pulse arrives
        for q in (0, 2): M.add('drums', soft_kick(), tb + q * BEAT, 0.55)
        for s in range(8): M.add('drums', shaker(), tb + s * E8, 0.14 if s % 2 else 0.08, 0.35)
        M.add('music', sub(ROOT56[bi], BAR * 0.95), tb, 0.35)
        for e, k in enumerate([0, 2, 1, 3, 2, 4, 3, 2]):
            M.add('music', kalimba(ch[k] + 12, 0.8), tb + e * E8, 0.3, 0.3 if e % 2 else -0.3, 0.4)
    elif bi == 2:    # the kiss: everything opens, a bell glissando for the new wall
        for q in (0, 2): M.add('drums', soft_kick(), tb + q * BEAT, 0.6)
        for s in range(16): M.add('drums', shaker(), tb + s * BEAT / 4, 0.12 if s % 2 else 0.07, 0.35)
        M.add('music', sub(ROOT56[bi], BAR * 0.95), tb, 0.4)
        for j, m in enumerate([64, 68, 71, 73, 76, 80, 83, 85]):
            M.add('music', celesta(m, 1.2, 0.8), tb + BEAT + j * 0.06, 0.26, -0.4 + 0.1 * j, 0.6)
        for e, k in enumerate([0, 4, 2, 3, 1, 4, 2, 3]):
            M.add('music', kalimba(ch[k] + 24, 0.7), tb + e * E8, 0.22, 0.35 if e % 2 else -0.35, 0.45)
    elif bi == 3:    # the double bubble turns: melody on celesta
        for q in (0, 2): M.add('drums', soft_kick(), tb + q * BEAT, 0.5)
        for s in range(8): M.add('drums', shaker(), tb + s * E8, 0.12 if s % 2 else 0.07, 0.35)
        M.add('music', sub(ROOT56[bi], BAR * 0.95), tb, 0.35)
        for (m, off) in [(75, 0), (73, 1.0), (71, 1.5), (68, 2.5), (66, 3.0)]:
            M.add('music', celesta(m, 1.4), tb + off * BEAT, 0.3, 0.2, 0.55)
    else:            # 8.0: the pop — a bright Emaj9 that rings out over the last bubble
        M.add('music', pad([x + 12 for x in ch[1:5]], BAR * 1.1, 2200, 0.01), tb, 0.45, 0, 0.6)
        M.add('music', sub(40, BAR * 1.1), tb, 0.35)
        for j, m in enumerate(ch[1:]):
            M.add('music', celesta(m + 12, 2.6, 0.9), tb + j * 0.03, 0.28, -0.3 + 0.15 * j, 0.6)
        M.add('music', kalimba(88, 1.2), tb + BEAT, 0.2, 0.3, 0.6)


# ---------------- sound effects ----------------
def garden_air(dur=3.0):
    n = t2n(dur); t = np.arange(n) / SR
    wind = lp(noise(n), 700) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.4 * t)) * 0.08
    y = wind * np.clip(t / 0.3, 0, 1) * np.clip((dur - t) / 0.8, 0, 1)
    # two little birds far away
    for k0 in (0.4, 1.35, 2.2):
        k = t2n(k0); L = t2n(0.09)
        for j in range(3):
            tt = np.arange(L) / SR; f0 = 3600 + 600 * _r.random()
            ch = np.sin(2 * np.pi * (f0 * tt + 9000 * tt * tt)) * np.sin(np.pi * tt / 0.09) * 0.05
            s0 = k + t2n(j * 0.11); y[s0:s0 + L] += ch[: max(0, min(L, n - s0))]
    return y


def breath_blow():
    n = t2n(0.9); t = np.arange(n) / SR
    y = bp(noise(n), 300, 2500) * np.sin(np.pi * np.clip(t / 0.9, 0, 1)) ** 1.5 * 0.35
    return y


def film_pinch():
    n = t2n(0.18); t = np.arange(n) / SR
    return sine(900 + 500 * (t / 0.18), n) * np.exp(-t / 0.03) * 0.25 + hp(noise(n), 3000) * np.exp(-t / 0.004) * 0.08


def bubble_drift():
    out = np.zeros(t2n(1.4))
    for j, m in enumerate([95, 99, 102]):
        b = bell(m, 1.0, 0.3) * 0.12; k = t2n(j * 0.2); out[k:k + len(b)] += b[: len(out) - k]
    return out


def bubble_kiss():
    n = t2n(0.5); t = np.arange(n) / SR
    y = sine(90 * np.exp(-t / 0.05) + 60, n) * np.exp(-t / 0.09) * 0.45
    y += sine(1900, n) * np.exp(-t / 0.15) * 0.06 + lp(noise(n), 900) * np.exp(-t / 0.03) * 0.15
    return y


def film_shimmer():
    out = np.zeros(t2n(1.6))
    for j, m in enumerate([88, 91, 95, 98, 100, 103]):
        b = bell(m, 0.9, 0.4) * 0.1; k = t2n(j * 0.07); out[k:k + len(b)] += b[: len(out) - k]
    return out


def bubble_pop():
    n = t2n(0.6); t = np.arange(n) / SR
    y = hp(noise(n), 2500) * np.exp(-t / 0.006) * 0.6 + sine(2400, n) * np.exp(-t / 0.01) * 0.2
    sp = np.zeros(n)                                  # the mist: a spray of tiny ticks fading fast
    for k in _r.integers(t2n(0.01), t2n(0.3), 60):
        L = 120; sp[k:k + L] += hp(noise(L), 6000) * np.exp(-np.arange(L) / 25) * 0.15 * np.exp(-k / SR / 0.12)
    return y + sp


SFX_NEW = {'garden_air': garden_air, 'breath_blow': breath_blow, 'film_pinch': film_pinch, 'bubble_drift': bubble_drift,
           'bubble_kiss': bubble_kiss, 'film_shimmer': film_shimmer, 'bubble_pop': bubble_pop}
