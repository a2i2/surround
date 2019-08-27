from abc import ABC, abstractmethod


class Runner(ABC):
    """
    Base class for runners which are responsible for:

    - Initializing an :class:`surround.assembler.Assembler`.
    - Loading/preparing input data.
    - Running the :class:`surround.assembler.Assembler`.

    Example batch runner::

        class BatchRunner(Runner):
            def run(self, is_training=False):
                self.assembler.init_assembler(True)

                config = self.assembler.get_config()
                path = os.path.join(config["data_path"], "input.txt")
                data = AssemblyState()

                with open(path, 'r') as f:
                    for line in f:
                        # Each line needs to be processed by the pipeline
                        data.input_data = line.rstrip() + " "

                        # Start assembler to process processed data
                        self.assembler.run(data)

                print("Batch Runner: %s" % data.output_data)

    .. note:: You get a Batch Runner and Web Runner (if web requested) when
              you generate a project using the CLI tool.
    """

    def __init__(self, assembler):
        """
        :param assembler: The assembler the runner will execute
        :type assembler: :class:`surround.assembler.Assembler`
        """

        self.assembler = assembler

    @abstractmethod
    def run(self, is_training=False):
        """
        Prepare data and execute the :class:`surround.assembler.Assembler`.

        :param is_training: Run the pipeline in training mode or not
        :type is_training: bool
        """
