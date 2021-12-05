# -*- coding: utf-8 -*-

from PyQt5.QtCore import pyqtSignal, Qt, QObject, QTimer
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

        self.dataT = None
        self.dataX = None
        self.dataZ = None
        self.dataI = None

        self.fftwT = None

        #self.data_to_process = None
        self.sng = None
        self.U = None
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

        # if self.type_to_process == 'X':
            # self.data_to_process = self.dataX
        # elif self.type_to_process == 'Z':
            # self.data_to_process = self.dataZ
        # else:
            # return

        self.data_decomposed_X = self.SVD(self.dataX)
        self.data_decomposed_Z = self.SVD(self.dataZ)

        self.data_decomposed.emit(self)

    def SVD(self, M1):
        """   """
        U, sng, data_decomposed= None
        U, sng, data_decomposed = lg.svd(M1)
        return (data_decomposed)



