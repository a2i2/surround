# Tensorboard Example

This example shows how you can use both Keras and Tensorboard in Surround.

The model being trained is very basic, the tutorial this example is based off can be found here: https://www.tensorflow.org/tensorboard/r2/scalars_and_keras

# Run project
- Run the following commands:
    ```
    $ pip3 install -r requirements.txt
    $ surround run trainLocal
    $ tensorboard --logdir logs/scalar
    ```

- Open the link displayed in the console to see the Tensorboard visualizations.