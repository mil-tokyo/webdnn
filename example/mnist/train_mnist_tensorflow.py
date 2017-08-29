import argparse
import json
import os

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

from webdnn.backend import generate_descriptor
from webdnn.frontend.tensorflow import TensorFlowConverter


def setup_model(model_type: str):
    # model based on Tensorflow's Get Started
    def weight_variable(shape):
        initial = tf.truncated_normal(shape, stddev=0.1)
        return tf.Variable(initial)

    def bias_variable(shape):
        initial = tf.constant(0.1, shape=shape)
        return tf.Variable(initial)

    def conv2d(x, W):
        return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

    def max_pool_2x2(x):
        return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                              strides=[1, 2, 2, 1], padding='SAME')

    x = tf.placeholder(tf.float32, [None, 784])
    if model_type == "fc":
        W = tf.Variable(tf.zeros([784, 10]))
        b = tf.Variable(tf.zeros([10]))
        y = tf.nn.softmax(tf.matmul(x, W) + b)
    elif model_type == "conv":
        W_conv1 = weight_variable([5, 5, 1, 32])
        b_conv1 = bias_variable([32])
        x_image = tf.reshape(x, [-1, 28, 28, 1])

        h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
        h_pool1 = max_pool_2x2(h_conv1)

        W_conv2 = weight_variable([5, 5, 32, 64])
        b_conv2 = bias_variable([64])

        h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
        h_pool2 = max_pool_2x2(h_conv2)

        W_fc1 = weight_variable([7 * 7 * 64, 1024])
        b_fc1 = bias_variable([1024])

        h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

        W_fc2 = weight_variable([1024, 10])
        b_fc2 = bias_variable([10])

        y = tf.nn.softmax(tf.matmul(h_fc1, W_fc2) + b_fc2)
    else:
        raise NotImplementedError
    t = tf.placeholder(tf.float32, [None, 10])
    loss = tf.reduce_mean(-tf.reduce_sum(t * tf.log(y), reduction_indices=[1]))
    accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(y, 1), tf.argmax(t, 1)), tf.float32))
    optimizer = tf.train.AdamOptimizer(1e-4).minimize(loss)

    return x, y, t, loss, accuracy, optimizer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="fc", choices=["fc", "conv"])
    parser.add_argument("--out", default="output_tensorflow")
    parser.add_argument("--backends", action="append", default=["webgpu", "webgl", "webassembly", "fallback"])
    args = parser.parse_args()

    session_path = os.path.join(args.out, "session")
    sample_path = os.path.join(args.out, "test_samples.json")
    data_path = os.path.join(args.out, "data")

    x, y, t, loss, accuracy, optimizer = setup_model(args.model)

    sess = tf.Session()

    if os.path.exists(session_path):
        # -------------------------------------------------------------------------------
        # Load pretrained model

        saver = tf.train.Saver()
        saver.restore(sess, os.path.join(session_path, f"session_{args.model}"))

    else:
        # -------------------------------------------------------------------------------
        # Train model

        mnist = input_data.read_data_sets(data_path, one_hot=True)

        with sess.as_default():
            tf.global_variables_initializer().run()

            for step in range(1000):
                batch_xs, batch_ys = mnist.train.next_batch(100)
                _, loss_val = sess.run([optimizer, loss], feed_dict={x: batch_xs, t: batch_ys})

                if step % 100 == 0:
                    print(f"Step {step}: loss = {loss_val}")

            print(f"accuracy: {sess.run(accuracy, feed_dict={x: mnist.test.images, t: mnist.test.labels})}")

            saver = tf.train.Saver()
            saver.save(sess, os.path.join(session_path, f"session_{args.model}"))

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
