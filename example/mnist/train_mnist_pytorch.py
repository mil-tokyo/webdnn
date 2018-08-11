# training part is based on PyTorch example https://github.com/pytorch/examples/blob/master/mnist/main.py

import os
import argparse
import json
import torch
import torch.autograd
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.onnx
from torchvision import datasets, transforms
import onnx

from webdnn.backend import generate_descriptor
from webdnn.frontend.onnx import ONNXConverter


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, 320)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)


def train(args, model, device, train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % 10 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                       100. * batch_idx / len(train_loader), loss.item()))


def test(args, model, device, test_loader):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.max(1, keepdim=True)[1]  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))


def output_test_samples(dataset, path):
    """
    Outputs test image for demo purpose
    """

    test_samples_json = []
    for i in range(10):
        image, label = dataset[i]
        test_samples_json.append({'x': image.numpy().flatten().tolist(), 'y': int(label)})
    with open(path, 'w') as f:
        json.dump(test_samples_json, f)


def main():
    # Training settings
    parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
    parser.add_argument('--out', '-o', default='output_pytorch',
                        help='Directory to output the graph descriptor and sample test data')
    parser.add_argument("--backend", default="webgpu,webgl,webassembly,fallback")
    args = parser.parse_args()

    training_dir = os.path.join(args.out, "pytorch_model")
    os.makedirs(training_dir, exist_ok=True)

    model_path = os.path.join(training_dir, "model.proto")

    if not os.path.exists(model_path):
        # model training part (as usual)
        torch.manual_seed(1)

        device = torch.device("cpu")

        train_loader = torch.utils.data.DataLoader(
            datasets.MNIST(os.path.join(args.out, 'data'), train=True, download=True,
                           transform=transforms.Compose([
                               transforms.ToTensor(),
                               # If input is normalized, input for WebDNN also have to be normalized with same parameter.
                               # Default of datasets.MNIST is 0=black, 1=white
                               # transforms.Normalize((0.1307,), (0.3081,))
                           ])),
            batch_size=64, shuffle=True)
        test_loader = torch.utils.data.DataLoader(
            datasets.MNIST(os.path.join(args.out, 'data'), train=False, transform=transforms.Compose([
                transforms.ToTensor(),
                # transforms.Normalize((0.1307,), (0.3081,))
            ])),
            batch_size=1000, shuffle=True)

        model = Net().to(device)
        optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.5)

        for epoch in range(1, 4):
            train(args, model, device, train_loader, optimizer, epoch)
            test(args, model, device, test_loader)

        # export model as ONNX format
        dummy_input = torch.autograd.Variable(torch.randn(1, 1, 28, 28))
        torch.onnx.export(model, dummy_input, model_path, verbose=True)

    # model conversion using WebDNN
    onnx_model = onnx.load(model_path)
    graph = ONNXConverter().convert(onnx_model)

    for backend in args.backend.split(","):
        exec_info = generate_descriptor(backend, graph)
        exec_info.save(args.out)

    # test data for demo
    output_test_samples(datasets.MNIST(os.path.join(args.out, 'data'), train=False, transform=transforms.Compose([
        transforms.ToTensor(),
        # transforms.Normalize((0.1307,), (0.3081,))
    ])), os.path.join(args.out, "test_samples.json"))


if __name__ == '__main__':
    main()
