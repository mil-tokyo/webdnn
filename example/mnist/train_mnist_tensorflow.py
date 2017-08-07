import argparse
import json
import os

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

from webdnn.backend import generate_descriptor
from webdnn.frontend.tensorflow import TensorFlowConverter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="output_tensorflow")
    parser.add_argument("--backends", action="append", default=["webgpu", "webassembly", "fallback"])
    args = parser.parse_args()

    session_path = os.path.join(args.out, "session")
    sample_path = os.path.join(args.out, "test_samples.json")
    data_path = os.path.join(args.out, "data")

    x = tf.placeholder(tf.float32, [None, 784])
    W = tf.Variable(tf.zeros([784, 10]))
    b = tf.Variable(tf.zeros([10]))
    y = tf.nn.softmax(tf.matmul(x, W) + b)
    t = tf.placeholder(tf.float32, [None, 10])
    loss = tf.reduce_mean(-tf.reduce_sum(t * tf.log(y), reduction_indices=[1]))
    accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(y, 1), tf.argmax(t, 1)), tf.float32))
    optimizer = tf.train.GradientDescentOptimizer(0.05).minimize(loss)

    sess = tf.Session()

    if os.path.exists(session_path):
        # -------------------------------------------------------------------------------
        # Load pretrained model

        saver = tf.train.Saver()
        saver.restore(sess, os.path.join(session_path, "session"))

    else:
        # -------------------------------------------------------------------------------
        # Train model

        mnist = input_data.read_data_sets(data_path, one_hot=True)

        tf.global_variables_initializer().run()

        for step in range(1000):
            batch_xs, batch_ys = mnist.train.next_batch(100)
            _, loss_val = sess.run([optimizer, loss], feed_dict={x: batch_xs, t: batch_ys})

            if step % 100 == 0:
                print(f"Step {step}: loss = {loss_val}")

        print(f"accuracy: {sess.run(accuracy, feed_dict={x: mnist.test.images, t: mnist.test.labels})}")

        saver = tf.train.Saver()
        saver.save(sess, os.path.join(session_path, "session"))

        with open(sample_path, "w") as f:
            json.dump([{"x": mnist.test.images[i].flatten().tolist(), "y": int(mnist.test.labels[i].argmax())} for i in range(10)], f)

    # -------------------------------------------------------------------------------
    # Convert

    webdnn_graph = TensorFlowConverter(sess, batch_size=1).convert([x], [y])

    # # When you try to convert more complex model, maybe WebDNN failed to infer the data order.
    # # In this case, you can give "data-order hints" to WebDNN graph converter.
    #
    # webdnn_graph = TensorFlowConverter(sess, batch_size=1).convert([x], [y], order_hints={
    #     x: OrderNC,
    #     W: OrderCN,
    #     b: OrderC,
    #     y: OrderNC
    # })

    for backend in args.backends:
        desc = generate_descriptor(backend, webdnn_graph)
        desc.save(args.out)


if __name__ == "__main__":
    main()
