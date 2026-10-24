# 奶蛙 Ref2AV 提示词写法总结（基于 optimized_v3）

- **样板工作流**：`DSH_ref2av_for_milkyfrog_optimized_v3.json`
- **结论来源**：用户判断「这个工作流生成的视频是我最满意的」
- **整理时间**：2026-10-24
- **适用任务**：绿幕白模视频 + 角色参考图 + 背景参考图 → 角色替换成片

---

## 0. 一句话结论

这份 prompt 之所以好用，不是因为它写得"华丽"，而是因为它**只做三件事，而且做得极干净**：

1. **给每个参考物划死边界**（谁能影响什么、不能影响什么）；
2. **把动作拆成一条带秒数的时间线**（13 个节拍，平均 1 秒一拍）；
3. **把不许出现的东西列成清单**（绿幕、白模、人手的形态、镜头运动）。

全文 **4,658 字符 / 703 词 / 33 行**，其中 **43% 的篇幅给了时间线**——这是它和普通描述型 prompt 最大的区别。

---

## 1. 整体结构

| 段落 | 字符数 | 占比 | 作用 |
|---|---:|---:|---|
| 首行 | 81 | 1.7% | 声明总时长、画幅、连续单镜头 |
| `REFERENCE ROLES` | 759 | 16.3% | 逐个参考物定义职责与禁区 |
| `PRIORITIES` | 1,063 | 22.8% | 4 条不可违反的优先级 |
| `MOTION TIMELINE` | 2,021 | **43.4%** | 逐秒动作表，13 个节拍 |
| `CONTINUITY AND IMAGE QUALITY` | 529 | 11.4% | 连续性与伪影清单 |
| `AUDIO` | 117 | 2.5% | 音频来源指令 |

六个段落，全部是大写标题 + 正文，没有嵌套、没有 Markdown 装饰、没有中文混排。

> **关键判断**：H3 的官方六段式（`subject_definitions` / `summary` / `retention_analysis` / `detailed_description` / `overall_soundscape` / `non_diegetic_music`）**不是硬性要求**。这份 v3 完全不用那套格式，改用自由英文结构，效果好于旧版（旧版 `DSH_ref2av_2` 正是六段式，5,905 字符）。文本编码器接受自然语言结构，结构化程度由你自己定。

---

## 2. 逐段拆解

### 2.1 首行：一句把基本参数钉死

```
Create one continuous 14.375-second vertical video using the supplied references.
```

三个信息，缺一不可：

| 要素 | 本例 | 说明 |
|---|---|---|
| `one continuous` | 单镜头不间断 | 事先排除多镜头/切镜 |
| `14.375-second` | **与实际输出时长完全一致** | 不是"约 14 秒"，是精确值 |
| `vertical` | 竖屏 | 与 `Resolution Selector` 的 9:16 对应 |

> **细节**：14.375 = 345 帧 ÷ 24fps。这个数字必须和工作流实际产出的时长一致，否则 prompt 里说 14.375 秒、实际生成 10 秒，时间线后半段就落空了。

### 2.2 REFERENCE ROLES：每个参考物都要划边界

三段，每段一个 `<标签>`，句式高度统一：

```
<Video 1> is the motion and timing reference only. Follow its original action order,
approximate timing, body orientation, gesture transitions, and overall rhythm.
Do not copy its grey mannequin or green-screen appearance.
```

拆开来看，每个角色行都包含 **"是什么 + 负责什么 + 不负责什么"** 三件事：

| 标签 | 负责 | 明确不负责（本例原话） |
|---|---|---|
| `<Video 1>` | 动作顺序、时间、身体朝向、手势转换、整体节奏 | `Do not copy its grey mannequin or green-screen appearance.` |
| `<Picture 1>` | 角色身份与设计：黄皮肤、头型、绿眼、圆肚、短粗四肢、比例、表面质感 | —— |
| `<Picture 2>` | 场景与背景：普通现代室内、白墙、可见地面、透视、构图、光照 | —— |

