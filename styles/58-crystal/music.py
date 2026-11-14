# 58 偏光显微 — a microscope room at night: crystalline, minimal electronica in D Lydian. Each nucleus that appears on a beat
# is a glassy pluck (rising), a low hum and soft ticks underneath; on the hook (4.0) the time-lapse ramps and an arpeggio
# runs up over a filter-swept pad; 7.55 the stage's detent ratchets round; 8.0 a bright chord as the colours flip, then it rings.
# (synth.py's functions are injected into this module by build.py)

_r = np.random.default_rng(5858)
E8, S16 = BEAT / 2, BEAT / 4
NUC = [62, 66, 69, 73, 74, 76, 78]          # D F# A C# D E F#: one per nucleus, 0.5 .. 3.5
CH58 = {0: [50, 57, 62, 64, 69], 1: [50, 57, 62, 66, 68], 2: [47, 54, 59, 62, 68], 3: [43, 50, 57, 62, 66], 4: [50, 57, 62, 66, 68, 73]}


def glass(m, dur=1.6, amp=1.0):
    n = t2n(dur); t = np.arange(n) / SR; f = mtof(m)
    y = sine(f, n) * np.exp(-t / 0.9) + 0.35 * sine(f * 2.76, n) * np.exp(-t / 0.35) + 0.18 * sine(f * 5.4, n) * np.exp(-t / 0.12)
    return y * (1 - np.exp(-t / 0.001)) * 0.32 * amp


def mus(M, tb, name, root, tones, bi):
    ch = CH58[bi]
    if bi < 4:
        M.add('music', pad([x + 12 for x in ch[1:]], BAR + 0.5, 900 + 500 * bi, 0.008), tb, 0.32, 0, 0.5)
        M.add('music', sub(ch[0] - 12, BAR * 0.95), tb, 0.3)
    if bi == 0:
        M.add('music', glass(81, 2.0, 0.7), tb, 0.25, 0.2, 0.6)               # the first crystal, already growing
        M.add('music', glass(NUC[0] + 12, 1.6), tb + BEAT, 0.3, -0.3, 0.55)
        M.add('music', glass(NUC[1] + 12, 1.6), tb + 2 * BEAT, 0.3, 0.3, 0.55)
        M.add('music', glass(NUC[2] + 12, 1.6), tb + 3 * BEAT, 0.3, -0.2, 0.55)
    elif bi == 1:
        for q in range(4):
            M.add('music', glass(NUC[3 + q] + 12, 1.4), tb + q * BEAT, 0.3, 0.3 if q % 2 else -0.3, 0.55)
        for s in range(16): M.add('drums', tick(5200 + 400 * (s % 2), 0.25), tb + s * S16, 0.12 if s % 4 == 2 else 0.06, 0.3)
        for q in (0, 2): M.add('drums', soft_kick(), tb + q * BEAT, 0.45)
    elif bi == 2:    # the time-lapse ramps: an arpeggio climbing in sixteenths, the pad opening
        for s in range(16):
            m = ch[1 + s % 4] + 12 + 12 * (s // 8)
            M.add('music', pluck_saw(m, 0.22, 1800 + 160 * s, 0.3), tb + s * S16, 0.18, 0.35 if s % 2 else -0.35, 0.35)
        for q in range(4): M.add('drums', soft_kick(), tb + q * BEAT, 0.55)
        for s in range(16): M.add('drums', tick(5600, 0.3), tb + s * S16, 0.1, 0.3)
        M.add('music', glass(86, 2.0), tb, 0.3, 0, 0.6)
    elif bi == 3:    # the field is full: slow glassy melody
        for (m, off) in [(81, 0), (80, 1.0), (78, 1.5), (76, 2.5), (73, 3.0)]:
            M.add('music', glass(m, 1.6), tb + off * BEAT, 0.3, 0.2, 0.55)
        for q in (0, 2): M.add('drums', soft_kick(), tb + q * BEAT, 0.45)
        for s in range(8): M.add('drums', tick(5200, 0.25), tb + s * E8, 0.08, 0.3)
    else:            # 8.0: the colours flip — a bright D Lydian chord, ringing
        M.add('music', pad([x + 12 for x in ch[1:]], BAR * 1.1, 2000, 0.008), tb, 0.4, 0, 0.6)
        M.add('music', sub(38, BAR * 1.1), tb, 0.3)
        for j, m in enumerate(ch[1:]):
            M.add('music', glass(m + 24, 2.8, 0.85), tb + j * 0.025, 0.26, -0.3 + 0.15 * j, 0.6)


# ---------------- sound effects ----------------
def scope_hum(dur=3.0):
    n = t2n(dur); t = np.arange(n) / SR
    y = (sine(50, n) * 0.5 + sine(100, n) * 0.25 + lp(noise(n), 400) * 0.25) * 0.12
    return y * np.clip(t / 0.4, 0, 1) * np.clip((dur - t) / 1.0, 0, 1)


def nucleate():
    n = t2n(0.4); t = np.arange(n) / SR
    y = sine(3800, n) * np.exp(-t / 0.05) * 0.18 + sine(5200, n) * np.exp(-t / 0.02) * 0.1
    y += hp(noise(n), 4000) * np.exp(-t / 0.004) * 0.12
    return y


def crystal_rush(dur=1.3):
    n = t2n(dur); t = np.arange(n) / SR
    y = np.zeros(n)
    for k in _r.integers(0, n - 600, int(900 * dur)):
        L = 400; tt = np.arange(L) / SR
        y[k:k + L] += np.sin(2 * np.pi * (3000 + 6000 * (k / n) + 2000 * _r.random()) * tt) * np.exp(-tt / 0.004) * 0.05
    y += bp(noise(n), 2000, 9000) * (t / dur) ** 1.5 * 0.1
    return y * np.clip((dur - t) / 0.2, 0, 1)


def stage_turn():
    out = np.zeros(t2n(0.5))
    for j in range(7):
        c = click() * 0.5 if 'click' in SFX else hp(noise(t2n(0.02)), 2000) * 0.3
        k = t2n(j * 0.06); out[k:k + len(c)] += c[: len(out) - k]
    return out


def flip_chime():
    out = np.zeros(t2n(2.0))
    for j, m in enumerate([86, 90, 93, 97]):
        b = bell(m, 1.8, 0.5) * 0.18; k = t2n(j * 0.02); out[k:k + len(b)] += b[: len(out) - k]
    return out


SFX_NEW = {'scope_hum': scope_hum, 'nucleate': nucleate, 'crystal_rush': crystal_rush, 'stage_turn': stage_turn, 'flip_chime': flip_chime}
