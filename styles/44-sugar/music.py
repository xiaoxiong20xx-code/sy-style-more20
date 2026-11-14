# 44 糖画 · 配乐：夜市糖画摊——琵琶（亮的拨弦与轮指）+ 笛子 + 木鱼，五声音阶；
# 浇糖段琵琶点在拍上；4.0 背光亮起时小锣一声，笛子进来，琵琶轮指铺满；8.0 糖画立起时和弦落下。
# 音效：夜市人声底（market）、浇糖细丝（syrup_pour）、糖落石板（syrup_tick）、甩线（syrup_flick）、
#       亮灯（glow_on）、按竹签（stick_press）、铲刀刮石（scrape）、揭起糖画（sugar_lift）
import numpy as np

PENT = [nm(x) for x in ['A3', 'C4', 'D4', 'E4', 'G4', 'A4', 'C5', 'D5', 'E5', 'G5', 'A5', 'C6', 'D6', 'E6']]


def pipa(m, dur=1.0, vel=1.0):
    y = ks(m, dur, 0.9, 0.995)
    n = len(y); t = np.arange(n) / SR
    return (y + hp(noise(n), 3500) * np.exp(-t / 0.002) * 0.25) * 0.5 * vel


def pipa_trem(m, dur, vel=0.8):
    out = np.zeros(t2n(dur + 0.8)); tt = 0.0; k = 0
    while tt < dur:
        b = pipa(m, 0.5, vel * (0.7 + 0.3 * (k % 2))); i = t2n(tt); out[i:i + len(b)] += b[: len(out) - i]; tt += 0.055; k += 1
    return out


def muyu(f=900):
    n = t2n(0.12); t = np.arange(n) / SR
    return (sine(f * (1 + 0.05 * np.exp(-t / 0.01)), n) * np.exp(-t / 0.035) + bp(noise(n), 600, 3000) * np.exp(-t / 0.006) * 0.4) * 0.5


def small_gong():
    out = np.zeros(t2n(2.6))
    for f0, a, d in [(620, 1.0, 1.2), (930, 0.6, 0.8), (1460, 0.35, 0.5), (2210, 0.2, 0.3)]:
        n = t2n(2.5); t = np.arange(n) / SR
        out[:n] += np.sin(2 * np.pi * f0 * (1 - 0.01 * np.exp(-t / 0.3)) * t) * np.exp(-t / d) * a
    return out * 0.12


DIZI = {2: [('E5', 1.0), ('G5', 0.5), ('A5', 0.5)], 3: [('G5', 0.5), ('E5', 0.5), ('D5', 1.0)]}


def mus(M, tb, name, root, tones, bi):
    last = bi == 4
    pt = [p for p in PENT]
    if not last:
        for q in range(4):     # pipa on each beat, with the pour
            k = [5, 7, 6, 8][q] if bi % 2 == 0 else [6, 8, 7, 5][q]
            M.add('music', pipa(pt[k], 1.0, 0.9), tb + q * BEAT, 0.35, -0.2 + 0.1 * q, 0.35)
            if bi >= 1: M.add('music', pipa(pt[k + 2], 0.7, 0.55), tb + q * BEAT + BEAT / 2, 0.22, 0.2, 0.3)
        M.add('music', pipa(root, 1.8, 0.8), tb, 0.4, -0.1, 0.25)
        M.add('drums', muyu(1000), tb + BEAT, 0.3, 0.25, 0.2); M.add('drums', muyu(820), tb + 3 * BEAT, 0.3, 0.25, 0.2)
        if bi >= 2:
            M.add('music', pipa_trem(pt[9], BEAT * 1.6, 0.6), tb + 2 * BEAT, 0.22, 0.3, 0.5)
            M.add('music', strings([x + 12 for x in tones], BAR * 1.02, 2000), tb, 0.22, 0, 0.6)
            M.add('drums', soft_kick(), tb, 0.45); M.add('drums', soft_kick(), tb + 2 * BEAT, 0.35)
        if bi in DIZI:
            tt = tb
            for sN, d in DIZI[bi]:
                M.add('music', flute(nm(sN), BEAT * d * 2 * 1.02) * 1.1, tt, 0.32, 0.15, 0.55); tt += BEAT * d * 2
        if bi == 2: M.add('drums', small_gong(), tb, 0.55, 0, 0.5)
        return
    for j, m in enumerate([tones[0] + 12, tones[1] + 12, tones[2] + 12, tones[0] + 24]):
        M.add('music', pipa(m, 2.4, 0.9), tb + j * 0.03, 0.38, -0.25 + 0.15 * j, 0.5)
    M.add('music', flute(tones[0] + 24, BAR * 0.9), tb + 0.02, 0.3, 0.15, 0.6)
    M.add('music', strings([x + 12 for x in tones], BAR * 0.95, 1800), tb, 0.24, 0, 0.6)
    M.add('drums', small_gong() * 0.8, tb, 0.45, 0, 0.5)