**写法要点：**

- 用 `... reference only.` 这个词组把"只负责这一件事"焊死；
- 每个角色行**都带一条否定句**（Video 1 否定白模与绿幕；后两段虽无显式否定，但 PRIORITIES 里补了）；
- `<Picture 1>` 用 **"Keep this same character throughout the entire clip"** + **"The character must remain the same recognizable individual in every frame."** 双保险，防身份漂移；
- 角色描述写成**可检验的物理特征**（黄色皮肤 / 绿色大眼 / 圆肚 / 短粗四肢），不写"可爱""呆萌"这类主观词。

> **标签顺序 = 接线顺序**：`<Picture 1>` → `ref_image_0`（节点 153），`<Picture 2>` → `ref_image_1`（节点 154），`<Video 1>` → `ref_video_0`（节点 157）。改了接线就必须改标签，否则模型认错参考。

### 2.3 PRIORITIES：4 条不可违反的规则

编号列表，每条一个祈使句开头。这四条的**排列顺序就是优先级顺序**：

| # | 原文开头 | 作用 |
|---|---|---|
| 1 | `Preserve the source action order and timing. Do not skip, reorder, repeat, or invent gestures.` | **动作保真排第一**，且用四个动词穷举了所有失败模式 |
| 2 | `Keep the yellow character's anatomy and identity consistent...` | 角色一致性，含手部形态与"最接近的可读手势"兜底规则 |
| 3 | `Keep the room from <Picture 2> as the background from the first frame to the last.` | 背景稳定，显式否定了绿幕/纯色/影棚背景 |
| 4 | `Use one fixed camera and one uninterrupted take.` | 运镜与构图稳定，附一长串"不许"清单 |

**最值得学的是第 2 条里的兜底规则：**

```
For finger-specific signs that the character cannot anatomically reproduce,
make the closest readable gesture using its own rounded hand shape
while preserving the same arm path, hand orientation, timing, and pose silhouette.
```

它解决了一个真实矛盾：源视频里有人手比划的数字手势，而奶蛙是圆手、做不出来。这句话没有让模型"硬做"（会出手指畸变），也没有让它"跳过"（会丢动作），而是给了第三条路：**用角色自己的手，做出最接近的可读手势，同时保住手臂轨迹、手部朝向、时间点和姿势剪影。**

> 这段是整份 prompt 里最"聪明"的地方，也是这类任务最容易忽略的。换任何非人形角色都必须保留这一条，只改角色名。

### 2.4 MOTION TIMELINE：整份 prompt 的核心

13 个节拍，从 `00:00.0` 到 `00:14.375`，格式统一：

```
00:01.5–00:02.0 — Raise both forearms inward and bring the hands together in front of the chest.
```

**统计数据：**

| 指标 | 值 |
|---|---|
| 节拍数 | 13 |
| 单拍时长 | 最短 0.4s / 最长 1.6s / **平均 1.01s** |
| 单拍描述长度 | 61 – 209 字符 |
| 节拍间隔 | 每拍之间留 **0.1 秒空隙**（00:01.4 → 00:01.5） |

三个值得注意的设计：

1. **平均一拍一秒**。太粗（3-4 秒一拍）模型记不住细节；太细（0.2 秒一拍）反而互相打架，模型会合并。
2. **节拍时长不均匀**，跟着动作的实际密度走——快的动作 0.4 秒，慢的过渡 1.6 秒。不是机械均分。
3. **每拍一个动词开头**（Raise / Separate / Turn / Open / Perform / Draw / Bring / Rise / Transition / Complete …），描述"做什么"，不描述"看起来像什么"。

**每拍写什么：**

- 肢体动作（`Raise both forearms inward`）
- 手的位置（`in front of the chest`、`near shoulder level`）
- 方向变化（`Turn the head to the side`）
- 明确的结束姿势（`finish with the hands raised in front of the upper torso`）

