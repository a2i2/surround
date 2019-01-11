from surround import Stage


class FirstStage(Stage):

    def operate(self, pipeline_data, config):
        pipeline_data.stage1 = "first stage"
