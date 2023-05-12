# -*- coding: utf-8 -*-

from PyQt5.QtCore import pyqtSignal, Qt, QObject, QTimer
import numpy as np
import math
from command_parser import TerminalParser


class DataProcessor(QObject):
    """   """
    data_processed = pyqtSignal(object)

    def __init__(self, data_vector=1, data_len=1024, parent=None):
        super().__init__(parent)

        #self.type_to_process = data_type
        argument_parser = TerminalParser()

        self.windowType = 'None'
        self.data_len = data_len
        self.algType = argument_parser.method_name_parsed
        self.bpm = argument_parser.bpm_name_parsed
        self.vect_num = int(data_vector)
        self.window = None

        self.regen_wind(self.windowType)

        self.left_bound = 0.05
        self.right_bound = 0.3
        self.boards = None

        self.dataT = None
        self.dataX = None
        self.dataZ = None
        self.dataI = None

        self.fftwT = None

        self.data_to_process_X = None
        self.data_to_process_Z = None
        self.fftw_to_process_X = None
        self.fftw_to_process_Z = None

        self.alpha = None
        self.falpha = None

        self.frq_founded_X = 0.0
        self.frq_founded_Z = 0.0


        self.warning = 0
        self.warningText = ""

    def on_wind_changed(self, windowType):
        """   """
        self.windowType = windowType
        self.regen_wind(self.windowType)

    def on_method_changed(self, algType):
        """   """
        self.algType = algType

    def on_vector_changed(self, vector_num):
        """   """
        self.vect_num = int(vector_num)

    def on_boards_changed(self, boards_dict):
        """   """
        self.boards = boards_dict
        self.left_bound = self.boards.get("lboard", 0.1)
        self.right_bound = self.boards.get("rboard", 0.5)

        #self.data_processed.emit(self)

    def regen_wind(self, windowType):
        """   """
        if windowType == 'None':
            self.window = np.ones(self.data_len)
        if windowType == 'Hann':
            self.window = np.hanning(self.data_len)
        if windowType == 'Hamming':
            self.window = np.hamming(self.data_len)

    def on_data_recv(self, data_decompositor):
        """   """
        self.data_len = data_decompositor.data_len

        self.regen_wind(self.windowType)

        self.dataT = data_decompositor.dataT
        self.dataX = data_decompositor.data_decomposed_X
        self.dataZ = data_decompositor.data_decomposed_Z
        self.dataI = data_decompositor.dataI

        self.data_to_process_X = self.dataX[ :, self.vect_num - 1]
        self.data_to_process_Z = self.dataZ[ :, self.vect_num - 1]

        # if self.type_to_process == 'X':
            # self.data_to_process = self.dataX
        # elif self.type_to_process == 'Z':
            # self.data_to_process = self.dataZ
        # else:
            # return

        self.data_to_process_X = self.window_adding(self.data_to_process_X)
        self.data_to_process_Z = self.window_adding(self.data_to_process_Z)

        # if self.bpm == "all":
            # self.fftwT = np.fft.rfftfreq(self.data_len, 1.0/4)
            # self.fftwT = self.fftwT[0:int(len(self.fftwT)/4)]
            # self.fftw_to_process = np.abs(np.fft.rfft(self.data_to_process - np.mean(self.data_to_process))) / self.data_len
            # self.fftw_to_process = self.fftw_to_process[0:int(len(self.fftw_to_process)/4)]

        # else:
            # self.fftwT = np.fft.rfftfreq(self.data_len, 1.0)
            # self.fftw_to_process = np.abs(np.fft.rfft(self.data_to_process - np.mean(self.data_to_process))) / self.data_len
        self.fftwT = np.fft.rfftfreq(self.data_len, 1.0)
        self.fftw_to_process_X = self.fftw_creating(self.data_to_process_X)
        self.fftw_to_process_Z = self.fftw_creating(self.data_to_process_Z)

        if self.algType == 'None':
            self.frq_founded = 0.0
            self.warning = 0
            self.warningText = 'OK!'

        if self.algType == 'Peak':
            self.frq_founded_X = self.on_peak_method(self.fftw_to_process_X)
            self.frq_founded_Z = self.on_peak_method(self.fftw_to_process_Z)

        if self.algType == 'Gassior':
            self.frq_founded_X = self.on_gassior_method(self.fftw_to_process_X)
            self.frq_founded_Z = self.on_gassior_method(self.fftw_to_process_Z)

        if self.algType == 'Naff':
            self.frq_founded_X = self.on_naff_method(self.fftw_to_process_X, self.data_to_process_X)
            self.frq_founded_Z = self.on_naff_method(self.fftw_to_process_Z, self.data_to_process_Z)

        self.data_processed.emit(self)

    def window_adding(self, data):
        """   """
        data = data * self.window
        return data

    def fftw_creating(self, data):
        """   """
        fftw_data = None
        fftw_data = np.abs(np.fft.rfft(data - np.mean(data))) / self.data_len
        return fftw_data

    def on_peak_method(self, data):
        """   """
        left_ind = math.floor(self.data_len * self.left_bound)
        right_ind = math.ceil(self.data_len * self.right_bound)

        tmp_t = self.fftwT[left_ind: right_ind]
        tmp_x = data[left_ind: right_ind]

        ind = np.argmax(tmp_x)

        self.frq_founded = tmp_t[ind]
        self.warning = 0
        self.warningText = 'OK!'

        return self.frq_founded

    def on_gassior_method(self, data):
        """   """
        left_ind = math.floor(self.data_len * self.left_bound)
        right_ind = math.ceil(self.data_len * self.right_bound)

        tmp_t = self.fftwT[left_ind: right_ind]
        tmp_x = data[left_ind: right_ind]

        if len(tmp_t) <= 1:
            tmp_t = self.fftwT[left_ind - 1: right_ind + 1]
            tmp_x = self.data[left_ind - 1: right_ind + 1]

        ind0 = np.argmax(tmp_x)
        indl = ind0 - 1
        indr = ind0 + 1

        if ind0 == 0 or ind0 == len(tmp_t) - 1:
            self.frq_founded = self.on_peak_method(data)
            self.warning = 1
            self.warningText = 'Borders!'
            print(self.warningText)
        else:
            self.frq_founded = tmp_t[ind0] + (tmp_x[indr] - tmp_x[indl]) /\
                            (2 * self.data_len * (2 * tmp_x[ind0] - tmp_x[indl] - tmp_x[indr]))
            self.warning = 0
            self.warningText = 'OK!'

        return self.frq_founded

    def on_naff_method(self, data_fftw, data):
        """   """
        left_ind = math.floor(self.data_len * self.left_bound)
        right_ind = math.ceil(self.data_len * self.right_bound)

        tmp_x = data_fftw[left_ind: right_ind]
        tmp_t = self.fftwT[left_ind: right_ind]

        if len(tmp_t) <= 1:
            tmp_t = self.fftwT[left_ind - 1: right_ind + 1]
            tmp_x = self.data_fftw[left_ind - 1: right_ind + 1]

        ind0 = np.argmax(tmp_x)

        if len(tmp_x) <= 1:
            print("Your borders too small, change it immediately!")

        if ind0 == 0:
            indl = ind0
            indr = ind0 + 1

            self.warning = 1
            self.warningText = 'Borders!'
            print(self.warningText)

        elif ind0 == len(tmp_t) - 1:
            indl = ind0 - 1
            indr = ind0

            self.warning = 1
            self.warningText = 'Borders!'
            print(self.warningText)
        else:
            indl = ind0 - 1
            indr = ind0 + 1

            self.warning = 0
            self.warningText = 'OK!'

        self.frq_founded = tmp_t[ind0]
        frql = tmp_t[indl]
        frqr = tmp_t[indr]

        alpha = np.arange(frql, frqr, 1.0e-5)
        falpha = np.copy(alpha)

        for it in range(len(alpha)):
            """   """
            omega = alpha[it]

            if False:
                ###Need to repair!
                conv_exp = np.exp(2 * np.pi * complex(0, 1) * self.dataT * omega)
                falpha[it] = np.abs(np.sum(conv_exp * self.data_to_process))
            else:
                conv_cos = np.sum(np.cos(2 * np.pi * self.dataT * omega) * data)
                conv_sin = np.sum(np.sin(2 * np.pi * self.dataT * omega) * data)
                falpha[it] = np.sqrt(conv_cos * conv_cos + conv_sin * conv_sin)

        self.alpha = alpha.copy()
        self.falpha = falpha.copy()

        ind_alpha = np.argmax(self.falpha)
        self.frq_founded = self.alpha[ind_alpha]

        return self.frq_founded
