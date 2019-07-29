from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime

import tensorflow as tf
from tensorflow import keras

import numpy as np

data_size = 1000
train_pct = 0.8

train_size = int(data_size * train_pct)

x = np.linspace(-1, 1, data_size)
np.random.shuffle(x)

y = 0.5 * x + 2 + np.random.normal(0, 0.05, (data_size, ))

x_train, y_train = x[:train_size], y[:train_size]
x_test, y_test = x[train_size:], y[train_size:]

logdir = "logs/scalars/" + datetime.now().strftime("%Y%m%d-%H%M%S")

file_writer = tf.summary.create_file_writer(logdir + "/metrics")
file_writer.set_as_default()

def lr_schedule(epoch):
	lr = 0.2

	if epoch > 10:
		lr = 0.02
	
	if epoch > 20:
		lr = 0.01
	
	if epoch > 50:
		lr = 0.005

	tf.summary.scalar('learning rate', data=lr, step=epoch)
	return lr

lr_callback = keras.callbacks.LearningRateScheduler(lr_schedule)
tensorboard_callback = keras.callbacks.TensorBoard(log_dir=logdir)

model = keras.models.Sequential([
	keras.layers.Dense(16, input_dim=1),
	keras.layers.Dense(1),
])

model.compile(
	loss='mse', # mean squared error
	optimizer=keras.optimizers.SGD(),
)

print("Training..")

training_history = model.fit(
	x_train,
	y_train,
	batch_size=train_size,
	verbose=0,
	epochs=100,
	validation_data=(x_test, y_test),
	callbacks=[tensorboard_callback, lr_callback]
)

print("Average test loss: ", np.average(training_history.history['loss']))