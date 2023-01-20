#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 17:12:10 2020

@author: inathero
"""

from PyQt5 import QtWidgets,uic

import sys
import notes_to_icd as Core



class Ui(QtWidgets.QMainWindow):
    note_sections = ''
    def __init__(self):
        super(Ui, self).__init__() 
        uic.loadUi('ui/viewer.ui', self) 
        note, self.note_sections = Core.readNote_Debug()
        self.plainTextEdit_Note.setPlainText(note)
        self.pushButton_extract.clicked.connect(self.buttonClicked)
        
        
    def buttonClicked(self):
        note = Core.set_sections_on_clips(self.plainTextEdit_Note.toPlainText())
        note, note_section_indexes = Core.recombine_for_aws(self.note_sections)
        entities = Core.request_amazon(note);
        entities_low, entities_high = Core.prune_entities_to_confidence(entities)
        entity_sections = Core.reformat_entities_to_section(entities_high,note_section_indexes)
        
        self.listWidget_HHPI.clear()
        self.listWidget_HAP.clear()
        self.listWidget_LHPI.clear()
        self.listWidget_LAP.clear()
        print("\n\nObtained from HPI:")
        for ents in entity_sections['Reason For Visit']:  
            self.listWidget_HHPI.addItem(f"{ents['Text']} ({ents['ICD10CMConcepts'][0]['Description']}) - {ents['ICD10CMConcepts'][0]['Code']}")
       
        for ents in entity_sections['Assessment']:  
            self.listWidget_HAP.addItem(f"{ents['Text']} ({ents['ICD10CMConcepts'][0]['Description']}) - {ents['ICD10CMConcepts'][0]['Code']}")
      
        entity_sections = Core.reformat_entities_to_section(entities_low,note_section_indexes)
        print("\n\nObtained from HPI:")
        for ents in entity_sections['Reason For Visit']:  
            self.listWidget_LHPI.addItem(f"{ents['Text']} ({ents['ICD10CMConcepts'][0]['Description']}) - {ents['ICD10CMConcepts'][0]['Code']}")
       
        for ents in entity_sections['Assessment']:  
            self.listWidget_LAP.addItem(f"{ents['Text']} ({ents['ICD10CMConcepts'][0]['Description']}) - {ents['ICD10CMConcepts'][0]['Code']}")
  
          
app = QtWidgets.QApplication(sys.argv) 
window = Ui() 
window.show()
app.exec()