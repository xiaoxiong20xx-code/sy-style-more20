# 46 榫卯 · 配乐：木作坊里的节奏——梆子和木鱼打出八分音符的骨架，阮（低音拨弦）走低音，
# 柳琴般明亮的拨弦在五声音阶上走旋律，钩子处加一面低沉的堂鼓；8.0 秒耍头锁死，一个拨弦和弦加低鼓落下，余音散开。
# 和其他几首（塑料放克、石磬大提琴、电子）完全不同：全是木头和丝弦的声音。
# 音效：刨削（plane_stroke）、木构件落位（wood_knock / wood_lap / wood_tick）、耍头滑入（beam_slide）、锁死（joint_lock）
# build.py 把 synth.py 的全部函数注入本模块：np, SR, BEAT, BAR, t2n, mtof, nm, sine, noise, lp, hp, bp, svf_bp, expenv, adsr, ks, pad ...
import numpy as np


def bangzi(f=1650, amp=1.0):
    """梆子: a hard hardwood click with a short, high body"""
    n = t2n(0.12); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.022) + 0.45 * np.sin(2 * np.pi * f * 2.3 * t) * np.exp(-t / 0.009)
    y += bp(noise(n), f * 0.7, f * 3.0) * np.exp(-t / 0.004) * 0.5
    return y * amp * 0.45


def muyu(f=520, amp=1.0):
    """木鱼: a hollow, rounder knock"""
    n = t2n(0.25); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.06) + 0.3 * np.sin(2 * np.pi * f * 1.52 * t) * np.exp(-t / 0.03)
    y += lp(noise(n), 1800) * np.exp(-t / 0.006) * 0.4
    return y * amp * 0.5


def tanggu(amp=1.0):
    """堂鼓: a low, warm drum"""
    n = t2n(0.9); t = np.arange(n) / SR
    y = sine(58 + 42 * np.exp(-t / 0.05), n) * np.exp(-t / 0.35)
    y += lp(noise(n), 400) * np.exp(-t / 0.04) * 0.35
    return np.tanh(y * 1.2) * 0.8 * amp


def ruan(m, dur=0.6, bright=0.35):
    return ks(m, dur, bright, 0.9965) * 0.9


def liuqin(m, dur=0.5):
    y = ks(m, dur, 0.85, 0.994)
    n = len(y); t = np.arange(n) / SR
    return (y + 0.25 * hp(y, 2500)) * 0.55 * (1 - np.exp(-t / 0.0015))


PENT = {'A3': 57, 'C4': 60, 'D4': 62, 'E4': 64, 'G4': 67, 'A4': 69, 'C5': 72, 'D5': 74, 'E5': 76, 'G5': 79, 'A5': 81}
MEL = [
    [None, None, None, None, 'E5', None, 'D5', None],
    ['A4', None, 'C5', 'D5', 'E5', None, 'G5', 'E5'],
    ['D5', 'E5', 'G5', 'A5', 'G5', 'E5', 'D5', 'C5'],
    ['A4', 'C5', 'D5', None, 'E5', 'D5', 'C5', 'A4'],
    ['A4', None, None, None, None, None, None, None],
]
BASS = [[33, None, None, None], [33, None, 40, 38], [29, 36, 31, 36], [31, None, 38, 40], [33, None, None, None]]


def mus(M, tb, name, root, tones, bi):
    # percussion: woodblocks on the eighths from bar 1 (the plane's stroke owns bar 0), low drum from the hook
    if bi == 0:
        for q in (1.0, 3.0): M.add('drums', muyu(500, 0.6), tb + q * BEAT, 0.5, 0.2, 0.15)
    elif bi < 4:
        for e in range(8):
            acc = e in (0, 3, 6)
            M.add('drums', bangzi(1650 if e % 2 == 0 else 1900, 1.0 if acc else 0.55), tb + e * BEAT / 2, 0.42 if acc else 0.25, -0.3 + 0.2 * (e % 3), 0.12)
        for q in (1.0, 3.0): M.add('drums', muyu(480, 0.9), tb + q * BEAT, 0.55, 0.25, 0.2)
        if bi >= 2:
            for q in ((0, 2.5) if bi == 2 else (0, 1.5, 2)): M.add('drums', tanggu(0.9), tb + q * BEAT, 0.75, 0, 0.3); M.sidechain(tb + q * BEAT, 0.3)
    # ruan bass
    for q, m in enumerate(BASS[bi]):
        if m: M.add('music', ruan(m + 12, BEAT * 1.6), tb + q * BEAT, 0.62, -0.1, 0.25)
    # liuqin melody on the pentatonic
    for e, sN in enumerate(MEL[bi]):
        if sN: M.add('music', liuqin(PENT[sN], 0.7), tb + e * BEAT / 2, 0.38 if bi < 4 else 0.5, 0.25 - 0.1 * (e % 3), 0.35)
    # a bowed bed under the hook
    if bi in (2, 3): M.add('music', pad([x + 12 for x in tones], BAR, 1400, 0.008), tb, 0.16, 0, 0.4)
    if bi == 4:   # the lock on 8.0: a rolled chord on the plucked strings, a deep drum, and they ring out
        for j, m in enumerate([45, 52, 57, 60, 64, 69]): M.add('music', ruan(m, 2.0, 0.5) if m < 55 else liuqin(m + 0, 1.8), tb + j * 0.018, 0.5, -0.3 + 0.12 * j, 0.5)
        M.add('drums', tanggu(1.0), tb, 0.85, 0, 0.45)
        M.add('music', pad([57, 64, 69, 72], BAR * 0.9, 1200, 0.006), tb, 0.22, 0, 0.6)


