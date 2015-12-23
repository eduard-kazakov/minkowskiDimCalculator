# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MinkowskyDimCalculator mdc_features
                                 A QGIS plugin
 Plugin calculates Minkowski dimension (also known as Minkowski–Bouligand
 dimension; box-counting dimension) for features of vector layer.

                              -------------------
        begin                : 2015-12-16
        copyright            : (C) 2015 by Eduard Kazakov
        email                : silenteddie@gmail.com
        homepage             : http://ekazakov.info
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtGui import QApplication

from ui import mdc_features_ui
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QVariant
from qgis.core import *
from qgis.core import QgsMapLayerRegistry
import mdc_lib
import resources
import numpy as np


class MDCFeaturesDlg(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = mdc_features_ui.Ui_Dialog()
        self.ui.setupUi(self)

        # Button's handlers
        self.connect(self.ui.cancelButton, QtCore.SIGNAL("clicked()"), self.cancel)
        self.connect(self.ui.runButton, QtCore.SIGNAL("clicked()"), self.run)
        self.connect(self.ui.layerGridAutoButton, QtCore.SIGNAL("clicked()"), self.autoSettings)

        # Auto check boxes interface handlers
        self.connect(self.ui.featureGridAutoCheckBox, QtCore.SIGNAL("clicked()"), self.featureGridCheckBoxesChanged)

        # Change fields selector when layer changed
        self.connect(self.ui.layerComboBox, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.layerChanged)

        #deactivate progress bar
        self.ui.progressBar.setVisible(False)

        # Fill vector layers combobox with polyline layers
        polylineLayers = [layer.name() for layer in QgsMapLayerRegistry.instance().mapLayers().values() if
                          (layer.type() == QgsMapLayer.VectorLayer) and (layer.wkbType() == 2)]
        self.ui.layerComboBox.addItems(polylineLayers)

    # Main function - run process after "Run" button is pressed
    def run(self):
        # Firstly, check inputs
        if self.ui.layerComboBox.currentText() == '':
            QtGui.QMessageBox.critical(None, "Error", 'No layer specified!')
            return

        if self.ui.tabWidget.currentIndex() == 0:
            self.runForLayerGrid()
        else:
            self.runForFeatureGrid()


    # If "run" was pressed with Layer Grid Tab activated
    def runForLayerGrid(self):
        # Firstly, check inputs for empty values
        if self.ui.layerGridStartSizeLineEdit.text() == '':
            QtGui.QMessageBox.critical(None, "Error", 'No start cell size specified!')
            return
        if self.ui.layerGridEndSizeLineEdit.text() == '':
            QtGui.QMessageBox.critical(None, "Error", 'No end cell size specified!')
            return
        if self.ui.layerGridNumberOfStepsSpinBox == '':
            QtGui.QMessageBox.critical(None, "Error", 'No number of steps specified!')
            return
        if len(self.ui.layerGridAttributeNameLineEdit.text()) == 0:
            QtGui.QMessageBox.critical(None, "Error", 'No attribute name specified!')
            return

        # Check selected layer
        userLayer = mdc_lib.getLayerByName(self.ui.layerComboBox.currentText())
        if userLayer == None:
            QtGui.QMessageBox.critical(None, "Error", 'Selected layer is not valid!')
            return

        # If attribute name more than 10 symbols, cut it (for shapefile)
        if len(self.ui.layerGridAttributeNameLineEdit.text()) > 10:
            mdcAttrName = self.ui.layerGridAttributeNameLineEdit.text()[0:10]
        else:
            mdcAttrName = self.ui.layerGridAttributeNameLineEdit.text()

        if self.ui.onlySelectedFeaturesCheckBox.isChecked():
            extentDict = mdc_lib.getExtentAsDictOfSelectedFeaturesAtLayer(userLayer)
        else:
            extentDict = mdc_lib.getLayerExtentAsDict(userLayer)

        try:
            numberOfSteps = int(self.ui.layerGridNumberOfStepsSpinBox.text())
            startCellSize = float(self.ui.layerGridStartSizeLineEdit.text())
            endCellSize = float(self.ui.layerGridEndSizeLineEdit.text())
        except:
            QtGui.QMessageBox.critical(None, "Error", 'Incorrect inputs!')
            return

        #activate progress bar
        self.ui.progressBar.setVisible(True)
        QApplication.processEvents()

        stepSize = (startCellSize - endCellSize) / (numberOfSteps + 1)

        currentStep = -1
        currentCellSize = startCellSize

        # featureDict is key thing at this part
        # it will contain feature id and two lists. N list will accumulate number of squres at each step,
        # and L list will accumulate size of this squares
        # for example: {'fet_id':1L, 'N':[4,7,11,22], 'L':[12,9,6,3]}
        # featuresDictsList contains featureDicts for all needed features
        featuresDictsList = []

        # first time going through all features to create empty featureDicts
        if self.ui.onlySelectedFeaturesCheckBox.isChecked():
            lineFeatures = userLayer.selectedFeatures()
        else:
            lineFeatures = userLayer.getFeatures()
        for feature in lineFeatures:
            featuresDictsList.append(dict(fet_id=feature.id(), N=[], L=[]))

        while currentStep < int(numberOfSteps + 1):
            QApplication.processEvents()
            memoryLayer = mdc_lib.generateMemoryGridByMinMaxAndSteps(userLayer.crs().authid(),
                extentDict, currentCellSize, currentCellSize)
            if self.ui.onlySelectedFeaturesCheckBox.isChecked():
                lineFeatures = userLayer.selectedFeatures()
            else:
                lineFeatures = userLayer.getFeatures()

            # filling featureDict for every feature
            for feature in lineFeatures:
                QApplication.processEvents()
                N = mdc_lib.getNumberOfIntersectedFeaturesBetweenLayerAndFeature(feature, memoryLayer)
                idx = mdc_lib.findDictIndexInList(featuresDictsList, 'fet_id', feature.id())
                featuresDictsList[idx]["N"].append(N)
                featuresDictsList[idx]["L"].append(currentCellSize)

            currentCellSize -= stepSize
            currentStep += 1

        userLayerDataProvider = userLayer.dataProvider()

        # Create field of not exist
        if userLayer.fieldNameIndex(mdcAttrName) == -1:
            userLayerDataProvider.addAttributes([QgsField(mdcAttrName, QVariant.Double)])

        userLayer.updateFields()
        userLayer.startEditing()

        if self.ui.onlySelectedFeaturesCheckBox.isChecked():
            lineFeatures = userLayer.selectedFeatures()
        else:
            lineFeatures = userLayer.getFeatures()

        # last time going through all features - calculating minkowsky dimension based
        # on N and L lists from featureDicts
        for feature in lineFeatures:
            QApplication.processEvents()
            idx = mdc_lib.findDictIndexInList(featuresDictsList, 'fet_id', feature.id())
            logN = []
            logL = []
            for N in featuresDictsList[idx]["N"]:
                logN.append(np.log(N))
            for L in featuresDictsList[idx]["L"]:
                logL.append(np.log(1 / L))

            minkowskyDimension = mdc_lib.getSlopeOfLinearRegression(logL, logN)
            attrIdx = userLayer.fieldNameIndex(mdcAttrName)
            userLayer.changeAttributeValue(feature.id(), attrIdx, float(minkowskyDimension))

        userLayer.updateFields()
        userLayer.commitChanges()

        #deactivate progress bar
        self.ui.progressBar.setVisible(False)

        QtGui.QMessageBox.about(None, "Success", "Done!")

    # If "run" was pressed with Feature Grid Tab activated
    def runForFeatureGrid(self):
        if len(self.ui.featureGridAttributeNameLineEdit.text()) == 0:
            QtGui.QMessageBox.critical(None, "Error", 'No attribute name specified!')
            return

        if not self.ui.featureGridAutoCheckBox.isChecked():
            if not self.ui.featureGridStartSizeComboBox.currentText():
                QtGui.QMessageBox.critical(None, "Error", 'No start cell size field specified!')
                return

        if not self.ui.featureGridAutoCheckBox.isChecked():
            if not self.ui.featureGridEndSizeComboBox.currentText():
                QtGui.QMessageBox.critical(None, "Error", 'No end cell size field specified!')
                return

        if not self.ui.featureGridAutoCheckBox.isChecked():
            if not self.ui.featureGridNumberOfStepsComboBox.currentText():
                QtGui.QMessageBox.critical(None, "Error", 'No number of steps field specified!')
                return

        # Check selected layer
        userLayer = mdc_lib.getLayerByName(self.ui.layerComboBox.currentText())
        if userLayer == None:
            QtGui.QMessageBox.critical(None, "Error", 'Selected layer is not valid!')
            return

        #activate progress bar
        self.ui.progressBar.setVisible(True)
        QApplication.processEvents()

        # If attribute name more than 10 symbols, cut it (for shapefile)
        if len(self.ui.featureGridAttributeNameLineEdit.text()) > 10:
            mdcAttrName = self.ui.featureGridAttributeNameLineEdit.text()[0:10]
        else:
            mdcAttrName = self.ui.featureGridAttributeNameLineEdit.text()

        if self.ui.onlySelectedFeaturesCheckBox.isChecked():
            lineFeatures = userLayer.selectedFeatures()
        else:
            lineFeatures = userLayer.getFeatures()

        userLayerDataProvider = userLayer.dataProvider()

        # Create field of not exist
        if userLayer.fieldNameIndex(mdcAttrName) == -1:
            userLayerDataProvider.addAttributes([QgsField(mdcAttrName, QVariant.Double)])

        userLayer.updateFields()
        userLayer.startEditing()

        # fo through all features, calculation minkowsky diimension for every
        for feature in lineFeatures:
            QApplication.processEvents()
            # get settings automaticly or from selected fields
            if self.ui.featureGridAutoCheckBox.isChecked():
                autoSettings = mdc_lib.getAutoParametersForFeature(feature)
                startCellSize = autoSettings["startCellSize"]
                endCellSize = autoSettings["endCellSize"]
                numberOfSteps = autoSettings["numberOfSteps"]
            else:
                try:
                    startCellSize = float(feature[self.ui.featureGridStartSizeComboBox.currentText()])
                    endCellSize = float(feature[self.ui.featureGridEndSizeComboBox.currentText()])
                    numberOfSteps = float(feature[self.ui.featureGridNumberOfStepsComboBox.currentText()])
                except:
                    # if some of parameters is invalid, skip feature
                    continue

            extentDict = mdc_lib.getFeatureExtentAsDict(feature)
            stepSize = (startCellSize - endCellSize) / (numberOfSteps + 1)

            currentStep = -1
            currentCellSize = startCellSize

            NList = []
            LList = []

            while currentStep < int(numberOfSteps + 1):
                QApplication.processEvents()
                memoryLayer = mdc_lib.generateMemoryGridByMinMaxAndSteps(userLayer.crs().authid(),
                                                                        extentDict, currentCellSize, currentCellSize)
                N = mdc_lib.getNumberOfIntersectedFeaturesBetweenLayerAndFeature(feature, memoryLayer)
                NList.append(N)
                LList.append(currentCellSize)

                currentCellSize -= stepSize
                currentStep += 1

            logN = []
            logL = []
            for N in NList:
                logN.append(np.log(N))
            for L in LList:
                logL.append(np.log(1 / L))

            QApplication.processEvents()
            minkowskyDimension = mdc_lib.getSlopeOfLinearRegression(logL, logN)
            attrIdx = userLayer.fieldNameIndex(mdcAttrName)
            userLayer.changeAttributeValue(feature.id(), attrIdx, float(minkowskyDimension))

        userLayer.updateFields()
        userLayer.commitChanges()

        #deactivate progress bar
        self.ui.progressBar.setVisible(False)
        QtGui.QMessageBox.about(None, "Success", "Done!")



    # Trying to calculate nice settings automaticly when "Auto" button is pressed
    # Main factor is layer extent
    # Now is under construction - very simple variant here.
    def autoSettings(self):
        if self.ui.layerComboBox.currentText() == '':
            QtGui.QMessageBox.critical(None, "Error", 'No layer specified!')
            return

        userLayer = mdc_lib.getLayerByName(self.ui.layerComboBox.currentText())
        if userLayer == None:
            QtGui.QMessageBox.critical(None, "Error", 'Selected layer is not valid!')
            return

        if self.ui.onlySelectedFeaturesCheckBox.isChecked():
            startCellSize = mdc_lib.getCellSizeFromBiggestFeature(userLayer,True)
        else:
            startCellSize = mdc_lib.getCellSizeFromBiggestFeature(userLayer)

        self.ui.layerGridStartSizeLineEdit.setText(str(startCellSize))

        endCellSize = startCellSize / 40
        stepsNumber = 30

        self.ui.layerGridEndSizeLineEdit.setText(str(endCellSize))
        self.ui.layerGridNumberOfStepsSpinBox.setValue(int(stepsNumber))

    # Interface changings when Auto checkBoxes clicked
    def featureGridCheckBoxesChanged(self):
        if self.ui.featureGridAutoCheckBox.isChecked():
            self.ui.featureGridStartSizeComboBox.setDisabled(True)
            self.ui.featureGridEndSizeComboBox.setDisabled(True)
            self.ui.featureGridNumberOfStepsComboBox.setDisabled(True)
        else:
            self.ui.featureGridStartSizeComboBox.setEnabled(True)
            self.ui.featureGridEndSizeComboBox.setDisabled(False)
            self.ui.featureGridNumberOfStepsComboBox.setEnabled(True)

    # Interface changings when layer is changed
    def layerChanged(self):
        userLayer = mdc_lib.getLayerByName(self.ui.layerComboBox.currentText())
        layerFields = mdc_lib.getAttributesListOfVectorLayer(userLayer,['Integer','Real'])
        self.ui.featureGridStartSizeComboBox.clear()
        self.ui.featureGridEndSizeComboBox.clear()
        self.ui.featureGridNumberOfStepsComboBox.clear()
        self.ui.featureGridStartSizeComboBox.addItems(layerFields)
        self.ui.featureGridEndSizeComboBox.addItems(layerFields)
        self.ui.featureGridNumberOfStepsComboBox.addItems(layerFields)

    # Close window by pressing "Cancel" button
    def cancel(self):
        self.close()