# This Python file uses the following encoding: utf-8

from PyQt5.QtCore import QCoreApplication, QSettings, QSize
from PyQt5.QtGui import QIcon
import signal
from mainwindow import *
from datadecompositor import DataDecompositor
from dataprocessor import DataProcessor
from settingscontrol import SettingsControl
from command_parser import TerminalParser
from datasources_all import BPMDataAll

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

# Allow CTRL+C and/or SIGTERM to kill us (PyQt blocks it otherwise)
signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)

if __name__ == "__main__":
    """   """
    import sys

    QCoreApplication.setOrganizationName("Denisov")
    QCoreApplication.setApplicationName("TDP")
    QSettings.setDefaultFormat(QSettings.IniFormat)

    app = QApplication(sys.argv)
    app.setStyle('Cleanlooks')

    argument_parser = TerminalParser()
    bpm_name_parsed = argument_parser.bpm_name_parsed
    v1_num_parsed = argument_parser.v1_parsed
    v2_num_parsed = argument_parser.v2_parsed
    data_source = None

    if bpm_name_parsed == "model":
        from datasources import BPMData
        data_source = BPMData()

    elif bpm_name_parsed == "all":
        from datasources_all import BPMDataAll
        data_source = BPMDataAll()

    # else:
        # from datasources_bpm import BPMData
        # data_source = BPMData(bpm_name=bpm_name_parsed)

    # if data_source is None:
        # print("Data source doesn't exists!!! You can't use this program!!!")
        # exit()


    #data_source = BPMDataAll()

    data_decompositor = DataDecompositor()
    data_proc_1 = DataProcessor(v1_num_parsed)
    data_proc_2 = DataProcessor(v2_num_parsed)
    settingsControl = SettingsControl()

    mw = MainWindow(data_source, data_proc_1, data_proc_2, settingsControl, bpm_name_parsed)
    mw.setWindowTitle('TDP ({})'.format('all'))

    icon_path = os.path.dirname(os.path.abspath(__file__))
    mw_icon = QIcon()
    mw_icon.addFile(os.path.join(icon_path, 'etc/icons/app_icon.png'), QSize(32, 32))
    mw.setWindowIcon(mw_icon)

    data_source.data_ready.connect(mw.on_data1_ready)
    data_source.data_ready.connect(mw.on_data2_ready)
    data_source.data_ready.connect(mw.on_data3_ready)
    data_source.data_ready.connect(mw.on_data4_ready)
    data_source.data_ready.connect(data_decompositor.on_data_recv)
    data_decompositor.data_decomposed.connect(data_proc_1.on_data_recv)
    data_decompositor.data_decomposed.connect(data_proc_2.on_data_recv)

    # data_source.data_ready.connect(data_proc_X.on_data_recv)
    # data_source.data_ready.connect(data_proc_Z.on_data_recv)


    settingsControl.add_object(mw)
    settingsControl.add_object(mw.controlWidget1)
    settingsControl.add_object(mw.controlWidget2)
    settingsControl.add_object(data_source)
    settingsControl.read_settings()

    data_proc_1.data_processed.connect(mw.on_freq_status_X)
    data_proc_2.data_processed.connect(mw.on_freq_status_Z)

    mw.controlWidget1.signature.connect(data_source.force_data_ready)
    mw.controlWidget2.signature.connect(data_source.force_data_ready)

    mw.show()
    sys.exit(app.exec_())
