# 给 AI 编程助手的说明（Codex / Cursor / Claude Code 等通用）

这个仓库是「再来 20 种」（sy-style-more20，20 MORE STYLES，作者 肖雄 / XIAOXIONG，MIT 协议）：编号 41–60 的 20 条 10 秒纯画面短片，每一帧都由代码在无头浏览器里算出来，`make.js` 一条命令出片（画面 + 程序合成的配乐音效 + 响度标准化）。上一批 21–40 在另一个仓库 sy-style-new20，不在这里。

**完整做法写在 [`skills/sy-style-more20/SKILL.md`](skills/sy-style-more20/SKILL.md)，开工前先读它，照着做。** 下面是最要紧的几条，方便你快速上手。

## 用户通常会说

- “帮我把万花筒那条做出来” → `node make.js style 57`
- “20 种全部渲染” → `node make.js style all`
- “把冰雕的灯改成暖黄色” → 备份后改 `styles/59-ice/index.html` 开头的 `const LIGHT_COL = [1, 1, 1];`（例如 `[2.4, 1.25, .35]`：LED 底色本来偏冷蓝，红要拉到 2 以上才看得出暖），`still 59 5 8 --compare` 出对比图给用户看，满意再出片

## 命令（都在仓库根目录运行）

```
node make.js check            # 先跑：检查 Node / Python / ffmpeg / 浏览器 / 字体 / 显卡
node make.js list             # 20 种：编号 41-60、中文名、英文名
node make.js still 57 5       # 出一张图 → out/57-万花筒_5s.jpg
node make.js still 59 5 8 --compare # 原版（index.原版.html）和修改后左右对比 → out/59-冰雕_5s_对比.jpg 等
node make.js style 57         # 出成片 → out/57-万花筒.mp4（编号 / 中文名 / 英文名；all = 全部）
node make.js sheet 57         # 成片抽 9 帧拼联系表
node make.js status           # 进度（也写在 out/进度.txt）
```

- 出片有显卡要 3 分钟到一个多小时（52 机械表芯约 72 分钟、53 烙画约 50 分钟），**放后台运行**，不要用短超时干等；中断后再跑同一条命令会接着做。
- 没有显卡时正式片要几个小时到几天，`style` 会停下（退出码 3）并列出办法：下载 Releases 里的成片 / `--draft` 草稿 / `--cpu` 过夜跑。把这几个办法告诉用户，让他选。
- `check` 有 × 时，请用户双击 `安装-Windows.bat`（Mac：`安装-Mac.command`）重新安装，不要自己改系统设置。
- 选项：`--gpu` / `--cpu` 强制显卡或软件渲染，`--force` 重做已完成的，`--draft` 快速草稿。
- 显卡接口（只有 Windows）：make.js 自己选，默认 gl，不行换 d3d11；54 X 光固定 d3d11（gl 会崩）。不要用 vulkan（会出黑帧）。

## 场景的规矩

- 每个风格：`styles/NN-name/index.html`（画面）、`music.py`（配乐和专属音效）、`render.args`（渲染参数）；55 还有 `table.js`（画面和配乐共用的节拍表）。公共库在 `lib/`，渲染器 `render.js`，声音合成 `audio/synth.py`。
- `render.args`：`--mb N` 运动模糊子帧数；`--soft` 柔和快门（子帧升余弦加权）；`--shutter 0.9` 快门长度；`--mbseg a-b:N` 这几秒改用 N 个子帧；`--angle d3d11` 指定显卡接口。51、52、53 的 `--soft --shutter 0.9 --mbseg …` 和 54 的 `--angle d3d11` 别删，成片就是这样渲的。
- `render(t)` 必须确定性：同一个 t 永远同一张图；不用 `Math.random()` / `Date.now()` 驱动画面，用 `Reel.rng(seed)`。
- 10 秒、30fps、1920×1080 不变；节拍 120 BPM（每拍 0.5 秒）。改了动作时间就同步改 `cues` 里的 `t`。
- 字体只认 `fonts/fonts.json` 里登记的（Noto Sans CJK SC 400/500/700、Inter 500/600/700、DejaVu Sans Mono、TeX Gyre Heros Cn），渲染器自动加载，不要装进系统。
- 改之前先把 `index.html` 备份成 `index.原版.html`；改完用 `node make.js still 编号 1 5 9.5 --compare`（59 冰雕用 `5 8`：底座灯 4 秒才亮；其他条用 `1 5 9.5`）出“原版 / 修改后”左右对比图，亲眼看过、给用户看过，再出片。
- **改光色和改配色是两回事**：光色要乘在光进入着色的每一个地方（受光面、高光、光柱、光斑、溢光），只改一处色值，最显眼的光柱、光斑往往不变。41–53、55、57、59、60 已经有光色旋钮 `LIGHT_COL`（44 另有 `BACK_COL`；59 的写在 JS 数组里），默认值 = 和成片逐像素一致。推荐值要看灯本身的底色：底色偏暖的要变冷、偏冷的要变暖，差距要拉大才看得出来（见 SKILL.md 7.1）。改速度见 SKILL.md 7.4：8.0 落拍、8.5 以后静止、和音效绑定的时间点都不能动。54、56、58 没有灯可调，改哪里见 SKILL.md 第 7 节的对照表。
- 出完片跑 `node make.js sheet 编号`，自己看一眼联系表再告诉用户。

## 和用户说话

用户多半是不懂编程的小白：简短、说人话、少提问、不贴日志。开工说要多久，做完说片子的完整路径。
