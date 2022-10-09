# This Python file uses the following encoding: utf-8

import os.path
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtCore import pyqtSignal, QRectF, Qt, QSettings, QSize, QPoint
from PyQt5 import uic
import pyqtgraph as pg
from helpwidget import HelpWidget
#from phasewidget import PhaseWidget
from statuswidget import StatusWidget


class MainWindow(QMainWindow):
    """   """
    decomp_changed_str = pyqtSignal(str)
    filter_changed_str = pyqtSignal(str)
    region_changed = pyqtSignal(object)
    filter_changed_str = pyqtSignal(str)

    def __init__(self, data_source, data_proc_1, data_proc_2, settings_control, bpm_name):
        super(MainWindow, self).__init__()

        ui_path = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(ui_path, 'MainWindow_new.ui'), self)

        self.window_str = "None"
        self.filter_state = "None"
        self.bpm = bpm_name

        # if self.bpm == "all":
            # """ Replace one widget with another """
        old_statusWidget = self.statusWidget
        new_statusWidget = data_source.get_status_widget()
        new_statusWidget.setParent(self.centralwidget)

        self.ui.verticalLayout.replaceWidget(old_statusWidget, new_statusWidget)
        old_statusWidget.deleteLater()
        self.statusWidget = new_statusWidget

        # else:
            # """ Creating phase button """
            # old_Widget = self.statusWidget
            # self.phasebtn = QPushButton('Phase', self)
            # self.phasebtn.setCheckable(True)
            # self.phasebtn.setStyleSheet("QPushButton:checked {color: black; background-color: green;}")

            # self.phase_widget = PhaseWidget(os.path.join(ui_path))
            # self.phasebtn.clicked.connect(self.phase_widget.show)

            # self.ui.verticalLayout.replaceWidget(old_Widget, self.phasebtn)
            # old_Widget.deleteLater()

        self.images_list = []
        self.r1_rect = None
        self.r2_rect = None
        self.r3_rect = None
        self.r4_rect = None
        self.sng1_rect = None
        self.sng2_rect = None

        self.data_source = data_source
        self.data_proc_1 = data_proc_1
        self.data_proc_2 = data_proc_2
        self.settingsControl = settings_control

        self.data_proc_1.data_processed.connect(self.on_data_sng_1_ready)
        self.data_proc_2.data_processed.connect(self.on_data_sng_2_ready)

        self.controlWidget1.window_changed_str.connect(self.data_proc_1.on_wind_changed)
        self.controlWidget1.groupBox.setTitle("1 Controller")
        self.controlWidget1.set_str_id("Data_1")
        self.controlWidget1.scale_changed_obj.connect(self.on_scale_changing)

        self.controlWidget2.window_changed_str.connect(self.data_proc_2.on_wind_changed)
        self.controlWidget2.groupBox.setTitle("2 Controller")
        self.controlWidget2.set_str_id("Data_2")
        self.controlWidget2.scale_changed_obj.connect(self.on_scale_changing)

        self.controlWidget1.method_changed_str.connect(self.data_proc_1.on_method_changed)
        self.controlWidget1.boards_changed.connect(self.data_proc_1.on_boards_changed)
        self.controlWidget1.vector_changed_int.connect(self.data_proc_1.on_vector_changed)

        self.controlWidget2.method_changed_str.connect(self.data_proc_2.on_method_changed)
        self.controlWidget2.boards_changed.connect(self.data_proc_2.on_boards_changed)
        self.controlWidget2.vector_changed_int.connect(self.data_proc_2.on_vector_changed)

        self.decompBox.currentIndexChanged.connect(self.on_decomp_changed)
        self.filterBox.stateChanged.connect(self.on_filter_checked)

        #self.phase_widget = PhaseWidget(os.path.join(ui_path))
        #self.phasebtn.clicked.connect(self.phase_widget.show)

        self.actionSave.triggered.connect(self.on_save_button)
        self.actionRead.triggered.connect(self.on_read_button)

        self.actionExit.triggered.connect(self.on_exit_button)
        self.actionExit.triggered.connect(QApplication.instance().quit)

        self.help_widget = HelpWidget(os.path.join(ui_path, 'etc/icons/Help_1.png'))
        self.actionHelp.triggered.connect(self.help_widget.show)

        self.controlWidget1.boards_changed.connect(self.boards_1_changed)
        self.controlWidget2.boards_changed.connect(self.boards_2_changed)

        self.ui.nu_x_label.setText('\u03BD<sub>1</sub> = ')
        self.ui.nu_z_label.setText('\u03BD<sub>2</sub> = ')

        self.plots_customization()

        self.data_curve11 = self.ui.plot1.plot(pen='r', title='X_plot')
        self.data_curve12 = self.ui.plot1.plot(pen='b', title='Z_plot')
        self.data_curve21 = self.ui.plot2.plot(pen='r', title='X_plot')
        self.data_curve22 = self.ui.plot2.plot(pen='b', title='Z_plot')
        self.data_curve31 = self.ui.plot3.plot(pen='r', title='X_plot')
        self.data_curve32 = self.ui.plot3.plot(pen='b', title='Z_plot')
        self.data_curve41 = self.ui.plot4.plot(pen='r', title='X_plot')
        self.data_curve42 = self.ui.plot4.plot(pen='b', title='Z_plot')

        self.data_curve5 = self.ui.plot_sng1.plot(pen='r', title='Fourier Transform X_plot')
        self.data_curve6 = self.ui.plot_sng1.plot(pen='b', title='Fourier Transform Z_plot')
        self.data_curve7 = self.ui.plot_sng2.plot(pen='r', title='Fourier Transform X_plot')
        self.data_curve8 = self.ui.plot_sng2.plot(pen='b', title='Fourier Transform Z_plot')

    @staticmethod
    def customise_label(plot, text_item, html_str):
        """   """
        plot_vb = plot.getViewBox()
        text_item.setHtml(html_str)
        text_item.setParentItem(plot_vb)

    def plots_customization(self):
        """   """
        label_str_1 = "<span style=\"color:red; font-size:16px\">{}</span>"
        label_str_2 = "<span style=\"color:blue;font-size:16px\">{}</span>"

        plot = self.ui.plot1
        self.customize_plot(plot)
        self.customise_label(plot, pg.TextItem(), label_str_1.format("1"))

        plot = self.ui.plot2
        self.customize_plot(plot)
        self.customise_label(plot, pg.TextItem(), label_str_1.format("2"))

        plot = self.ui.plot3
        plot = self.ui.plot3
        self.customize_plot(plot)
        self.customise_label(plot, pg.TextItem(), label_str_1.format("3"))

        plot = self.ui.plot4
        self.customize_plot(plot)
        self.customise_label(plot, pg.TextItem(), label_str_1.format("4"))

        plot = self.ui.plot_sng1
        self.customize_plot(plot)
        self.customise_label(plot, pg.TextItem(), label_str_2.format("V1"))

        self.sng1 = pg.LinearRegionItem([self.controlWidget1.lboard, self.controlWidget1.rboard])
        self.sng1.setBounds([0,0.5])
        plot.addItem(self.sng1)
        self.sng1.sigRegionChangeFinished.connect(self.region_1_changed)

        plot = self.ui.plot_sng2
        self.customize_plot(plot)
        self.customise_label(plot, pg.TextItem(), label_str_2.format("V2"))

        self.sng2 = pg.LinearRegionItem([self.controlWidget2.lboard, self.controlWidget2.rboard])
        self.sng2.setBounds([0,0.5])
        plot.addItem(self.sng2)
        self.sng2.sigRegionChangeFinished.connect(self.region_2_changed)

        """ Here can be the cross-marker on plots """
        # vLine = pg.InfiniteLine(angle=90, movable=False)
        # hLine = pg.InfiniteLine(angle=0, movable=False)
        # p1.addItem(vLine, ignoreBounds=True)
        # p1.addItem(hLine, ignoreBounds=True)
        # vb = p1.vb

    # def mouseMoved(evt):
        # pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        # if p1.sceneBoundingRect().contains(pos):
            # mousePoint = vb.mapSceneToView(pos)
            # index = int(mousePoint.x())
            # if index > 0 and index < len(data1):
                # label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data1[index], data2[index]))
            # vLine.setPos(mousePoint.x())

    @staticmethod
    def customize_plot(plot):
        """   """
        plot.setBackground('w')
        plot.showAxis('top')
        plot.showAxis('right')
        plot.getAxis('top').setStyle(showValues=False)
        plot.getAxis('right').setStyle(showValues=False)
        plot.showGrid(x=True, y=True)

    def on_scale_changing(self, control_widget):
        """   """
        scale = control_widget.scale
        if control_widget.str_id == "Data_1":
            self.plot_mode(self.ui.plot_sng1, scale)
        elif control_widget.str_id == "Data_2":
            self.plot_mode(self.ui.plot_sng2, scale)
        else:
            print("Error in control_widget!")

    @staticmethod
    def plot_mode(plot, scale):
        """   """
        if scale == "Normal":
            plot.setLogMode(False, False)
        if scale == 'Log_Y':
            plot.setLogMode(False, True)

    def boards_1_changed(self, dict):
        """   """
        self.sng1.setRegion([dict.get("lboard", 0.1), dict.get("rboard", 0.5)])

    def boards_2_changed(self, dict):
        """   """
        self.sng2.setRegion([dict.get("lboard", 0.1), dict.get("rboard", 0.5)])

    def region_1_changed(self):
        """   """
        self.controlWidget1.on_boards_changed_ext(self.sng1.getRegion())

    def region_2_changed(self):
        """   """
        self.controlWidget2.on_boards_changed_ext(self.sng2.getRegion())

    def on_decomp_changed(self, state):
        if state == 0:
            self.decomp_method = "PCA"
        elif state == 1:
            self.decomp_method = "ICA"
        else:
            self.decomp_method = "PCA"

        self.decomp_changed_str.emit(self.decomp_method)

    def on_filter_checked(self, state):
        """   """
        if state == Qt.Checked:
            self.filter_state = "Kalman"
        else:
            self.filter_state = "None"
        self.filter_changed_str.emit(self.filter_state)

    def on_exit_button(self):
        """   """
        print(self, ' Exiting... Bye...')

    def on_read_button(self):
        """   """
        self.settingsControl.read_settings()

    def on_save_button(self):
        """   """
        self.settingsControl.save_settings()

    def on_data1_ready(self, data_source):
        """   """
        self.data_curve11.setData(data_source.dataT, data_source.dataX[:,0])
        self.data_curve12.setData(data_source.dataT, data_source.dataZ[:,0])
        self.r1_rect = self.ui.plot1.viewRange()

    def on_data2_ready(self, data_source):
        """   """
        self.data_curve21.setData(data_source.dataT, data_source.dataX[:,1])
        self.data_curve22.setData(data_source.dataT, data_source.dataZ[:,1])
        self.r2_rect = self.ui.plot2.viewRange()

    def on_data3_ready(self, data_source):
        """   """
        self.data_curve31.setData(data_source.dataT, data_source.dataX[:,2])
        self.data_curve32.setData(data_source.dataT, data_source.dataZ[:,2])
        self.r3_rect = self.ui.plot3.viewRange()

    def on_data4_ready(self, data_source):
        """   """
        self.data_curve41.setData(data_source.dataT, data_source.dataX[:,3])
        self.data_curve42.setData(data_source.dataT, data_source.dataZ[:,3])
        self.r4_rect = self.ui.plot4.viewRange()

    def on_data_sng_1_ready(self, data_processor):
        """   """
        self.data_curve5.setData(data_processor.fftwT, data_processor.fftw_to_process_X)
        self.data_curve6.setData(data_processor.fftwT, data_processor.fftw_to_process_Z)
        self.sng1_rect = self.ui.plot_sng1.viewRange()

    def on_data_sng_2_ready(self, data_processor):
        """   """
        self.data_curve7.setData(self.data_proc_2.fftwT, self.data_proc_2.fftw_to_process_X)
        self.data_curve8.setData(self.data_proc_2.fftwT, self.data_proc_2.fftw_to_process_Z)
        self.sng2_rect = self.ui.plot_sng2.viewRange()

    def on_freq_status_1(self, data_processor):
        """   """
        if data_processor.warning == 0:
            self.ui.frq_x1.setText('{:.5f}'.format(data_processor.frq_founded_X))
            self.ui.frq_z1.setText('{:.5f}'.format(data_processor.frq_founded_Z))
        elif data_processor.warning == 1:
            self.ui.frq_x1.setText(data_processor.warningText)
            self.ui.frq_z1.setText(data_processor.warningText)
        else:
            self.ui.frq_x1.setText('Unexpected value!')
            self.ui.frq_z1.setText('Unexpected value!')

    def on_freq_status_2(self, data_processor):
        """   """
        if data_processor.warning == 0:
            self.ui.frq_x2.setText('{:.5f}'.format(data_processor.frq_founded_X))
            self.ui.frq_z2.setText('{:.5f}'.format(data_processor.frq_founded_Z))
        elif data_processor.warning == 1:
            self.ui.frq_x2.setText(data_processor.warningText)
            self.ui.frq_z2.setText(data_processor.warningText)
        else:
            self.ui.frq_x2.setText('Unexpected value!')
            self.ui.frq_z2.setText('Unexpected value!')

    def save_settings(self):
        """   """
        settings = QSettings()
        settings.beginGroup(self.bpm)
        settings.beginGroup("Plots")
        settings.setValue("1_zoom", self.r1_rect)
        settings.setValue("2_zoom", self.r2_rect)
        settings.setValue("3_zoom", self.r3_rect)
        settings.setValue("4_zoom", self.r4_rect)
        settings.setValue("sng1_zoom", self.sng1_rect)
        print(self.sng1_rect)
        settings.setValue("sng2_zoom", self.sng2_rect)
        print(self.sng2_rect)
        settings.setValue('size', self.size())
        settings.setValue('pos', self.pos())
        settings.endGroup()
        settings.endGroup()
        settings.sync()

    def read_settings(self):
        """   """
        rect_def = [[0, 0.5], [0, 0.1]]
        settings = QSettings()
        settings.beginGroup(self.bpm)
        settings.beginGroup("Plots")
        self.r1_rect = settings.value("1_zoom", rect_def)
        self.r2_rect = settings.value("2_zoom", rect_def)
        self.r3_rect = settings.value("3_zoom", rect_def)
        self.r4_rect = settings.value("4_zoom", rect_def)
        self.sng1_rect = settings.value("sng1_zoom", rect_def)
        self.sng2_rect = settings.value("sng2_zoom", rect_def)
        self.resize(settings.value('size', QSize(500, 500)))
        self.move(settings.value('pos', QPoint(60, 60)))
        settings.endGroup()
        settings.endGroup()

        self.ui.plot1.setRange(xRange=self.r1_rect[0], yRange=self.r1_rect[1])
        self.ui.plot2.setRange(xRange=self.r2_rect[0], yRange=self.r2_rect[1])
        self.ui.plot3.setRange(xRange=self.r3_rect[0], yRange=self.r3_rect[1])
        self.ui.plot4.setRange(xRange=self.r4_rect[0], yRange=self.r4_rect[1])

        self.ui.plot_sng1.setRange(xRange=self.sng1_rect[0], yRange=self.sng1_rect[1])
        print(self.sng1_rect)
        self.ui.plot_sng2.setRange(xRange=self.sng2_rect[0], yRange=self.sng2_rect[1])
        print(self.sng2_rect)
        

