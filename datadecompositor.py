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
        super(DataDecompositor, self).__init__(parent)

        self.data_len = data_len

        self.method = "PCA"
        self.filter_state = "None"

        self.dataT = None
        self.dataX = None
        self.dataZ = None
        self.dataI = None

        self.fftwT = None

        # self.data_to_process = None
        # self.sng = None
        # self.U = None
        self.data_decomposed_X = None
        self.data_decomposed_Z = None

        self.warning = 0
        self.warningText = ""

    def on_data_recv(self, data_source):
        """   """
        self.data_len = data_source.data_len

        self.dataT = data_source.dataT
        self.dataX = data_source.dataX
        self.dataZ = data_source.dataZ
        self.dataI = data_source.dataI

        self.dataX = self.vect_multiplication(data_source.dataX)
        self.dataZ = self.vect_multiplication(data_source.dataZ)
        self.dataI = self.vect_multiplication(data_source.dataI)

        # if self.type_to_process == 'X':
            # self.data_to_process = self.dataX
        # elif self.type_to_process == 'Z':
            # self.data_to_process = self.dataZ
        # else:
            # return

        if self.method == "PCA":
            self.data_decomposed_X = self.SVD(self.dataX)
            self.data_decomposed_Z = self.SVD(self.dataZ)
        elif self.method == "ICA":
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
        U, sng, data_decomposed = lg.svd(M1.T)

        return (data_decomposed)

    def ICA(self, M1):
        """   """
        data_decomposed = None
        ica = FastICA(n_components=16)
        data_decomposed = ica.fit_transform(M1)

        return(data_decomposed)

    def method_changed(self, method):
        self.method = method

    def filter_state_changed(self, state):
        """   """
        self.filter_state = state






