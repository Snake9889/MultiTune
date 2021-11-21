
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
import numpy as np
from BPM_template import BPMTemplate


class BPMData(BPMTemplate):
    """   """

    def __init__(self, bpm_name='', parent=None):
        super(BPMData, self).__init__(bpm_name, parent)

        self.bpm_phase = 0.0;

        if bpm_name == "bpm01":
            self.bpm_phase = 0.01
        elif bpm_name == "bpm02":
            self.bpm_phase = 0.02
        elif bpm_name == "bpm03":
            self.bpm_phase = 0.03
        elif bpm_name == "bpm04":
            self.bpm_phase = 0.04
        else:
            self.bpm_phase = 0.0

        self.def_time = 1000
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_update)
        self.timer.start(self.def_time)

    def on_timer_update(self):
        """   """
        self.generate_bpm_data()
        self.data_ready.emit(self)

    def generate_bpm_data(self):
        """   """
        self.dataT = np.arange(0, self.data_len, dtype=float)
        self.dataX = np.sin(2 * np.pi * 0.25 * self.dataT + self.bpm_phase) + 2 * np.cos(2 * np.pi * 0.4 * self.dataT + self.bpm_phase * 2)  # Frq = 0.25 + Frq = 0.4
        self.dataZ = np.exp(-1 * 0.15 * 10.0e-8 * self.dataT * self.dataT) * np.cos(2 * np.pi * 0.1 * self.dataT + self.bpm_phase)  # Frq = 0.1, dec = 0.15
        self.dataI = np.ones(self.data_len)
        self.dataX = self.dataX + 0.3 * np.random.normal(size=self.data_len)  # 30% noise
        self.dataZ = self.dataZ + 0.1 * np.random.normal(size=self.data_len)  # 10% noise

    def force_data_ready(self, signature):
        """   """
        super().force_data_ready(signature)
