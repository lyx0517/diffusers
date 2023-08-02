# Copyright 2023 Ollin Boer Bohan and The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from dataclasses import dataclass
from typing import Tuple, Union

import torch

from ..configuration_utils import ConfigMixin, register_to_config
from ..utils import BaseOutput, apply_forward_hook
from .modeling_utils import ModelMixin
from .vae import DecoderOutput, DecoderTiny, EncoderTiny


@dataclass
class AutoencoderTinyOutput(BaseOutput):
    """
    Output of AutoencoderTiny encoding method.

    Args:
        latents (`torch.Tensor`): Encoded outputs of the `Encoder`.

    """

    latents: torch.Tensor


class AutoencoderTiny(ModelMixin, ConfigMixin):
    r"""
    A tiny VAE model for encoding images into latents and decoding latent representations into images. It was distilled
    by Ollin Boer Bohan as detailed in [https://github.com/madebyollin/taesd](https://github.com/madebyollin/taesd).

    [`AutoencoderTiny`] is just wrapper around the original implementation of `TAESD` found in the above-mentioned
    repository.

    This model inherits from [`ModelMixin`]. Check the superclass documentation for its generic methods implemented for
    all models (such as downloading or saving).

    Parameters:
        in_channels (int, *optional*, defaults to 3): Number of channels in the input image.
        out_channels (int,  *optional*, defaults to 3): Number of channels in the output.
        TODO(sayakpaul): Fill rest of the docstrings.
    """
    _supports_gradient_checkpointing = True

    @register_to_config
    def __init__(
        self,
        in_channels=3,
        out_channels=3,
        encoder_block_out_channels: Tuple[int] = (64, 64, 64, 64),
        decoder_block_out_channels: Tuple[int] = (64, 64, 64, 64),
        act_fn: str = "relu",
        latent_channels: int = 4,
        upsampling_scaling_factor: int = 2,
        num_encoder_blocks: Tuple[int] = (1, 3, 3, 3),
        num_decoder_blocks: Tuple[int] = (3, 3, 3, 1),
        latent_magnitude: int = 3,
        latent_shift: float = 0.5,
        force_upcast: float = False,
        scaling_factor: float = 1.0,
    ):
        super().__init__()

        if len(encoder_block_out_channels) != len(num_encoder_blocks):
            raise ValueError("`encoder_block_out_channels` should have the same length as `num_encoder_blocks`.")
        if len(decoder_block_out_channels) != len(num_decoder_blocks):
            raise ValueError("`decoder_block_out_channels` should have the same length as `num_decoder_blocks`.")

        self.encoder = EncoderTiny(
            in_channels=in_channels,
            out_channels=latent_channels,
            num_blocks=num_encoder_blocks,
            block_out_channels=encoder_block_out_channels,
            act_fn=act_fn,
        )

        self.decoder = DecoderTiny(
            in_channels=latent_channels,
            out_channels=out_channels,
            num_blocks=num_decoder_blocks,
            block_out_channels=decoder_block_out_channels,
            upsampling_scaling_factor=upsampling_scaling_factor,
            act_fn=act_fn,
        )

        self.latent_magnitude = latent_magnitude
        self.latent_shift = latent_shift
        self.scaling_factor = scaling_factor

    def _set_gradient_checkpointing(self, module, value=False):
        if isinstance(module, (EncoderTiny, DecoderTiny)):
            module.gradient_checkpointing = value

    def scale_latents(self, x):
        """raw latents -> [0, 1]"""
        return x.div(2 * self.latent_magnitude).add(self.latent_shift).clamp(0, 1)

    def unscale_latents(self, x):
        """[0, 1] -> raw latents"""
        return x.sub(self.latent_shift).mul(2 * self.latent_magnitude)

    @apply_forward_hook
    def encode(
        self, x: torch.FloatTensor, return_dict: bool = True
    ) -> Union[AutoencoderTinyOutput, Tuple[torch.FloatTensor]]:
        output = self.encoder(x)

        if not return_dict:
            return (output,)

        return AutoencoderTinyOutput(latents=output)

    @apply_forward_hook
    def decode(self, x: torch.FloatTensor, return_dict: bool = True) -> Union[DecoderOutput, Tuple[torch.FloatTensor]]:
        output = self.decoder(x)
        # Refer to the following discussion to know why this is needed.
        # https://github.com/huggingface/diffusers/pull/4384#discussion_r1279401854
        output = output.mul_(2).sub_(1)

        if not return_dict:
            return (output,)

        return DecoderOutput(sample=output)

    def forward(
        self,
        x: torch.FloatTensor,
        return_dict: bool = True,
    ) -> Union[DecoderOutput, Tuple[torch.FloatTensor]]:
        r"""
        Args:
            sample (`torch.FloatTensor`): Input sample.
            return_dict (`bool`, *optional*, defaults to `True`):
                Whether or not to return a [`DecoderOutput`] instead of a plain tuple.
        """
        enc = self.encode(x)
        scaled_enc = self.scale_latents(enc).mul_(255).round_().byte()
        unscaled_enc = self.unscale_latents(scaled_enc)
        dec = self.decode(unscaled_enc)

        if not return_dict:
            return (dec,)
        return DecoderOutput(sample=dec)
