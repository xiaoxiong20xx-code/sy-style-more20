/* mosaic.js — 51 马赛克专用：按“走向”（andamento）排布镶嵌石块
   - 图案用 2D 距离场描述（负数在形内）；石块沿等值线一排排排布：形内向里收、形外绕外轮廓几圈，再往外是横排（opus tessellatum）
   - 等值线用 marching squares 提取并串成折线，沿折线等距放石块，方向取切线
   - 输出 tiles：{x, y, ang, hl, hw, mat, row, ring}，以及给着色器用的格子索引表
   只给 styles-new/51-mosaic 用。 */
(function (g) {
  const MS = {};
  // marching squares -> polylines at one level of a sampled field
  MS.contours = function (F, nx, ny, x0, y0, gs, L) {
    const H = nx * ny;
    const segs = [];   // [keyA, ax, ay, keyB, bx, by]
    const ip = (fa, fb) => (L - fa) / (fb - fa);
    for (let j = 0; j < ny - 1; j++) for (let i = 0; i < nx - 1; i++) {
      const fa = F[j * nx + i], fb = F[j * nx + i + 1], fc = F[(j + 1) * nx + i + 1], fd = F[(j + 1) * nx + i];
      const c = (fa > L) | ((fb > L) << 1) | ((fc > L) << 2) | ((fd > L) << 3);
      if (c === 0 || c === 15) continue;
      const E = [
        () => [j * nx + i, x0 + (i + ip(fa, fb)) * gs, y0 + j * gs],                  // bottom a-b
        () => [H + j * nx + i + 1, x0 + (i + 1) * gs, y0 + (j + ip(fb, fc)) * gs],     // right b-c
        () => [(j + 1) * nx + i, x0 + (i + ip(fd, fc)) * gs, y0 + (j + 1) * gs],       // top d-c
        () => [H + j * nx + i, x0 + i * gs, y0 + (j + ip(fa, fd)) * gs],               // left a-d
      ];
      const T = { 1: [[3, 0]], 2: [[0, 1]], 3: [[3, 1]], 4: [[1, 2]], 5: [[3, 2], [0, 1]], 6: [[0, 2]], 7: [[3, 2]], 8: [[2, 3]], 9: [[0, 2]], 10: [[0, 3], [1, 2]], 11: [[1, 2]], 12: [[1, 3]], 13: [[0, 1]], 14: [[3, 0]] }[c];
      for (const [e1, e2] of T) { const a = E[e1](), b = E[e2](); segs.push([a[0], a[1], a[2], b[0], b[1], b[2]]); }
    }
    const adj = new Map();
    segs.forEach((s, k) => { for (const key of [s[0], s[3]]) { const l = adj.get(key); if (l) l.push(k); else adj.set(key, [k]); } });
    const used = new Uint8Array(segs.length), lines = [];
    for (let k0 = 0; k0 < segs.length; k0++) {
      if (used[k0]) continue;
      used[k0] = 1;
      const s0 = segs[k0];
      const pts = [[s0[1], s0[2]], [s0[4], s0[5]]];
      for (const dir of [1, -1]) {
        let key = dir > 0 ? s0[3] : s0[0];
        for (;;) {
          const l = adj.get(key); if (!l) break;
          const k = l.find((q) => !used[q]); if (k === undefined) break;
          used[k] = 1; const s = segs[k];
          const nxt = s[0] === key ? [s[3], s[4], s[5]] : [s[0], s[1], s[2]];
          if (dir > 0) pts.push([nxt[1], nxt[2]]); else pts.unshift([nxt[1], nxt[2]]);
          key = nxt[0];
        }
      }
      lines.push(pts);
    }
    return lines;
  };
  // walk a polyline and drop tile centres every `sp` (+ jitter); returns [{x, y, ang}]
  MS.alongLine = function (pts, sp, rnd, closedHint) {
    const out = [];
    let acc = sp * (0.3 + 0.4 * rnd()), next = acc;
    let s = 0;
    for (let k = 0; k < pts.length - 1; k++) {
      const [ax, ay] = pts[k], [bx, by] = pts[k + 1];
      const L = Math.hypot(bx - ax, by - ay); if (L < 1e-9) continue;
      while (next <= s + L) {
        const u = (next - s) / L;
        out.push({ x: ax + (bx - ax) * u, y: ay + (by - ay) * u, ang: Math.atan2(by - ay, bx - ax) });
        next += sp * (0.90 + 0.22 * rnd());
      }
      s += L;
    }
    // drop the last one if it crowds the first on a closed ring
    if (out.length > 2 && closedHint) { const a = out[0], b = out[out.length - 1]; if (Math.hypot(a.x - b.x, a.y - b.y) < sp * 0.7) out.pop(); }
    return out;
  };
  g.MS = MS;
})(typeof window !== 'undefined' ? window : globalThis);
