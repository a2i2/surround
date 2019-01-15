import logging
from surround import Model, SurroundData, Surround

class TrainGaussianNB(Model):

    def __init__(self):
        self.classifier = None

    def operate(self, surround_data, config):
        self.classifier = self.fit(surround_data.data, surround_data.target, config)
        self.predict(surround_data.predict, config)

    def fit(self, data, target, config):
        from sklearn.naive_bayes import GaussianNB
        gnb = GaussianNB()
        return gnb.fit(data, target)

    def predict(self, data, config):
        print(self.classifier.predict(data))

class BasicData(SurroundData):
    data = [[0, 0], [1, 1], [3, 3], [4, 4], [5, 5]]
    target = [0, 1, 3, 4, 5]
    predict = [[4, 4]]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    surround = Surround([TrainGaussianNB()])
    surround.process(BasicData())
