# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/reactions.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(382, 262)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(170, 220, 191, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.final_target_atom = QtWidgets.QLineEdit(Dialog)
        self.final_target_atom.setGeometry(QtCore.QRect(170, 150, 83, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.final_target_atom.sizePolicy().hasHeightForWidth())
        self.final_target_atom.setSizePolicy(sizePolicy)
        self.final_target_atom.setMinimumSize(QtCore.QSize(50, 0))
        self.final_target_atom.setObjectName("final_target_atom")
        self.QEnergy_label = QtWidgets.QLabel(Dialog)
        self.QEnergy_label.setGeometry(QtCore.QRect(40, 180, 131, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.QEnergy_label.sizePolicy().hasHeightForWidth())
        self.QEnergy_label.setSizePolicy(sizePolicy)
        self.QEnergy_label.setMinimumSize(QtCore.QSize(0, 0))
        self.QEnergy_label.setToolTipDuration(-1)
        self.QEnergy_label.setObjectName("QEnergy_label")
        self.exit_label = QtWidgets.QLabel(Dialog)
        self.exit_label.setGeometry(QtCore.QRect(40, 120, 84, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exit_label.sizePolicy().hasHeightForWidth())
        self.exit_label.setSizePolicy(sizePolicy)
        self.exit_label.setMinimumSize(QtCore.QSize(0, 0))
        self.exit_label.setToolTipDuration(-1)
        self.exit_label.setObjectName("exit_label")
        self.save_button = QtWidgets.QPushButton(Dialog)
        self.save_button.setGeometry(QtCore.QRect(290, 50, 75, 23))
        self.save_button.setObjectName("save_button")
        self.initial_target_atom = QtWidgets.QLineEdit(Dialog)
        self.initial_target_atom.setGeometry(QtCore.QRect(170, 60, 83, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.initial_target_atom.sizePolicy().hasHeightForWidth())
        self.initial_target_atom.setSizePolicy(sizePolicy)
        self.initial_target_atom.setMinimumSize(QtCore.QSize(50, 0))
        self.initial_target_atom.setObjectName("initial_target_atom")
        self.incident_label = QtWidgets.QLabel(Dialog)
        self.incident_label.setGeometry(QtCore.QRect(40, 90, 84, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.incident_label.sizePolicy().hasHeightForWidth())
        self.incident_label.setSizePolicy(sizePolicy)
        self.incident_label.setMinimumSize(QtCore.QSize(0, 0))
        self.incident_label.setToolTipDuration(-1)
        self.incident_label.setObjectName("incident_label")
        self.delete_button = QtWidgets.QPushButton(Dialog)
        self.delete_button.setGeometry(QtCore.QRect(290, 80, 75, 23))
        self.delete_button.setObjectName("delete_button")
        self.add_button = QtWidgets.QPushButton(Dialog)
        self.add_button.setGeometry(QtCore.QRect(290, 20, 75, 23))
        self.add_button.setObjectName("add_button")
        self.final_target_label = QtWidgets.QLabel(Dialog)
        self.final_target_label.setGeometry(QtCore.QRect(40, 150, 131, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.final_target_label.sizePolicy().hasHeightForWidth())
        self.final_target_label.setSizePolicy(sizePolicy)
        self.final_target_label.setMinimumSize(QtCore.QSize(0, 0))
        self.final_target_label.setToolTipDuration(-1)
        self.final_target_label.setObjectName("final_target_label")
        self.qenergy = QtWidgets.QLineEdit(Dialog)
        self.qenergy.setGeometry(QtCore.QRect(170, 180, 83, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qenergy.sizePolicy().hasHeightForWidth())
        self.qenergy.setSizePolicy(sizePolicy)
        self.qenergy.setMinimumSize(QtCore.QSize(50, 0))
        self.qenergy.setObjectName("qenergy")
        self.initial_target_label = QtWidgets.QLabel(Dialog)
        self.initial_target_label.setGeometry(QtCore.QRect(40, 60, 131, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.initial_target_label.sizePolicy().hasHeightForWidth())
        self.initial_target_label.setSizePolicy(sizePolicy)
        self.initial_target_label.setMinimumSize(QtCore.QSize(0, 0))
        self.initial_target_label.setToolTipDuration(-1)
        self.initial_target_label.setObjectName("initial_target_label")
        self.comboReactions = QtWidgets.QComboBox(Dialog)
        self.comboReactions.setGeometry(QtCore.QRect(20, 20, 241, 23))
        self.comboReactions.setObjectName("comboReactions")
        self.comboReactions.addItem("")
        self.exit_ion = QtWidgets.QLineEdit(Dialog)
        self.exit_ion.setGeometry(QtCore.QRect(170, 120, 83, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exit_ion.sizePolicy().hasHeightForWidth())
        self.exit_ion.setSizePolicy(sizePolicy)
        self.exit_ion.setMinimumSize(QtCore.QSize(50, 0))
        self.exit_ion.setObjectName("exit_ion")
        self.incident_ion = QtWidgets.QLineEdit(Dialog)
        self.incident_ion.setGeometry(QtCore.QRect(170, 90, 83, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.incident_ion.sizePolicy().hasHeightForWidth())
        self.incident_ion.setSizePolicy(sizePolicy)
        self.incident_ion.setMinimumSize(QtCore.QSize(50, 0))
        self.incident_ion.setObjectName("incident_ion")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.comboReactions, self.initial_target_atom)
        Dialog.setTabOrder(self.initial_target_atom, self.incident_ion)
        Dialog.setTabOrder(self.incident_ion, self.exit_ion)
        Dialog.setTabOrder(self.exit_ion, self.final_target_atom)
        Dialog.setTabOrder(self.final_target_atom, self.qenergy)
        Dialog.setTabOrder(self.qenergy, self.add_button)
        Dialog.setTabOrder(self.add_button, self.save_button)
        Dialog.setTabOrder(self.save_button, self.delete_button)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.QEnergy_label.setToolTip(_translate("Dialog", "In keV"))
        self.QEnergy_label.setText(_translate("Dialog", "Q Energy"))
        self.exit_label.setToolTip(_translate("Dialog", "In keV"))
        self.exit_label.setText(_translate("Dialog", "Exit ion"))
        self.save_button.setText(_translate("Dialog", "Save"))
        self.incident_label.setToolTip(_translate("Dialog", "In keV"))
        self.incident_label.setText(_translate("Dialog", "Incident ion"))
        self.delete_button.setText(_translate("Dialog", "Delete"))
        self.add_button.setText(_translate("Dialog", "Add"))
        self.final_target_label.setToolTip(_translate("Dialog", "In keV"))
        self.final_target_label.setText(_translate("Dialog", "Final target atom"))
        self.initial_target_label.setToolTip(_translate("Dialog", "In keV"))
        self.initial_target_label.setText(_translate("Dialog", "Initial target atom"))
        self.comboReactions.setItemText(0, _translate("Dialog", "Edit reactions..."))
