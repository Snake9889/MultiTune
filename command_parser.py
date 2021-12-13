# This Python file uses the following encoding: utf-8

from PyQt5.QtCore import Qt, QObject
import argparse

class TerminalParser(QObject):
    """   """
    def __init__(self, parent=None):
        super(TerminalParser, self).__init__(parent)

        self.parser = argparse.ArgumentParser(description='Startup settings for software')

        self.parser.add_argument('-bn', action='store', default='all', dest='bpm_name',
                                  help='name of bpm, like all / model, '
                                         'where model - simulated signal, and all - data from all bpms.')
        self.parser.add_argument('-mt', action='store', default='peak', dest='method_name',
                                  help='naff / peak / gass - NAFF / Peak / Gassior detection method.')
        self.parser.add_argument('-v1', action='store', default='1', dest='first_vect',
                                  help='number of decomposed singular vector for the first plot')
        self.parser.add_argument('-v2', action='store', default='2', dest='second_vect',
                                  help='number of decomposed singular vector for the second plot')

        self.results = self.parser.parse_args()
        self.bpm_name_parsed = self.results.bpm_name
        self.method_name_parsed = self.results.method_name
        self.v1_parsed = self.results.first_vect
        self.v2_parsed = self.results.second_vect

