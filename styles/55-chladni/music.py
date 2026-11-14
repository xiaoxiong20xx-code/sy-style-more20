# 55 声音的形状 — a live house at night: 120 BPM house. Four-on-the-floor kick, offbeat open hats, a rolling saw bass, claps
# on 2 and 4. The lead synth plays the plate's own tone: its pitch is read from table.js, the same timetable the picture
# reads, so each beat's new note is the beat the sand jumps into a new figure. 4.0–5.0: the glide becomes a riser (the
# kick drops out, white noise sweeps up, the lead slides A4 -> D5) and slams back on 5.0. 8.0: the last chord hits with
# a kick and a crash, then everything is cut dead; only the reverb tail is left.
# (synth.py's functions are injected into this module by build.py)
import json, os

_HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(_HERE, 'table.js'), encoding='utf8').read()
TBL = json.loads(_src[_src.index('=', _src.index('window.CHLADNI')) + 1: _src.rindex(';')])
_r = np.random.default_rng(5555)
E8, S16 = BEAT / 2, BEAT / 4
END = TBL['chord']['t']                     # 8.0: the music stops dead after the last hit


def plate_lead(f, dur, amp=1.0):
    """the plate's tone, made musical: a sine with a little saw on top through a soft filter (f may be an array: a glide)"""
    n = t2n(dur); t = np.arange(n) / SR
    f = np.broadcast_to(np.asarray(f, float), (n,))
    y = sine(f, n) * 0.7 + lp(polyblep_saw(f, n), 2400) * 0.22 + sine(f * 2, n) * 0.1
    return y * adsr(n, 0.004, 0.08, 0.85, 0.05) * 0.32 * amp


def hb(m, dur):
    return bass_saw(m, dur, 1200) * 0.8


def open_hat():
    return hat(True) * 0.8


def crash(dur=1.6):
    n = t2n(dur); t = np.arange(n) / SR
    return hp(noise(n), 4000) * np.exp(-t / 0.5) * 0.35


def mus(M, tb, name, root, tones, bi):
    if bi != 0:
        return                                   # the whole cue is laid out from the timetable in one pass
    beats = TBL['beats']; g = TBL['glide']; ch = TBL['chord']
    # ---- the lead: one note per beat, the glide, the chord ----
    for k, b in enumerate(beats):
        t0 = b['t']; t1 = beats[k + 1]['t'] if k + 1 < len(beats) else ch['t']
        if t0 < g['t0'] <= t1 - 1e-6: t1 = g['t0']
        M.add('music', plate_lead(mtof(b['midi']), t1 - t0 + 0.02), t0, 0.5, 0.0, 0.3)
    n = t2n(g['t1'] - g['t0'] + 0.02); u = np.clip(np.arange(n) / t2n(g['t1'] - g['t0']), 0, 1)
    fg = mtof(g['midi0'] + (g['midi1'] - g['midi0']) * u ** 1.6)            # the riser: slow at first, then rushing up
    M.add('music', plate_lead(fg, g['t1'] - g['t0'] + 0.02, 1.1), g['t0'], 0.5, 0.0, 0.35)
    for m in ch['midi']:
        M.add('music', plate_lead(mtof(m), 0.5, 0.9) * np.exp(-np.arange(t2n(0.5)) / SR / 0.16), ch['t'], 0.42, 0.0, 0.6)
    # ---- drums ----
    for k in range(20):
        t = k * BEAT
        if t >= END: break
        riser = g['t0'] <= t < g['t1']
        if t >= 1.0 and not riser: M.add('drums', kick(0.42, 165, 46, 1.8, 0.28), t, 0.95); M.sidechain(t, 0.55)
        M.add('drums', open_hat(), t + E8, 0.32 if t >= 1.0 else 0.2, 0.25)           # the hats come in first
        if t >= 2.0 and not riser and k % 2 == 1: M.add('drums', clap(), t, 0.5, 0, 0.25)
    for s in range(int(END / S16)):
        t = s * S16
        if t >= 1.0 and not (g['t0'] <= t < g['t1']) and s % 2 == 1: M.add('drums', hat(False), t, 0.12, -0.25)
    # ---- bass: a rolling offbeat line on each note's root, two octaves down ----
    for k, b in enumerate(beats):
        if b['t'] >= END: break
        r = b['midi'] - 24
        while r > 45: r -= 12
        M.add('music', hb(r, E8 * 0.9), b['t'] + E8, 0.5)
        if b['t'] + BEAT < END and not (g['t0'] <= b['t'] + BEAT - 1e-6 < g['t1']) and b['t'] + BEAT not in [x['t'] for x in beats]:
            M.add('music', hb(r, E8 * 0.9), b['t'] + BEAT + E8, 0.45)
    # the riser itself: white noise sweeping up, then a snare roll accelerating into 5.0
    nr = t2n(g['t1'] - g['t0']); tt = np.arange(nr) / SR
    sweep = svf_bp(noise(nr), 400 + 7000 * (tt / (g['t1'] - g['t0'])) ** 2, 0.4) * (tt / (g['t1'] - g['t0'])) ** 1.2 * 0.35
    M.add('music', sweep, g['t0'], 0.6, 0, 0.4)
    for j in range(16):
        tj = g['t0'] + (g['t1'] - g['t0']) * (1 - (1 - j / 16) ** 1.4)
        M.add('drums', clap() * (0.3 + 0.7 * j / 16), tj, 0.25, 0.1, 0.2)
    # 8.0: the last hit — kick, crash, chord; then nothing
    M.add('drums', kick(0.6, 150, 40, 2.2, 0.35), END, 1.0)
    M.add('drums', crash(1.4), END, 0.6, 0, 0.6)
    M.add('music', pad([m for m in ch['midi']], 0.45, 3000, 0.01), END, 0.45, 0, 0.8)


# ---------------- sound effects ----------------
def sand_sprinkle(dur=1.1):
    n = t2n(dur); t = np.arange(n) / SR
    y = np.zeros(n)
    for k in _r.integers(0, n - 300, int(2600 * dur)):
        L = 200; y[k:k + L] += hp(noise(L), 5000) * np.exp(-np.arange(L) / 30) * (0.1 + 0.2 * _r.random())
    return y * np.clip(t / 0.05, 0, 1) * np.clip((dur - t) / 0.25, 0, 1) * 0.5


def sand_jump():
    # the whole plate's sand thrown up at once: a dry rattling buzz, quickly settling
    n = t2n(0.4); t = np.arange(n) / SR
    y = bp(noise(n), 2500, 9000) * (0.6 + 0.4 * np.sin(2 * np.pi * 60 * t)) * np.exp(-t / 0.12) * 0.3
    return y


def sand_rush():
    n = t2n(1.0); t = np.arange(n) / SR
    return bp(noise(n), 2500, 9000) * (0.6 + 0.4 * np.sin(2 * np.pi * (60 + 90 * t) * t)) * (0.4 + 0.6 * t) * 0.22


def sand_settle():
    n = t2n(0.45); t = np.arange(n) / SR
    return bp(noise(n), 3000, 9000) * np.exp(-t / 0.12) * 0.25


SFX_NEW = {'sand_sprinkle': sand_sprinkle, 'sand_jump': sand_jump, 'sand_rush': sand_rush, 'sand_settle': sand_settle}
