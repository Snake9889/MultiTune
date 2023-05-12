# -*- coding: utf-8 -*-

from PyQt5.QtCore import pyqtSignal, Qt, QObject, QTimer
from sklearn.decomposition import FastICA
import numpy as np
import numpy.linalg as lg
import math
from command_parser import TerminalParser


class DataDecompositor(QObject):
    """   """
    data_decomposed = pyqtSignal(object)

    def __init__(self, data_len=1024, parent=None):
        super().__init__(parent)

        self.data_len = data_len

        self.method = "PCA"
        self.filter_state = "None"

        self.dataT = None
        self.dataX = None
        self.dataZ = None
        self.dataI = None

        self.fftwT = None

        self.data_decomposed_X = None
        self.data_decomposed_Z = None

        self.warning = 0
        self.warningText = ""

        # Q - предполагаемая ошибка в центре этого раунда
        self.Q = 0.3
        # R - погрешность измерения следующего раунда
        self.R = 0.3
        # Accumulated_Error - это оценочная ошибка предыдущего раунда = накопление всех ошибок
        self.Accumulated_Error = 1
        # Начальное старое значение
        self.kalman_adc_old = 0

        self.scope = 50

    def kalman(self, adc_Value):
        """   """
        # Отслеживать, когда новое значение слишком отличается от старого значения
        if (abs(adc_Value - self.kalman_adc_old)/self.scope > 0.25):
            Old_Input = adc_Value*0.382 + self.kalman_adc_old*0.618
        else:
            Old_Input = self.kalman_adc_old

        # Общая ошибка предыдущего раунда = накопленная ошибка ^ 2 + оценочная ошибка ^ 2
        Old_Error_All = (self.Accumulated_Error**2 + self.Q**2)**(1/2)

        # R - расчетная ошибка этого раунда
        # H - доверие обеих сторон, рассчитанное с использованием среднеквадратичной ошибки
        H = Old_Error_All**2/(Old_Error_All**2 + self.R**2)

        # Старое значение + 1.00001 / (1.00001 + 0.1) * (новое значение - старое значение)
        kalman_adc = Old_Input + H * (adc_Value - Old_Input)

        # Рассчитать новую накопленную ошибку
        self.Accumulated_Error = ((1 - H)*Old_Error_All**2)**(1/2)
        # Новое значение становится старым значением
        self.kalman_adc_old = kalman_adc
        
        return (kalman_adc)

    def filtration(self, sig):
        """   """
        adc=np.empty([sig.shape[0], 1])
        for i in range(len(sig)):
            np.append(adc, self.kalman(sig[i]))

        return (adc)

    def filter(self, sig):
        """   """
        print(sig, 'sig')
        filtered_sig = np.empty([sig.shape[0], sig.shape[1]])
        for i in range (sig.shape[1]):
            adc_sig = self.filtration(np.take(sig,i,axis=1))
            #filtered_sig = np.append(filtered_sig, adc_sig, axis=1)
            filtered_sig[:, [i]] = adc_sig
        
        print(sig-filtered_sig, 'diff!!!')
        return (filtered_sig)


    def on_data_recv(self, data_source):
        """   """
        self.data_len = data_source.data_len

        self.dataT = data_source.dataT
        self.dataX = data_source.dataX
        self.dataZ = data_source.dataZ
        self.dataI = data_source.dataI

        if self.filter_state == "None":
            pass
        elif self.filter_state == "Kalman":
            self.dataX = self.filter(self.dataX)
            self.dataZ = self.filter(self.dataZ)
            self.dataI = self.filter(self.dataI)
        else:
            pass

        self.dataX = self.vect_multiplication(data_source.dataX)
        self.dataZ = self.vect_multiplication(data_source.dataZ)
        self.dataI = self.vect_multiplication(data_source.dataI)

        if self.method == "PCA":
            self.data_decomposed_X = self.SVD(self.dataX)
            self.data_decomposed_Z = self.SVD(self.dataZ)
            
        elif self.method == "ICA":
            np.random.seed(0)
            self.data_decomposed_X = self.ICA(self.dataX)
            self.data_decomposed_Z = self.ICA(self.dataZ)

        self.data_decomposed.emit(self)

    def vect_multiplication(self, Mas):
        """   """
        Mass = Mas
        Mass2 = np.delete(Mass, (0), axis=0)
        zeros = np.array([0, 0, 0, 0])
        Mass2 = np.vstack((Mass2, zeros))
        Mass = np.concatenate((Mass, Mass2), axis=1)

        Mass2 = np.delete(Mass, (0, 1), axis=0)
        zeros_2 = np.zeros((2, 8))
        Mass2 = np.vstack((Mass2, zeros_2))
        Mass = np.concatenate((Mass, Mass2), axis=1)

        return (Mass)

    def SVD(self, M1):
        """   """
        U, sng, data_decomposed = None, None, None
        U, sng, data_decomposed = lg.svd(M1.T, full_matrices=False)

        return (data_decomposed.T)

    def ICA(self, M1):
        """   """
        data_decomposed = None
        ica = FastICA(n_components=16, max_iter=5000, tol=0.1)
        data_decomposed = ica.fit_transform(M1)

        return(data_decomposed)

    def method_changed(self, method):
        self.method = method

    def filter_state_changed(self, state):
        """   """
        self.filter_state = state






