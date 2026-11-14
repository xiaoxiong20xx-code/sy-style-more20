// 55 声音的形状 · the one timetable shared by the picture (index.html) and the sound (music.py reads the JSON after "=")
// beats: at t the plate is driven with `midi` (sine tone) and vibrates in the listed modes [n, m, sign, weight]
//   mode shape on the square plate (u, v in 0..1): cos(nπu)cos(mπv) + sign·cos(mπu)cos(nπv)
// glide: t0 -> t1 the tone slides midi0 -> midi1 and the shape morphs through `modes` in order
// chord: the final chord, every note sounding at once, its modes superposed; then the drive dies away by `release`
window.CHLADNI = {
  "sprinkle": [-0.8, 0.95],
  "beats": [
    {"t": 1.0, "midi": 50, "modes": [[2, 0, 1, 1]]},
    {"t": 1.5, "midi": 53, "modes": [[2, 4, 1, 1]]},
    {"t": 2.0, "midi": 57, "modes": [[4, 0, 1, 1]]},
    {"t": 2.5, "midi": 60, "modes": [[4, 2, -1, 1]]},
    {"t": 3.0, "midi": 62, "modes": [[6, 2, 1, 1]]},
    {"t": 3.5, "midi": 65, "modes": [[6, 4, 1, 1]]},
    {"t": 5.0, "midi": 74, "modes": [[10, 4, 1, 1]]},
    {"t": 5.5, "midi": 77, "modes": [[10, 6, 1, 1]]},
    {"t": 6.0, "midi": 76, "modes": [[12, 4, 1, 1]]},
    {"t": 6.5, "midi": 79, "modes": [[12, 6, -1, 1]]},
    {"t": 7.0, "midi": 81, "modes": [[14, 6, 1, 1]]},
    {"t": 7.5, "midi": 84, "modes": [[12, 10, 1, 1]]}
  ],
  "glide": {"t0": 4.0, "t1": 5.0, "midi0": 69, "midi1": 74,
            "modes": [[6, 4, 1], [8, 2, 1], [8, 4, -1], [10, 2, 1], [8, 6, 1], [10, 4, 1]]},
  "chord": {"t": 8.0, "release": 8.45, "midi": [62, 69, 77, 86],
            "modes": [[10, 4, 1, 0.7], [14, 8, 1, 0.6], [6, 12, -1, 0.5]]}
};
