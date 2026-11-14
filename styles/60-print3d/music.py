# 60 3D 打印 · 配乐：创客桌上的干净电子——开头是步进电机自己「唱」出的旋律（stepper_run），
# 延时段每拍一声轻轻的快门（timelapse_tick，延时摄影的拍照声），底下是柔和的底鼓、八分音符的闭镲、
# 拨弦合成器琶音；钩子（镜头贴着层纹上升）加入一串玻璃般的高音点，像层线一道道闪；
# 8.0 秒打印完成：机器的三音完成提示（print_done）和一个开阔的和弦，余音散开。
import numpy as np


def pluck(m, dur=0.3, cut=3200, vel=1.0):
    n = t2n(dur); t = np.arange(n) / SR; f = mtof(m)
    y = polyblep_saw(f, n) * 0.6 + polyblep_saw(f * 1.004, n) * 0.4
    y = svf_lp(y, 300 + cut * np.exp(-t / 0.07), 0.35)
    return y * adsr(n, 0.002, 0.12, 0.25, 0.08) * 0.22 * vel


def glass(m, dur=0.8):
    n = t2n(dur); t = np.arange(n) / SR; f = mtof(m)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.35) + 0.3 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t / 0.08)
    return y * (1 - np.exp(-t / 0.0007)) * 0.16


def subb(m, dur):
    n = t2n(dur); t = np.arange(n) / SR
    return sine(mtof(m), n) * adsr(n, 0.01, 0.1, 0.8, 0.1) * 0.5


ARP = {1: [57, 60, 64, 67], 2: [53, 57, 60, 64], 3: [55, 59, 62, 67]}


def mus(M, tb, name, root, tones, bi):
    if bi == 0:
        M.add('music', subb(33, BAR), tb, 0.45)
        return
    if bi < 4:
        # soft kick on 1 and 3 (and the 'and' of 4 in the hook), closed hats on the eighths
        for q in ((0, 2) if bi != 2 else (0, 2, 3.5)): M.add('drums', soft_kick(), tb + q * BEAT, 0.7); M.sidechain(tb + q * BEAT, 0.35)
        for e in range(8): M.add('drums', hat(), tb + e * BEAT / 2, 0.10 if e % 2 else 0.06, 0.35)
        M.add('drums', snap(), tb + 1 * BEAT, 0.25, -0.1, 0.2); M.add('drums', snap(), tb + 3 * BEAT, 0.25, -0.1, 0.2)
        # sub bass on the root
        M.add('music', subb(root - 12, BAR * 0.98), tb, 0.45)
        # plucked arpeggio in eighths
        pat = ARP[bi]
        for e in range(8):
            m = pat[e % 4] + (12 if e >= 4 else 0)
            M.add('music', pluck(m, 0.28, 2600 + 1600 * (bi == 2), 1.0 if e % 2 == 0 else 0.7), tb + e * BEAT / 2, 0.45, -0.3 + 0.6 * (e % 2), 0.25)
        M.add('music', pad([x + 12 for x in tones], BAR, 1500, 0.01), tb, 0.22, 0, 0.35)
        if bi == 2:   # the hook: glassy points climbing with the layer lines
            for s16 in range(16):
                M.add('music', glass([76, 79, 81, 84][s16 % 4] + (12 if s16 >= 8 else 0), 0.6), tb + s16 * BEAT / 4, 0.30, 0.4 - 0.8 * (s16 % 2), 0.4)
        return
    # bar 4: done — the open chord rings out under the completion chime
    M.add('music', pad([57, 64, 69, 71, 76], BAR * 0.95, 2000, 0.01), tb, 0.38, 0, 0.55)
    M.add('music', subb(33, BAR * 0.9), tb, 0.45)
    for j, m in enumerate([69, 76, 81]): M.add('music', glass(m, 1.8), tb + j * 0.03, 0.4, -0.2 + 0.2 * j, 0.5)


# ---------------- SFX ----------------
def stepper_run():
    """the stepper motors sing as the head draws the first perimeter: a whining square tone whose pitch follows the moves"""
    n = t2n(1.6); t = np.arange(n) / SR
    notes = [(0.0, 69), (0.25, 72), (0.5, 76), (0.75, 74), (1.0, 72), (1.25, 69)]
    f = np.full(n, mtof(69))
    for t0, m in notes: f[t2n(t0):] = mtof(m)
    f = lp(f, 40)                                     # the motors glide a little between speeds
    ph = np.cumsum(f) / SR
    y = np.where((ph % 1.0) < 0.5, 1.0, -1.0) * 0.5 + np.sin(2 * np.pi * ph * 2) * 0.2
    y = bp(y, 300, 3000)
    y += bp(noise(n), 2000, 8000) * 0.03
    env = np.clip(t / 0.03, 0, 1) * np.clip((1.55 - t) / 0.1, 0, 1)
    return y * env * 0.09


def timelapse_tick():
    """a soft mirrorless shutter for each time-lapse frame"""
    n = t2n(0.09); t = np.arange(n) / SR
    y = hp(noise(n), 2500) * np.exp(-t / 0.004) * 0.5
    k = t2n(0.045); y[k:] += hp(noise(n - k), 3000) * np.exp(-np.arange(n - k) / SR / 0.003) * 0.35
    return y * 0.6


def layer_rise():
    n = t2n(1.4); t = np.arange(n) / SR; u = t / 1.4
    return svf_bp(noise(n), 400 + 3000 * u, 0.6) * np.sin(np.pi * u) ** 1.2 * 0.22


def print_done():
    """the printer's own three-note 'finished' chime"""
    out = np.zeros(t2n(1.4))
    for j, m in enumerate([81, 76, 88]):
        n = t2n(0.5); t = np.arange(n) / SR
        y = np.where((np.cumsum(np.full(n, mtof(m))) / SR % 1.0) < 0.5, 1.0, -1.0) * np.exp(-t / 0.12)
        y = lp(y, 5000) * 0.10
        k = t2n(j * 0.13); out[k:k + n] += y[: len(out) - k]
    n = t2n(0.5); t = np.arange(n) / SR
    out[:n] += (hp(noise(n), 1500) * np.exp(-t / 0.01) * 0.2)    # the z-hop's little clunk
    return out


SFX_NEW = {'stepper_run': stepper_run, 'timelapse_tick': timelapse_tick, 'layer_rise': layer_rise, 'print_done': print_done}
