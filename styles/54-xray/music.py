# 54 X光透视 · 配乐：前半是 X 光机的嗡声和继电器的轻响；盒盖弹开后，八音盒的旋律由画面里被拨的梳片奏出（cues 里的 comb_N），
# 下面垫一层柔和的弦乐；8.0 最后一个音落在 C 大三和弦上。build.py 注入 synth.py 的函数。

SCALE = [0, 2, 3, 5, 7, 8, 10]                 # A 自然小调，从 A3 起：第 i 根梳片的音高


def tooth_pitch(i):
    return 57 + SCALE[i % 7] + 12 * (i // 7)


def mbox(m, dur=1.8, vel=1.0):
    """八音盒：钢片的非谐波分音，针拨的瞬间"""
    n = t2n(dur); f = mtof(m); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / .9) + .35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / .12) + .18 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / .04)
    y += hp(noise(n), 4000) * np.exp(-t / .002) * .3
    return y * (1 - np.exp(-t / .0008)) * .3 * vel


def hum(dur, vel=1.0):
    n = t2n(dur); t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * 100 * t) + .5 * np.sin(2 * np.pi * 200 * t) + .25 * np.sin(2 * np.pi * 300 * t)) * .05
    y += np.sin(2 * np.pi * 7800 * t) * .004 + bp(noise(n), 2000, 5000) * .006
    return y * vel


def mus(M, tb, name, root, tones, bi):
    if bi < 2:
        M.add('music', hum(BAR * 1.02, 1.), tb, .6)
        M.add('music', strings([45, 52, 57], BAR * 1.05, 900), tb, .3, 0, .4)
        for q in range(4): M.add('drums', tick(2600, .25), tb + q * BEAT, .25, .3)
    elif bi == 2:
        M.add('music', strings([45, 52, 57, 60], BAR * 1.05, 1600), tb, .35, 0, .5)
        M.add('music', hum(BAR * 1.02, .5), tb, .4)
    elif bi == 3:
        M.add('music', strings([41, 48, 53, 57], BAR * .52, 1600), tb, .35, 0, .5)
        M.add('music', strings([43, 50, 55, 59], BAR * .52, 1600), tb + BAR / 2, .35, 0, .5)
    else:
        M.add('music', strings([48, 55, 60, 64, 67], BAR * 1.0, 1800), tb, .38, 0, .55)


# ---------- SFX ----------
def xray_hum():
    n = t2n(2.0); t = np.arange(n) / SR
    return hum(2.0, 1.4) * np.clip(t / .3, 0, 1) * np.exp(-np.clip(t - 1.2, 0, None) / .4)


def xray_click():
    n = t2n(.25); t = np.arange(n) / SR
    return (sine(900, n) * np.exp(-t / .01) * .4 + hp(noise(n), 2500) * np.exp(-t / .004) * .5) * .6


def lid_open():
    """盒盖弹开：木头的一声闷响 + 合页的吱声 + 弹簧的颤音"""
    n = t2n(1.0); t = np.arange(n) / SR
    y = sine(150 + 90 * np.exp(-t / .02), n) * np.exp(-t / .06) * .5 + lp(noise(n), 1200) * np.exp(-t / .02) * .3
    sq = svf_bp(noise(n), 1800 + 900 * np.sin(2 * np.pi * 3 * t), .3) * np.exp(-((t - .12) / .08) ** 2) * .25
    spring = np.sin(2 * np.pi * 420 * t * (1 + .05 * np.exp(-t / .1))) * np.exp(-t / .25) * np.sin(2 * np.pi * 16 * t) * .15
    return y + sq + spring


def xray_thunk():
    n = t2n(1.6); t = np.arange(n) / SR
    return sine(55 + 30 * np.exp(-t / .04), n) * np.exp(-t / .35) * .6 + lp(noise(n), 500) * np.exp(-t / .03) * .3


SFX_NEW = {'xray_hum': xray_hum, 'xray_click': xray_click, 'lid_open': lid_open, 'xray_thunk': xray_thunk}
for _i in range(24):
    SFX_NEW['comb_%d' % _i] = (lambda i=_i: mbox(tooth_pitch(i), 1.8, 1.0))

# AAC-safe: take the edge off near-impulse transients so the codec does not ring past the true-peak ceiling
SFX_NEW = {k: (lambda f=f: lp(f(), 11000)) for k, f in SFX_NEW.items()}
