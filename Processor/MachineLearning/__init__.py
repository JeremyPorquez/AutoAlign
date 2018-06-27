# Contains machine learning code used to calculate target point
from sklearn.linear_model import LinearRegression
from multiprocessing import Pool
from PyQt5 import QtCore
import time
import numpy as np


class ML(object):

    class Signal(QtCore.QObject):
        prediction_finished = QtCore.pyqtSignal(list)

    def __init__(self):
        self.signal = self.Signal()
        self.LinearRegression = LinearRegression()
        # self.signal.prediction_finished.emit([self.set_data()])
        self.setupSignals()
        self.mp = False
        self.has_fitted = False
        # self.mp_goto_target()

    def setupSignals(self):
        pass
        # probably not needed?
        # self.signal.prediction_finished.connect(self.get_prediction)

    def set_train_data_X(self, data = None, transpose=False):
        # x should have format (data, feature) else need to transpose
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        if transpose:
            data = data.T
        self.data = data

    def set_train_data_Y(self,target,transpose=False):
        # target should have (data in 1 column)
        assert isinstance(target, np.ndarray)
        if transpose:
            target = target.T
        self.target = target

    def fit_train_data(self):
        self.LinearRegression.fit(self.data,self.target)
        self.has_fitted = True

    def goto_target(self):
        # print(np.random.random((1)))
        self.LinearRegression.fit(self.data)
        # prediction = self.LinearRegression.predict(self.target)
        # self.prediction = prediction
        # self.signal.prediction_finished.emit()
        # return prediction


        # while True:
        #     print('1+1')
        #     time.sleep(1)


    def mp_goto_target(self,refresh=100):
        self.run_goto_target = True
        mp = Pool()


        print('apply async')
        # result = mp.apply_async(goto_target_x,[5])
        time.sleep(1)
        print(result.get())
        # print('wait 2 seconds')
        # time.sleep(2)
        # mp.close()


        print('close')
        self.run_goto_target = False

    def predict(self,target):

        if not self.has_fitted:
            self.fit_train_data()

        if not isinstance(target, np.ndarray):
            target = np.array(target)

        prediction = self.LinearRegression.predict(target)
        self.prediction = prediction
        return prediction

    def get_prediction(self):
        return self.prediction

if __name__ == "__main__":
    ml = ML()
    data_x = np.array([[1,2,3,4,5]])
    data_y = np.array([1,2,3,4,5])
    ml.set_train_data_X(data_x,transpose=True)
    ml.set_train_data_Y(data_y,transpose=True)
    print(ml.predict([[6]]))

