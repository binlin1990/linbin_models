# -*- coding: utf-8 -*-

import tensorflow as tf
from sleep_inputdata import *
import sleep_inference
import os
import numpy as np

BATCH_SIZE = 200
LEARNING_RATE_BASE = 0.01
LEARNING_RATE_DECAY = 0.99
REGULARIZATION_RATE = 0.0001
TRAINING_STEPS = 200000
MOVING_AVERAGE_DECAY = 0.99

MODEL_SAVE_PATH = "E:\\sleep_dir\\data_mat_final_new2\\sleep_experiment\\Saved_model"
MODEL_NAME = "model_sleep.ckpt"

def train(sleep):
    # 定义输出为4维矩阵的placeholder
    x = tf.placeholder(tf.float32, [
        BATCH_SIZE,
        sleep_inference.IMAGE_SIZE,
        sleep_inference.IMAGE_SIZE,
        sleep_inference.NUM_CHANNELS],
                       name='x-input')
    y_ = tf.placeholder(tf.float32, [None, sleep_inference.OUTPUT_NODE], name='y-input')

    regularizer = tf.contrib.layers.l2_regularizer(REGULARIZATION_RATE)
    y = sleep_inference.inference(x, True, regularizer)
    global_step = tf.Variable(0, trainable=False)

    # 定义损失函数、学习率、滑动平均操作以及训练过程。
    variable_averages = tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY, global_step)
    variables_averages_op = variable_averages.apply(tf.trainable_variables())
    
    cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=y, labels=tf.argmax(y_, 1))
    cross_entropy_mean = tf.reduce_mean(cross_entropy)
    loss = cross_entropy_mean + tf.add_n(tf.get_collection('losses'))
    learning_rate = tf.train.exponential_decay(
        LEARNING_RATE_BASE,
        global_step,
        sleep.train.num_examples / BATCH_SIZE, LEARNING_RATE_DECAY,
        staircase=True)

    train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss, global_step=global_step)
    with tf.control_dependencies([train_step, variables_averages_op]):
        train_op = tf.no_op(name='train')

    # 初始化TensorFlow持久化类。
    ### add by linbin 20180404
    saver = tf.train.Saver()
    # variable_averages = tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY)
#     variables_to_restore = variable_averages.variables_to_restore()
#     saver = tf.train.Saver(variables_to_restore)
    
    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        for i in range(TRAINING_STEPS):
            xs, ys = sleep.train.next_batch(BATCH_SIZE)

            reshaped_xs = np.reshape(xs, (
                BATCH_SIZE,
                sleep_inference.IMAGE_SIZE,
                sleep_inference.IMAGE_SIZE,
                sleep_inference.NUM_CHANNELS))
            _, loss_value, step = sess.run([train_op, loss, global_step], feed_dict={x: reshaped_xs, y_: ys})

            if i % 1000 == 0:
                print("After %d training step(s), loss on training batch is %g." % (step, loss_value))
                lr = sess.run([learning_rate], feed_dict={x: reshaped_xs, y_: ys})
                print('learning rate: %.6f' % (lr[0]))
                saver.save(sess, os.path.join(MODEL_SAVE_PATH, MODEL_NAME),
                           global_step=global_step)

def main(argv=None):
    sleep = read_data_sets("sleep", one_hot=True)
    train(sleep)

if __name__ == "__main__":
        tf.app.run()