不写：情绪、气氛、形容词堆叠。

### 2.5 CONTINUITY AND IMAGE QUALITY：连续性与伪影清单

```
Movement must progress continuously from the opening pose to the final pose.
Match the source's relative timing rather than holding one pose for too long
or rushing through several actions at once.
```

这句针对的是**两个反向错误**：定格太久（模型偷懒）和一口气赶完几个动作（模型压缩）。中间那条"相对时间"的说法，比"严格遵守时间线"更可行。

然后是伪影清单，一条一句、逗号分隔：

```
avoid green spill, green tint, sudden darkening, background replacement,
flicker, morphing, duplicated limbs, disappearing hands,
or transitions to the source mannequin
```

> 里面 **`disappearing hands`（手消失）** 和 **`transitions to the source mannequin`（退回白模）** 是两个非常具体的失败现象，不是泛泛的"画质要好"。写伪影要写**你实际见过的样子**。

### 2.6 AUDIO

```
Use the original audio track from <Video 1> unchanged.
Do not generate replacement dialogue, music, or sound effects.
```

两句话：说清来源（原片音轨）+ 排除替代方案（不要生成对白/音乐/音效）。

> **必须和接线一致**：本例把 `Get Video Components.audio` 直接接到 `Create Video.audio`（连线 #300），并且**没有**接 `ref_video_audio_0`。prompt 说用原音轨，接线也必须走原音轨，否则等于说一套做一套。

---

## 3. 时间线怎么写（方法论）

这是整份文档最需要动手的部分。步骤：

1. **用播放器逐帧看源视频**，把"姿态发生实质变化"的时刻记下来。判据是**剪影变了**，不是"动了一下"。
2. **合并过短的**：小于 0.3 秒的相邻变化并成一拍。
3. **拆分过长的**：超过 2 秒的单一姿势，按"起势 / 保持 / 收势"拆成两到三拍。
4. **控制总数**：14 秒左右 → **12–16 拍**。少于 10 拍模型会丢动作，多于 20 拍模型会合并。
5. **每拍取一个动词开头**，写出：肢体 + 手的位置 + 方向 + 结束姿势。
6. **第一拍和最后一拍必须明确**：开场姿势、结束姿势，各写清手在哪。
7. **时间戳保留 3 位小数**（`00:01.5`），区间用小写 en-dash `–` 连接，破折号后用 `—` 分隔描述——这套符号在 v3 里是统一的。

**自检清单：**

- [ ] 时间线总长 = 首行声明的时长
- [ ] 节拍首尾相接，允许 0.1 秒空隙
- [ ] 每拍都有动词
- [ ] 没有"然后大概动几下"这类模糊描述
- [ ] 与源视频实际顺序一致（不要凭记忆，边看边记）

---

## 4. 节点侧的硬性配套

prompt 只占一半，另一半是这些参数。v3 的实际取值：

| 节点 | 参数 | 值 | 为什么 |
|---|---|---|---|
| 115 `Resolution Selector` | 画幅 / MP | **9:16 竖屏 / 1.0 MP** | 与源视频竖屏一致；1.0 MP 保细节 |
| 136 `Reference to Video` | `ref_image_size` | **`max`** | 参考图走 2048px 短边，身份保真最好；代价是慢数倍 |
| 136 | `length` | 由 `frame_count` 连线 | 自动匹配，不手填 |
| 151 `Trim Video` | `start` / `duration` | `0` / **`14.4`** | 截取源视频 14.4 秒，与输出 14.375 秒基本对齐 |
| 157 `H3 Frame Rate Align` | `source_fps` | 由视频解析节点连线（实际 24） | 控件值 24 只是断线时的兜底 |
| 130 `Create Video` | fps | **24** | 与 H3 输出帧率一致 |
| 152 → 130 | `audio` 连线 | **原片音轨直连** | 配合 AUDIO 段 |
| 129 `Random Noise` | 模式 / 种子 | **`fixed` / 829721249551274** | 固定种子才能复现与对比 |
| 146 / 142 `ComfySwitch` | LoRA 开关 | **`true` → 4 步 turbo** | ⚠️ 见下方说明 |
| 153 `Load Image` | 角色图 | `绿幕奶娃.png` | `<Picture 1>` |
| 154 `Load Image` | 背景图 | `白墙室内竖屏.png` | `<Picture 2>` |
| 92 `SaveVideo` | 前缀 | `video/DSH_test` | 输出命名 |

