from surround import Stage


class SecondStage(Stage):

    def operate(self, data, config):
        data.stage2 = "second stage"