# ---------------- SFX ----------------
def market():
    n = t2n(10.0); t = np.arange(n) / SR
    crowd = bp(noise(n), 250, 1800) * (0.6 + 0.4 * lp(np.abs(noise(n)), 3)) * 0.08
    r = np.random.default_rng(44)
    for k in range(10):                      # snatches of voices, far off
        t0 = r.uniform(0.3, 9.0); nn = t2n(r.uniform(0.25, 0.6)); tt = np.arange(nn) / SR
        f = r.uniform(160, 320) * (1 + 0.1 * np.sin(2 * np.pi * r.uniform(3, 6) * tt))
        v = bp(polyblep_saw(f, nn), 300, 2500) * np.sin(np.pi * tt / (nn / SR)) ** 2 * 0.025
        i0 = t2n(t0); crowd[i0:i0 + nn] += v[: n - i0]
    return crowd * np.clip(t / 0.4, 0, 1)


def syrup_pour():
    n = t2n(0.9); t = np.arange(n) / SR
    r = np.random.default_rng(1)
    y = svf_bp(noise(n), 2500 + 800 * np.sin(2 * np.pi * 3 * t), 0.8) * 0.12
    y += hp((r.random(n) > 0.998).astype(float), 3000) * 0.12          # tiny crackles as it cools
    return y * np.clip(t / 0.05, 0, 1) * np.clip((0.9 - t) / 0.2, 0, 1)


def syrup_tick():
    n = t2n(0.08); t = np.arange(n) / SR
    return lp(hp(noise(n), 3500), 10000) * np.exp(-t / 0.003) * np.clip(t / 0.001, 0, 1) * 0.15 + sine(3200, n) * np.exp(-t / 0.01) * 0.06


def syrup_flick():
    n = t2n(0.35); t = np.arange(n) / SR
    return svf_bp(noise(n), 1500 + 5000 * (t / 0.35), 0.6) * np.sin(np.pi * t / 0.35) ** 2 * 0.25


def glow_on():
    n = t2n(1.6); t = np.arange(n) / SR
    hum = (sine(100, n) * 0.5 + sine(200, n) * 0.3) * np.clip(t / 0.3, 0, 1) * np.exp(-t / 1.0) * 0.12
    return hum + lp(hp(noise(n), 3000), 9000) * np.exp(-t / 0.01) * np.clip(t / 0.002, 0, 1) * 0.1


def stick_press():
    n = t2n(0.2); t = np.arange(n) / SR
    return bp(noise(n), 800, 4000) * np.exp(-t / 0.012) * np.clip(t / 0.001, 0, 1) * 0.3 + sine(950, n) * np.exp(-t / 0.03) * 0.15


def scrape():
    n = t2n(0.45); t = np.arange(n) / SR
    am = 0.5 + 0.5 * (np.sin(2 * np.pi * 70 * t) > 0)
    return bp(noise(n), 2000, 9000) * lp(am.astype(float), 2000) * np.sin(np.pi * t / 0.45) * 0.35


def sugar_lift():
    n = t2n(0.8); t = np.arange(n) / SR
    y = lp(hp(noise(n), 2000), 9000) * np.exp(-t / 0.012) * np.clip(t / 0.002, 0, 1) * 0.2   # the crisp release from the stone
    y += bell(nm('A6'), 0.8, 0.5)[:n] * 0.12 + bell(nm('E7'), 0.8, 0.5)[:n] * 0.08
    return y


SFX_NEW = {'market': market, 'syrup_pour': syrup_pour, 'syrup_tick': syrup_tick, 'syrup_flick': syrup_flick, 'glow_on': glow_on,
           'stick_press': stick_press, 'scrape': scrape, 'sugar_lift': sugar_lift}
