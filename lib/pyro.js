/* pyro.js — 53 烙画专用：画一棵黄山松（迎客松）的笔画，并“烧”进一张时间贴图
   - 笔画 = 折线 + 起止时间 + 深浅 + 线宽；按组安排时间（一组在一个时间窗内一笔接一笔烧完）
   - bake()：在 CPU 上把每个像素最早被烧到的时间 tb 和最终深浅 dk 写进 Float32Array（RG），交给着色器
   - penAt(t)：烙笔笔尖在 t 时刻的位置（落笔 / 抬笔过渡），烟从这里冒出
   只给 styles-new/53-pyro 用。坐标单位：厘米，u 向右，v 向上（画面上方）。 */
(function (g) {
  const PY = {};
  const hyp = Math.hypot, cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), lerp = (a, b, t) => a + (b - a) * t;
  function cr(P, u) {   // Catmull-Rom through points P at u in [0,1]
    const n = P.length - 1, x = u * n, i = Math.min(n - 1, Math.floor(x)), f = x - i;
    const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(n, i + 2)];
    const f2 = f * f, f3 = f2 * f;
    return [0, 1].map((k) => 0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * f + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * f2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * f3));
  }
  PY.cr = cr;
  const len = (pts) => { let L = 0; for (let i = 1; i < pts.length; i++) L += hyp(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); return L; };
  // a limb: centreline P, radius from r0 to r1 -> two edge strokes (+ its frame for bark / shading)
  function limb(P, r0, r1, R, n = 60) {
    const L = [], Rt = [], C = [];
    const ph1 = R() * 6, ph2 = R() * 6;
    for (let k = 0; k <= n; k++) {
      const u = k / n, p = cr(P, u), q = cr(P, Math.min(1, u + 0.01)), q0 = cr(P, Math.max(0, u - 0.01));
      let dx = q[0] - q0[0], dy = q[1] - q0[1]; const l = hyp(dx, dy) || 1; dx /= l; dy /= l;
      const r = lerp(r0, r1, u) * (1 + 0.07 * Math.sin(u * 9 + ph1) + 0.04 * Math.sin(u * 17 + ph2));
      L.push([p[0] - dy * r, p[1] + dx * r]); Rt.push([p[0] + dy * r, p[1] - dx * r]); C.push({ p, t: [dx, dy], r, u });
    }
    return { L, Rt, C };
  }
  PY.build = function (seed) {
    const R = (() => { let a = seed >>> 0; return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; })();
    const S = [];   // strokes: {pts, L (darkness 0..1), r (half width cm), grp, taper: 'both'|'tail'|'dot'}
    const add = (pts, L, r, grp, taper = 'both') => { if (pts.length > 1) S.push({ pts, L, r, grp, taper, sd: R() }); };
    const dot = (x, y, L, r, grp) => S.push({ pts: [[x, y], [x + 0.004, y + 0.003]], L, r, grp, taper: 'dot', sd: R() });
    // shading-tip wash: parallel rows of short flat strokes whose depth follows the tone underneath
    function wash(maskTone, ang, sp, Lmax, r, grp, box, floor) {
      const [u0, u1, v0, v1] = box, ca = Math.cos(ang), sa = Math.sin(ang), nx = -sa, ny = ca;
      const cs = [[u0, v0], [u1, v0], [u0, v1], [u1, v1]];
      const pr = cs.map(([x, y]) => x * nx + y * ny), pa = cs.map(([x, y]) => x * ca + y * sa);
      const d0 = Math.min(...pr), d1 = Math.max(...pr), a0 = Math.min(...pa), a1 = Math.max(...pa);
      for (let d = d0; d <= d1; d += sp) {
        let run = [];
        const flush = () => { if (run.length > 2) { const tm = run.reduce((q, p) => q + p[2], 0) / run.length; if (tm > floor) add(run.map((p) => [p[0], p[1]]), Lmax * tm * (0.92 + 0.08 * R()), r, grp, 'flat'); } run = []; };
        for (let a = a0; a <= a1 + 0.02; a += 0.06) {
          const x = nx * d + ca * a, y = ny * d + sa * a;
          const tn = x >= u0 && x <= u1 && y >= v0 && y <= v1 ? maskTone(x, y) : -1;
          if (tn <= 0) { flush(); continue; }
          run.push([x, y, tn]);
          if (run.length >= 6) { const last = run[run.length - 1]; flush(); run.push(last); }
        }
        flush();
      }
    }
    // ---------- the trunk: thick, gnarled, leaning out from the cliff
    const T = limb([[-6.0, -3.2], [-6.5, -1.3], [-5.9, 0.5], [-4.9, 2.0], [-4.45, 3.4], [-4.6, 4.7]], 1.28, 0.55, R, 90);
    // the welcoming arm: one long branch reaching flat out to the right, and the lesser limbs
    const ARM = limb([[-5.3, 0.9], [-2.6, 1.15], [0.4, 0.75], [3.4, 1.05], [6.4, 0.6], [8.9, 0.95]], 0.46, 0.05, R, 90);
    const B2 = limb([[-4.6, 4.5], [-3.1, 5.35], [-0.6, 5.75]], 0.34, 0.035, R);
    const B3 = limb([[-4.7, 4.3], [-6.4, 4.95], [-8.0, 4.85]], 0.30, 0.035, R);
    const B4 = limb([[-6.2, 1.7], [-7.8, 2.35], [-9.0, 2.15]], 0.28, 0.035, R);
    const twigs = [[-1.0, 1.05, -0.7, 2.0], [2.0, 0.95, 2.3, 1.85], [5.0, 0.85, 5.3, 1.7], [7.8, 0.80, 8.1, 1.55]].map(([ax, ay, bx, by]) => limb([[ax, ay], [(ax + bx) / 2 - 0.15, (ay + by) / 2], [bx, by]], 0.16, 0.06, R, 16));
    add(T.L, 0.96, 0.075, 'trunkL'); add(T.Rt, 0.98, 0.085, 'trunkR');
    for (const l of [ARM, B2, B3, B4]) { add(l.L, 0.94, 0.062, 'branch'); add(l.Rt, 0.96, 0.068, 'branch'); }   // limbs taper to a point: their two edges meet
    for (const l of twigs) add(l.C.map((c) => c.p), 0.95, 0.055, 'branch', 'tail');   // a twig is one tapering line, not a pair
    // bark: irregular plates — short curved strokes along the trunk, crowded toward the shaded side
    for (const [l, dens] of [[T, 1.6], [ARM, 0.7], [B2, 0.5], [B3, 0.5], [B4, 0.5]]) {
      for (const c of l.C) {
        for (let k = 0; k < 3; k++) {
          if (R() > 0.42 * dens) continue;
          const w = (R() * 1.7 - 0.85) * c.r * 0.85, base = [c.p[0] - c.t[1] * w, c.p[1] + c.t[0] * w];
          const ln = 0.22 + R() * 0.38, bend = (R() - 0.5) * 0.35;
          const pts = []; for (let j = 0; j <= 6; j++) { const s = j / 6 - 0.5; pts.push([base[0] + c.t[0] * s * ln - c.t[1] * bend * (0.25 - s * s), base[1] + c.t[1] * s * ln + c.t[0] * bend * (0.25 - s * s)]); }
          const side = -w / Math.max(c.r, 1e-3);   // + on the shaded (right-hand) side
          add(pts, 0.55 + 0.35 * cl(side * 0.5 + 0.5) + 0.1 * R(), 0.030 + 0.012 * R(), 'bark');
        }
      }
    }
    // ---------- the cliff: an outline, facet edges, a ledge
    const rockC = [[-11.0, -7.3], [-10.6, -4.7], [-9.6, -3.5], [-8.0, -3.05], [-6.4, -3.35], [-5.0, -2.95], [-3.6, -3.65], [-2.6, -4.65], [-1.8, -5.85], [-1.2, -7.3]];
    const rockOut = []; for (let k = 0; k <= 110; k++) { const p = cr(rockC, k / 110); rockOut.push([p[0] + 0.06 * Math.sin(k * 0.9), p[1] + 0.06 * Math.cos(k * 1.3)]); }
    add(rockOut, 0.95, 0.070, 'rock');
    const FX = [[-9.6, -3.5, -9.25, -5.2, -9.8, -7.25], [-8.0, -3.05, -7.45, -4.6, -7.9, -6.4], [-6.4, -3.35, -6.05, -5.0, -5.3, -7.1], [-5.0, -2.95, -4.45, -4.45, -3.85, -6.5]];
    for (const f of FX) { const pts = []; for (let k = 0; k <= 16; k++) { const p = cr([[f[0], f[1]], [f[2], f[3]], [f[4], f[5]]], k / 16); pts.push([p[0] + 0.05 * Math.sin(k * 1.7), p[1]]); } add(pts, 0.80, 0.045, 'rock'); }
    { const pts = []; const L = [[-9.25, -5.2], [-7.45, -4.6], [-6.05, -5.0], [-4.45, -4.45], [-2.65, -4.7]]; for (let k = 0; k <= 30; k++) pts.push(cr(L, k / 30)); add(pts, 0.70, 0.040, 'rock'); }
    const rockTop = (u) => { const k = cl((u + 11.0) / 9.8) * (rockC.length - 1); const i = Math.min(rockC.length - 2, Math.floor(k)), f = k - i; return lerp(rockC[i][1], rockC[i + 1][1], f); };
    const inRock = (u, v) => u > -11 && u < -1.2 && v > -7.35 && v < rockTop(u) - 0.10;
    // tone over the cliff: each facet is lit on its left, falls into shadow on its right; deeper low down
    const FB = [-11.2, -9.5, -7.75, -6.2, -4.7, -2.9, -1.2];
    const rockTone = (u, v) => { let i = 0; while (i < FB.length - 2 && u > FB[i + 1]) i++; const f = cl((u - FB[i]) / (FB[i + 1] - FB[i])); return cl(0.08 + 0.86 * Math.pow(f, 1.25) + 0.24 * cl((-4.4 - v) / 2.5) + 0.08 * Math.sin(u * 3.1 + v * 2.3)); };
    // ---------- pads of needles: flat-topped clouds, darker underneath
    const PADS = [[-0.9, 2.25, 1.55, 0.95], [2.1, 2.05, 1.75, 0.95], [5.15, 1.85, 1.6, 0.9], [8.05, 1.75, 1.3, 0.8], [-0.9, 6.65, 2.3, 1.0], [-4.25, 5.85, 1.6, 0.9], [-7.6, 5.65, 1.5, 0.85], [-8.7, 3.05, 1.2, 0.75]]
      .map(([cx, top, a, h]) => [cx, top + 0.30 * h, a, h * 1.35]);   // deeper clouds: they read as volumes, not fringes
    const padShape = (u, v, P) => { const [cx, top, a, h] = P; const x = (u - cx) / a; if (Math.abs(x) > 1) return false; const bot = top - h * (0.62 + 0.38 * Math.sqrt(Math.max(0, 1 - x * x))) - 0.10 * Math.abs(Math.sin(x * 7)); const t2 = top - 0.18 * Math.pow(Math.abs(x), 4); return v < t2 && v > bot; };
    PADS.forEach((P, pi) => {
      const [cx, top, a, h] = P, grp = pi < 4 ? 'padsA' : 'padsB';
      const rows = Math.round(h / 0.15);
      for (let r = 0; r < rows; r++) {
        const fr = r / Math.max(1, rows - 1);            // 0 underneath -> 1 on top
        const ry = top - h * 0.92 + r * 0.15;
        const n = Math.round(a * 2 * 5.5);
        for (let k = 0; k < n; k++) {
          const x = cx - a + (k + R()) / n * 2 * a;
          if (!padShape(x, ry + 0.05, P) || R() < 0.5 * fr * fr) continue;   // the sunlit top stays open
          const ang = Math.PI / 2 + (R() - 0.5) * 1.5 + (x - cx) / a * 0.5;
          const l = 0.30 + 0.25 * R();
          let ex = x + Math.cos(ang) * l, ey = ry + Math.sin(ang) * l;
          if (ey > top) { const s2 = (top - ry) / Math.max(1e-3, ey - ry); ex = x + (ex - x) * s2; ey = top; }   // the flat top of the cloud
          add([[x, ry], [ex, ey]], lerp(0.92, 0.40, fr) + 0.06 * R(), lerp(0.030, 0.021, fr), grp, 'tail');
        }
      }
      // a crisp, ragged top edge of needle tips
      const n2 = Math.round(a * 2 * 7);
      for (let k = 0; k < n2; k++) { const x = cx - a * 0.92 + k / n2 * 1.84 * a; if (!padShape(x, top - 0.12, P)) continue; add([[x, top - 0.22], [x + (R() - 0.5) * 0.12, top - 0.02]], 0.44, 0.019, grp, 'tail'); }
      // volume: 0 on the sunlit flat top -> 1 deep underneath and in toward the limb that carries the pad
      const padTone = (u, v) => {
        if (!padShape(u, v, P)) return -1;
        const x = (u - cx) / a, bot = top - h * (0.62 + 0.38 * Math.sqrt(Math.max(0, 1 - x * x)));
        const fv = cl((v - bot) / Math.max(0.05, top - bot));
        return cl(Math.pow(1 - fv, 1.25) * 0.95 + 0.12 * (1 - Math.abs(x)) - 0.10 * x * x + 0.07 * Math.sin(u * 9.0 + v * 13.0));
      };
      // layer 1: a pale scorch wash from the shading tip, deeper toward the bottom
      wash(padTone, 0.0, 0.085, 0.44, 0.075, grp, [cx - a, cx + a, top - h - 0.1, top - 0.08], 0.0);
      // layer 2: short needle ticks fanning up and out, thickest in the lower body
      const ticks = [];
      for (let k = 0, N = Math.round(a * h * 70); k < N; k++) {
        const u = cx - a + R() * 2 * a, v = top - R() * h * 1.05, tn = padTone(u, v);
        if (tn < 0 || R() > 0.25 + 0.85 * tn) continue;
        const ang = Math.PI / 2 + (R() - 0.5) * 1.9 + (u - cx) / a * 0.45, l = 0.10 + 0.14 * R();
        const ex = u + Math.cos(ang) * l, ey = Math.min(top - 0.03, v + Math.sin(ang) * l);
        ticks.push([[u, v], [ex, ey], tn]);
      }
      ticks.sort((p, q) => p[0][0] - q[0][0]).forEach(([p0, p1, tn]) => add([p0, p1], 0.42 + 0.50 * tn + 0.05 * R(), 0.017 + 0.006 * R(), grp, 'tail'));
      // layer 3: stipple, packed into the deep underside and the core near the limb
      const dots = [];
      for (let k = 0, N = Math.round(a * h * 110); k < N; k++) {
        const u = cx - a + R() * 2 * a, v = top - R() * h * 1.05, tn = padTone(u, v);
        if (tn < 0 || R() > Math.pow(tn, 1.7) * 1.1) continue;
        dots.push([u, v, tn]);
      }
      dots.sort((p, q) => p[0] - q[0]).forEach(([u, v, tn]) => dot(u, v, 0.62 + 0.36 * tn, 0.022 + 0.016 * R(), grp));
    });
    // ---------- hatching and stippling (the hook): cliff, trunk shadow side, under the pads
    function hatch(maskTone, ang, sp, Lmax, r, grp, box, cross) {
      const [u0, u1, v0, v1] = box;
      const ca = Math.cos(ang), sa = Math.sin(ang), nx = -sa, ny = ca;
      const cs = [[u0, v0], [u1, v0], [u0, v1], [u1, v1]];
      const pr = cs.map(([x, y]) => x * nx + y * ny), pa = cs.map(([x, y]) => x * ca + y * sa);
      const d0 = Math.min(...pr), d1 = Math.max(...pr), a0 = Math.min(...pa), a1 = Math.max(...pa);
      const lines = []; let li = 0;
      for (let d = d0; d <= d1; d += sp * (0.85 + 0.3 * R()), li++) {
        const thr = [0.18, 0.52, 0.34, 0.68][li % 4] + (cross ? 0.2 : 0);       // light areas get every 4th line, dark areas all of them
        let run = null; const segs = [];
        for (let a = a0; a <= a1 + 0.02; a += 0.04) {
          const x = nx * d + ca * a, y = ny * d + sa * a;
          const tn = x >= u0 && x <= u1 && y >= v0 && y <= v1 ? maskTone(x, y) : -1;
          if (tn > thr) { if (!run) run = []; run.push([x + (R() - 0.5) * 0.012, y + (R() - 0.5) * 0.012, tn]); } else if (run) { if (run.length > 2) segs.push(run); run = null; }
        }
        if (run && run.length > 2) segs.push(run);
        for (const s of segs) lines.push(s);
      }
      lines.sort((p, q) => (p[0][0] + p[p.length - 1][0]) - (q[0][0] + q[q.length - 1][0]));
      lines.forEach((l) => { const tm = l.reduce((a, p) => a + p[2], 0) / l.length; add(l.map((p) => [p[0], p[1]]), Lmax * (0.55 + 0.45 * tm), r * (0.8 + 0.4 * tm), grp); });
    }
    const rockMT = (u, v) => (inRock(u, v) ? rockTone(u, v) : -1);
    hatch(rockMT, 1.22, 0.085, 0.95, 0.031, 'hatch', [-11.1, -1.2, -7.35, -2.9], false);
    hatch(rockMT, -0.42, 0.10, 0.92, 0.029, 'hatch', [-11.1, -1.2, -7.35, -2.9], true);
    const rockDeep = (u, v) => { const tn = rockMT(u, v); return tn > 0.55 ? tn : -1; };
    hatch(rockDeep, 0.42, 0.065, 0.98, 0.030, 'hatch', [-11.1, -1.2, -7.35, -2.9], true);
    wash(rockMT, 1.22, 0.11, 0.62, 0.075, 'hatch', [-11.1, -1.2, -7.35, -2.9], 0.15);
    const trunkMT = (u, v) => { let best = -1; for (const l of [T, ARM, B2, B3, B4]) { let bd = 1e9, side = 0, rr = 1; for (let i = 0; i < l.C.length; i += 2) { const c = l.C[i]; const dx = u - c.p[0], dy = v - c.p[1], d = hyp(dx, dy); if (d < bd) { bd = d; side = (dx * -c.t[1] + dy * c.t[0]) / Math.max(c.r, 1e-3); rr = c.r; } } if (bd < rr * 0.95) best = Math.max(best, cl(-side * 0.85 + 0.1)); } return best; };
    hatch(trunkMT, 0.30, 0.075, 0.92, 0.026, 'hatch', [-7.9, 9.2, -3.3, 5.2], false);
    const underMT = (u, v) => { let best = -1; for (const P of PADS) { const [cx, top, a, h] = P; const x = (u - cx) / a; if (Math.abs(x) > 1) continue; const bot = top - h * (0.62 + 0.38 * Math.sqrt(Math.max(0, 1 - x * x))); const dd = bot - v; if (dd > -0.05 && dd < 0.42) best = Math.max(best, cl(1 - dd / 0.42) * (1 - 0.6 * x * x)); } return best; };
    hatch(underMT, 1.45, 0.06, 0.90, 0.024, 'hatch', [-10.2, 9.6, -0.2, 6.0], false);
    // stipple: dots fill the mid-tones of the cliff and the shadow under the long arm
    for (let k = 0; k < 2600; k++) {
      const u = -11 + R() * 9.8, v = -7.3 + R() * 4.4;
      if (!inRock(u, v)) continue; const tn = rockTone(u, v);
      if (R() < tn * 0.55) dot(u, v, 0.45 + 0.4 * tn + 0.1 * R(), 0.030 + 0.02 * R(), 'hatch');
    }
    // ---------- far mountains and the moon: pale scorch only. Three ranges, the farther the paler; mist at their feet.
    const G = (u, c, w) => Math.exp(-Math.pow((u - c) / w, 2));
    const RNG = [   // ridge v(u), extent, ridge-line depth, wash depth, hatch depth, mist fall-off
      { f: (u) => -0.95 + 1.05 * G(u, 3.7, 1.5) + 1.15 * G(u, 9.7, 1.3) + 0.45 * G(u, 6.6, 1.1) + 0.07 * Math.sin(u * 6.3), u0: 1.2, u1: 10.9, Lr: 0.15, Lw: 0.13, Lh: 0.20, fall: 1.1 },
      { f: (u) => -2.0 + 1.5 * G(u, 5.5, 1.7) + 0.85 * G(u, 8.8, 1.2) + 0.10 * Math.sin(u * 5.1), u0: 1.0, u1: 10.9, Lr: 0.25, Lw: 0.21, Lh: 0.32, fall: 0.95 },
      { f: (u) => -3.4 + 0.95 * G(u, 7.0, 1.5) + 0.35 * G(u, 4.6, 0.9) + 0.07 * Math.sin(u * 7.3), u0: 3.0, u1: 10.9, Lr: 0.36, Lw: 0.29, Lh: 0.44, fall: 0.8 },
    ];
    const edgeF = (R0, u) => cl((u - R0.u0) / 1.2) * cl((R0.u1 - u) / 0.4);
    const front = (i, u) => { let m = -99; for (let j = i + 1; j < RNG.length; j++) if (u > RNG[j].u0 && u < RNG[j].u1) m = Math.max(m, RNG[j].f(u)); return m; };
    RNG.forEach((R0, i) => {
      // tone below the crest: strongest just under it and on slopes turned away from the light (right), fading into mist
      const tone = (u, v) => {
        if (u < R0.u0 || u > R0.u1) return -1;
        const top = R0.f(u), dd = top - v; if (dd < 0 || v < front(i, u) + 0.04) return -1;
        const sl = (R0.f(u + 0.05) - R0.f(u - 0.05)) / 0.1;
        return cl((0.45 + 0.55 * cl(-sl * 0.9 + 0.2)) * Math.exp(-dd / R0.fall) * edgeF(R0, u));
      };
      wash(tone, 0.0, 0.075, R0.Lw, 0.07, 'far', [R0.u0, R0.u1, -6.0, 1.4], 0.04);
      hatch((u, v) => { const tn = tone(u, v); return tn > 0 ? Math.min(1, tn * 1.25) : -1; }, -0.30, 0.085, R0.Lh, 0.020, 'far', [R0.u0, R0.u1, -6.0, 1.4], false);
      let ridge = [];
      for (let k = 0; k <= 90; k++) {
        const u = lerp(R0.u0 + 0.3, R0.u1, k / 90);
        if (R0.f(u) > front(i, u) + 0.04) ridge.push([u, R0.f(u)]);
        else { if (ridge.length > 2) add(ridge, R0.Lr, 0.024, 'far'); ridge = []; }
      }
      if (ridge.length > 2) add(ridge, R0.Lr, 0.024, 'far');
    });
    // the moon: no outline. The disc is bare wood, held by a faint scorched glow around it
    for (let ring = 0; ring < 15; ring++) {
      const rr = 1.18 + ring * 0.06, Lr = 0.115 * Math.exp(-ring / 5.5);   // a broad, even glow; the rim is only where the glow stops
      const nseg = 6, ph = R() * 6.28;
      for (let sgi = 0; sgi < nseg; sgi++) {
        const arc = [];
        for (let k = 0; k <= 14; k++) { const a = ph + (sgi + k / 14 * 1.08) / nseg * Math.PI * 2; const w = rr * (1 + 0.012 * Math.sin(a * 3 + ring)); arc.push([7.6 + w * Math.cos(a), 5.0 + w * Math.sin(a)]); }
        add(arc, Lr * (0.9 + 0.2 * R()), 0.075, 'far', 'flat');
      }
    }
    // the closing accent: one slow, deep stroke into the shadow under the arm, near the trunk
    { const pts = ARM.C.filter((c) => c.u > 0.07 && c.u < 0.24).map((c) => [c.p[0] + c.t[1] * c.r * 0.55, c.p[1] - c.t[0] * c.r * 0.55]); add(pts, 1.0, 0.07, 'final'); }
    return S;
  };
  // schedule groups into time windows; each stroke gets t0..t1 (pen down), lifts in between
  PY.schedule = function (S, plan) {
    for (const [grp, t0, t1] of plan) {
      const G = S.filter((s) => s.grp === grp); if (!G.length) continue;
      const Ls = G.map((s) => len(s.pts)), Lt = Ls.reduce((a, b) => a + b, 0);
      const gap = Math.min(0.06, (t1 - t0) * 0.25 / G.length), k = (t1 - t0 - gap * G.length) / Lt;
      let t = t0;
      G.forEach((s, i) => { s.t0 = t; s.t1 = t + Ls[i] * k; t = s.t1 + gap; });
    }
    return S.filter((s) => s.t0 !== undefined).sort((a, b) => a.t0 - b.t0);
  };
  // CPU bake: per texel the burn time (tb) and final darkness (dk). Each stroke has a pressure/dwell profile:
  // its width and depth swell and taper along it; the burn is a dark core fading into a pale scorch halo.
  PY.bake = function (S, W, H, u0, v0, du, dv) {
    // 4 floats per texel: [burn time, darkness] of the stroke that ends up darkest, and of the first stroke to mark it
    const D = new Float32Array(W * H * 4);
    for (let i = 0; i < W * H; i++) { D[i * 4] = 20; D[i * 4 + 1] = 0; D[i * 4 + 2] = 20; D[i * 4 + 3] = 0; }
    const sx = W / du, sy = H / dv;
    const wprof = (s, f) => s.taper === 'dot' || s.taper === 'none' || s.taper === 'flat' ? 1 : s.taper === 'tail' ? (1 - 0.62 * f) * (0.72 + 0.28 * Math.min(1, f * 5)) : 0.42 + 0.58 * Math.pow(Math.sin(Math.PI * cl(f)), 0.55);
    const lprof = (s, f) => s.taper === 'dot' || s.taper === 'flat' ? 1 : (0.80 + 0.20 * Math.sin(Math.PI * cl(f))) * (1 + 0.12 * Math.max(0, 1 - f * 10)) * (0.93 + 0.07 * Math.sin(f * 19 + s.sd * 40));
    for (const s of S) {
      const P = s.pts; let acc = 0; const Lt = len(P) || 1;
      for (let k = 0; k < P.length - 1; k++) {
        const [ax, ay] = P[k], [bx, by] = P[k + 1];
        const sl = hyp(bx - ax, by - ay); if (sl < 1e-6) continue;
        const a0 = acc; acc += sl;
        const ta = s.t0 + (s.t1 - s.t0) * a0 / Lt, tb = s.t0 + (s.t1 - s.t0) * acc / Lt;
        const flat = s.taper === 'flat', halo = flat ? s.r * 1.45 : s.r * 1.1 * 3.0;   // shading washes: soft core, no halo
        const x0 = Math.max(0, Math.floor((Math.min(ax, bx) - halo - u0) * sx)), x1 = Math.min(W - 1, Math.ceil((Math.max(ax, bx) + halo - u0) * sx));
        const y0 = Math.max(0, Math.floor((Math.min(ay, by) - halo - v0) * sy)), y1 = Math.min(H - 1, Math.ceil((Math.max(ay, by) + halo - v0) * sy));
        const bax = bx - ax, bay = by - ay, bb = bax * bax + bay * bay;
        for (let y = y0; y <= y1; y++) {
          const py = v0 + (y + 0.5) / sy;
          for (let x = x0; x <= x1; x++) {
            const px = u0 + (x + 0.5) / sx;
            const pax = px - ax, pay = py - ay; const h = cl((pax * bax + pay * bay) / bb);
            const ex = pax - bax * h, ey = pay - bay * h, d2 = ex * ex + ey * ey;
            if (d2 > halo * halo) continue;
            const d = Math.sqrt(d2);
            const fr = (a0 + h * sl) / Lt;
            const rl = s.r * wprof(s, fr);
            const q = d / rl;
            const q9 = q / 0.9, core = Math.exp(-q9 * q9 * q9);
            const Ll = Math.min(1, s.L * lprof(s, fr));
            const hal = flat ? 0 : 0.20 * Math.min(1, Ll * 2.2) * Math.exp(-q * q / 6.76);   // pale strokes leave a paler halo
            const val = 1 - (1 - Ll * core) * (1 - hal);
            if (val < 0.012) continue;
            const i = (y * W + x) * 4;
            const tt = ta + (tb - ta) * h + Math.min(q, 3) * 0.015;
            if (tt < D[i + 2] || (Math.abs(tt - D[i + 2]) < 1e-3 && val > D[i + 3])) { D[i + 2] = tt; D[i + 3] = val; }
            // the stroke that dominates this texel's darkness decides when it burns
            if (val > D[i + 1] + 1e-4) { D[i + 1] = val; D[i] = tt; }
            else if (val > D[i + 1] - 1e-4 && tt < D[i]) D[i] = tt;
          }
        }
      }
    }
    return D;
  };
  // where is the nib at time t: on a stroke (down) or travelling between strokes (lifted)
  PY.penAt = function (S, t) {
    if (!S.length) return { u: 0, v: 0, h: 2, down: 0 };
    const first = S[0], last = S[S.length - 1];
    if (t <= first.t0) { const k = cl((first.t0 - t) / 0.5); return { u: first.pts[0][0] + 0.4 * k, v: first.pts[0][1] - 0.2 * k, h: 1.6 * k * k * (3 - 2 * k) + 0.0, down: t > first.t0 - 0.02 ? 1 : 0 }; }
    // find the stroke in progress or the gap we are in
    let lo = 0, hi = S.length - 1;
    while (lo < hi) { const m = (lo + hi + 1) >> 1; if (S[m].t0 <= t) lo = m; else hi = m - 1; }
    const s = S[lo];
    if (t <= s.t1) {
      const u = (t - s.t0) / Math.max(1e-6, s.t1 - s.t0); const P = s.pts, Lt = len(P); let target = u * Lt, acc = 0;
      for (let k = 0; k < P.length - 1; k++) { const sl = hyp(P[k + 1][0] - P[k][0], P[k + 1][1] - P[k][1]); if (acc + sl >= target) { const f = (target - acc) / Math.max(sl, 1e-6); return { u: lerp(P[k][0], P[k + 1][0], f), v: lerp(P[k][1], P[k + 1][1], f), h: 0, down: 1 }; } acc += sl; }
      const e = P[P.length - 1]; return { u: e[0], v: e[1], h: 0, down: 1 };
    }
    const e = s.pts[s.pts.length - 1];
    if (lo === S.length - 1) { return { u: e[0], v: e[1], h: 0, down: 0, after: t - s.t1 }; }
    const n = S[lo + 1], b = n.pts[0];
    const f = (t - s.t1) / Math.max(1e-6, n.t0 - s.t1), dist = hyp(b[0] - e[0], b[1] - e[1]);
    const ff = f * f * (3 - 2 * f);
    return { u: lerp(e[0], b[0], ff), v: lerp(e[1], b[1], ff), h: Math.min(0.9, 0.08 + dist * 0.18) * 4 * f * (1 - f), down: 0 };
  };
  g.PY = PY;
})(typeof window !== 'undefined' ? window : globalThis);
