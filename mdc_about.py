# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MinkowskyDimCalculator mdc_about
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

import mdc_about_ui
from PyQt4 import QtGui


class MDCAboutDlg(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = mdc_about_ui.Ui_Dialog()
        self.ui.setupUi(self)