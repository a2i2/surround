from surround import Stage


class SecondStage(Stage):

    def operate(self, surround_data, config=None):
        surround_data.stage2 = "second stage"
