
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
import numpy as np
from BPM_template import BPMTemplate
from statuswidget import StatusWidget


class BPMData(BPMTemplate):
    """   """

    def __init__(self, bpm_name='', parent=None):
        super(BPMData, self).__init__('model', parent)

        self.statusWidget = StatusWidget()

        self.data_len = 1024
        self.phase1 = 0.01
        self.phase2 = 0.02
        self.phase3 = 0.03
        self.phase4 = 0.04

        self.dataX = None
        self.dataZ = None
        self.dataI = None

        self.dataT = np.arange(0, self.data_len, dtype=float)

        self.def_time = 1000
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_update)
        self.timer.start(self.def_time)


    def on_timer_update(self):
        """   """

        dataX1, dataZ1, dataI1 = self.generate_bpm_data(self.phase1, self.dataT)
        dataX2, dataZ2, dataI2 = self.generate_bpm_data(self.phase2, self.dataT)
        dataX3, dataZ3, dataI3 = self.generate_bpm_data(self.phase3, self.dataT)
        dataX4, dataZ4, dataI4 = self.generate_bpm_data(self.phase4, self.dataT)

        self.dataX = self.reshaping_arrays(dataX1, dataX2, dataX3, dataX4)
        self.dataZ = self.reshaping_arrays(dataZ1, dataZ2, dataZ3, dataZ4)
        self.dataI = self.reshaping_arrays(dataI1, dataI2, dataI3, dataI4)
        self.data_ready.emit(self)

    def get_status_widget(self):
        """   """
        return self.statusWidget

    def reshaping_arrays(self, M1, M2, M3, M4):
        """   """
        print(M1.shape[0])
        newMass = np.zeros((self.data_len, 4))
        newMass[:,0] = M1
        newMass[:,1] = M2
        newMass[:,2] = M3
        newMass[:,3] = M4
        print(newMass.shape)
        return(newMass)

    def generate_bpm_data(self, phase, dataT):
        """   """

        dataX = np.sin(2 * np.pi * 0.25 * dataT + phase) + 2 * np.cos(2 * np.pi * 0.4 * dataT + phase * 2)  # Frq = 0.25 + Frq = 0.4
        dataZ = np.exp(-1 * 0.15 * 10.0e-8 * dataT * dataT) * np.cos(2 * np.pi * 0.1 * dataT + phase)  # Frq = 0.1, dec = 0.15
        dataI = np.ones(self.data_len)
        dataX = dataX + 0.3 * np.random.normal(size=self.data_len)  # 30% noise
        dataZ = dataZ + 0.4 * np.random.normal(size=self.data_len)  # 10% noise
        return(dataX, dataZ, dataI)

    def force_data_ready(self, signature):
        """   """
        super().force_data_ready(signature)
