# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MinkowskyDimCalculator mdc_lib
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

from qgis.core import *

# Return vector layer by it's name, or None
from PyQt4.QtCore import QVariant, Qt

import numpy as np

# return QgsLayer by it's name
def getLayerByName(vectorLayerName):
    layer = None
    for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
        if lyr.name() == vectorLayerName:
            layer = lyr
            break

    return layer

# return list of names of layer's fields. Second parameter can contain types of needed fields
# e.g. ['Integer','Real']
def getAttributesListOfVectorLayer(layer, types=None):
    names = []

    for field in layer.pendingFields():
        if not types:
            names.append(field.name())
        else:
            if str(field.typeName()) in types:
                names.append(field.name())

    return names

# Return dictionary - description of layer extent. Keys are xMax, xMin, yMax, yMin
def getLayerExtentAsDict(vectorLayer):
    extentDict = dict(xMax=vectorLayer.extent().xMaximum(), xMin=vectorLayer.extent().xMinimum(),
                      yMax=vectorLayer.extent().yMaximum(), yMin=vectorLayer.extent().yMinimum())
    return extentDict

# Return dictionary - description of feature extent. Keys are xMax, xMin, yMax, yMin
def getFeatureExtentAsDict(feature):
    extentDict = dict (xMax = feature.geometry().boundingBox().xMaximum(), xMin = feature.geometry().boundingBox().xMinimum(),
                       yMax = feature.geometry().boundingBox().yMaximum(), yMin = feature.geometry().boundingBox().yMinimum())
    return extentDict

# Return max of difference between xMax-xMin or yMax-yMin for feature, where this difference is biggest
def getCellSizeFromBiggestFeature (vectorLayer, onlySelected=False):
    if onlySelected:
        features = vectorLayer.selectedFeatures()
    else:
        features = vectorLayer.getFeatures()
    cellSize = None
    for feature in features:
        if (cellSize == None) or \
                (feature.geometry().boundingBox().xMaximum() - feature.geometry().boundingBox().xMinimum() > cellSize):
            cellSize = feature.geometry().boundingBox().xMaximum() - feature.geometry().boundingBox().xMinimum()

        if (cellSize == None) or \
                (feature.geometry().boundingBox().yMaximum() - feature.geometry().boundingBox().yMinimum() > cellSize):
            cellSize = feature.geometry().boundingBox().yMaximum() - feature.geometry().boundingBox().yMinimum()

    return cellSize

# return dictionary with startCellSize, endCellSize and numberOfSteps for feature.
# for now calculated in very simple way (demo)
def getAutoParametersForFeature (feature):
    startCellSize = max([feature.geometry().boundingBox().xMaximum()-feature.geometry().boundingBox().xMinimum(),
                         feature.geometry().boundingBox().yMaximum()-feature.geometry().boundingBox().yMinimum()])
    endCellSize = startCellSize / 40
    numberOfSteps = 30

    return dict(startCellSize = startCellSize, endCellSize = endCellSize, numberOfSteps = numberOfSteps)

# Return dictionary - description of selected features common extent. Keys are xMax, xMin, yMax, yMin
def getExtentAsDictOfSelectedFeaturesAtLayer(vectorLayer):
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
def generateMemoryGridByMinMaxAndSteps (crsAuthId, extentDict, stepX, stepY):
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

            currentCellGeometry = QgsGeometry.fromPolygon([[QgsPoint(currentX, currentY), QgsPoint(nextX, currentY),
                                                    QgsPoint(nextX, nextY), QgsPoint(currentX,nextY)]])
            currentCell = QgsFeature()
            currentCell.setGeometry(currentCellGeometry)
            currentCell.setFeatureId(currentID)
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
def getNumberOfIntersectedFeaturesBetweenLayerAndFeature (feature, vectorLayer):
    areas = []
    cands = vectorLayer.getFeatures(QgsFeatureRequest().setFilterRect(feature.geometry().boundingBox()))
    for area_feature in cands:
        if feature.geometry().intersects(area_feature.geometry()):
            areas.append(area_feature.id())
    return len(areas)

# return slope of regression line with numpy functions
def getSlopeOfLinearRegression(x, y):
    A = np.array([x, np.ones(len(x))])
    w = np.linalg.lstsq(A.T, y)[0]
    return w[0]

# returns needed dictionary index from list of dictionaries by key
def findDictIndexInList(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1