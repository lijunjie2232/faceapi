from pathlib import PosixPath

import cv2
import numpy as np
import torch
import torch.nn as nn
from timm.models.layers import DropPath, trunc_normal_

from .FaceRecModel import register_model


class ConvBN(torch.nn.Sequential):
    def __init__(
        self,
        in_planes,
        out_planes,
        kernel_size=1,
        stride=1,
        padding=0,
        dilation=1,
        groups=1,
        with_bn=True,
    ):
        super().__init__()
        self.add_module(
            "conv",
            torch.nn.Conv2d(
                in_planes, out_planes, kernel_size, stride, padding, dilation, groups
            ),
        )
        if with_bn:
            self.add_module("bn", torch.nn.BatchNorm2d(out_planes))
            torch.nn.init.constant_(self.bn.weight, 1)
            torch.nn.init.constant_(self.bn.bias, 0)


class Block(nn.Module):
    def __init__(self, dim, mlp_ratio=3, drop_path=0.0):
        super().__init__()
        self.dwconv = ConvBN(dim, dim, 7, 1, (7 - 1) // 2, groups=dim, with_bn=True)
        self.f1 = ConvBN(dim, mlp_ratio * dim, 1, with_bn=False)
        self.f2 = ConvBN(dim, mlp_ratio * dim, 1, with_bn=False)
        self.g = ConvBN(mlp_ratio * dim, dim, 1, with_bn=True)
        self.dwconv2 = ConvBN(dim, dim, 7, 1, (7 - 1) // 2, groups=dim, with_bn=False)
        self.act = nn.ReLU6()
        self.drop_path = DropPath(drop_path) if drop_path > 0.0 else nn.Identity()

    def forward(self, x):
        input = x
        x = self.dwconv(x)
        x1, x2 = self.f1(x), self.f2(x)
        x = self.act(x1) * x2
        x = self.dwconv2(self.g(x))
        x = input + self.drop_path(x)
        return x


class StarNet(nn.Module):
    fc_scale = 7 * 7

    def __init__(
        self,
        base_dim=32,
        depths=[3, 3, 12, 5],
        mlp_ratio=4,
        dropout=0.0,
        num_classes=1000,
        num_features=512,
        fp16=True,
        **kwargs,
    ):
        super().__init__()
        self.num_classes = num_classes
        self.in_channel = 32
        self.fp16 = fp16
        # ステム層
        self.stem = nn.Sequential(
            ConvBN(3, self.in_channel, kernel_size=3, stride=2, padding=1), nn.ReLU6()
        )
        dpr = [x.item() for x in torch.linspace(0, dropout, sum(depths))]  # 確率的深度
        # ステージを構築
        self.stages = nn.ModuleList()
        cur = 0
        for i_layer in range(len(depths)):
            embed_dim = base_dim * 2**i_layer
            down_sampler = ConvBN(self.in_channel, embed_dim, 3, 2, 1)
            self.in_channel = embed_dim
            blocks = [
                Block(self.in_channel, mlp_ratio, dpr[cur + i])
                for i in range(depths[i_layer])
            ]
            cur += depths[i_layer]
            self.stages.append(nn.Sequential(down_sampler, *blocks))
        # ヘッド
        self.norm = nn.BatchNorm2d(self.in_channel)
        self.avgpool = nn.AdaptiveAvgPool2d(1)
        # self.head = nn.Linear(self.in_channel, num_classes)
        self.head = nn.Linear(self.in_channel, num_features)
        self.features = nn.BatchNorm1d(num_features, eps=1e-05)
        self.apply(self._init_weights)
        nn.init.constant_(self.features.weight, 1.0)
        self.features.weight.requires_grad = False

    def _init_weights(self, m):
        if isinstance(m, nn.Linear or nn.Conv2d):
            trunc_normal_(m.weight, std=0.02)
            if isinstance(m, nn.Linear) and m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.LayerNorm or nn.BatchNorm2d):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)

    def forward(self, x, cuda=True):
        with torch.amp.autocast("cuda" if cuda else "cpu", enabled=self.fp16):
            x = self.stem(x)
            for stage in self.stages:
                x = stage(x)
            x = torch.flatten(self.avgpool(self.norm(x)), 1)
        return self.features(self.head(x.float() if self.fp16 else x))


@torch.no_grad()
def inference(net, img, device="cuda", to_array=True):
    use_cuda = device == "cuda"
    if img is None:
        img = np.random.randint(0, 255, size=(112, 112, 3), dtype=np.uint8)
    elif isinstance(img, str) or isinstance(img, PosixPath):
        img = cv2.imread(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (112, 112))
    img = np.transpose(img, (2, 0, 1))
    img = torch.from_numpy(img).unsqueeze(0).float()
    img.div_(255).sub_(0.5).div_(0.5)
    # net.eval()
    # ampモードで推論
    img = img.to(device)
    net = net.to(device)
    feat = net(img, cuda=use_cuda)
    try:
        feat_c = feat.cpu()
        feat = feat_c
    except:
        pass
    if to_array:
        feat = feat.numpy()
    return feat


@register_model("star_s1")
def get_s1(
    weight="model.pt",
    train=False,
    device="cpu",
):
    model = StarNet(
        base_dim=24,
        depths=[2, 2, 8, 3],
        num_features=512,
        fp16=True,
    )
    model = model.to(device)
    model.load_state_dict(torch.load(weight, map_location=device))
    return model.train() if train else model.eval()


@register_model("star_s2")
def get_s2(
    weight="model.pt",
    train=False,
    device="cpu",
):
    model = StarNet(
        base_dim=32,
        depths=[1, 2, 6, 2],
        num_features=512,
        fp16=True,
    )
    model = model.to(device)
    model.load_state_dict(torch.load(weight, map_location=device))
    return model.train() if train else model.eval()


@register_model("star_s3")
def get_s3(
    weight="model.pt",
    train=False,
    device="cpu",
):
    model = StarNet(
        base_dim=32,
        depths=[2, 2, 8, 4],
        num_features=512,
        fp16=True,
    )
    model = model.to(device)
    model.load_state_dict(torch.load(weight, map_location=device))
    return model.train() if train else model.eval()


@register_model("star_s4")
def get_s4(
    weight="model.pt",
    train=False,
    device="cpu",
):
    model = StarNet(
        base_dim=32,
        depths=[3, 3, 12, 5],
        num_features=512,
        fp16=True,
    )
    model = model.to(device)
    model.load_state_dict(torch.load(weight, map_location=device))
    return model.train() if train else model.eval()


class faceDetector:
    """
    cv2ベースの顔検出器
    """

    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def __call__(self, image):
        return self.detect(image)

    def detect(self, image):
        image = cv2.imread(image, cv2.COLOR_BGR2RGB)
        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray_image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
        )
        # 画像を切り取る
        return [image[y : y + h, x : x + w] for (x, y, w, h) in faces]


if __name__ == "__main__":
    from pathlib import Path

    ROOT = Path(__file__).parent.resolve()
    weight = ROOT / "model.pt"

    model = StarNet(
        base_dim=24,
        depths=[2, 2, 8, 3],
        num_features=512,
        fp16=True,
    ).eval()
    model.load_state_dict(torch.load(weight, map_location="cpu"))
    feat1 = inference(model, "head1.png")
    feat2 = inference(model, "head2.png")
