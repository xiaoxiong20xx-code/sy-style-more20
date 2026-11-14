/* craftd.js — 肖雄 XIAOXIONG 新风格 D 组（44 糖画 / 47 毛线编织 / 48 扎染 / 49 蓝晒 / 50 刮画）共用的小工具，只给这几条场景用。
   依赖 strokegl.js（SG.prog / SG.tex / SG.fbo / SG.quad / SG.bind）。
   - CD.init(stage)                         建 WebGL2 画布（尺寸 = 1920×1080×RS），返回 gl
   - CD.post(gl, o)                         HDR 场景缓冲（rgb = 线性颜色，a = 带符号的弥散圈半径，单位：1080p 像素）
                                            → 景深（散景收集）→ 泛光 → ACES → 暗角 / 色散 / 颗粒
       P.begin()                            绑定场景缓冲（场景着色器写进来）
       P.finish(u)                          u = { exposure, vignette, grain, ca, seed, bloom, bloomThresh, tint:[r,g,b], lift:[r,g,b], sat, contrast, dof }
   - CD.GLSL                                噪声、SDF、相机光线、ACES 等 GLSL 片段
   - CD.cam(pos, target, fovDeg, roll)      相机基向量 → { pos, fw, rt, up, tanh }
   - CD.camU(prog, cam, focus, aperture)    把相机写进 uniform（uCamP / uCamF / uCamR / uCamU / uTan / uFocus / uAper / uRes / uJit） */
