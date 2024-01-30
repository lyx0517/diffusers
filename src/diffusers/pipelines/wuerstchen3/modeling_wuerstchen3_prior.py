# Copyright (c) 2023 Dominic Rampas MIT License
# Copyright 2023 The HuggingFace Team. All rights reserved.
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


import torch

from ...configuration_utils import register_to_config
from .modeling_wuerstchen3_common import WuerstchenV3Unet


class WuerstchenV3Prior(WuerstchenV3Unet):
    @register_to_config
    def __init__(
        self,
        c_in=16,
        c_out=16,
        c_r=64,
        patch_size=1,
        c_cond=2048,
        c_hidden=[2048, 2048],
        nhead=[32, 32],
        blocks=[[8, 24], [24, 8]],
        block_repeat=[[1, 1], [1, 1]],
        level_config=["CTA", "CTA"],
        c_clip_text=1280,
        c_clip_text_pooled=1280,
        c_clip_img=768,
        c_clip_seq=4,
        kernel_size=3,
        dropout=[0.1, 0.1],
        self_attn=True,
        t_conds=["sca", "crp"],
        switch_level=[False],
    ):
        super().__init__(
            c_in=c_in,
            c_out=c_out,
            c_r=c_r,
            patch_size=patch_size,
            c_cond=c_cond,
            c_hidden=c_hidden,
            nhead=nhead,
            blocks=blocks,
            block_repeat=block_repeat,
            level_config=level_config,
            c_clip_text=c_clip_text,
            c_clip_text_pooled=c_clip_text_pooled,
            c_clip_img=c_clip_img,
            c_clip_seq=c_clip_seq,
            kernel_size=kernel_size,
            dropout=dropout,
            self_attn=self_attn,
            t_conds=t_conds,
            switch_level=switch_level,
        )

    def forward(self, x, r, clip_text, clip_text_pooled, clip_img, **kwargs):
        # Process the conditioning embeddings
        r_embed = self.gen_r_embedding(r)
        for c in self.t_conds:
            t_cond = kwargs.get(c, torch.zeros_like(r))
            r_embed = torch.cat([r_embed, self.gen_r_embedding(t_cond)], dim=1)
        clip = self.gen_c_embeddings(clip_txt_pooled=clip_text_pooled, clip_txt=clip_text, clip_img=clip_img)

        x = self.embedding(x)
        level_outputs = self._down_encode(x, r_embed, clip)
        x = self._up_decode(level_outputs, r_embed, clip)
        return self.clf(x)