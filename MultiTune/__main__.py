# This Python file uses the following encoding: utf-8

from PyQt5.QtCore import QCoreApplication, QSettings, QSize
from PyQt5.QtGui import QIcon
import signal
from MultiTune.Modules.MainWindow.mainwindow import *
from MultiTune.Modules.datadecompositor import DataDecompositor
from MultiTune.Modules.dataprocessor import DataProcessor
from MultiTune.Modules.settingscontrol import SettingsControl
from MultiTune.Modules.command_parser import TerminalParser
from MultiTune.Modules.DataSources.datasources_all import BPMDataAll
from MultiTune.Modules.DataSources.datasources import BPMData

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
        data_source = BPMData()

    elif bpm_name_parsed == "all":
        # from datasources_all import BPMDataAll
        data_source = BPMDataAll()

    if data_source is None:
        print("Data source doesn't exists!!! You can't use this program!!!")
        exit()

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

    data_proc_1.data_processed.connect(mw.on_freq_status_1)
    data_proc_2.data_processed.connect(mw.on_freq_status_2)

    settingsControl.add_object(mw)
    settingsControl.add_object(mw.controlWidget1)
    settingsControl.add_object(mw.controlWidget2)
    settingsControl.add_object(data_source)
    settingsControl.read_settings()

    mw.decomp_changed_str.connect(data_decompositor.method_changed)
    mw.filter_changed_str.connect(data_decompositor.filter_state_changed)
    mw.controlWidget1.signature.connect(data_source.force_data_ready)
    mw.controlWidget2.signature.connect(data_source.force_data_ready)

    mw.show()
    sys.exit(app.exec_())