# ---------------- SFX ----------------
def plane_stroke():
    """a long plane stroke: the iron shearing a ribbon off fir, a rasp riding on a hiss, ending as the plane slows"""
    n = t2n(1.9); t = np.arange(n) / SR
    env = np.clip(t / 0.05, 0, 1) * (1 - np.clip((t - 1.35) / 0.4, 0, 1)) ** 1.5
    rasp = 0.65 + 0.35 * np.sin(2 * np.pi * (38 + 6 * np.sin(t * 3)) * t)
    y = svf_bp(noise(n), 2600 + 900 * np.sin(t * 2.2), 0.7) * rasp * 0.5
    y += bp(noise(n), 300, 900) * 0.25 * rasp
    y += sine(190, n) * 0.04 * rasp
    return y * env * 0.9


def wood_knock():
    n = t2n(0.45); t = np.arange(n) / SR
    y = sine(120 + 60 * np.exp(-t / 0.02), n) * np.exp(-t / 0.07) * 0.9
    for f, a, d in ((240, .5, .09), (510, .35, .05), (930, .22, .03), (1650, .12, .015)):
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
    y += bp(noise(n), 800, 5000) * np.exp(-t / 0.004) * 0.6
    return y * 0.7


def wood_lap():
    a = wood_knock(); b = wood_knock() * 0.7
    out = np.zeros(t2n(0.6)); out[:len(a)] += a
    k = t2n(0.035); m = min(len(b), len(out) - k); out[k:k + m] += b[:m] * 0.8
    n2 = t2n(0.08); t = np.arange(n2) / SR
    out[:n2] += bp(noise(n2), 1500, 6000) * np.exp(-t / 0.02) * 0.25
    return out


def wood_tick():
    n = t2n(0.25); t = np.arange(n) / SR
    y = np.zeros(n)
    for f, a, d in ((620, .5, .04), (1240, .35, .02), (2150, .2, .012)):
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
    y += bp(noise(n), 1500, 7000) * np.exp(-t / 0.003) * 0.5
    return y * 0.55


def beam_slide():
    """the beam head pushed through the slots: wood on wood, a little stick-slip, louder as it nears home"""
    n = t2n(1.2); t = np.arange(n) / SR
    env = np.clip(t / 0.3, 0, 1) * np.clip((1.12 - t) / 0.05, 0, 1)
    jit = 0.6 + 0.4 * (np.sin(2 * np.pi * 23 * t + 3 * np.sin(2 * np.pi * 3.1 * t)) > 0.3)
    y = svf_bp(noise(n), 700 + 900 * t, 0.6) * jit * 0.4 + bp(noise(n), 2500, 6000) * 0.08 * jit
    return y * env * (0.5 + 0.5 * t / 1.2)


def joint_lock():
    """咔: the beam seats home — a crisp hardwood crack over a deep, hollow thunk"""
    n = t2n(1.2); t = np.arange(n) / SR
    y = sine(70 + 70 * np.exp(-t / 0.03), n) * np.exp(-t / 0.18) * 1.0
    for f, a, d in ((180, .6, .12), (420, .4, .07), (880, .3, .04), (2300, .25, .012)):
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
    y += hp(noise(n), 2500) * np.exp(-t / 0.003) * 0.9
    return np.tanh(y * 1.1) * 0.85


SFX_NEW = {'plane_stroke': plane_stroke, 'wood_knock': wood_knock, 'wood_lap': wood_lap, 'wood_tick': wood_tick, 'beam_slide': beam_slide, 'joint_lock': joint_lock}
