# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MinkowskiDimCalculator
                                 A QGIS plugin
 Minkowski fractal dimension calculation for vector layer features

                              -------------------
        begin                : 2019-01-01
        copyright            : (C) 2019 by Eduard Kazakov
        email                : silenteddie@gmail.com
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

import os

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from qgis.core import *
from PyQt5.QtCore import QVariant, Qt

import numpy as np

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'minkowskiDimCalculator_dialog_base.ui'))


class MinkowskiDimCalculatorDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(MinkowskiDimCalculatorDialog, self).__init__(parent)
        self.setupUi(self)

        # deactivate progress bar
        self.progressBar.setVisible(False)

        self.layerComboBox.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.featureGridStartSizeComboBox.setLayer(self.layerComboBox.currentLayer())
        self.featureGridStartSizeComboBox.setFilters(QgsFieldProxyModel.Numeric)
        self.featureGridEndSizeComboBox.setLayer(self.layerComboBox.currentLayer())
        self.featureGridEndSizeComboBox.setFilters(QgsFieldProxyModel.Numeric)
        self.featureGridNumberOfStepsComboBox.setLayer(self.layerComboBox.currentLayer())
        self.featureGridNumberOfStepsComboBox.setFilters(QgsFieldProxyModel.Numeric)

        self.layerComboBox.currentIndexChanged.connect(self.layerChanged)
        self.featureGridAutoCheckBox.clicked.connect(self.featureGridCheckBoxesChanged)

        self.layerGridAutoButton.clicked.connect(self.autoSettings)

        self.runButton.clicked.connect(self.run)
        self.cancelButton.clicked.connect(self.cancel)

        ## Button's handlers
        #self.connect(self.ui.cancelButton, QtCore.SIGNAL("clicked()"), self.cancel)
        #self.connect(self.ui.runButton, QtCore.SIGNAL("clicked()"), self.run)
        #self.connect(self.ui.layerGridAutoButton, QtCore.SIGNAL("clicked()"), self.autoSettings)
