# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ndf_more_options.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1055, 176)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox_8 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_8.setGeometry(QtCore.QRect(380, 10, 661, 111))
        self.groupBox_8.setObjectName("groupBox_8")
        self.adhoc_parameters_2 = QtWidgets.QLineEdit(self.groupBox_8)
        self.adhoc_parameters_2.setEnabled(False)
        self.adhoc_parameters_2.setGeometry(QtCore.QRect(480, 35, 171, 25))
        self.adhoc_parameters_2.setObjectName("adhoc_parameters_2")
        self.label_16 = QtWidgets.QLabel(self.groupBox_8)
        self.label_16.setEnabled(False)
        self.label_16.setGeometry(QtCore.QRect(386, 40, 88, 17))
        self.label_16.setObjectName("label_16")
        self.checkAdhoc_correction_2 = QtWidgets.QCheckBox(self.groupBox_8)
        self.checkAdhoc_correction_2.setEnabled(False)
        self.checkAdhoc_correction_2.setGeometry(QtCore.QRect(15, 35, 148, 23))
        self.checkAdhoc_correction_2.setCheckable(False)
        self.checkAdhoc_correction_2.setObjectName("checkAdhoc_correction_2")
        self.comboBox = QtWidgets.QComboBox(self.groupBox_8)
        self.comboBox.setEnabled(False)
        self.comboBox.setGeometry(QtCore.QRect(166, 35, 201, 25))
        self.comboBox.setObjectName("comboBox")
        self.label_13 = QtWidgets.QLabel(self.groupBox_8)
        self.label_13.setEnabled(False)
        self.label_13.setGeometry(QtCore.QRect(163, 70, 57, 25))
        self.label_13.setObjectName("label_13")
        self.adhoc_element = QtWidgets.QLineEdit(self.groupBox_8)
        self.adhoc_element.setEnabled(False)
        self.adhoc_element.setGeometry(QtCore.QRect(226, 70, 140, 25))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.adhoc_element.sizePolicy().hasHeightForWidth())
        self.adhoc_element.setSizePolicy(sizePolicy)
        self.adhoc_element.setText("")
        self.adhoc_element.setObjectName("adhoc_element")
        self.adhoc_parameters = QtWidgets.QLineEdit(self.groupBox_8)
        self.adhoc_parameters.setEnabled(False)
        self.adhoc_parameters.setGeometry(QtCore.QRect(480, 70, 171, 25))
        self.adhoc_parameters.setText("")
        self.adhoc_parameters.setObjectName("adhoc_parameters")
        self.label_15 = QtWidgets.QLabel(self.groupBox_8)
        self.label_15.setEnabled(False)
        self.label_15.setGeometry(QtCore.QRect(386, 70, 88, 25))
        self.label_15.setObjectName("label_15")
        self.checkAdhoc_correction = QtWidgets.QCheckBox(self.groupBox_8)
        self.checkAdhoc_correction.setGeometry(QtCore.QRect(11, 71, 140, 23))
        self.checkAdhoc_correction.setObjectName("checkAdhoc_correction")
        self.groupBox_9 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_9.setGeometry(QtCore.QRect(10, 10, 361, 111))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_9.sizePolicy().hasHeightForWidth())
        self.groupBox_9.setSizePolicy(sizePolicy)
        self.groupBox_9.setToolTip("")
        self.groupBox_9.setObjectName("groupBox_9")
        self.checkRutherford = QtWidgets.QCheckBox(self.groupBox_9)
        self.checkRutherford.setGeometry(QtCore.QRect(10, 65, 151, 23))
        self.checkRutherford.setChecked(False)
        self.checkRutherford.setObjectName("checkRutherford")
        self.checkFoil = QtWidgets.QCheckBox(self.groupBox_9)
        self.checkFoil.setGeometry(QtCore.QRect(10, 30, 61, 23))
        self.checkFoil.setChecked(False)
        self.checkFoil.setObjectName("checkFoil")
        self.foilMaterialCombo = QtWidgets.QComboBox(self.groupBox_9)
        self.foilMaterialCombo.setEnabled(False)
        self.foilMaterialCombo.setGeometry(QtCore.QRect(140, 30, 121, 25))
        self.foilMaterialCombo.setObjectName("foilMaterialCombo")
        self.foilMaterialCombo.addItem("")
        self.foilMaterialThickness = QtWidgets.QLineEdit(self.groupBox_9)
        self.foilMaterialThickness.setEnabled(False)
        self.foilMaterialThickness.setGeometry(QtCore.QRect(270, 30, 81, 25))
        self.foilMaterialThickness.setObjectName("foilMaterialThickness")
        self.closeButton = QtWidgets.QPushButton(self.centralwidget)
        self.closeButton.setGeometry(QtCore.QRect(960, 130, 80, 23))
        self.closeButton.setDefault(True)
        self.closeButton.setObjectName("closeButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.checkFoil.toggled['bool'].connect(self.foilMaterialCombo.setEnabled) # type: ignore
        self.checkFoil.toggled['bool'].connect(self.foilMaterialThickness.setEnabled) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "More options"))
        self.groupBox_8.setTitle(_translate("MainWindow", "Models"))
        self.adhoc_parameters_2.setText(_translate("MainWindow", " "))
        self.adhoc_parameters_2.setPlaceholderText(_translate("MainWindow", "Cutoff  a0  P(Cutoff)"))
        self.label_16.setText(_translate("MainWindow", "Parameter(s)"))
        self.checkAdhoc_correction_2.setText(_translate("MainWindow", "Roughness"))
        self.label_13.setText(_translate("MainWindow", "Element"))
        self.adhoc_parameters.setPlaceholderText(_translate("MainWindow", "Cutoff  a0  P(Cutoff)"))
        self.label_15.setText(_translate("MainWindow", "Parameter(s)"))
        self.checkAdhoc_correction.setText(_translate("MainWindow", "Ad-hoc Correction"))
        self.groupBox_9.setTitle(_translate("MainWindow", "Geometry"))
        self.checkRutherford.setText(_translate("MainWindow", "Non-Rutherford"))
        self.checkFoil.setText(_translate("MainWindow", "Foil"))
        self.foilMaterialCombo.setItemText(0, _translate("MainWindow", "Material"))
        self.foilMaterialThickness.setText(_translate("MainWindow", "Thickness"))
        self.closeButton.setText(_translate("MainWindow", "Close"))
