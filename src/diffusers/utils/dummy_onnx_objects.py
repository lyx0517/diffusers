# This file is autogenerated by the command `make fix-copies`, do not edit.


from ..utils import DummyObject, requires_backends


class OnnxRuntimeModel(metaclass=DummyObject):
    _backends = ["onnx"]

    def __init__(self, *args, **kwargs):
        requires_backends(self, ["onnx"])

    @classmethod
    def from_config(cls, *args, **kwargs):
        requires_backends(cls, ["onnx"])

    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        requires_backends(cls, ["onnx"])