#
        ## Auto check boxes interface handlers
        #self.connect(self.ui.featureGridAutoCheckBox, QtCore.SIGNAL("clicked()"), self.featureGridCheckBoxesChanged)


    # Trying to calculate nice settings automaticly when "Auto" button is pressed
    # Main factor is layer extent
    # Now is under construction - very simple variant here.
    def autoSettings(self):
        if self.layerComboBox.currentText() == '':
            QtWidgets.QMessageBox.critical(None, "Error", 'No layer specified!')
            return

        userLayer = self.layerComboBox.currentLayer()
        if userLayer == None:
            QtWidgets.QMessageBox.critical(None, "Error", 'Selected layer is not valid!')
            return

        if self.onlySelectedFeaturesCheckBox.isChecked():
            startCellSize = self.getCellSizeFromBiggestFeature(userLayer, True)
        else:
            startCellSize = self.getCellSizeFromBiggestFeature(userLayer)

        self.layerGridStartSizeLineEdit.setText(str(startCellSize))

        endCellSize = startCellSize / 40
        stepsNumber = 30

        self.layerGridEndSizeLineEdit.setText(str(endCellSize))
        self.layerGridNumberOfStepsSpinBox.setValue(int(stepsNumber))

    # Interface changings when Auto checkBoxes clicked
    def featureGridCheckBoxesChanged(self):
        if self.featureGridAutoCheckBox.isChecked():
            self.featureGridStartSizeComboBox.setDisabled(True)
            self.featureGridEndSizeComboBox.setDisabled(True)
            self.featureGridNumberOfStepsComboBox.setDisabled(True)
        else:
            self.featureGridStartSizeComboBox.setEnabled(True)
            self.featureGridEndSizeComboBox.setDisabled(False)
            self.featureGridNumberOfStepsComboBox.setEnabled(True)

    # Interface changings when layer is changed
    def layerChanged(self):
        self.featureGridStartSizeComboBox.setLayer(self.layerComboBox.currentLayer())
        self.featureGridStartSizeComboBox.setFilters(QgsFieldProxyModel.Numeric)
        self.featureGridEndSizeComboBox.setLayer(self.layerComboBox.currentLayer())
        self.featureGridEndSizeComboBox.setFilters(QgsFieldProxyModel.Numeric)
        self.featureGridNumberOfStepsComboBox.setLayer(self.layerComboBox.currentLayer())
        self.featureGridNumberOfStepsComboBox.setFilters(QgsFieldProxyModel.Numeric)

    # Close window by pressing "Cancel" button
    def cancel(self):
        self.close()

    # Main function - run process after "Run" button is pressed
    def run(self):
        # Firstly, check inputs
        if self.layerComboBox.currentText() == '':
            QtWidgets.QMessageBox.critical(None, "Error", 'No layer specified!')
            return
        self.progressBar.setVisible(True)
        try:
            if self.tabWidget.currentIndex() == 0:
                self.runForLayerGrid()
            else:
                self.runForFeatureGrid()
        except Exception as e:
            self.progressBar.setVisible(False)
            QtWidgets.QMessageBox.critical(None, "Error", 'Something going wrong! %s' % str(e))
            return
        self.progressBar.setVisible(False)

        # If "run" was pressed with Layer Grid Tab activated
    def runForLayerGrid(self):
        # Firstly, check inputs for empty values
        if self.layerGridStartSizeLineEdit.text() == '':
            QtWidgets.QMessageBox.critical(None, "Error", 'No start cell size specified!')
            return
        if self.layerGridEndSizeLineEdit.text() == '':
            QtWidgets.QMessageBox.critical(None, "Error", 'No end cell size specified!')
            return
        if self.layerGridNumberOfStepsSpinBox == '':
            QtWidgets.QMessageBox.critical(None, "Error", 'No number of steps specified!')
            return
        if len(self.layerGridAttributeNameLineEdit.text()) == 0:
            QtWidgets.QMessageBox.critical(None, "Error", 'No attribute name specified!')
            return

        # Check selected layer
        userLayer = self.layerComboBox.currentLayer()
        if userLayer == None:
            QtWidgets.QMessageBox.critical(None, "Error", 'Selected layer is not valid!')
            return

        # If attribute name more than 10 symbols, cut it (for shapefile)
        if len(self.layerGridAttributeNameLineEdit.text()) > 10:
            mdcAttrName = self.layerGridAttributeNameLineEdit.text()[0:10]
        else:
            mdcAttrName = self.layerGridAttributeNameLineEdit.text()

        if self.onlySelectedFeaturesCheckBox.isChecked():
            extentDict = self.getExtentAsDictOfSelectedFeaturesAtLayer(userLayer)
        else:
            extentDict = self.getLayerExtentAsDict(userLayer)

        try:
            numberOfSteps = int(self.layerGridNumberOfStepsSpinBox.text())
            startCellSize = float(self.layerGridStartSizeLineEdit.text())
            endCellSize = float(self.layerGridEndSizeLineEdit.text())
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Error", 'Incorrect inputs! %s' % str(e))
            return

        # activate progress bar

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
        if self.onlySelectedFeaturesCheckBox.isChecked():
            lineFeatures = userLayer.selectedFeatures()
        else:
            lineFeatures = userLayer.getFeatures()
        for feature in lineFeatures:
            featuresDictsList.append(dict(fet_id=feature.id(), N=[], L=[]))

        while currentStep < int(numberOfSteps + 1):
            QApplication.processEvents()
            memoryLayer = self.generateMemoryGridByMinMaxAndSteps(userLayer.crs().authid(),
                                                                     extentDict, currentCellSize, currentCellSize)
            if self.onlySelectedFeaturesCheckBox.isChecked():
                lineFeatures = userLayer.selectedFeatures()
            else:
                lineFeatures = userLayer.getFeatures()

            # filling featureDict for every feature
            for feature in lineFeatures:
                QApplication.processEvents()
                N = self.getNumberOfIntersectedFeaturesBetweenLayerAndFeature(feature, memoryLayer)
                idx = self.findDictIndexInList(featuresDictsList, 'fet_id', feature.id())
                featuresDictsList[idx]["N"].append(N)
                featuresDictsList[idx]["L"].append(currentCellSize)

            currentCellSize -= stepSize
            currentStep += 1

        userLayerDataProvider = userLayer.dataProvider()

        # Create field of not exist
        if userLayer.fields().indexFromName(mdcAttrName) == -1:
            userLayerDataProvider.addAttributes([QgsField(mdcAttrName, QVariant.Double)])

        userLayer.updateFields()
        userLayer.startEditing()

        if self.onlySelectedFeaturesCheckBox.isChecked():
            lineFeatures = userLayer.selectedFeatures()
        else:
            lineFeatures = userLayer.getFeatures()

        # last time going through all features - calculating minkowsky dimension based
        # on N and L lists from featureDicts
        for feature in lineFeatures:
            QApplication.processEvents()
            idx = self.findDictIndexInList(featuresDictsList, 'fet_id', feature.id())
            logN = []
            logL = []
            for N in featuresDictsList[idx]["N"]:
                logN.append(np.log(N))
            for L in featuresDictsList[idx]["L"]:
                logL.append(np.log(1 / L))

            minkowskyDimension = self.getSlopeOfLinearRegression(logL, logN)
            attrIdx = userLayer.fields().indexFromName(mdcAttrName)
            userLayer.changeAttributeValue(feature.id(), attrIdx, float(minkowskyDimension))
            userLayer.updateFields()

        userLayer.updateFields()
        userLayer.commitChanges()

        QtWidgets.QMessageBox.about(None, "Success", "Done!")

        # If "run" was pressed with Feature Grid Tab activated
    def runForFeatureGrid(self):
        if len(self.featureGridAttributeNameLineEdit.text()) == 0:
            QtWidgets.QMessageBox.critical(None, "Error", 'No attribute name specified!')
            return

        if not self.featureGridAutoCheckBox.isChecked():
            if not self.featureGridStartSizeComboBox.currentText():
                QtWidgets.QMessageBox.critical(None, "Error", 'No start cell size field specified!')
                return

        if not self.featureGridAutoCheckBox.isChecked():
            if not self.featureGridEndSizeComboBox.currentText():
                QtWidgets.QMessageBox.critical(None, "Error", 'No end cell size field specified!')
                return

        if not self.featureGridAutoCheckBox.isChecked():
            if not self.featureGridNumberOfStepsComboBox.currentText():
                QtWidgets.QMessageBox.critical(None, "Error", 'No number of steps field specified!')
                return

        # Check selected layer
        userLayer = self.layerComboBox.currentLayer()
        if userLayer == None:
            QtWidgets.QMessageBox.critical(None, "Error", 'Selected layer is not valid!')
            return

        # activate progress bar
        QApplication.processEvents()

        # If attribute name more than 10 symbols, cut it (for shapefile)
        if len(self.featureGridAttributeNameLineEdit.text()) > 10:
            mdcAttrName = self.featureGridAttributeNameLineEdit.text()[0:10]
        else:
            mdcAttrName = self.featureGridAttributeNameLineEdit.text()

        if self.onlySelectedFeaturesCheckBox.isChecked():
            lineFeatures = userLayer.selectedFeatures()
        else:
            lineFeatures = userLayer.getFeatures()

        userLayerDataProvider = userLayer.dataProvider()

        # Create field of not exist
        if userLayer.fields().indexFromName(mdcAttrName) == -1:
            userLayerDataProvider.addAttributes([QgsField(mdcAttrName, QVariant.Double)])

        userLayer.updateFields()
        userLayer.startEditing()

        # fo through all features, calculation minkowsky diimension for every
        for feature in lineFeatures:
            QApplication.processEvents()
            # get settings automaticly or from selected fields
            if self.featureGridAutoCheckBox.isChecked():
                autoSettings = self.getAutoParametersForFeature(feature)
                startCellSize = autoSettings["startCellSize"]
                endCellSize = autoSettings["endCellSize"]
                numberOfSteps = autoSettings["numberOfSteps"]
            else:
                try:
                    startCellSize = float(feature[self.featureGridStartSizeComboBox.currentText()])
                    endCellSize = float(feature[self.featureGridEndSizeComboBox.currentText()])
                    numberOfSteps = float(feature[self.featureGridNumberOfStepsComboBox.currentText()])
                except:
                    # if some of parameters is invalid, skip feature
                    continue

            extentDict = self.getFeatureExtentAsDict(feature)
            stepSize = (startCellSize - endCellSize) / (numberOfSteps + 1)

            currentStep = -1
            currentCellSize = startCellSize

            NList = []
            LList = []

            while currentStep < int(numberOfSteps + 1):
                QApplication.processEvents()
                memoryLayer = self.generateMemoryGridByMinMaxAndSteps(userLayer.crs().authid(),
                                                                         extentDict, currentCellSize,
                                                                         currentCellSize)
                N = self.getNumberOfIntersectedFeaturesBetweenLayerAndFeature(feature, memoryLayer)
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
            minkowskyDimension = self.getSlopeOfLinearRegression(logL, logN)
            attrIdx = userLayer.fields().indexFromName(mdcAttrName)
            userLayer.changeAttributeValue(feature.id(), attrIdx, float(minkowskyDimension))
            userLayer.updateFields()

        userLayer.updateFields()
        userLayer.commitChanges()

        QtWidgets.QMessageBox.about(None, "Success", "Done!")



    # MDC Lib

    # return list of names of layer's fields. Second parameter can contain types of needed fields
    # e.g. ['Integer','Real']
    def getAttributesListOfVectorLayer(self, layer, types=None):
        names = []

        for field in layer.pendingFields():
            if not types:
                names.append(field.name())
            else:
                if str(field.typeName()) in types:
                    names.append(field.name())

        return names

    # Return dictionary - description of layer extent. Keys are xMax, xMin, yMax, yMin
    def getLayerExtentAsDict(self, vectorLayer):
        extentDict = dict(xMax=vectorLayer.extent().xMaximum(), xMin=vectorLayer.extent().xMinimum(),
                          yMax=vectorLayer.extent().yMaximum(), yMin=vectorLayer.extent().yMinimum())
        return extentDict

    # Return dictionary - description of feature extent. Keys are xMax, xMin, yMax, yMin
    def getFeatureExtentAsDict(self, feature):
        extentDict = dict(xMax=feature.geometry().boundingBox().xMaximum(),
                          xMin=feature.geometry().boundingBox().xMinimum(),
                          yMax=feature.geometry().boundingBox().yMaximum(),
                          yMin=feature.geometry().boundingBox().yMinimum())
        return extentDict

    # Return max of difference between xMax-xMin or yMax-yMin for feature, where this difference is biggest
    def getCellSizeFromBiggestFeature(self, vectorLayer, onlySelected=False):
        if onlySelected:
            features = vectorLayer.selectedFeatures()
        else:
            features = vectorLayer.getFeatures()
        cellSize = None
        for feature in features:
            if (cellSize == None) or \
                    (
                            feature.geometry().boundingBox().xMaximum() - feature.geometry().boundingBox().xMinimum() > cellSize):
                cellSize = feature.geometry().boundingBox().xMaximum() - feature.geometry().boundingBox().xMinimum()

            if (cellSize == None) or \
                    (
                            feature.geometry().boundingBox().yMaximum() - feature.geometry().boundingBox().yMinimum() > cellSize):
                cellSize = feature.geometry().boundingBox().yMaximum() - feature.geometry().boundingBox().yMinimum()

        return cellSize

    # return dictionary with startCellSize, endCellSize and numberOfSteps for feature.
    # for now calculated in very simple way (demo)
    def getAutoParametersForFeature(self, feature):
        startCellSize = max([feature.geometry().boundingBox().xMaximum() - feature.geometry().boundingBox().xMinimum(),
                             feature.geometry().boundingBox().yMaximum() - feature.geometry().boundingBox().yMinimum()])
        endCellSize = startCellSize / 40
        numberOfSteps = 30

        return dict(startCellSize=startCellSize, endCellSize=endCellSize, numberOfSteps=numberOfSteps)

    # Return dictionary - description of selected features common extent. Keys are xMax, xMin, yMax, yMin
    def getExtentAsDictOfSelectedFeaturesAtLayer(self, vectorLayer):
        features = vectorLayer.selectedFeatures()
        xMax = None
        xMin = None
        yMax = None
        yMin = None
        for feature in features:
            if (xMax == None) or (xMax < feature.geometry().boundingBox().xMaximum()):
                xMax = feature.geometry().boundingBox().xMaximum()
            if (xMin == None) or (xMin > feature.geometry().boundingBox().xMinimum()):
                xMin = feature.geometry().boundingBox().xMinimum()
            if (yMax == None) or (yMax < feature.geometry().boundingBox().yMaximum()):
                yMax = feature.geometry().boundingBox().yMaximum()
            if (yMin == None) or (yMin > feature.geometry().boundingBox().yMinimum()):
                yMin = feature.geometry().boundingBox().yMinimum()
        extentDict = dict(xMax=xMax, xMin=xMin, yMax=yMax, yMin=yMin)
        return extentDict

    # returns memory polygon vector layer - grid with given step and extent from extentDict
    def generateMemoryGridByMinMaxAndSteps(self, crsAuthId, extentDict, stepX, stepY):
        memoryLayerString = 'Polygon?crs=' + crsAuthId
        memoryLayer = QgsVectorLayer(memoryLayerString, 'Temp vector grid', "memory")
        memoryLayer.startEditing()
        memoryLayerDataProv = memoryLayer.dataProvider()

        memoryLayerDataProv.addAttributes([QgsField("FID", QVariant.Int)])

        currentX = extentDict['xMin']
        currentY = extentDict['yMin']

        currentID = 0

        while currentX < extentDict['xMax']:
            while currentY < extentDict['yMax']:
                nextX = currentX + stepX
                nextY = currentY + stepY
                if currentX + stepX > extentDict['xMax']:
                    nextX = extentDict['xMax']
                if currentY + stepY > extentDict['yMax']:
                    nextY = extentDict['yMax']
                currentID = currentID + 1

                currentCellGeometry = QgsGeometry.fromPolygonXY([[QgsPointXY(currentX, currentY), QgsPointXY(nextX, currentY),
                                                                QgsPointXY(nextX, nextY), QgsPointXY(currentX, nextY)]])
                currentCell = QgsFeature()
                currentCell.setGeometry(currentCellGeometry)
                currentCell.setId(currentID)
                currentCell.setAttributes([currentID])

                memoryLayerDataProv.addFeatures([currentCell])
                currentY = currentY + stepY
                currentID += 1

            currentY = extentDict['yMin']
            currentX = currentX + stepX

        memoryLayer.updateExtents()
        memoryLayer.commitChanges()

        return memoryLayer

    # returns how much features from vector layer are intersected with given feature
    # used for calculating N in box-counting algorithm
    def getNumberOfIntersectedFeaturesBetweenLayerAndFeature(self, feature, vectorLayer):
        areas = []
        cands = vectorLayer.getFeatures(QgsFeatureRequest().setFilterRect(feature.geometry().boundingBox()))
        for area_feature in cands:
            if feature.geometry().intersects(area_feature.geometry()):
                areas.append(area_feature.id())
        return len(areas)

    # return slope of regression line with numpy functions
    def getSlopeOfLinearRegression(self,x, y):
        A = np.array([x, np.ones(len(x))])
        w = np.linalg.lstsq(A.T, y)[0]
        return w[0]

    # returns needed dictionary index from list of dictionaries by key
    def findDictIndexInList(self, lst, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        return -1