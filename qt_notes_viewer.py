#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 17:12:10 2020

@author: inathero
"""

from PyQt5 import QtWidgets,uic

import sys
import notes_to_icd as core


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() 
        uic.loadUi('ui/viewer.ui', self) 
        # self.pushButton.clicked.connect(self.buttonClicked)
        
        
    def buttonClicked(self):
        text = self.plainTextEdit.toPlainText().split('\n')
        self.plainTextEdit.setPlainText("Notes Exported")
 
        
app = QtWidgets.QApplication(sys.argv) 
window = Ui() 
window.show()
app.exec()