"""Resample an H3 reference-frame sequence to 24 fps.

MiniMax H3 treats its `ref_videos` image batch as a 24 fps sequence (the frame
rate is not carried on the IMAGE type at all), so a source clip at any other
frame rate is interpreted as sped up or slowed down. This node measures the real
duration from the frame count and the source frame rate, then resamples the
batch with nearest-neighbour interpolation so that 24 fps playback reproduces
the original timing, and returns the matching output frame count.
"""

import math

import torch

from comfy_api.latest import ComfyExtension, io

FPS = 24
FRAME_GRID = 17
GRID_OFFSET = 5
TRAINED_MAX_FRAMES = 362


def _output_frame_count(duration_seconds):
    requested = round(duration_seconds * FPS)
    frames = (requested // FRAME_GRID) * FRAME_GRID + GRID_OFFSET
    return min(TRAINED_MAX_FRAMES, max(GRID_OFFSET, frames))


class H3FrameRateAlign(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="H3FrameRateAlign",
            display_name="H3 Frame Rate Align",
            category="model/conditioning/minimax",
            search_aliases=["fps", "framerate", "resample", "24fps", "minimax"],
            description="Resample H3 reference frames from their real frame rate to 24 fps and return the matching output frame count.",
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


class H3FrameRateAlignExtension(ComfyExtension):
    @classmethod
    async def get_node_list(cls):
        return [H3FrameRateAlign]


async def comfy_entrypoint():
    return H3FrameRateAlignExtension()
