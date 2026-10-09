# Gong_comfyui

ComfyUI 自定义节点与工作流合集，面向本地 MiniMax H3 视频生成。

作者：**宫鸿翔 (Hongxiang Gong)**

---

## 一、这是什么

本仓库只包含两样东西：

1. **两条 ComfyUI 工作流**（全部基于 MiniMax H3 的 `ref2va` 参考生视频能力）：

   | 工作流 | 作用 |
   |---|---|
   | `DSH_ref2av.json` | **正向替换**：输入「白模 + 绿幕」视频 + 人物参考图 + 背景参考图，输出「人物换到白模身上、背景替换绿幕」的成品视频，同时保留原视频的动作、节奏与运镜 |
   | `DSH_av2ref.json` | **反向生成**：输入任意成品视频，输出「白色无特征人偶 + 纯绿幕」的素材视频，动作与时长保持一致 |

2. **一个自定义节点**（本仓库唯一的原创代码）：

   | 文件 | 节点名 | 作用 |
   |---|---|---|
   | `custom_nodes/comfyui_h3_frame_align.py` | `H3 Frame Rate Align` | 把参考视频的帧序列**按源帧率重采样到 24fps 语义**，并返回与 H3 帧数网格对齐的输出帧数 |

   **为什么需要它**：H3 的 `ref_videos` 输入是一个 IMAGE 批次，本身不携带帧率信息；而 H3 内部把任何帧序列都**当作 24fps**（`FPS = 24` 是硬编码常量）。所以如果源视频是 30fps / 25fps / 60fps，模型会按 24fps 去解释它，导致参考动作被加速或减速。这个节点就是把这个问题在**工作流内部**解决掉：无论你的源视频是什么帧率，输出时长都等于源时长，动作速度也保持正确。

   > 如果你只用 24fps 的素材，理论上可以不装它，但工作流里已经连线到这个节点，建议直接安装。

**不包含**：模型文件、第三方节点、任何媒体素材。

---

## 二、安装步骤

### 1. 安装自定义节点

把 `custom_nodes/comfyui_h3_frame_align.py` 复制到你的 ComfyUI 目录下：

```
<你的 ComfyUI>/custom_nodes/comfyui_h3_frame_align.py
```

它是一个单文件节点，**不需要额外的依赖**，复制进去后**重启 ComfyUI** 即可生效。重启后在节点搜索里搜 `H3 Frame Rate Align` 或 `fps` 就能找到（分类：`model/conditioning/minimax`）。

### 2. 安装工作流

把 `workflows/` 下的两个 JSON 复制到：

```
<你的 ComfyUI>/user/default/workflows/
```

重启后（或刷新页面）在 ComfyUI 的工作流列表里就能看到 `DSH_ref2av` 与 `DSH_av2ref`。

也可以不复制文件，直接在 ComfyUI 界面里把 JSON **拖进画布**导入。

### 3. 准备模型（本仓库不提供）

两条工作流都使用 MiniMax H3 的 **ref2va** 权重，请自行下载并放到对应目录（文件名需一致）：

| 类型 | 文件名 | 放置目录 |
|---|---|---|
| Diffusion 模型 | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | `models/diffusion_models/` |
| 视频 VAE | `minimax_h3_video_vae_int8_convrot.safetensors` | `models/vae/` |
| 音频 VAE | `minimax_h3_audio_vae_fp32.safetensors` | `models/vae/` |
| 文本编码器 | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | `models/text_encoders/` |

这些是 ComfyUI 官方与 MiniMax 官方发布的模型，请从官方渠道获取（Comfy-Org 在 Hugging Face 上的 MiniMax-H3 仓库）。

### 4. 其他依赖

工作流还用到以下**本身就存在**的节点，请确认你的 ComfyUI 已具备：

- ComfyUI 核心自带的视频节点：`Load Video`、`Trim Video`（Video Slice）、`Get Video Components`、`Create Video`、`SaveVideo`
- 核心自带的 `If/Else Switch`（`ComfySwitchNode`）

