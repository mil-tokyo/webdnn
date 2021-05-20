from PIL import Image
import os
import numpy as np
import json
import requests

import torch
from torch import nn
from torchvision.models import resnet50
import torchvision.transforms as T
from webdnn.tensor_export import serialize_tensors


class DETROnnx(nn.Module):
    """
    Demo DETR implementation.

    Demo implementation of DETR in minimal number of lines, with the
    following differences wrt DETR in the paper:
    * learned positional encoding (instead of sine)
    * positional encoding is passed at input (instead of attention)
    * fc bbox predictor (instead of MLP)
    The model achieves ~40 AP on COCO val5k and runs at ~28 FPS on Tesla V100.
    Only batch size 1 supported.
    """
    def __init__(self, num_classes, hidden_dim=256, nheads=8,
                 num_encoder_layers=6, num_decoder_layers=6):
        super().__init__()

        # create ResNet-50 backbone
        self.backbone = resnet50()
        del self.backbone.fc

        # create conversion layer
        self.conv = nn.Conv2d(2048, hidden_dim, 1)

        # create a default PyTorch transformer
        self.transformer = nn.Transformer(
            hidden_dim, nheads, num_encoder_layers, num_decoder_layers)

        # prediction heads, one extra class for predicting non-empty slots
        # note that in baseline DETR linear_bbox layer is 3-layer MLP
        self.linear_class = nn.Linear(hidden_dim, num_classes + 1)
        self.linear_bbox = nn.Linear(hidden_dim, 4)

        # output positional encodings (object queries)
        # self.query_pos_us = nn.Parameter(torch.rand(100, 1, hidden_dim))

        # spatial positional encodings
        # note that in baseline DETR we use sine positional encodings
        # self.embed_const = nn.Parameter(torch.rand(850, 1, 256)) # depends on shape of output of self.conv(x)

    def forward(self, inputs, embed_const, query_pos_us):
        # propagate inputs through ResNet-50 up to avg-pool layer
        x = self.backbone.conv1(inputs)
        x = self.backbone.bn1(x)
        x = self.backbone.relu(x)
        x = self.backbone.maxpool(x)

        x = self.backbone.layer1(x)
        x = self.backbone.layer2(x)
        x = self.backbone.layer3(x)
        x = self.backbone.layer4(x)

        # convert from 2048 to 256 feature planes for the transformer
        h = self.conv(x)

        # propagate through the transformer
        #h = self.transformer(self.embed_const + 0.1 * h.flatten(2).permute(2, 0, 1),
        #                     self.query_pos_us).transpose(0, 1)
        # query_pos_usをモデルのパラメータとして持つと、onnx変換に失敗する
        # RuntimeError: Tensors must have same number of dimensions: got 1 and 2
        # 出力機構のバグと思われる
        h = self.transformer(embed_const + 0.1 * h.flatten(2).permute(2, 0, 1),
                             query_pos_us).transpose(0, 1)
        
        # finally project transformer outputs to class labels and bounding boxes
        # pred_logits, pred_boxes
        return self.linear_class(h), self.linear_bbox(h).sigmoid()

def download_sample_image(path, url):
    if os.path.exists(path):
        return
    img = requests.get(url).content
    with open(path, "wb") as f:
        f.write(img)

def export_test_data(output_dir, model, embed_const, query_pos_us):
    im = Image.open(os.path.join(output_dir, "000000039769.jpg"))
    
    # standard PyTorch mean-std input image normalization
    transform = T.Compose([
        T.Resize(800),
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # for output bounding box post-processing
    def box_cxcywh_to_xyxy(x):
        x_c, y_c, w, h = x.unbind(1)
        b = [(x_c - 0.5 * w), (y_c - 0.5 * h),
            (x_c + 0.5 * w), (y_c + 0.5 * h)]
        return torch.stack(b, dim=1)

    def rescale_bboxes(out_bbox, size):
        img_w, img_h = size
        b = box_cxcywh_to_xyxy(out_bbox)
        b = b * torch.tensor([img_w, img_h, img_w, img_h], dtype=torch.float32)
        return b
    
    img_preprocessed = transform(im).unsqueeze(0)
    
    pred_logits, pred_boxes = model(img_preprocessed, embed_const, query_pos_us)
    serialize_tensors(os.path.join(output_dir, "expected.bin"), {
                    "input_0": img_preprocessed.numpy(),
                    "input_embed_const": embed_const.numpy(),
                    "input_query_pos_us": query_pos_us.numpy(),
                    "output_logits": pred_logits.numpy(),
                    "output_boxes": pred_boxes.numpy()})

def dump_detr(output_dir):
    os.makedirs(output_dir, exist_ok=True)

    torch.set_grad_enabled(False)
    download_sample_image(os.path.join(output_dir, "000000039769.jpg"), 'http://images.cocodataset.org/val2017/000000039769.jpg')
    state_dict = torch.hub.load_state_dict_from_url(
    url='https://dl.fbaipublicfiles.com/detr/detr_demo-da2a99e9.pth',
    map_location='cpu', check_hash=True)

    state_dict_onnx = {k:v.float() for k, v in state_dict.items()}
    H, W = 25, 34
    query_pos_us = state_dict_onnx["query_pos"].unsqueeze(1)
    embed_const = torch.cat([
        state_dict_onnx["col_embed"][:W].unsqueeze(0).repeat(H, 1, 1),
        state_dict_onnx["row_embed"][:H].unsqueeze(1).repeat(1, W, 1),
    ], dim=-1).flatten(0, 1).unsqueeze(1)
    del state_dict_onnx["row_embed"]
    del state_dict_onnx["col_embed"]
    del state_dict_onnx["query_pos"]

    detr_onnx = DETROnnx(num_classes=91)
    detr_onnx.load_state_dict(state_dict_onnx)
    detr_onnx.eval()

    img_preprocessed = torch.zeros(1, 3, 800, 1066)
    torch.onnx.export(detr_onnx, (img_preprocessed, embed_const, query_pos_us), f"{output_dir}/model.onnx",
                  verbose=True,
                  input_names=["input_0", "input_embed_const", "input_query_pos_us"],
                  output_names=["output_logits", "output_boxes"], opset_version=10)

    export_test_data(output_dir, detr_onnx, embed_const, query_pos_us)
