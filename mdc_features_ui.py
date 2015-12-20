# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mdc_features_ui.ui'
#
# Created: Sun Dec 20 04:54:40 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(362, 342)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icon/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.runButton = QtGui.QPushButton(Dialog)
        self.runButton.setGeometry(QtCore.QRect(260, 306, 85, 27))
        self.runButton.setObjectName(_fromUtf8("runButton"))
        self.onlySelectedFeaturesCheckBox = QtGui.QCheckBox(Dialog)
        self.onlySelectedFeaturesCheckBox.setGeometry(QtCore.QRect(9, 42, 204, 22))
        self.onlySelectedFeaturesCheckBox.setObjectName(_fromUtf8("onlySelectedFeaturesCheckBox"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(9, 9, 38, 31))
        self.label.setObjectName(_fromUtf8("label"))
        self.cancelButton = QtGui.QPushButton(Dialog)
        self.cancelButton.setGeometry(QtCore.QRect(169, 306, 85, 27))
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.layerComboBox = QtGui.QComboBox(Dialog)
        self.layerComboBox.setGeometry(QtCore.QRect(60, 9, 291, 27))
        self.layerComboBox.setObjectName(_fromUtf8("layerComboBox"))
        self.tabWidget = QtGui.QTabWidget(Dialog)
        self.tabWidget.setGeometry(QtCore.QRect(9, 70, 341, 221))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.layerGridTab = QtGui.QWidget()
        self.layerGridTab.setObjectName(_fromUtf8("layerGridTab"))
        self.layerGridGroupBox = QtGui.QGroupBox(self.layerGridTab)
        self.layerGridGroupBox.setGeometry(QtCore.QRect(10, 10, 311, 174))
        self.layerGridGroupBox.setObjectName(_fromUtf8("layerGridGroupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.layerGridGroupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.layerGridAttributeNameLineEdit = QtGui.QLineEdit(self.layerGridGroupBox)
        self.layerGridAttributeNameLineEdit.setObjectName(_fromUtf8("layerGridAttributeNameLineEdit"))
        self.gridLayout_2.addWidget(self.layerGridAttributeNameLineEdit, 1, 1, 1, 1)
        self.layerGridNumberOfStepsSpinBox = QtGui.QSpinBox(self.layerGridGroupBox)
        self.layerGridNumberOfStepsSpinBox.setMaximum(999999999)
        self.layerGridNumberOfStepsSpinBox.setProperty("value", 10)
        self.layerGridNumberOfStepsSpinBox.setObjectName(_fromUtf8("layerGridNumberOfStepsSpinBox"))
        self.gridLayout_2.addWidget(self.layerGridNumberOfStepsSpinBox, 4, 1, 1, 1)
        self.layerGridAutoButton = QtGui.QPushButton(self.layerGridGroupBox)
        self.layerGridAutoButton.setObjectName(_fromUtf8("layerGridAutoButton"))
        self.gridLayout_2.addWidget(self.layerGridAutoButton, 5, 0, 1, 1)
        self.layerGridStartSizeLineEdit = QtGui.QLineEdit(self.layerGridGroupBox)
        self.layerGridStartSizeLineEdit.setObjectName(_fromUtf8("layerGridStartSizeLineEdit"))
        self.gridLayout_2.addWidget(self.layerGridStartSizeLineEdit, 2, 1, 1, 1)
        self.layerGridEndSizeLineEdit = QtGui.QLineEdit(self.layerGridGroupBox)
        self.layerGridEndSizeLineEdit.setObjectName(_fromUtf8("layerGridEndSizeLineEdit"))
        self.gridLayout_2.addWidget(self.layerGridEndSizeLineEdit, 3, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.layerGridGroupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.layerGridGroupBox)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 4, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.layerGridGroupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.layerGridGroupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1)
        self.tabWidget.addTab(self.layerGridTab, _fromUtf8(""))
        self.featureGridTab = QtGui.QWidget()
        self.featureGridTab.setObjectName(_fromUtf8("featureGridTab"))
        self.featureGridGroupBox = QtGui.QGroupBox(self.featureGridTab)
        self.featureGridGroupBox.setGeometry(QtCore.QRect(10, 10, 311, 171))
        self.featureGridGroupBox.setObjectName(_fromUtf8("featureGridGroupBox"))
        self.label_7 = QtGui.QLabel(self.featureGridGroupBox)
        self.label_7.setGeometry(QtCore.QRect(7, 25, 112, 23))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.featureGridAttributeNameLineEdit = QtGui.QLineEdit(self.featureGridGroupBox)
        self.featureGridAttributeNameLineEdit.setGeometry(QtCore.QRect(125, 25, 181, 23))
        self.featureGridAttributeNameLineEdit.setObjectName(_fromUtf8("featureGridAttributeNameLineEdit"))
        self.featureGridStartSizeComboBox = QtGui.QComboBox(self.featureGridGroupBox)
        self.featureGridStartSizeComboBox.setGeometry(QtCore.QRect(125, 60, 124, 27))
        self.featureGridStartSizeComboBox.setObjectName(_fromUtf8("featureGridStartSizeComboBox"))
        self.label_8 = QtGui.QLabel(self.featureGridGroupBox)
        self.label_8.setGeometry(QtCore.QRect(7, 60, 112, 23))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.featureGridEndSizeComboBox = QtGui.QComboBox(self.featureGridGroupBox)
        self.featureGridEndSizeComboBox.setGeometry(QtCore.QRect(125, 100, 124, 27))
        self.featureGridEndSizeComboBox.setObjectName(_fromUtf8("featureGridEndSizeComboBox"))
        self.featureGridAutoCheckBox = QtGui.QCheckBox(self.featureGridGroupBox)
        self.featureGridAutoCheckBox.setGeometry(QtCore.QRect(255, 58, 51, 31))
        self.featureGridAutoCheckBox.setObjectName(_fromUtf8("featureGridAutoCheckBox"))
        self.label_9 = QtGui.QLabel(self.featureGridGroupBox)
        self.label_9.setGeometry(QtCore.QRect(7, 100, 112, 23))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.label_10 = QtGui.QLabel(self.featureGridGroupBox)
        self.label_10.setGeometry(QtCore.QRect(7, 140, 112, 23))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.featureGridNumberOfStepsComboBox = QtGui.QComboBox(self.featureGridGroupBox)
        self.featureGridNumberOfStepsComboBox.setGeometry(QtCore.QRect(125, 140, 124, 27))
        self.featureGridNumberOfStepsComboBox.setObjectName(_fromUtf8("featureGridNumberOfStepsComboBox"))
        self.tabWidget.addTab(self.featureGridTab, _fromUtf8(""))

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Minkowski dimension for features", None))
        self.runButton.setText(_translate("Dialog", "Run", None))
        self.onlySelectedFeaturesCheckBox.setText(_translate("Dialog", "Only for selected features", None))
        self.label.setText(_translate("Dialog", "Layer", None))
        self.cancelButton.setText(_translate("Dialog", "Cancel", None))
        self.layerGridGroupBox.setTitle(_translate("Dialog", "Settings", None))
        self.layerGridAttributeNameLineEdit.setText(_translate("Dialog", "mink_dem", None))
        self.layerGridAutoButton.setText(_translate("Dialog", "Auto", None))
        self.label_2.setText(_translate("Dialog", "Attribute name", None))
        self.label_5.setText(_translate("Dialog", "Number of steps", None))
        self.label_3.setText(_translate("Dialog", "Start cell size", None))
        self.label_4.setText(_translate("Dialog", "End cell size", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.layerGridTab), _translate("Dialog", "Layer grid", None))
        self.featureGridGroupBox.setTitle(_translate("Dialog", "Settings", None))
        self.label_7.setText(_translate("Dialog", "Attribute name", None))
        self.featureGridAttributeNameLineEdit.setText(_translate("Dialog", "mink_dem", None))
        self.label_8.setText(_translate("Dialog", "Start cell size", None))
        self.featureGridAutoCheckBox.setText(_translate("Dialog", "Auto", None))
        self.label_9.setText(_translate("Dialog", "End cell size", None))
        self.label_10.setText(_translate("Dialog", "Number of steps", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.featureGridTab), _translate("Dialog", "Feature grid", None))

import res_rc
