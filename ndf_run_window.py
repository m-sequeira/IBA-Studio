from NDF_run_ui import Ui_MainWindow
from sys import argv, path as syspath
from platform import platform
from subprocess import Popen
from os.path import dirname, isfile, join as osjoin#, dirname, realpath
from os import mkdir, listdir
from shutil import copyfile, copytree
from datetime import datetime
from copy import deepcopy
from time import sleep
from glob import glob 

from PyQt5.QtWidgets import (
	QApplication, QLabel, QLineEdit, QFormLayout,QShortcut,
	 QDialog, QMainWindow, QMessageBox,
	QFileDialog, QTableWidgetItem, 
	QLineEdit, QComboBox, QWidget, QTableWidget, QPlainTextEdit, QVBoxLayout,
	QCheckBox, QSpacerItem
	)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, pyqtSlot, QObject, QThread, pyqtSignal

syspath.insert(0, osjoin(dirname(__file__), 'pyIBA'))
from pyIBA import IDF
from pyIBA.codes.IDF2NDF import IDF2NDF
from NDF_project import project



class Window(QMainWindow, Ui_MainWindow):
	def __init__(self, main_window, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.connectSignalsSlots()

		self.main_window = main_window
		self.project = main_window.project
		# self.idf_file_h = main_window.idf_file

		self.fields = []

		self.default_flags = {
					'fitmethod': '0 - Simulate one spectrum from ndf.prf, no fit',
					'channelcompreesion': '0 - No compression',
					'convolute': '1 - Convolute FWHM',
					'distribution': '1 - Use isotropic distribution',
					'smooth': '0 - Don\'t smooth data',
					'normalisation': '1 - Normalise profile'
		}


		# Step 2: Create a QThread object
		self.thread = QThread()
		# Step 3: Create a worker object
		self.worker = load_results_worker()
		
		# Step 4: Move worker to the thread
		self.worker.moveToThread(self.thread)
		# Step 5: Connect signals and slots
		self.thread.started.connect(self.worker.run)
		# self.worker.finished.connect(self.worker.deleteLater)
		# self.thread.finished.connect(self.thread.deleteLater)
		# self.worker.progress.connect(self.main_window.update_runList)
		self.worker.progress.connect(lambda x: self.update_load_loop(x))
		self.worker.finished.connect(self.finished_load_loop)
		self.worker.finished.connect(self.thread.quit)


		self.debug = self.main_window.debug

	def connectSignalsSlots(self):
		self.runButton.clicked.connect(self.run_ndf)
		self.closeButton.clicked.connect(self.close_window)

		self.comboRun_speed.currentIndexChanged.connect(self.tcn_warning)

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
		self.run_ndf()

	def update_idf_file_version(self):
		# self.idf_file_h = self.main_window.idf_file
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


		## populate simulation group box
		names = self.main_window.idf_file.get_all_spectra_filenames()
		
		self.fields = []
		nspectra = self.main_window.idf_file.get_number_of_spectra()
		for i in range(nspectra):
			sim_group = self.main_window.idf_file.get_simulation_group(spectra_id = i)
			field = QLineEdit(str(sim_group[0]))

			name = names[i]
			nameLabel = QLabel(name)

			self.formLayout.addRow(nameLabel, field)	
			field.setFixedWidth(30)
			nameLabel.setMinimumSize(180, 15)

			self.fields.append(field)

		self.set_run_options()

		if nspectra > 1:
			for f in self.fields:
				f.setEnabled(True)
			self.checkSharedCharge.setEnabled(True)
			self.checkSharedCharge.setChecked(sim_group[2])
		else:
			for f in self.fields:
				f.setEnabled(False)
			self.checkSharedCharge.setEnabled(False)



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
			_, model = self.main_window.idf_file.get_NDF_run_option(k)

			if model is None:
				model = self.default_flags[k]
			
			if model is None:
				o.setCurrentIndex(-1)
			else:
				combo_index = o.findText(model)
				o.setCurrentIndex(combo_index)


	def run_ndf(self):
		print('Opening NDF...')
		if self.debug: 
			print('ndf_run_windoww, run_ndf - at start nversions:', len(self.project.sim_version_history))
			for p in self.project.sim_version_history:
				print('\t', p.path_dir.split('/')[-1])

		self.main_window.pushLoad_results.setEnabled(True)

		# create folder and copy the files from previous simulation to there (to avoid double scattering calculation etc)
		new_folder = self.project.path_dir + self.project.name + '_' + datetime.now().strftime('%d-%m-%Y_%Hh%M:%S') + '_idv'
		path_new_idf = new_folder + '/' + self.main_window.idf_file.name + '.xml'

		try:
			mkdir(new_folder)

			if len(self.project.sim_version_history) > 1:
				prev_folder = self.project.sim_version_history[-1].path_dir				
				# copytree(prev_folder, new_folder)
				file_codes_copy = [self.project.name[:3] + 'u*', # pileup
									self.project.name[:3] + 'ds*'] # double scattering

				for code in file_codes_copy:
					files = glob(prev_folder + code)
					for file in files:
						copyfile(file, new_folder + '/' + file.split('/')[-1])
		except Exception as e:
			# if self.debug: raise e
			pass


		## Save any changes made in the main window while ndf_run_window is open
		self.main_window.save_state()
		
		for i,f in enumerate(self.fields):
			self.main_window.idf_file.set_simulation_group(f.text(), shared_charge = self.checkSharedCharge.isChecked(), spectra_id=i)			

		self.save_run_options(self.main_window.idf_file)

		
		# a copy of self.main_window.idf_file should be created before saving to avoid changing the origianl path_dir 
		idf_file_run = deepcopy(self.main_window.idf_file)
		idf_file_run.save_idf(path_new_idf)

		# project.append makes a deepcopy of the idf_file			
		self.project.append(idf_file_run)		
		self.project.save()
		
		## decompress the IDF file into NDF files here instead of sentind the xml file to the NDF
		try:
			idf_file_run.export_ndf_inputs(path_dir = idf_file_run.path_dir)
		except Exception as e:
			if self.main_window.debug: raise e
			self.main_window.error_window.setText('Check geometry input\n' + str(e))
			self.main_window.error_window.exec_()
			return

		OSname = platform()
		if 'Linux' in OSname:
			self.run_ndf_linux(idf_file_run)
		elif 'Windows' in OSname:
			self.run_ndf_windows(idf_file_run)

		
		self.worker.main_window = self.main_window
		
		if not self.thread.isRunning():
			print('Loading thread started')
			self.thread.start()

		self.main_window.update_runList()
		self.main_window.runList.setCurrentRow(0)


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
		# file = idf_file.name + '.xml'
		file = idf_file.spc_files[0]

		# cwd = getcwd()
		cwd = idf_file.executable_dir[:-1]
		cmd = cwd + ndf_path + ' ' + file + ' ' + ndf_flags
		path_bat = path + 'ndf.bat'

		if self.debug: print(cmd)

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
		file = idf_file.spc_files[0]

		cwd = idf_file.executable_dir[:-1]
		cmd = wine + ' ' + cwd + ndf_path + ' ' + file + ' ' + ndf_flags
		path_bat = path + 'ndf.bat'

		if self.debug: print(cmd)
		
		with open(path_bat,'w') as file:
			file.write('cd ' + path + '\n')
			file.write('echo \'Run started...\' > run_status.res \n')
			file.write(cmd + '\n')
			file.write('echo \'Finished\' > run_status.res \n')
			file.write('echo \'\n\nPress enter to close:\'\n')
			if self.main_window.settings['Actions'].getboolean('keep_NDF_open'):
				file.write('read line')

		
		run = Popen(shell + ' -- bash ' + path_bat, shell = True)
		
		# self.run_state = run

		while run.poll() is None:
			sleep(1)


	def update_load_loop(self, run_state):
		index_runList = self.main_window.runList.currentRow()
		index_run = run_state[0]

		# don't understand why but need to loaded one last time here after worker finish this
		# run...
		if run_state[1] == 'F':
			self.main_window.load_results(index_run = index_run)


		if index_run == index_runList:
			self.main_window.idf_file = self.main_window.project.get_idf_version(index_run)
			self.main_window.set_results_box()
			# as to update for the case of multi simulations running
			self.main_window.update_runList()





	def finished_load_loop(self):
		self.main_window.update_runList()

		# self.pushLoad_results.setEnabled(False)
		if not self.main_window.settings['Actions'].getboolean('keep_NDF_files'):			
			self.main_window.clear_files()

	def wait_NDF(self):
		with open('run_status.res', 'r') as file:
			status = True
			print('Running ndf')
			while status:
				line = file.readline()
				if 'Run' in line:
					print('.', end='')
					sleep(2)
					file.seek(0,0)
				else:
					print('Finished')
					status = False
					

	def tcn_warning(self):
		file = self.main_window.idf_file.path_dir + 'ndf.tcn'
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
		fileName, _ = QFileDialog.getOpenFileName(self, "Add TCN file", "", "tcn files (*.tcn)", options=options)

		if fileName != '':
			copyfile(fileName, self.main_window.idf_file.path_dir + 'ndf.tcn')

		return fileName



	def close_window(self):
		for i,f in enumerate(self.fields):
			self.main_window.idf_file.set_simulation_group(f.text(), shared_charge = self.checkSharedCharge.isChecked(), spectra_id=i)

		self.save_run_options(self.main_window.idf_file)

		self.close()



class load_results_worker(QObject):
	finished = pyqtSignal()
	progress = pyqtSignal(list)

	def run(self):
		self.load_results_loop()

	def load_results_loop(self):
		is_running = True
		# last_loop = False
		old_run_states = []

		while is_running:	
			run_states = self.main_window.project.check_simulations_running()
			


			if len(old_run_states) != len(run_states):
				old_run_states.insert(0, True)

			index_run = 0
			try:
				for old, state in zip(old_run_states, run_states):
					if old != state:
						self.main_window.load_results(index_run = index_run)
						self.progress.emit([index_run, 'F'])


					if state:
						self.main_window.load_results(index_run = index_run)
						self.progress.emit([index_run, 'R'])


					index_run += 1

			except Exception as e:
				print(e)
				sleep(1)
				pass


			if True not in run_states:
				break

			old_run_states[:] = run_states[:]

			sleep(1)
		
		self.main_window.project.save()
		self.finished.emit()





if __name__ == "__main__":
	app = QApplication(argv)

	idf_file = IDF()
	win = Window(idf_file)


	if len(argv)>1:
		win.open(fileName = fileName)

	win.show()

	exit(app.exec())
