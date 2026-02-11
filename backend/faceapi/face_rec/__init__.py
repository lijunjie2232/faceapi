from ..core import _CONFIG_
from .FaceRecModel import get_model, has_model, list_models, register_model
from .StarNet import StarNet

_MODEL_ = get_model(
    _CONFIG_.MODEL_LOADER,
    weight=_CONFIG_.MODEL_PATH,
    device=_CONFIG_.MODEL_DEVICE,
    train=False,
)


__ALL__ = [
    "_MODEL_",
    "has_model",
    "get_model",
    "register_model",
    "list_models",
    "StarNet",
]
