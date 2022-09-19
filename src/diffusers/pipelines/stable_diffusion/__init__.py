from dataclasses import dataclass
from typing import List, Union

import numpy as np

import flax
import PIL
from PIL import Image

from ...schedulers.scheduling_pndm_flax import PNDMSchedulerState
from ...utils import BaseOutput, is_flax_available, is_onnx_available, is_transformers_available


@dataclass
class StableDiffusionPipelineOutput(BaseOutput):
    """
    Output class for Stable Diffusion pipelines.

    Args:
        images (`List[PIL.Image.Image]` or `np.ndarray`)
            List of denoised PIL images of length `batch_size` or numpy array of shape `(batch_size, height, width,
            num_channels)`. PIL images or numpy array present the denoised images of the diffusion pipeline.
        nsfw_content_detected (`List[bool]`)
            List of flags denoting whether the corresponding generated image likely represents "not-safe-for-work"
            (nsfw) content.
    """

    images: Union[List[PIL.Image.Image], np.ndarray]
    nsfw_content_detected: List[bool]


@flax.struct.dataclass
class FlaxStableDiffusionPipelineOutput(BaseOutput):
    """
    Output class for Stable Diffusion pipelines.

    Args:
        images (`List[PIL.Image.Image]` or `np.ndarray`)
            List of denoised PIL images of length `batch_size` or numpy array of shape `(batch_size, height, width,
            num_channels)`. PIL images or numpy array present the denoised images of the diffusion pipeline.
        nsfw_content_detected (`List[bool]`)
            List of flags denoting whether the corresponding generated image likely represents "not-safe-for-work"
            (nsfw) content.
    """

    images: Union[List[PIL.Image.Image], np.ndarray]
    nsfw_content_detected: List[bool]


@flax.struct.dataclass
class InferenceState:
    text_encoder_params: flax.core.FrozenDict
    unet_params: flax.core.FrozenDict
    vae_params: flax.core.FrozenDict
    scheduler_state: PNDMSchedulerState


if is_transformers_available():
    from .pipeline_stable_diffusion import StableDiffusionPipeline
    from .pipeline_stable_diffusion_img2img import StableDiffusionImg2ImgPipeline
    from .pipeline_stable_diffusion_inpaint import StableDiffusionInpaintPipeline
    from .safety_checker import StableDiffusionSafetyChecker

if is_transformers_available() and is_onnx_available():
    from .pipeline_stable_diffusion_onnx import StableDiffusionOnnxPipeline

if is_transformers_available() and is_flax_available():
    from .pipeline_flax_stable_diffusion import FlaxStableDiffusionPipeline
    from .safety_checker_flax import FlaxStableDiffusionSafetyChecker
