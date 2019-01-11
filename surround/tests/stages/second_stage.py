from surround import Stage


class SecondStage(Stage):

    def operate(self, pipeline_data, config):
        pipeline_data.stage2 = "second stage"
