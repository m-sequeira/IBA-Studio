from PyQt5.QtWidgets import (
	QApplication, QLabel, QLineEdit, QFormLayout,QShortcut,
	 QDialog, QMainWindow, QMessageBox,
	QFileDialog, QTableWidgetItem, 
	QLineEdit, QComboBox, QWidget, QTableWidget, QPlainTextEdit, QVBoxLayout,
	QCheckBox, QSpacerItem
	)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, pyqtSlot

# syspath.insert(0, osjoin(dirname(__file__), 'pyIBA'))
# from pyIBA import IDF
# from pyIBA.codes.IDF2NDF import IDF2NDF
# from NDF_project import project

from ndf_more_options_ui import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
	def __init__(self, main_window, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.connectSignalsSlots()

		self.main_window = main_window


		foil_materials = self.main_window.settings['Foils']
		foil_names = [name.capitalize() for name in foil_materials]
		foil_compositions = [foil_materials[name] for name in foil_names]

		foil_names = ['%s - %s'%(name, composition) for name, composition in zip(foil_names, foil_compositions)]

		self.foilMaterialCombo.clear()
		self.foilMaterialCombo.addItems(foil_names)



	def connectSignalsSlots(self):
		self.closeButton.clicked.connect(self.close_window)

		QShortcut(
			QKeySequence("Escape"), self, activated=self.on_Escape
		)
		QShortcut(
			QKeySequence("Return"), self, activated=self.on_Enter
		)


	@pyqtSlot()
	def on_Escape(self):
		self.close_window()
	@pyqtSlot()
	def on_Enter(self):
		self.close_window()

	def close_window(self):
		self.close()


