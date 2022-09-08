
from PyQt5.QtCore import pyqtSignal, QObject, QTimer, QSettings
import numpy as np
from BPM_template import BPMTemplate
from statuswidget import StatusWidget


class BPMData(BPMTemplate):
    """   """

    def __init__(self, bpm_name='', parent=None):
        super(BPMData, self).__init__('model', parent)

        self.statusWidget = StatusWidget()

        self.data_len = 1024

        self.mu, self.sigma = 0, 1
        self.a0 = 1
        self.a1 = 0.8
        self.a2 = 0.5
        self.w0 = 0.181
        self.w1 = 0.176
        self.w2 = 0.02
        self.k = 0.0000005

        # self.phase1 = 0.00101
        # self.phase2 = 0.00425
        # self.phase3 = 0.0085
        # self.phase4 = 0.01275
        self.phase = np.array([0.00101, 0.00425, 0.0085, 0.01275])
        self.n_amp = np.array([0.1, 0.05, 0.09, 0.11])
        self.bn_amp = np.array([0.25, 0.3, 0.2, 0.1])

        self.dataX = None
        self.dataZ = None
        self.dataI = None

        self.dataT = np.arange(0, self.data_len, dtype=float)

        self.def_time = 8*10**3
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_update)
        self.timer.start(self.def_time)
        self.particles = "e+"
        self.bpm = bpm_name


    def on_timer_update(self):
        """   """

        dataX1, dataZ1, dataI1 = self.generate_bpm_data(self.phase[0], self.dataT, self.n_amp[0], self.bn_amp[0])
        dataX2, dataZ2, dataI2 = self.generate_bpm_data(self.phase[1], self.dataT, self.n_amp[1], self.bn_amp[1])
        dataX3, dataZ3, dataI3 = self.generate_bpm_data(self.phase[2], self.dataT, self.n_amp[2], self.bn_amp[2])
        dataX4, dataZ4, dataI4 = self.generate_bpm_data(self.phase[3], self.dataT, self.n_amp[3], self.bn_amp[3])

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

    def generate_bpm_data(self, phase, dataT, namp, bnamp):
        """   """

        dataX = np.exp(-1*self.k*dataT**2)*\
                (self.harmonic_oscillations(phase, dataT, self.a0, self.w0, namp) + \
                self.harmonic_oscillations(phase, dataT, self.a1, self.w1, namp) + \
                self.harmonic_oscillations(phase, dataT, self.a2, self.w2, namp)) + \
                [x for x in bnamp*(np.random.normal(self.mu, self.sigma, self.data_len))]

        dataZ = np.exp(-0.5*self.k*dataT**2)*\
                (self.harmonic_oscillations(phase, dataT, self.a0, self.w0, namp) + \
                1.5*self.harmonic_oscillations(phase, dataT, self.a1, self.w1, namp) + \
                3* self.harmonic_oscillations(phase, dataT, self.a2, self.w2, namp)) + \
                [x for x in bnamp*(np.random.normal(self.mu, self.sigma, self.data_len))]

        dataI = np.ones(self.data_len)

        #dataX = dataX + 0.3 * np.random.normal(size=self.data_len)  # 30% noise
        #dataZ = dataZ + 0.4 * np.random.normal(size=self.data_len)  # 10% noise
        return(dataX, dataZ, dataI)

    def harmonic_oscillations(self, phase, dataT, amp1, freq, amp2):
        """   """
        osc = (amp1 + amp2*(np.random.normal(self.mu, self.sigma, self.data_len)))*np.sin(2 * np.pi * freq * dataT + 2 * np.pi * phase)

        return(osc)

    def force_data_ready(self, signature):
        """   """
        super().force_data_ready(signature)

    def read_settings(self):
        """   """
        settings = QSettings()
        settings.beginGroup(self.bpm)
        self.particles = settings.value("particles", "e-")
        settings.endGroup()

        #self.statusWidget.particles_type.setCurrentText(self.particles)

    def save_settings(self):
        """   """
        settings = QSettings()
        settings.beginGroup(self.bpm)
        settings.setValue("particles", self.particles)
        settings.endGroup()
        print("Saved!!!!!")
        settings.sync()
