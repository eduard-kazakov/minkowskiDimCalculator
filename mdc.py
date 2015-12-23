# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MinkowskyDimCalculator mdc
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from mdc_features import MDCFeaturesDlg
from mdc_about import MDCAboutDlg
import os

class MDC:

    def __init__(self,iface):
        self.iface=iface
        self.dlg = MDCFeaturesDlg()

    def initGui(self):

        dirPath = os.path.dirname(os.path.abspath(__file__))
        self.action = QAction(u"Minkowski dimension calculator", self.iface.mainWindow())
        self.action.setIcon(QIcon(dirPath + "/icon.png"))
        self.iface.addPluginToVectorMenu(u"Minkowski dimension calculator",self.action)
        self.action.setStatusTip(u"Minkowski dimension calculator")
        self.iface.addVectorToolBarIcon(self.action)
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)

        self.aboutAction = QAction(u"About", self.iface.mainWindow())
        QObject.connect(self.aboutAction, SIGNAL("triggered()"), self.about)
        self.iface.addPluginToVectorMenu(u"Minkowski dimension calculator", self.aboutAction)

    def unload(self):
        self.iface.removeVectorToolBarIcon(self.action)
        self.iface.removePluginVectorMenu(u"Minkowski dimension calculator",self.action)

        self.iface.removePluginVectorMenu(u"Minkowski dimension calculator",self.aboutAction)

    def run(self):
        self.MDCFeaturesDlg = MDCFeaturesDlg()
        self.MDCFeaturesDlg.show()

    def about(self):
        self.MDCAboutDlg = MDCAboutDlg()
        self.MDCAboutDlg.show()