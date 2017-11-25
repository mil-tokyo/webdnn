import argparse

from model_keras import SqueezeNet

from webdnn.backend import generate_descriptor
from webdnn.frontend.keras import KerasConverter
from webdnn.util import console


def generate_graph():
    model = SqueezeNet()
    graph = KerasConverter(batch_size=1).convert(model)

    return model, graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', '-o', default='output_keras', help='Directory to output the graph descriptor')
    parser.add_argument("--encoding", help="name of weight encoder")
    parser.add_argument("--backend", default="webgpu,webgl,webassembly,fallback", help="backend")
    args = parser.parse_args()

    _, graph = generate_graph()

    for backend in args.backend.split(","):
        graph_exec_data = generate_descriptor(backend, graph, constant_encoder_name=args.encoding)
        graph_exec_data.save(args.out)

    console.stderr("Done.")


if __name__ == "__main__":
    main()
