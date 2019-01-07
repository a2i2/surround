from surround import Stage


class FirstStage(Stage):

    def operate(self, data, config):
        data.stage = "first stage"
