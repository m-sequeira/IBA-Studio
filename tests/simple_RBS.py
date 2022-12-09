from sys import argv, exit, path as syspath
from os.path import dirname, realpath, join as osjoin

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtTest import QTest
import unittest


syspath.insert(0, osjoin(dirname(__file__), '../'))
syspath.append("../ui")
from main_window_ui import Ui_MainWindow

from NDF_gui import Window


app = QApplication(argv)

class MakeSimpleRBS(unittest.TestCase):
	main = None
	ui   = None

	def setUp(self):
		# self.main = QMainWindow()
		# self.ui = Ui_MainWindow()
		# self.ui.setupUi(self.main)
		self.main = Window()

	def test_setGEOValues(self):
		self.main.geo_calibration_b.setText(str(1))

	def test_loading_file(self):
		# self.main.loadSpectrumButton.click()
		self.main.load_spectrum()



	def test_show(self):
		self.main.show()

# test = MakeSimpleRBS()
# test.setUp()

unittest.main(exit=False)