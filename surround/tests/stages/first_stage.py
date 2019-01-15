from surround import Stage


class FirstStage(Stage):

    def operate(self, surround_data, config):
        surround_data.stage1 = "first stage"
