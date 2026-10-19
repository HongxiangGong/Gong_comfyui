"""Resample an H3 reference-frame sequence to 24 fps, with a ~30 s cap.

Same node as `comfyui_h3_frame_align.py`; the only behavioural difference is
`TRAINED_MAX_FRAMES`, raised from 362 (15.08 s) to 719 (29.96 s). The original
file is kept untouched, so workflows that use `H3FrameRateAlign` keep their
15 s ceiling and only the `*_30s` workflows pick up the longer one.
"""

import math

import torch

from comfy_api.latest import ComfyExtension, io

FPS = 24
FRAME_GRID = 17
GRID_OFFSET = 5
TRAINED_MAX_FRAMES = 719


def _output_frame_count(duration_seconds):
    requested = round(duration_seconds * FPS)
    frames = (requested // FRAME_GRID) * FRAME_GRID + GRID_OFFSET
    return min(TRAINED_MAX_FRAMES, max(GRID_OFFSET, frames))


class H3FrameRateAlign30s(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="H3FrameRateAlign30s",
            display_name="H3 Frame Rate Align (30s)",
            category="model/conditioning/minimax",
            search_aliases=["fps", "framerate", "resample", "24fps", "minimax", "30s"],
            description="Resample H3 reference frames from their real frame rate to 24 fps and return the matching output frame count. 30 s variant, capped at 719 frames.",
            inputs=[
                io.Image.Input("images", tooltip="Reference video frames, straight from Get Video Components."),
                io.Float.Input("source_fps", default=30.0, min=0.01, max=1000.0, step=0.01),
            ],
            outputs=[
                io.Image.Output(display_name="aligned_frames"),
                io.Int.Output(display_name="frame_count"),
            ],
        )

    @classmethod
    def execute(cls, images, source_fps) -> io.NodeOutput:
        total = int(images.shape[0])
        if total == 0 or source_fps <= 0:
            raise ValueError("H3 Frame Rate Align needs at least one frame and a positive source frame rate")

        duration = total / source_fps
        output_frames = _output_frame_count(duration)

        if total == 1:
            return io.NodeOutput(images, output_frames)

        scale = output_frames / total
        indices = torch.linspace(0, total - 1, output_frames).round().to(torch.long).clamp_(0, total - 1)
        return io.NodeOutput(images[indices], output_frames)


class H3FrameRateAlign30sExtension(ComfyExtension):
    @classmethod
    async def get_node_list(cls):
        return [H3FrameRateAlign30s]


async def comfy_entrypoint():
    return H3FrameRateAlign30sExtension()
