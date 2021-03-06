# -*- coding: utf-8 -*-

import time
import math
import tensorflow as tf
import numpy as np
# from tensorflow.examples.tutorials.mnist import input_data
import sleep_inference
import sleep_train
from sleep_inputdata import *

def evaluate(sleep):
    with tf.Graph().as_default() as g:
        # 定义输出为4维矩阵的placeholder
        x = tf.placeholder(tf.float32, [
            sleep.test.num_examples,
            #LeNet5_train.BATCH_SIZE,
            sleep_inference.IMAGE_SIZE,
            sleep_inference.IMAGE_SIZE,
            sleep_inference.NUM_CHANNELS],
                           name='x-input')
        y_ = tf.placeholder(tf.float32, [None, sleep_inference.OUTPUT_NODE], name='y-input')
        validate_feed = {x: sleep.test.images, y_: sleep.test.labels}
        global_step = tf.Variable(0, trainable=False)

        regularizer = tf.contrib.layers.l2_regularizer(sleep_train.REGULARIZATION_RATE)
        y = sleep_inference.inference(x, False, regularizer)
        correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

        variable_averages = tf.train.ExponentialMovingAverage(sleep_train.MOVING_AVERAGE_DECAY)
        variables_to_restore = variable_averages.variables_to_restore()
        saver = tf.train.Saver(variables_to_restore)
        
        #n = math.ceil(mnist.test.num_examples / LeNet5_train.BATCH_SIZE)
        n = math.ceil(sleep.test.num_examples / sleep.test.num_examples)
        for i in range(n):
            with tf.Session() as sess:
                ckpt = tf.train.get_checkpoint_state(sleep_train.MODEL_SAVE_PATH)
                if ckpt and ckpt.model_checkpoint_path:
                    saver.restore(sess, ckpt.model_checkpoint_path)
                    global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
                    xs, ys = sleep.test.next_batch(sleep.test.num_examples)
                    #xs, ys = mnist.test.next_batch(LeNet5_train.BATCH_SIZE)
                    reshaped_xs = np.reshape(xs, (
                        sleep.test.num_examples,
                        #LeNet5_train.BATCH_SIZE,
                        sleep_inference.IMAGE_SIZE,
                        sleep_inference.IMAGE_SIZE,
                        sleep_inference.NUM_CHANNELS))
                    accuracy_score = sess.run(accuracy, feed_dict={x:reshaped_xs, y_:ys})
                    print("After %s training step(s), test accuracy = %g" % (global_step, accuracy_score))
                else:
                    print('No checkpoint file found')
                    return

# 主程序
def main(argv=None):
    mnist = read_data_sets("sleep", one_hot=True)
    evaluate(sleep)

    sleep = read_data_sets("sleep", one_hot=True)
    evaluate(sleep)

if __name__ == '__main__':
    main()