(function () {
  const CD = {};
  CD.init = function (stage) {
    const RS = Reel.RS, W = Math.round(1920 * RS), H = Math.round(1080 * RS);
    const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
    cv.style.cssText = 'position:absolute;left:0;top:0;width:1920px;height:1080px'; stage.appendChild(cv);
    const gl = cv.getContext('webgl2', { preserveDrawingBuffer: true, antialias: false, alpha: false, premultipliedAlpha: false, powerPreference: 'high-performance' });
    gl.getExtension('EXT_color_buffer_float'); gl.getExtension('OES_texture_float_linear');
    CD.W = W; CD.H = H; CD.RS = RS;
    return gl;
  };

  CD.GLSL = `
#define PI 3.14159265
#define TAU 6.2831853
float hash11(float p){ p=fract(p*.1031); p*=p+33.33; p*=p+p; return fract(p); }
float hash12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float hash13(vec3 p3){ p3=fract(p3*.1031); p3+=dot(p3,p3.zyx+31.32); return fract((p3.x+p3.y)*p3.z); }
vec2 hash22(vec2 p){ vec3 p3=fract(vec3(p.xyx)*vec3(.1031,.1030,.0973)); p3+=dot(p3,p3.yzx+33.33); return fract((p3.xx+p3.yz)*p3.zy); }
vec3 hash32(vec2 p){ vec3 p3=fract(vec3(p.xyx)*vec3(.1031,.1030,.0973)); p3+=dot(p3,p3.yxz+33.33); return fract((p3.xxy+p3.yzz)*p3.zyx); }
float vn(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(hash12(i),hash12(i+vec2(1,0)),f.x), mix(hash12(i+vec2(0,1)),hash12(i+vec2(1,1)),f.x), f.y); }
float vn3(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
  float a=mix(mix(hash13(i),hash13(i+vec3(1,0,0)),f.x), mix(hash13(i+vec3(0,1,0)),hash13(i+vec3(1,1,0)),f.x), f.y);
  float b=mix(mix(hash13(i+vec3(0,0,1)),hash13(i+vec3(1,0,1)),f.x), mix(hash13(i+vec3(0,1,1)),hash13(i+vec3(1,1,1)),f.x), f.y);
  return mix(a,b,f.z); }
float vn1(float x){ float i=floor(x), f=fract(x); f=f*f*(3.-2.*f); return mix(hash11(i), hash11(i+1.), f); }
float fbm(vec2 p){ float a=.5, s=0.; for(int i=0;i<5;i++){ s+=a*vn(p); p=mat2(1.6,1.2,-1.2,1.6)*p+3.1; a*=.5; } return s; }
float fbm3(vec2 p){ float a=.5, s=0.; for(int i=0;i<3;i++){ s+=a*vn(p); p=mat2(1.6,1.2,-1.2,1.6)*p+3.1; a*=.5; } return s; }
float fbmv(vec3 p){ float a=.5, s=0.; for(int i=0;i<4;i++){ s+=a*vn3(p); p=p*2.03+vec3(1.7,9.2,3.3); a*=.5; } return s; }
// Worley (cellular) distance, returns (F1, F2)
vec2 worley(vec2 p){ vec2 i=floor(p), f=fract(p); float d1=8., d2=8.;
  for(int y=-1;y<=1;y++) for(int x=-1;x<=1;x++){ vec2 g=vec2(x,y); vec2 o=hash22(i+g); float d=length(g+o-f);
    if(d<d1){ d2=d1; d1=d; } else if(d<d2) d2=d; }
  return vec2(d1,d2); }
float smin(float a, float b, float k){ float h=clamp(.5+.5*(b-a)/k,0.,1.); return mix(b,a,h)-k*h*(1.-h); }
float smax(float a, float b, float k){ return -smin(-a,-b,k); }
float sdCapsule(vec3 p, vec3 a, vec3 b, float r){ vec3 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/dot(ba,ba),0.,1.); return length(pa-ba*h)-r; }
vec2 seg2(vec2 p, vec2 a, vec2 b){ vec2 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/dot(ba,ba),0.,1.); return vec2(length(pa-ba*h), h); }
float sdBox(vec3 p, vec3 b){ vec3 q=abs(p)-b; return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.); }
float sdRoundBox(vec3 p, vec3 b, float r){ vec3 q=abs(p)-b+r; return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.)-r; }
mat2 rot2(float a){ float c=cos(a), s=sin(a); return mat2(c,s,-s,c); }
vec3 aces(vec3 x){ const float a=2.51, b=.03, c=2.43, d=.59, e=.14; return clamp((x*(a*x+b))/(x*(c*x+d)+e),0.,1.); }
float luma(vec3 c){ return dot(c, vec3(.2126,.7152,.0722)); }
// camera
uniform vec3 uCamP, uCamF, uCamR, uCamU; uniform float uTan, uFocus, uAper; uniform vec2 uRes, uJit;
vec3 camRay(vec2 fc){
  vec2 q = (fc + uJit)/uRes*2. - 1.; q.x *= uRes.x/uRes.y;
  return normalize(uCamF + (uCamR*q.x + uCamU*q.y)*uTan);
}
// signed circle of confusion (1080p pixels) for a hit at distance d along the view axis
float cocOf(float d){ return uAper*(d - uFocus)/max(d, 1e-3); }
`;

  CD.cam = function (pos, target, fovDeg, roll = 0, worldUp = [0, 0, 1]) {
    const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
    const nrm = (a) => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
    const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
    const fw = nrm(sub(target, pos));
    let wu = worldUp; if (Math.abs(fw[0] * wu[0] + fw[1] * wu[1] + fw[2] * wu[2]) > 0.999) wu = [wu[1], wu[2], wu[0]];
    let rt = nrm(cross(fw, wu)); let up = cross(rt, fw);
    if (roll) { const c = Math.cos(roll), s = Math.sin(roll); const r2 = rt.map((x, i) => x * c + up[i] * s), u2 = up.map((x, i) => -rt[i] * s + x * c); rt = r2; up = u2; }
    return { pos, fw, rt, up, tanh: Math.tan(fovDeg * Math.PI / 360), target };
  };
  CD.camU = function (P, cam, focus, aper) {
    const jit = Reel.jit || [0, 0];
    P.f('uCamP', ...cam.pos).f('uCamF', ...cam.fw).f('uCamR', ...cam.rt).f('uCamU', ...cam.up).f('uTan', cam.tanh)
      .f('uFocus', focus).f('uAper', aper).f('uRes', CD.W, CD.H).f('uJit', jit[0], -jit[1]);
    return P;
  };
  // view-projection matrix (column-major) matching camRay(): same basis, same tan(fov/2), same sub-pixel jitter
  CD.viewProj = function (cam, near, far) {
    const { rt, up, fw, pos } = cam, asp = CD.W / CD.H, th = cam.tanh;
    const jit = Reel.jit || [0, 0];
    const jx = -jit[0] * 2 / CD.W, jy = jit[1] * 2 / CD.H;   // the opposite of camRay()'s offset, so both agree
    const d = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    // view: x = rt, y = up, z = -fw (GL convention: camera looks down -z)
    const V = [rt[0], up[0], -fw[0], 0, rt[1], up[1], -fw[1], 0, rt[2], up[2], -fw[2], 0, -d(rt, pos), -d(up, pos), d(fw, pos), 1];
    const sx = 1 / (th * asp), sy = 1 / th, A = -(far + near) / (far - near), B = -2 * far * near / (far - near);
    // projection with jitter: x_ndc += jx (applied as  -jx * z_view  in clip space)
    const P = [sx, 0, 0, 0, 0, sy, 0, 0, -jx, -jy, A, -1, 0, 0, B, 0];
    const M = new Float32Array(16);
    for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) { let s = 0; for (let k = 0; k < 4; k++) s += P[k * 4 + r] * V[c * 4 + k]; M[c * 4 + r] = s; }
    return M;
  };
  CD.GLSL_DEPTH = `
uniform float uNear, uFar;
// window-space depth for a hit at distance t along rd (matches CD.viewProj)
float rayDepth(vec3 rd, float t){ float z = t*dot(rd, uCamF); float A = -(uFar + uNear)/(uFar - uNear), B = -2.*uFar*uNear/(uFar - uNear);
  float ndc = (A*(-z) + B)/z; return clamp(ndc*.5 + .5, 0., 1.); }
`;
  // distance from camera to a world point along the view axis
  CD.depthOf = function (cam, p) { return (p[0] - cam.pos[0]) * cam.fw[0] + (p[1] - cam.pos[1]) * cam.fw[1] + (p[2] - cam.pos[2]) * cam.fw[2]; };

  CD.post = function (gl, o = {}) {
    const W = CD.W, H = CD.H, RS = CD.RS;
    const HD = '#version 300 es\nprecision highp float;\n';
    const tS = SG.tex(gl, W, H, { ifmt: gl.RGBA16F, type: gl.HALF_FLOAT }), fS = SG.fbo(gl, [tS]);
    if (o.depth) {   // optional depth buffer, for scenes that rasterize meshes over a ray-traced background
      const rb = gl.createRenderbuffer(); gl.bindRenderbuffer(gl.RENDERBUFFER, rb);
      gl.renderbufferStorage(gl.RENDERBUFFER, gl.DEPTH_COMPONENT24, W, H);
      gl.bindFramebuffer(gl.FRAMEBUFFER, fS.fb); gl.framebufferRenderbuffer(gl.FRAMEBUFFER, gl.DEPTH_ATTACHMENT, gl.RENDERBUFFER, rb);
    }
    const tD = SG.tex(gl, W, H, { ifmt: gl.RGBA16F, type: gl.HALF_FLOAT }), fD = SG.fbo(gl, [tD]);
    const BW = Math.max(8, Math.round(W / 4)), BH = Math.max(8, Math.round(H / 4));
    const tB1 = SG.tex(gl, BW, BH, { ifmt: gl.RGBA16F, type: gl.HALF_FLOAT }), fB1 = SG.fbo(gl, [tB1]);
    const tB2 = SG.tex(gl, BW, BH, { ifmt: gl.RGBA16F, type: gl.HALF_FLOAT }), fB2 = SG.fbo(gl, [tB2]);
    const CW = Math.max(8, Math.round(W / 16)), CH = Math.max(8, Math.round(H / 16));
    const tC1 = SG.tex(gl, CW, CH, { ifmt: gl.RGBA16F, type: gl.HALF_FLOAT }), fC1 = SG.fbo(gl, [tC1]);
    const tC2 = SG.tex(gl, CW, CH, { ifmt: gl.RGBA16F, type: gl.HALF_FLOAT }), fC2 = SG.fbo(gl, [tC2]);
    const Q = SG.quad(gl);
    // depth of field: scatter-as-gather on a golden-angle spiral (alpha = signed CoC in 1080p px)
    const pDof = SG.prog(gl, SG.VS_QUAD, HD + `in vec2 uv; out vec4 o; uniform sampler2D S; uniform vec2 px; uniform float rs, maxR, on;
void main(){
  vec4 c0 = texture(S, uv); if (any(isnan(c0)) || any(isinf(c0))) c0 = vec4(0.); float cs = abs(c0.a)*rs; float cd = c0.a;
  if (on < .5 || maxR < .5) { o = vec4(c0.rgb, c0.a); return; }
  vec3 acc = c0.rgb; float tot = 1.; float r = .7; float ga = 2.39996;
  float ang = 0.;
  for (int i = 0; i < 900; i++) {
    if (r > maxR*rs) break;
    vec2 tc = uv + vec2(cos(ang), sin(ang))*r*px;
    vec4 s = texture(S, tc); if (any(isnan(s)) || any(isinf(s))) s = vec4(0.); float ss = abs(s.a)*rs;
    if (s.a > cd) ss = clamp(ss, 0., cs*2.);
    float m = smoothstep(r - .5, r + .5, ss);
    acc += mix(acc/tot, s.rgb, m); tot += 1.;
    ang += ga; r += .7/r;
  }
  o = vec4(acc/tot, c0.a);
}`);
    const pDown = SG.prog(gl, SG.VS_QUAD, HD + `in vec2 uv; out vec4 o; uniform sampler2D S; uniform vec2 px; uniform float th;
void main(){ vec3 c = vec3(0.);
  for (int y=-1;y<=1;y++) for (int x=-1;x<=1;x++) c += texture(S, uv + vec2(x,y)*px*1.5).rgb;
  c /= 9.; float l = max(c.r, max(c.g, c.b)); float k = max(l - th, 0.)/max(l, 1e-4);
  o = vec4(c*k, 1.); }`);
    const pBlur = SG.prog(gl, SG.VS_QUAD, HD + `in vec2 uv; out vec4 o; uniform sampler2D S; uniform vec2 dir;
void main(){ vec3 c = texture(S, uv).rgb*.227;
  c += (texture(S, uv + dir*1.385).rgb + texture(S, uv - dir*1.385).rgb)*.316;
  c += (texture(S, uv + dir*3.231).rgb + texture(S, uv - dir*3.231).rgb)*.070;
  o = vec4(c, 1.); }`);
    const pFin = SG.prog(gl, SG.VS_QUAD, HD + `in vec2 uv; out vec4 o; uniform sampler2D S, B1, B2; uniform vec2 res;
uniform float exposure, vig, grain, ca, seed, bloom, sat, contrast; uniform vec3 tint, lift; uniform vec2 streak;
float hash12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
vec3 aces(vec3 x){ const float a=2.51, b=.03, c=2.43, d=.59, e=.14; return clamp((x*(a*x+b))/(x*(c*x+d)+e),0.,1.); }
void main(){
  vec2 d = uv - .5;
  vec3 c;
  c.r = texture(S, uv - d*ca*.006).r; c.g = texture(S, uv).g; c.b = texture(S, uv + d*ca*.006).b;
  if (dot(streak, streak) > 1.) {      // whip pan: average along the motion direction (streak in px)
    vec3 acc = vec3(0.);
    for (int i = 0; i < 48; i++) { float k = (float(i) + .5)/48. - .5; acc += texture(S, uv + streak*k/res).rgb; }
    c = acc/48.;
  }
  c += (texture(B1, uv).rgb*.6 + texture(B2, uv).rgb*.4)*bloom;
  c *= exposure*tint;
  c = aces(c);
  c = pow(c, vec3(1./2.2));
  float l = dot(c, vec3(.2126,.7152,.0722));
  c = mix(vec3(l), c, sat);
  c = (c - .5)*contrast + .5;
  c = c + lift*(1. - c);
  c *= 1. - vig*smoothstep(.3, 1.15, length(d*vec2(1.25, 1.)));
  float g = hash12(floor(uv*res) + seed*37.3) + hash12(floor(uv*res*.5) + seed*11.1) - 1.;
  c += g*grain*(.6 + .4*(1. - l));
  o = vec4(clamp(c, 0., 1.), 1.);
}`);
    const P = {
      tS, fS, tD, fD,
      begin() { SG.bind(gl, fS); },
      finish(u = {}) {
        const dof = u.dof ?? 22;
        SG.bind(gl, fD); pDof.use().t('S', tS).f('px', 1 / W, 1 / H).f('rs', RS).f('maxR', dof).f('on', dof > 0 ? 1 : 0); Q.draw();
        SG.bind(gl, fB1); pDown.use().t('S', tD).f('px', 1 / W, 1 / H).f('th', u.bloomThresh ?? 1.0); Q.draw();
        SG.bind(gl, fB2); pBlur.use().t('S', tB1).f('dir', 1 / BW, 0); Q.draw();
        SG.bind(gl, fB1); pBlur.use().t('S', tB2).f('dir', 0, 1 / BH); Q.draw();
        SG.bind(gl, fC1); pDown.use().t('S', tB1).f('px', 1 / BW, 1 / BH).f('th', 0); Q.draw();
        for (let k = 0; k < 2; k++) {
          SG.bind(gl, fC2); pBlur.use().t('S', tC1).f('dir', (1 + k) / CW, 0); Q.draw();
          SG.bind(gl, fC1); pBlur.use().t('S', tC2).f('dir', 0, (1 + k) / CH); Q.draw();
        }
        SG.bind(gl, null); gl.viewport(0, 0, W, H);
        const tn = u.tint || [1, 1, 1], lf = u.lift || [0, 0, 0];
        pFin.use().t('S', tD).t('B1', tB1).t('B2', tC1).f('res', W, H).f('exposure', u.exposure ?? 1).f('vig', u.vignette ?? 0.3)
          .f('grain', (u.grain ?? 0.03)).f('ca', u.ca ?? 0.5).f('seed', u.seed ?? 0).f('bloom', u.bloom ?? 0.15)
          .f('sat', u.sat ?? 1).f('contrast', u.contrast ?? 1).f('tint', tn[0], tn[1], tn[2]).f('lift', lf[0], lf[1], lf[2])
          .f('streak', ...(u.streak || [0, 0]));
        Q.draw();
        gl.finish();
      },
    };
    return P;
  };
  window.CD = CD;
})();
