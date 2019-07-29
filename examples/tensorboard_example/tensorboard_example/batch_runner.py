import logging
import os
from surround import Runner, Config
from stages import TensorboardExampleData

import numpy as np

logging.basicConfig(level=logging.INFO)

class BatchRunner(Runner):
    def run(self, is_training=False):
        data = TensorboardExampleData()
        config = Config(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))

        self.assembler.set_config(config)
        self.assembler.init_assembler(True)

        data_size = config['data_size']   

        if is_training:
            train_pct = config['train_pct']
            train_size = data.train_size = int(data_size * train_pct)

            # Generate values between -1 and 1
            x = np.linspace(-1, 1, data_size)
            np.random.shuffle(x)

            # Generate data following y = 0.5x + 2 + noise
            y = 0.5 * x + 2 + np.random.normal(0, 0.05, (data_size, ))

            data.x_train, data.y_train = x[:train_size], y[:train_size]
            data.x_test, data.y_test = x[train_size:], y[train_size:]
        else:
            # Generate true values that can be used for evaluation
            data.x_test = np.linspace(-10, 10, data_size)
            data.y_test = 0.5 * data.x_test + 2

        # Run assembler
        self.assembler.run(data, is_training)