> ⚠️ **一处需要注意的矛盾**：说明节点里写着「关闭 4-step Turbo LoRA，切换到基础模型 20 steps」，但**实际保存的节点值是开关 `true` → 4 步**（节点 143 的 20 步当前未被选中）。也就是说你满意的这条成片是 **4 步 turbo + LoRA 开**跑出来的，说明文档里那句已经过期。复现时以节点实际值为准。

> **帧数网格**：源 480×864、24fps、345 帧、14.375 秒。345 正好是 `17k+5` 网格上的值（`17×20+5`），所以帧率对齐节点原样放行，不做任何重采样。选素材时优先挑**总帧数落在 17k+5 网格上**的片段，可以省掉一层重采样误差。

---

## 5. 可填空模板

替换 `{}` 中的内容即可。段落顺序不要变——优先级是从上往下传递的。

```
Create one continuous {时长}-second {vertical|horizontal} video using the supplied references.

REFERENCE ROLES
<Video 1> is the motion and timing reference only. Follow its original action order, approximate timing, body orientation, gesture transitions, and overall rhythm. Do not copy its {源素材的占位外观：grey mannequin / green screen} appearance.
<Picture 1> is the identity and design reference for the {角色名}. Keep this same character throughout the entire clip: {物理特征 1}, {物理特征 2}, {物理特征 3}, and the same proportions and surface appearance. The character must remain the same recognizable individual in every frame.
<Picture 2> is the scene and background reference. Use the same {场景描述：房间类型、墙面、地面、透视、构图、光照} throughout the whole video.

PRIORITIES
1. Preserve the source action order and timing. Do not skip, reorder, repeat, or invent gestures.
2. Keep the {角色名}'s anatomy and identity consistent, including both hands and arms. No {白模/灰模/绿幕} parts may appear, even briefly. Do not turn the character's hands into realistic human hands. For finger-specific signs that the character cannot anatomically reproduce, make the closest readable gesture using its own {手部形态} while preserving the same arm path, hand orientation, timing, and pose silhouette.
3. Keep the {场景} from <Picture 2> as the background from the first frame to the last. The green screen is only part of the motion-reference footage and must not appear in the generated scene. Do not replace it with a green, dark, blank, or studio background.
4. Use one fixed camera and one uninterrupted take. Keep the character approximately the same size and position in frame as the source performer. No cuts, zooms, reframing, camera movement, scene transitions, extra characters, clothing, accessories, or text.

MOTION TIMELINE
00:00.0–{t1} — {开场姿势，手在哪}
{t1}–{t2} — {动作 1}
...
{t12}–{总时长} — {结束姿势，手在哪}

CONTINUITY AND IMAGE QUALITY
Movement must progress continuously from the opening pose to the final pose. Match the source's relative timing rather than holding one pose for too long or rushing through several actions at once. Keep the character's {列举关键部位} attached and anatomically coherent during movement. Preserve the {场景} layout and lighting consistently; avoid {你实际见过的伪影}, green spill, flicker, morphing, duplicated limbs, disappearing hands, or transitions to the source mannequin.

AUDIO
Use the original audio track from <Video 1> unchanged. Do not generate replacement dialogue, music, or sound effects.
```

---

## 6. 换素材时怎么改

