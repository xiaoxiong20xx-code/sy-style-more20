# 50 刮画 · 配乐：深夜台灯下的神秘与绚烂——低音脉冲 + 拨弦钢片琴琶音 + 暗色铺底；
# 尾屏四次炸开每次一记鼓和上行闪光；眼斑段钟琴点点；8.0 吹走蜡屑时和弦落下。
# 音效：长刮（scratch_long）、短刮（scratch_s）、点刮（scratch_taps）、排线（scratch_hatch）、扇形爆开（scratch_burst）、吹气（breath）
import numpy as np


def celesta(m, dur=1.2, vel=1.0):
    n = t2n(dur); t = np.arange(n) / SR; f = mtof(m)
    y = sine(f, n) * np.exp(-t / 0.8) + 0.4 * sine(2 * f, n) * np.exp(-t / 0.3) + 0.15 * sine(3.98 * f, n) * np.exp(-t / 0.1)
    return y * (1 - np.exp(-t / 0.0015)) * 0.24 * vel


def mus(M, tb, name, root, tones, bi):
    last = bi == 4
    if not last:
        M.add('music', pad([x for x in tones], BAR * 1.02, 900 if bi < 2 else 1600), tb, 0.3, 0, 0.5)
        for q in range(4): M.add('music', sub(root - 12, BEAT * 0.8), tb + q * BEAT, 0.35 if bi < 2 else 0.45)
        arp = [tones[0], tones[1], tones[2], tones[1] + 12, tones[2] + 12, tones[0] + 12, tones[2], tones[1]]
        step = BEAT / 2 if bi < 2 else BEAT / 4
        for e in range(8 if bi < 2 else 16):
            M.add('music', celesta(arp[e % 8] + 24, 0.9, 0.85 if e % 2 == 0 else 0.6), tb + e * step, 0.3, -0.35 + 0.09 * (e % 8), 0.5)
        if bi >= 2:
            M.add('drums', kick(0.4, 140, 45, 1.2, 0.2), tb, 0.6); M.add('drums', kick(0.4, 140, 45, 1.2, 0.2), tb + 2 * BEAT, 0.5)
            for s16 in range(16): M.add('drums', hat(), tb + s16 * BEAT / 4, 0.08 if s16 % 2 else 0.05, 0.35)
            M.add('music', strings([x + 12 for x in tones], BAR * 1.02, 2600), tb, 0.25, 0, 0.6)
        if bi == 2:      # the four bursts of the train
            for q in range(4):
                M.add('drums', impact(0.35, 0.6), tb + q * BEAT / 2, 0.25, 0, 0.4)
        return
    for j, m in enumerate(tones + [tones[0] + 12]):
        M.add('music', celesta(m + 24, 2.6), tb + j * 0.04, 0.35, -0.3 + 0.2 * j, 0.6)
        M.add('music', bell(m + 24, 2.4, 0.6), tb + j * 0.06, 0.1, 0.3 - 0.2 * j, 0.6)
    M.add('music', pad([x + 12 for x in tones], BAR * 0.95, 1800), tb, 0.3, 0, 0.6)
    M.add('music', sub(root - 12, BAR * 0.7), tb, 0.4)


# ---------------- SFX ----------------
def _scrape(dur, lo, hi, rate, amp, seed):
    n = t2n(dur); t = np.arange(n) / SR
    am = 0.45 + 0.55 * (np.sin(2 * np.pi * rate * t + 2.1 * np.sin(2 * np.pi * 3.3 * t + seed)) > 0.25)   # the wax catches and slips
    am = lp(am.astype(float), 1200)
    y = bp(noise(n), lo, hi) * am * amp
    r = np.random.default_rng(seed)
    y += hp((r.random(n) > 0.996).astype(float), 3000) * 0.15                                             # crumbs flicking off
    return y * np.clip(t / 0.015, 0, 1) * np.clip((dur - t) / 0.05, 0, 1)


def scratch_taps():
    out = np.zeros(t2n(0.5)); r = np.random.default_rng(4)
    for i in range(6):
        x = _scrape(0.05, 2500, 8000, 50, 0.35, i); k = t2n(i * 0.075 + r.random() * 0.02); out[k:k + len(x)] += x[: len(out) - k]
    return out


def scratch_hatch():
    out = np.zeros(t2n(1.0)); r = np.random.default_rng(6)
    for i in range(12):
        x = _scrape(0.06, 2200, 7500, 45, 0.3 * (0.6 + 0.4 * r.random()), i + 10); k = t2n(i * 0.075); out[k:k + len(x)] += x[: len(out) - k]
    return out


def scratch_burst():
    out = np.zeros(t2n(0.7)); r = np.random.default_rng(8)
    for i in range(11):
        x = _scrape(0.09, 1800, 8000, 38, 0.3, i + 30); k = t2n(i * 0.013 + r.random() * 0.01); out[k:k + len(x)] += x[: len(out) - k]
    n = t2n(0.7); t = np.arange(n) / SR
    for j, m in enumerate(['E6', 'A6', 'C7', 'E7']):
        b = bell(nm(m), 0.6, 0.3) * 0.05; k = t2n(j * 0.04); out[k:k + len(b)] += b[: len(out) - k]
    return out


def breath():
    n = t2n(1.0); t = np.arange(n) / SR
    y = svf_bp(noise(n), 700 + 1500 * np.sin(np.pi * t / 1.0), 0.5) * np.sin(np.pi * np.clip(t / 0.8, 0, 1)) ** 1.5 * 0.5
    y += lp(noise(n), 300) * np.sin(np.pi * np.clip(t / 0.8, 0, 1)) ** 2 * 0.2
    return y


SFX_NEW = {'scratch_long': lambda: _scrape(0.6, 2000, 7500, 30, 0.35, 1), 'scratch_s': lambda: _scrape(0.25, 2200, 8000, 36, 0.33, 2),
           'scratch_taps': scratch_taps, 'scratch_hatch': scratch_hatch, 'scratch_burst': scratch_burst, 'breath': breath}
