import os

from datetime import datetime

import numpy as np
import tensorflow as tf
from tensorflow import keras
from surround import Estimator, SurroundData, Validator

class TensorboardExampleData(SurroundData):
    x_train = None
    y_train = None
    x_test = None
    y_test = None
    train_size = None
    training_history = None

class ValidateData(Validator):
    def validate(self, surround_data, config):
        if surround_data.x_test is None or surround_data.y_test is None:
            raise ValueError('x_test and y_test cannot be None!')

class Main(Estimator):
    def init_stage(self, config):
        # Setup logging for tensorboard
        logdir = "logs/scalars/" + datetime.now().strftime("%Y%m%d-%H%M%S")
        file_writer = tf.summary.create_file_writer(logdir + "/metrics")
        file_writer.set_as_default()

        # Setup callbacks for tensorboard and learning rate setting
        self.lr_callback = keras.callbacks.LearningRateScheduler(self.learning_rate_schedule)
        self.tensorboard_callback = keras.callbacks.TensorBoard(log_dir=logdir)

        model_path = os.path.join(config['models_path'], 'keras_model.json')
        weights_path = os.path.join(config['models_path'], 'keras_model.hd5')

        if os.path.exists(model_path) and os.path.exists(weights_path):
            # Load the model from the JSON file
            with open(model_path) as json_file:
                model_json = json_file.read()
                self.model = keras.models.model_from_json(model_json)

            # Load the weights from the HDF5 file
            self.model.load_weights(weights_path)
        else:
            # Create the model
            self.model = keras.models.Sequential([
                keras.layers.Dense(16, input_dim=1),
                keras.layers.Dense(1),
            ])

        # Compile the model, make ready for training
        self.model.compile(
            loss='mse',
            optimizer=keras.optimizers.SGD(),
        )

    def estimate(self, surround_data, config):
        print("Evaluating model...")
        score = self.model.evaluate(surround_data.x_test, surround_data.y_test)
        print("Score: ", score)

    def fit(self, surround_data, config):
        surround_data.training_history = self.model.fit(
            surround_data.x_train,
            surround_data.y_train,
            batch_size=surround_data.train_size,
            verbose=0,
            epochs=config['epochs'],
            validation_data=(surround_data.x_test, surround_data.y_test),
            callbacks=[self.lr_callback, self.tensorboard_callback]
        )

        print("Average loss: ", np.average(surround_data.training_history.history['loss']))

        print("Saving the model..")
        model_json = self.model.to_json()
        with open(os.path.join(config['models_path'], "keras_model.json"), "w+") as model_file:
            model_file.write(model_json)

        self.model.save_weights(os.path.join(config['models_path'], "keras_model.hd5"))
        print("Model saved!")

    def learning_rate_schedule(self, epoch):
        lr = 0.2

        if epoch > 10:
            lr = 0.02

        if epoch > 20:
            lr = 0.01

        if epoch > 50:
            lr = 0.005

        tf.summary.scalar('learning rate', data=lr, step=epoch)
        return lr