| 改动 | 只改这些 | 不要动 |
|---|---|---|
| 换源视频（别的白模动作） | 首行时长、`MOTION TIMELINE` 全文、`PRIORITIES` 第 1 条保持不变 | 技术性段落（CONTINUITY 后半、AUDIO） |
| 换角色（奶蛙 → 别的角色） | `REFERENCE ROLES` 第 2 段的物理特征、`PRIORITIES` 第 2 条的角色名与手部形态 | 时间线（动作与角色无关） |
| 换背景 | `REFERENCE ROLES` 第 3 段的场景描述、`PRIORITIES` 第 3 条 | 首行、时间线 |
| 改时长 | 首行秒数、时间线末拍时间戳、`Trim Video` 的 duration | 节拍数量比例（按时长÷1 秒估算） |
| 改画幅 | 首行的 `vertical/horizontal`、`Resolution Selector` | 其余全部 |
| 源视频不是 24fps | 无需改 prompt；`H3 Frame Rate Align` 会自动重采样 | —— |
| 源视频没有音轨 | `AUDIO` 段整段删掉，同时不要接 `152.audio` | —— |

**换角色的特别注意：**

- 特征要写成**可见的、可检验的**（`yellow skin` / `large green eyes` / `rounded belly`），不写性格词；
- `PRIORITIES` 第 2 条的"不要变成人手 / 用最接近的可读手势"必须保留并改成新角色的手部形态——这是防止手指畸变的关键；
- 如果新角色有尾巴、翅膀、角等额外肢体，加一句 `Keep the {肢体} attached and consistent`，否则容易中途消失。

---

## 7. 常见失败现象 → 对应改法

| 现象 | 大概率原因 | 改法 |
|---|---|---|
| 动作顺序被打乱、某段被搬到别处 | 时间线缺失或过粗 | 按 §3 重做时间线，粒度压到 ~1 秒一拍 |
| 中途某一拍被跳过 | 该拍描述太短或动词太多 | 一拍只写一个主动作；必要时把该拍拆成两拍 |
| 手消失 / 手指长成人手 | 缺兜底规则 | 补 `PRIORITIES` 第 2 条的手势兜底句 |
| 背景被换成绿幕或纯色 | 缺背景否定 | 在 `PRIORITIES` 第 3 条补 `Do not replace it with...` |
| 画面出现白模/灰模 | `<Video 1>` 的否定句太弱 | 在角色行补 `Do not copy its ... appearance`，并在 CONTINUITY 里补 `transitions to the source mannequin` |
| 一次定格太久 | 缺连续性别约束 | 补 `rather than holding one pose for too long` |
| 动作被压缩成几秒 | 同上 | 补 `or rushing through several actions at once` |
| 角色前后不是同一个人 | 缺身份双保险 | 补 `must remain the same recognizable individual in every frame` |
| 出现额外人物 / 字幕 / 衣服变化 | 缺"不许"清单 | 在 `PRIORITIES` 第 4 条补全清单 |
| 声音是模型生成的，不是原音 | 接线没走原音轨 | 把 `152.audio` 接到 `Create Video.audio`，并删掉 `ref_video_audio_0` 连线 |

---

## 8. 与旧版六段式格式的关系

| 项 | 旧版（`DSH_ref2av_2`） | v3（本样板） |
|---|---|---|
| 格式 | H3 官方六段式（`subject_definitions` / `summary` / `retention_analysis` / `detailed_description` / `overall_soundscape` / `non_diegetic_music`） | 自由英文六段（ROLES / PRIORITIES / TIMELINE / CONTINUITY / AUDIO） |
| 长度 | 5,905 字符 | 4,658 字符 |
| 动作描述 | 按镜头（`[Shot 1]` / `[Shot 2]` / `[Shot 3]`）粗分，含硬编码秒数 7.5s / 13s | 13 拍逐秒时间线，覆盖到最后一帧 |
| 结果 | 用户反馈动作对不上 | 用户最满意 |

