import numpy as np
import lfdnn

class MLP(lfdnn.Graph):
    def __init__(self,config):
        super().__init__(config)

    def construct_model(self, InputDim, OutputDim, LayerNum=1, HiddenNum=[1], LearningRate=0.05, EpochNum=1, BatchSize=None, _lambda=0.0):
        '''
            EpochNum: int, number of epochs in traning
            BatchSize: int, batch size used in SGD, default to all data
            InputDim: int, number of feature for each input data
            OutputDim: int, number of classes for output label
            LayerNum: int, number of intermediate layer
            HiddenNum: array-like, len(HiddenNum) = LayerNum, the number of nodes at each hidden layer
            LearningRate: double, learning rate in SGD
            _lambda: double, regularization parameter
        '''
        if BatchSize is None:
            BatchSize = InputDim
        self.weight = {}
        self.weight_value = {}
        self.input = lfdnn.tensor([BatchSize, InputDim], 'Input')
        self.label = lfdnn.tensor([BatchSize, OutputDim], 'Label')
        h = self.input
        for i in range(LayerNum):
            if i == 0:
                w = lfdnn.tensor([InputDim, HiddenNum[i]], 'Weight' + str(i))
                self.weight['Weight'+str(i)] = w
            else:
                w = lfdnn.tensor([HiddenNum[i-1], HiddenNum[i]], 'Weight' + str(i))
                self.weight['Weight'+str(i)] = w
            b = lfdnn.tensor([1, HiddenNum[i]],'Bias' + str(i))
            self.weight['Bias'+str(i)] = b
            h = lfdnn.add(lfdnn.matmul(h, w), b)
            h = lfdnn.sigmoid(h)
        if len(HiddenNum) > 0:
            w = lfdnn.tensor([HiddenNum[-1], OutputDim], 'OutputWeight')
        else:
            w = lfdnn.tensor([InputDim, OutputDim], 'OutputWeight')
        self.weight['OutputWeight'] = w
        b = lfdnn.tensor([1, OutputDim], 'OutputBias')
        self.weight['OutputBias'] = b
        h = lfdnn.add(lfdnn.matmul(h, w), b)
        self.out = lfdnn.softmax(h)
        self.loss = lfdnn.CE_with_logit(h, self.label)
        if _lambda > 0:
            for w in self.weight.values():
                self.loss = lfdnn.add(self.loss, lfdnn.scale(lfdnn.reduce_mean(lfdnn.product(w, w)), config['lambda']))
        self.accuracy = lfdnn.accuracy(self.out, self.label)
