import argparse
import os
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from PIL import Image
from model import TransformerNet

MEAN = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
STD = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)


def normalize_batch(x):  # x は [0,255] -> VGG 入力へ
    return (x / 255.0 - MEAN.to(x.device)) / STD.to(x.device)


class Vgg16(torch.nn.Module):
    def __init__(self):
        super().__init__()
        vgg = models.vgg16(weights=models.VGG16_Weights.DEFAULT).features.eval()
        for p in vgg.parameters():
            p.requires_grad_(False)
        # relu1_2, relu2_2, relu3_3, relu4_3
        self.slices = torch.nn.ModuleList([vgg[0:4], vgg[4:9], vgg[9:16], vgg[16:23]])

    def forward(self, x):
        feats, h = [], x
        for s in self.slices:
            h = s(h)
            feats.append(h)
        return feats


def gram(x):
    b, c, h, w = x.shape
    f = x.view(b, c, h * w)
    return f.bmm(f.transpose(1, 2)) / (c * h * w)


def load_style(path, size, device):
    img = Image.open(path).convert("RGB").resize((size, size))
    return transforms.ToTensor()(img).mul(255).unsqueeze(0).to(device)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True, help="COCO train2014 親ディレクトリ（ImageFolder形式）")
    p.add_argument("--style-image", required=True)
    p.add_argument("--out", required=True, help=".pth 出力先")
    p.add_argument("--size", type=int, default=256)
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--batch", type=int, default=4)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--content-weight", type=float, default=1e5)
    p.add_argument("--style-weight", type=float, default=1e10)
    p.add_argument("--base", type=int, default=16)  # 既定 = light
    p.add_argument("--num-res", type=int, default=3)
    p.add_argument("--end-k", type=int, default=3)
    args = p.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    tfm = transforms.Compose([
        transforms.Resize(args.size), transforms.CenterCrop(args.size),
        transforms.ToTensor(), transforms.Lambda(lambda x: x.mul(255)),
    ])
    loader = DataLoader(datasets.ImageFolder(args.dataset, tfm),
                        batch_size=args.batch, shuffle=True, num_workers=4, drop_last=True)

    net = TransformerNet(base=args.base, num_res=args.num_res, end_k=args.end_k).to(device).train()
    opt = torch.optim.Adam(net.parameters(), args.lr)
    vgg = Vgg16().to(device)
    style = load_style(args.style_image, args.size, device)
    style_grams = [gram(f) for f in vgg(normalize_batch(style))]

    step = 0
    for epoch in range(args.epochs):
        for x, _ in loader:
            x = x.to(device)
            opt.zero_grad()
            y = net(x)
            fx, fy = vgg(normalize_batch(x)), vgg(normalize_batch(y.clamp(0, 255)))
            content = args.content_weight * F.mse_loss(fy[1], fx[1])  # relu2_2
            style_loss = 0.0
            for fyl, sg in zip(fy, style_grams):
                style_loss = style_loss + F.mse_loss(gram(fyl), sg.expand(fyl.size(0), -1, -1))
            style_loss = args.style_weight * style_loss
            (content + style_loss).backward()
            opt.step()
            if step % 200 == 0:
                print(f"e{epoch} s{step} content={content.item():.1f} style={style_loss.item():.1f}")
            step += 1
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    torch.save(net.cpu().eval().state_dict(), args.out)
    print("saved", args.out)


if __name__ == "__main__":
    main()
