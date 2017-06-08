import argparse
import json
import os
from os import path

import torch
import torchvision
from torch import nn
from torch import optim
from torch.autograd import Variable as PTVariable
from torch.nn import functional as F

from webdnn.backend.interface.generator import generate_descriptor
from webdnn.graph.converters.pytorch import PyTorchConverter


class Model(nn.Module):
    def __init__(self, n_units, n_out):
        super(Model, self).__init__()
        self.l1 = nn.Linear(28 * 28, n_units)
        self.l2 = nn.Linear(n_units, n_units)
        self.l3 = nn.Linear(n_units, n_out)

    def forward(self, x: PTVariable):

        x = x.view(x.size(0), -1)
        h1 = F.relu(self.l1(x))
        h2 = F.relu(self.l2(h1))
        return self.l3(h2)


def main():
    parser = argparse.ArgumentParser(description="PyTorch example: MNIST")
    parser.add_argument("--batchsize", "-b", type=int, default=100, help="Number of images in each mini-batch")
    parser.add_argument("--epoch", "-e", type=int, default=5, help="Number of sweeps over the dataset to train")
    parser.add_argument("--gpu", "-g", action="store_true", help="If true, training is executed by GPU")
    parser.add_argument("--out", "-o", default="output_pytorch", help="Directory to output the graph descriptor and sample test data")
    parser.add_argument("--unit", "-u", type=int, default=100, help="Number of hidden units")
    parser.add_argument("--data", "-d", default="./output_pytorch/dataset/mist", help="Root directory of dataset")
    args = parser.parse_args()

    print("Setting:")
    print("  GPU: {}".format(args.gpu))
    print("  # of unit: {}".format(args.unit))
    print("  # of Minibatch-size: {}".format(args.batchsize))
    print("  # of epoch: {}".format(args.epoch))
    print("")

    # setup
    model = Model(args.unit, 10)
    if args.gpu:
        model.cuda()

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
    trainset = torchvision.datasets.MNIST(root=args.data, train=True, download=True, transform=torchvision.transforms.ToTensor())
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=args.batchsize, shuffle=True, num_workers=2)
    testset = torchvision.datasets.MNIST(root=args.data, train=False, download=True, transform=torchvision.transforms.ToTensor())
    testloader = torch.utils.data.DataLoader(testset, batch_size=1, shuffle=False, num_workers=2)

    # training
    print("Training:")
    for epoch in range(args.epoch):
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            inputs, labels = data
            inputs, labels = PTVariable(inputs), PTVariable(labels)

            optimizer.zero_grad()

            loss = criterion(model(inputs), labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.data[0] * inputs.size()[0]

        print(f"  epoch:{epoch+1:d} loss:{running_loss / len(trainset):.3f}")
    print("  Training finished")
    print("")

    # save model state
    print("Save trained model state:")
    os.makedirs(path.join(args.out, "torch_model"), exist_ok=True)
    filename = path.join(args.out, "torch_model/checkpoint.pth.tar")
    torch.save({'state_dict': model.state_dict(), 'optimizer': optimizer.state_dict()}, filename)
    print(f"  {filename}")
    print("")

    # convert
    print("Convert model into WebDNN GraphDescriptor")
    converter = PyTorchConverter()
    x = PTVariable(torch.FloatTensor(1, 1, 28, 28).zero_())  # dummy data
    y = model(x)
    graph = converter.convert([x], [y])
    for backend in ["webgpu", "webassembly", "fallback"]:
        # noinspection PyBroadException
        try:
            exec_info = generate_descriptor(backend, graph)
            exec_info.save(args.out)
        except Exception as ex:
            print(f"Failed generating descriptor for backend {backend}: {str(ex)}\n")
        else:
            print(f"Backend {backend} ok\n")

    # prepare test samples
    print('Exporting test samples (for demo purpose)')
    test_samples_json = []
    test_iter = testloader.__iter__()
    for i in range(10):
        image, label = test_iter.next()
        test_samples_json.append({
            'x': image.numpy().flatten().tolist(),
            'y': label[0]
        })
    with open(os.path.join(args.out, 'test_samples.json'), 'w') as f:
        json.dump(test_samples_json, f)


if __name__ == "__main__":
    main()
