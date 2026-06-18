import torch
import torch.nn as nn


class ConvLayer(nn.Module):
    """ReflectionPad + Conv（WebDNN は Pad reflect 対応）。"""
    def __init__(self, in_ch, out_ch, kernel_size, stride):
        super().__init__()
        self.pad = nn.ReflectionPad2d(kernel_size // 2)
        self.conv = nn.Conv2d(in_ch, out_ch, kernel_size, stride)

    def forward(self, x):
        return self.conv(self.pad(x))


class ResidualBlock(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.conv1 = ConvLayer(ch, ch, 3, 1)
        self.in1 = nn.InstanceNorm2d(ch, affine=True)
        self.conv2 = ConvLayer(ch, ch, 3, 1)
        self.in2 = nn.InstanceNorm2d(ch, affine=True)
        self.relu = nn.ReLU()

    def forward(self, x):
        residual = x
        out = self.relu(self.in1(self.conv1(x)))
        out = self.in2(self.conv2(out))
        return out + residual


class UpsampleConvT(nn.Module):
    """ConvTranspose による 2x アップサンプル（Resize op を使わず WebDNN 🟢 を保証）。"""
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.convt = nn.ConvTranspose2d(
            in_ch, out_ch, kernel_size=3, stride=2, padding=1, output_padding=1
        )

    def forward(self, x):
        return self.convt(x)


class TransformerNet(nn.Module):
    """fast-style transfer の生成器。

    既定 (base=32, num_res=5, end_k=9) は Johnson 標準構成（heavy）。
    軽量版は TransformerNet(base=16, num_res=3, end_k=3)。
    入出力は同形（[1,3,H,W] → [1,3,H,W]）。全演算子 WebDNN 対応（🟢）。
    """
    def __init__(self, base=32, num_res=5, end_k=9):
        super().__init__()
        c1, c2, c3 = base, base * 2, base * 4
        self.conv1 = ConvLayer(3, c1, end_k, 1)
        self.in1 = nn.InstanceNorm2d(c1, affine=True)
        self.conv2 = ConvLayer(c1, c2, 3, 2)
        self.in2 = nn.InstanceNorm2d(c2, affine=True)
        self.conv3 = ConvLayer(c2, c3, 3, 2)
        self.in3 = nn.InstanceNorm2d(c3, affine=True)
        self.res = nn.ModuleList([ResidualBlock(c3) for _ in range(num_res)])
        self.up1 = UpsampleConvT(c3, c2)
        self.in4 = nn.InstanceNorm2d(c2, affine=True)
        self.up2 = UpsampleConvT(c2, c1)
        self.in5 = nn.InstanceNorm2d(c1, affine=True)
        self.conv_out = ConvLayer(c1, 3, end_k, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        y = self.relu(self.in1(self.conv1(x)))
        y = self.relu(self.in2(self.conv2(y)))
        y = self.relu(self.in3(self.conv3(y)))
        for r in self.res:
            y = r(y)
        y = self.relu(self.in4(self.up1(y)))
        y = self.relu(self.in5(self.up2(y)))
        return self.conv_out(y)  # 活性化なし。後処理で[0,255]へclamp