**可以确定的结论**：官方六段式**不是必需格式**，H3 的文本编码器接受任意结构良好的英文；**逐秒时间线**是 v3 优于旧版的最可能原因（旧版只有 3 个粗粒度镜头划分，且 7.5s/13s 这两个秒数是写死的，与参考视频真实节拍无关）。

> 这一点是**较可能**而非已证实：两次输出的变量不止格式一个（种子、`ref_image_size`、步数、背景素材都不同），没有做过单变量对照。

---

## 9. 已知边界

- 这份 prompt 提高的是**跟随度与一致性**，不能保证逐帧精确复制动作。说明节点里也写明：「当前流程仍然是生成式重绘，而不是对原视频做传统的像素级人物分割与合成」。
- 背景只能"看起来一样"，不能保证像素级不变。
- 时间线写得再细，也需要源视频本身动作清晰、单镜头、无遮挡切换。
- 换了模型版本、LoRA 或采样器后，最佳 prompt 可能需要重调，不能假定完全迁移。

---

## 10. 快速上手：从新素材到成品 prompt

1. 量源视频：分辨率、fps、总时长、总帧数（是否落在 17k+5 网格上）。
2. 决定输出画幅与 MP，算清最终帧数与秒数（`round(秒数×24)` 再对齐网格）。
3. 把最终秒数写进首行。
4. 边看边记 12–16 拍，写成 `MM:SS.s–MM:SS.s — 动词开头的动作描述`。
5. 填 `REFERENCE ROLES`（角色物理特征 + 背景场景描述）。
6. 抄 `PRIORITIES` 四条，替换角色名与白模形态，保留手势兜底句。
7. 抄 `CONTINUITY`，把伪影清单换成你实际见过的现象。
8. 抄 `AUDIO`（无音轨则删）。
9. 接线核对：`<Picture 1>`→`ref_image_0`、`<Picture 2>`→`ref_image_1`、`<Video 1>`→`ref_video_0`；`152.audio`→`Create Video.audio`。
10. 参数核对：`ref_image_size=max`、种子设 `fixed`、`Trim duration` ≈ 输出时长、CreateVideo fps=24。
11. 先跑一次，**只改一个变量**再迭代。

---

## 附录 A：v3 参数快照

| 节点 | 类型 | 取值 |
|---|---|---|
| 115 | ResolutionSelector | `["9:16 (Portrait Widescreen)", 1, 32]` |
| 136 | MiniMaxH3ReferenceToVideo | `["", 1344, 768, 124, "max"]`（宽高由 115 连线驱动） |
| 143 | PrimitiveInt | `20`（当前未选中） |
| 144 | PrimitiveInt | `4`（当前生效） |
| 146 | PrimitiveBoolean | `true` |
| 151 | Video Slice | `[0, 14.4, false]` |
| 157 | H3FrameRateAlign | `[24]`（source_fps 由连线驱动） |
| 130 | CreateVideo | `[24, 8, "sRGB", "none"]` |
| 129 | RandomNoise | `829721249551274`，模式 `fixed` |
| 123 | KSamplerSelect | `res_multistep` |
| 124 | BasicScheduler | `["simple", 20, 1]` |
| 92 | SaveVideo | `video/DSH_test` |
| 153 | LoadImage | `绿幕奶娃.png` |
| 154 | LoadImage | `白墙室内竖屏.png` |
| 150 | LoadVideo | `chicken_dinner (1).mp4` |

工作流规模：28 节点 / 35 连线。

## 附录 B：素材文件

| 文件 | 内容 |
|---|---|
| `.dsh\milkyfrog-v3\text_138_PrimitiveStringMultiline.txt` | v3 prompt 原文（4,658 字符） |
| `.dsh\milkyfrog-v3\text_116_MarkdownNote.txt` | v3 说明节点原文 |
| `.dsh\milkyfrog-v3\analyze.py` | 结构统计脚本（可对新 prompt 重跑） |