---

## 三、使用流程

### 正向：白模 + 绿幕 → 成品（`DSH_ref2av`）

1. **节点 150 `Load Video`**：选择你的「白模 + 绿幕」源视频（放到 `input` 目录后在下拉框里选）。
2. **节点 153 `Load Image`**：人物参考图（三视图，接到 `<Picture 1>`）。
   - 想要人脸更清晰，建议**再补一张面部近景**接到 `ref_images.ref_image_2`，并在提示词里说明它是面部细节参考。
3. **节点 154 `Load Image`**：背景参考图（接到 `<Picture 2>`）。
4. **节点 138 的提示词**：已写好「白模→人物、绿幕→背景」的 Ref2VA 六段式提示词，标签与接线严格对应（`<Video 1>` = 源视频、`<Picture 1>` = 人物、`<Picture 2>` = 背景）。**如果你改了接线，必须同步改提示词里的标签**，否则模型会认错参考。
5. 直接运行。输出保存在 `output/video/`。

### 反向：成品 → 白模 + 绿幕（`DSH_av2ref`）

1. **节点 150 `Load Video`**：选择任意成品源视频。
2. **节点 138 的提示词**：已写好「成品→白模+绿幕」的提示词。
3. 直接运行，得到可用于正向工作流的素材。

---

## 四、参数说明

| 参数 | 位置 | 说明 |
|---|---|---|
| `megapixels` | `ResolutionSelector` | **决定实际生成分辨率**，H3 不会夹取，你填多少就生成多少。`0.4` ≈ 832×480，`1.0` ≈ 1344×736，`1.5` ≈ 1632×928。经验值：**0.98 ~ 1.2 是画质与显存的最佳区间**；再往上属于模型的未验证区间，且 `VAEDecode` 要在所有帧上解码，显存开销会陡增 |
| `ref_image_size` | `MiniMaxH3ReferenceToVideo` | `match` = 参考图缩到生成分辨率（快）；`max` = 保参考短边 2048（人物身份与背景保真更强，但明显更慢） |
| `start_time` / `duration` | `Trim Video` | 裁剪源视频。**`duration = 0` 表示不裁剪（用整段）** |
| 时长上限 | `H3 Frame Rate Align` 节点源码 | H3 训练区间为 15 秒（362 帧）以内；节点内 `TRAINED_MAX_FRAMES = 362`。源视频超出时会被截断到该上限，需要更长请自行修改该常量 |
| `Enable Lightning LoRA` | 布尔开关 | `False` = 20 步完整采样（质量优先）；`True` = 4 步 turbo LoRA（快速试跑） |

---

## 五、常见问题

**Q：为什么输出时长和我源视频一样，但动作还是被加速了？**
A：请确认工作流里的 `H3 Frame Rate Align` 节点在链路上（它的 `source_fps` 应连到 `Get Video Components` 的 `fps`）。若你手动填了帧率，请填写源视频的真实帧率。

**Q：输出被截断到 15 秒了。**
A：这是 H3 的训练上限（362 帧 @24fps）。要更长请修改节点里的 `TRAINED_MAX_FRAMES`，但超出训练区间的效果无保证。

**Q：背景中途变回绿幕了。**
A：这属于长视频的条件漂移。工作流的提示词里已在多个时间点复述背景约束；如仍有残留，可尝试把 `ref_image_size` 改为 `max`，或再补一张同背景环境的不同角度参考图。

**Q：正向工作流输出的人物不够清晰。**
A：清晰度上限主要由**参考图**决定。优先补充一张人物面部近景参考图，其次才是提高 `megapixels`。

---

## 六、许可

本仓库中的工作流与自定义节点由 **宫鸿翔 (Hongxiang Gong)** 编写并开源，可自由使用与修改。如需转载或二次分发，请保留作者署名。

工作流依赖的 MiniMax H3 模型与 ComfyUI 本体遵循其各自的许可协议，与本仓库无关。
