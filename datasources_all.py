#
#
from PyQt5.QtCore import pyqtSignal, QObject, QTimer, QSettings
import numpy as np
import pycx4.qcda as cda
from BPM_template import BPMTemplate
from datasources_bpm import BPMData
from statuswidget import StatusWidget

class BPMDataAll(BPMTemplate):
    """   """

    """Default time for timer in ms"""
    DEFAULT_TIME = 5*1000
    """Control for hash"""
    control = (1, 1, 1, 1)
    """BPM name"""
    bpm = "all"
    """istart type"""
    istart_work = (0, 0, 0, 0)

    def __init__(self, bpm_name='', parent=None):
        super(BPMDataAll, self).__init__("bpm_all", parent)

        self.hash = [0, 0, 0, 0]
        self.l = [0, 0, 0, 0]
        self.istart = [1, 1, 1, 1]
        self.particles = "e+"

        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_update)
        self.def_time = self.DEFAULT_TIME

        self.statusWidget = StatusWidget()
        self.no_data(self.statusWidget.status_1)
        self.no_data(self.statusWidget.status_2)
        self.no_data(self.statusWidget.status_3)
        self.no_data(self.statusWidget.status_4)

        self.BPM1 = BPMData("bpm01")
        self.BPM2 = BPMData("bpm02")
        self.BPM3 = BPMData("bpm03")
        self.BPM4 = BPMData("bpm04")

        self.statusWidget.particles_type.currentIndexChanged.connect(self.on_particles_checked)

        self.BPM1.data_ready.connect(self.on_data_ready)
        self.BPM2.data_ready.connect(self.on_data_ready)
        self.BPM3.data_ready.connect(self.on_data_ready)
        self.BPM4.data_ready.connect(self.on_data_ready)

    def get_status_widget(self):
        """   """
        return self.statusWidget

    def on_particles_checked(self, state):
        """   """
        if state == 0:
            self.particles = "e-"

        elif state == 1:
            self.particles = "e+"

        else:
            pass

    def on_data_ready(self, BPM):
        """   """
        print(BPM.bpm_name)
        self.bpm_name = BPM.bpm_name
        if self.hash == [0, 0, 0, 0]:
            self.timer.start(self.def_time)

        print("time")

        if self.bpm_name == "bpm01":
            self.hash[0] = self.hash[0] + 1
            self.istart[0] = BPM.istart

        elif self.bpm_name == "bpm02":
            self.hash[1] = self.hash[1] + 1
            self.istart[1] = BPM.istart

        elif self.bpm_name == "bpm03":
            self.hash[2] = self.hash[2] + 1
            self.istart[2] = BPM.istart

        elif self.bpm_name == "bpm04":
            self.hash[3] = self.hash[3] + 1
            self.istart[3] = BPM.istart

        else:
            pass

        if (self.hash[0], self.hash[1], self.hash[2], self.hash[3]) == self.control:
            self.everyting_ok(self.statusWidget.status_1)
            self.len_check()

    def len_check(self):
        """   """
        self.l = [len(self.BPM1.dataT), len(self.BPM2.dataT), len(self.BPM3.dataT), len(self.BPM4.dataT)]

        if all(self.l[i] == self.l[i+1] for i in range(len(self.l)-1)):
            self.everyting_ok(self.statusWidget.status_2)
            self.start_type_check()

        else:
            self.hash = [0, 0, 0, 0]
            self.statusWidget.status_2.setToolTip("Lengths of arrays from BPM-s are different")
            self.statusWidget.status_2.setStyleSheet("QLabel{background-color: red; border: 1px solid black; border-radius: 10px;}")
            pass

    def start_type_check(self):
        """   """
        if (self.istart[0], self.istart[1], self.istart[2], self.istart[3]) == self.istart_work:
            self.everyting_ok(self.statusWidget.status_3)
            self.reshaping_data()

        else:
            self.statusWidget.status_3.setToolTip("Types of start for diff. BPM's are different")
            self.statusWidget.status_2.setStyleSheet("QLabel{background-color: red; border: 1px solid black; border-radius: 10px;}")
            pass

    def on_timer_update(self):
        """   """
        if self.hash == [0, 0, 0, 0]:
            self.no_data(self.statusWidget.status_1)
            self.statusWidget.status_4.setToolTip("No connection to server")
            self.statusWidget.status_4.setStyleSheet("QLabel{background-color: red; border: 1px solid black; border-radius: 10px;}")

        else:
            self.statusWidget.status_1.setToolTip("Some of BPM's send data too frequently or send nothing")
            self.statusWidget.status_1.setStyleSheet("QLabel{background-color: red; border: 1px solid black; border-radius: 10px;}")
            self.everyting_ok(self.statusWidget.status_4)
        self.hash = [0, 0, 0, 0]
        self.l = [0, 0, 0, 0]
        pass

    def reshaping_data(self):
        """   """
        self.dataT = np.arange(0, len(self.BPM1.dataT) * 4, dtype=float)
        self.data_len = len(self.dataT)

        if self.particles == "e-":
            self.dataX = self.reshaping_arrays(self.BPM4.dataX, self.BPM1.dataX, self.BPM2.dataX, self.BPM3.dataX)
            self.dataZ = self.reshaping_arrays(self.BPM4.dataZ, self.BPM1.dataZ, self.BPM2.dataZ, self.BPM3.dataZ)
            self.dataI = self.reshaping_arrays(self.BPM4.dataI, self.BPM1.dataI, self.BPM2.dataI, self.BPM3.dataI)

        elif self.particles == "e+":
            self.dataX = self.reshaping_arrays(self.BPM3.dataX, self.BPM2.dataX, self.BPM1.dataX, self.BPM4.dataX)
            self.dataZ = self.reshaping_arrays(self.BPM3.dataZ, self.BPM2.dataZ, self.BPM1.dataZ, self.BPM4.dataZ)
            self.dataI = self.reshaping_arrays(self.BPM3.dataI, self.BPM2.dataI, self.BPM1.dataI, self.BPM4.dataI)

        else:
            pass

        self.everyting_ok(self.statusWidget.status_4)
        self.data_ready.emit(self)
        self.hash = [0, 0, 0, 0]

    def reshaping_arrays(self, M1, M2, M3, M4):
        """   """
        newMass = np.zeros(len(M1)*4)
        for i in range(len(M1)):
            newMass[4*i + 0] = M1[i]
            newMass[4*i + 1] = M2[i]
            newMass[4*i + 2] = M3[i]
            newMass[4*i + 3] = M4[i]

        return(newMass)

    def everyting_ok(self, label):
        """   """
        label.setToolTip("Everything alright")
        label.setStyleSheet("QLabel{background-color: green; border: 1px solid black; border-radius: 10px;}")

    def no_data(self, label):
        """   """
        label.setToolTip("Data didn't come")
        label.setStyleSheet("QLabel{background-color: blue; border: 1px solid black; border-radius: 10px;}")

    def read_settings(self):
        """   """
        settings = QSettings()
        settings.beginGroup(self.bpm)
        self.particles = settings.value("particles", "e-")
        settings.endGroup()

        self.statusWidget.particles_type.setCurrentText(self.particles)

    def save_settings(self):
        """   """
        settings = QSettings()
        settings.beginGroup(self.bpm)
        settings.setValue("particles", self.particles)
        settings.endGroup()
        print("Saved!!!!!")
        settings.sync()
