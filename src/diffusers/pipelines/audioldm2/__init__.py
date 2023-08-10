from ...utils import (
    OptionalDependencyNotAvailable,
    is_torch_available,
    is_transformers_available,
    is_transformers_version,
)


try:
    if not (is_transformers_available() and is_torch_available() and is_transformers_version(">=", "4.27.0")):
        raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    from ...utils.dummy_torch_and_transformers_objects import (
        AudioLDMPipeline,
        Sequence2AudioMAE,
    )
else:
    from .pipeline_audioldm2 import AudioLDM2Pipeline
    from .modeling_gpt2 import Sequence2AudioMAE
