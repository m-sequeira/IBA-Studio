from ui.about_window_ui import Ui_dialog_about


from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices, QPixmap
from PyQt5.QtWidgets import QMainWindow


import os
import sys


class About_Window(QMainWindow, Ui_dialog_about):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		 # Check if the application is running as a bundled application
		if getattr(sys, 'frozen', False):
			# The application is bundled and sys._MEIPASS is set
			base_dir = sys._MEIPASS
		else:
	    # The application is not bundled, so use the location of the script file
			base_dir = os.path.dirname(os.path.realpath(__file__))

		image_path = os.path.join(base_dir, 'logos', 'icon_text_nobackground.png')
		self.label_logo.setPixmap(QPixmap(image_path))

		self.manual_path = os.path.join(base_dir, 'pyIBA', 'aux_files', 'MANUAL_100a.pdf')

		self.push_openNDFManual.clicked.connect(self.open_NDF_manual)


	def open_NDF_manual(self):
		# The path finding has to be repeated so that open_NDF_manual can be used without initiallizing the About_window,
		# for instance when clickin on the open NDF manual menu item

		if getattr(sys, 'frozen', False):
			# The application is bundled and sys._MEIPASS is set
			base_dir = sys._MEIPASS
		else:
	    # The application is not bundled, so use the location of the script file
			base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pyIBA')

		manual_path = os.path.join(base_dir, 'pyIBA', 'aux_files', 'MANUAL_100a.pdf')


		# convert the file path to a QUrl object
		url = QUrl.fromLocalFile(manual_path)

		# open the PDF file
		QDesktopServices.openUrl(url)