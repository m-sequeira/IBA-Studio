from NDF_run_ui import Ui_MainWindow
from sys import argv, path as syspath
from platform import platform
from subprocess import Popen
from os.path import dirname, isfile, join as osjoin#, dirname, realpath
from os import mkdir, listdir
from shutil import copyfile, copytree
from datetime import datetime
from copy import deepcopy
# from pickle import dump, load



from PyQt5.QtWidgets import (
	QApplication, QLabel, QLineEdit, QFormLayout,
	 QDialog, QMainWindow, QMessageBox,
	QFileDialog, QTableWidgetItem, 
	QLineEdit, QComboBox, QWidget, QTableWidget, QPlainTextEdit, QVBoxLayout,
	QCheckBox, QSpacerItem
	)
# from PyQt5.QtCore.Qt import MatchContains
from PyQt5.QtCore import Qt

syspath.insert(0, osjoin(dirname(__file__), 'pyIBA'))
from pyIBA import IDF
from NDF_project import project

class Window(QMainWindow, Ui_MainWindow):
	def __init__(self, main_window, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.connectSignalsSlots()

		self.main_window = main_window
		self.project = main_window.project
		self.idf_file = main_window.idf_file

		self.fields = []



	def connectSignalsSlots(self):
		self.runButton.clicked.connect(self.run_ndf)
		self.closeButton.clicked.connect(self.close_window)

		self.comboRun_speed.currentIndexChanged.connect(self.tcn_warning)


	def update_idf_file_version(self):
		self.idf_file = self.main_window.idf_file
		self.project = self.main_window.project
		self.initialize()

	def reset_sim_group_form(self):
		# self.verticalLayout.removeWidget(self.formLayout)
		self.formLayout.hide()
		self.formLayout = QFormLayout()
		self.formLayout.setObjectName("formLayout")
		self.verticalLayout.addLayout(self.formLayout)
		self.scrollArea.setWidget(self.scrollAreaWidgetContents)

	def initialize(self):
		### This is creating more and more rows in the formLayout, it is a small memory leak though
		for f in self.fields:
			f.deleteLater()
			l = self.formLayout.labelForField(f)
			l.deleteLater()

		# self.reset_sim_group_form()
		# for l, f in zip(self.labels, self.fields):
		# 	l.deleteLater()
		# 	f.deleteLater()
		# for i in range(self.formLayout.rowCount()):
		# 	self.formLayout.removeRow(i)
			


		names = self.idf_file.get_all_spectra_filenames()
		
		self.fields = []

		for i in range(self.idf_file.get_number_of_spectra()):
			sim_group = self.idf_file.get_simulation_group(spectra_id = i)
			field = QLineEdit(str(sim_group[0]))

			name = names[i]
			nameLabel = QLabel(name)

			self.formLayout.addRow(nameLabel, field)	
			field.setFixedWidth(30)
			nameLabel.setMinimumSize(180, 15)

			self.fields.append(field)

			self.set_run_options()




	def save_run_options(self, idf_file):
		options_combo = {
					'fitmethod': self.comboRun_speed,
					'channelcompreesion': self.comboRun_compression,
					'convolute': self.comboRun_FWHM,
					'distribution': self.comboRun_isodist,
					'smooth': self.comboRun_smooth,
					'normalisation': self.comboRun_normalise
		}
								
		for k,o in options_combo.items():
			idf_file.set_NDF_run_option(k, o.currentText())

	def set_run_options(self):
		options_combo = {
					'fitmethod': self.comboRun_speed,
					'channelcompreesion': self.comboRun_compression,
					'convolute': self.comboRun_FWHM,
					'distribution': self.comboRun_isodist,
					'smooth': self.comboRun_smooth,
					'normalisation': self.comboRun_normalise
		}
								
		for k,o in options_combo.items():			
			_, model = self.idf_file.get_NDF_run_option(k)
			
			if model is None:
				o.setCurrentIndex(-1)
			else:
				combo_index = o.findText(model)
				o.setCurrentIndex(combo_index)


	def run_ndf(self):
		print('Opening NDF...')

		self.main_window.save_state()

		# create folder and copy the files from previous simulation to there (to avoid double scattering calculation etc)
		new_folder = self.project.path_dir + self.project.name + '_' + datetime.now().strftime('%d-%m-%Y_%Hh%M')
		print('ln139', new_folder)
		try:
			if len(self.project.sim_version_history) > 0:
				# prev_folder = self.idf_file.path_dir
				prev_folder = self.project.sim_version_history[-1].path_dir
				
				print('ln145', prev_folder)
				# files = listdir(prev_folder)
				copytree(prev_folder, new_folder)
			else:
				mkdir(new_folder)

		except Exception as e:
			raise e
			pass


		idf_file_run = deepcopy(self.idf_file)		
		self.project.sim_version_history.append(idf_file_run)
		# self.idf_file = self.project.sim_version_history[-1]

		
		for i,f in enumerate(self.fields):
			idf_file_run.set_simulation_group(f.text(), spectra_id=i)
		self.save_run_options(idf_file_run)

		idf_file_run.save_idf(new_folder + '/' + self.idf_file.name + '.xml')
		self.project.save()

		# self.project.sim_version_history.append(idf_file_run)


		OSname = platform()
		if 'Linux' in OSname:
			self.run_ndf_linux(idf_file_run)
		elif 'Windows' in OSname:
			self.run_ndf_windows(idf_file_run)


		# dump(self.project, open(self.project.path_dir + self.project.name + '.idv', 'wb'))
		

	def run_ndf_windows(self, idf_file):
		shell = 'start cmd.exe /c'
		# ndf_path = '\\NDF_10.0_2021-06-05\\NDF.exe'
		ndf_path = '\\codes\\NDF_11_MS\\NDF.exe'

		# get flags:
		options = ['fitmethod','channelcompreesion','convolute','distribution','smooth','normalisation']
		code = []					
		for o in options:			
			code.append(idf_file.get_NDF_run_option(o)[0])

		ndf_flags = ' '.join(code)


		path = idf_file.path_dir
		file = idf_file.name + '.xml'

		# cwd = getcwd()
		cwd = idf_file.executable_dir[:-1]
		cmd = cwd + ndf_path + ' ' + file + ' ' + ndf_flags
		path_bat = path + 'ndf.bat'

		print(cmd)
		with open(path_bat,'w') as file:
			file.write('@echo off \n')
			file.write('cd ' + path + '\n')
			file.write(cmd + '\n\n\n')
			file.write('echo \n')
			file.write('echo Press enter to close:\n')
			file.write('pause >null')

		# run = subprocess.Popen(['bash', 'ndf.bat'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)#, text=True) #, shell = True
		run = Popen(shell + ' ' + path_bat, shell = True)#, text=True) #
		
	def run_ndf_linux(self, idf_file):
		shell = 'gnome-terminal'
		wine = 'wine'
		ndf_path = '/codes/NDF_11_MS/NDF.exe'


		# get flags:
		options = ['fitmethod','channelcompreesion','convolute','distribution','smooth','normalisation']
		code = []					
		for o in options:			
			code.append(idf_file.get_NDF_run_option(o)[0])

		ndf_flags = ' '.join(code)


		path = idf_file.path_dir
		file = idf_file.name + '.xml' 

		cwd = idf_file.executable_dir[:-1]
		cmd = wine + ' ' + cwd + ndf_path + ' ' + file + ' ' + ndf_flags
		path_bat = path + 'ndf.bat'

		print(cmd)
		with open(path_bat,'w') as file:
			file.write('cd ' + path + '\n')
			file.write(cmd + '\n')
			file.write('echo \'\n\nPress enter to close:\'\n')
			file.write('read line')

		
		run = Popen(shell + ' -- bash ' + path_bat, shell = True)
		
		




	


	def tcn_warning(self):
		file = self.idf_file.path_dir + 'ndf.tcn'
		current_option = str(self.comboRun_speed.currentText())

		if 'TCN' in current_option:
			if isfile(file) is False:
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Information)

				msg.setText("ndf.tcn file not found")
				# msg.setInformativeText("This is additional information")
				msg.setWindowTitle("Warning: ndf.tcn")
				# msg.setDetailedText("The details are as follows:")
				msg.setStandardButtons(QMessageBox.Open | QMessageBox.Cancel)
				buttonAdd = msg.button(QMessageBox.Open)
				buttonAdd.setText('Add file')

				result = msg.exec_()
				if result == QMessageBox.Open:
					self.add_tcn_file()	

	def add_tcn_file(self):
		options = QFileDialog.Options()
		fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*)", options=options)

		if fileName != '':
			copyfile(fileName, self.idf_file.path_dir + 'ndf.tcn')

		return fileName




	def close_window(self):
		for i,f in enumerate(self.fields):
			self.idf_file.set_simulation_group(f.text(), spectra_id=i)

		self.close()




if __name__ == "__main__":
	app = QApplication(argv)

	idf_file = IDF('/home/msequeira/Dropbox/CTN/Radiate/IDF_python/testing/multi_files/combined_4spectra.xml')
	win = Window(idf_file)


	if len(argv)>1:
		win.open(fileName = fileName)

	win.show()

	exit(app.exec())
