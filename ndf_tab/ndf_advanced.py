
from os import mkdir
from shutil import copyfile
from platform import platform
from os.path import dirname, realpath, isfile, join as osjoin
from subprocess import Popen

from numpy import loadtxt
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QMainWindow

from pyIBA import IDF
from ndf_tab.ndf_run_window import Window as NDF_Window
from ui.ndf_spectra_fit_ui import Ui_MainWindow as Ui_NDF_Fit_Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar


class NDF_advanced():
	def __init__(self, window):
		self.window = window
		self.idf_file = window.idf_file
		self.path_advanced = None
		self.paths_advanced = []
		self.ndf_window = run_ndf_from_ori_files(self.window)
		self.ndf_window.checkSharedCharge.setEnabled(False)

		self.connectSignalsSlots()

		# try:
		# 	mkdir(self.path_dir_tmp)
		# except:
		# 	pass

		# self.figure_result_advanced = plt.figure(figsize=(4,4))
		# self.canvas_result_advanced = FigureCanvas(self.figure_result_advanced)
		# self.window.spectra_result_plot_advanced.addWidget(self.canvas_result_advanced)
		self.window.canvas_result_advanced.mpl_connect('button_press_event', self.onclick_spectra_fit_result_advanced)


	def connectSignalsSlots(self):
		self.window.pushLoad_advanced_inputs.clicked.connect(self.load_advanced_inputs)
		self.window.pushLoad_tcn.clicked.connect(self.add_tcn_file)
		self.window.comboBox_Advanced.currentIndexChanged.connect(self.load_advanced_geo_input)
		self.window.comboBox_Advanced.view().pressed.connect(self.save_state)

		self.window.comboBox_results_Advanced.currentIndexChanged.connect(self.load_results_advanced)

		self.window.pushSave_advanced_inputs.clicked.connect(self.save_advanced)
		self.window.pushSaveAs_advanced_inputs.clicked.connect(self.save_as_advanced)
		self.window.pushOpenFolder_advanced.clicked.connect(self.open_folder)
		self.window.pushLoad_results_advanced.clicked.connect(self.load_results_advanced)
		self.window.run_NDF_button_advanced.clicked.connect(self.run_ndf)

	def onclick_spectra_fit_result_advanced(self,event):
		self.window.new_windows.append(NDF_Fit_Figure(self))
		self.window.new_windows[-1].show()

	def save_state(self):
		current_id = self.window.comboBox_Advanced.currentIndex()
		text = self.window.advanced_geo_input_field.toPlainText()
		self.geo_text[current_id] = text


	def load_advanced_inputs(self):
		self.window.save_state()

		# path used just to create the files everytime the generate button is pressed
		self.path_dir_tmp = self.window.path_dir + 'advanced_inputs/'
		try:
			mkdir(self.path_dir_tmp)
		except:
			pass

		self.idf_file = self.window.idf_file

		self.window.tabAdvanced.setCurrentIndex(0)

		try:
			self.filenames_advanced = self.idf_file.export_ndf_inputs(path_dir = self.path_dir_tmp)
		except Exception as e:
			self.window.error_window.setText('Check geometry input\n' + str(e))
			self.window.error_window.exec_()
			return

		geo_paths = []

		# to create a 1-D list with the reactions inculded
		for file_group in self.filenames_advanced['geo_files']:
			for file in file_group:
				geo_paths.append(file)

		self.filenames_advanced['geo_files'] = geo_paths

		self.geo_text = []
		for p in self.filenames_advanced['geo_files']:
			with open(self.path_dir_tmp + p, 'r') as file:
				self.geo_text.append(file.readlines())

		self.update_combo_id()

		self.load_advanced_geo_input()
		self.load_advanced_str_input()
		self.load_advanced_prf_input()
		self.load_advanced_spc_input()


		try:
			self.load_advanced_tcn_input()
		except Exception as e:
			# raise e
			pass
		# 		msg = QMessageBox()
		# 		msg.setIcon(QMessageBox.Information)
		# 		msg.setText("ndf.tcn file not found")
		# 		msg.setWindowTitle("Warning: ndf.tcn")
		# 		msg.setStandardButtons(QMessageBox.Open | QMessageBox.Cancel)
		# 		buttonAdd = msg.button(QMessageBox.Open)
		# 		buttonAdd.setText('Add file')

		# 		result = msg.exec_()
		# 		if result == QMessageBox.Open:
		# 			tcn_filename = self.add_tcn_file()

		# 			if tcn_filename != '':
		# 				self.load_advanced_tcn_input()



	def load_advanced_geo_input(self):
		current_id = self.window.comboBox_Advanced.currentIndex()

		data = self.geo_text[current_id]
		
		self.window.advanced_geo_input_field.clear()
		self.window.advanced_geo_input_field.insertPlainText(''.join(data))

	def load_advanced_str_input(self, files_path = ''):
		str_filename = self.filenames_advanced['str_files'][0]

		with open(self.path_dir_tmp + str_filename, 'r') as file:
			data = file.readlines()
		
		self.window.advanced_str_input_field.clear()
		self.window.advanced_str_input_field.insertPlainText(''.join(data))

	def load_advanced_prf_input(self, files_path = ''):  
		if None in self.filenames_advanced['prf_files']:
			return

		prf_filename = self.filenames_advanced['prf_files'][0]

		with open(self.path_dir_tmp + prf_filename, 'r') as file:
			data = file.readlines()
		
		self.window.advanced_prf_input_field.clear()
		self.window.advanced_prf_input_field.insertPlainText(''.join(data))

	def load_advanced_spc_input(self, files_path = ''):
		spc_filename = self.filenames_advanced['spc_files'][0]

		with open(self.path_dir_tmp + spc_filename, 'r') as file:
			data = file.readlines()

		self.window.advanced_spc_input_field.clear()
		self.window.advanced_spc_input_field.insertPlainText(''.join(data))

	def load_advanced_tcn_input(self):
		tcn_path = self.idf_file.path_dir + 'ndf.tcn'

		with open(tcn_path, 'r') as file:
			data = file.readlines()
		
		self.window.advanced_tcn_input_field.clear()
		self.window.advanced_tcn_input_field.insertPlainText(''.join(data))


	def add_tcn_file(self):
		options = QFileDialog.Options()
		fileName, _ = QFileDialog.getOpenFileName(self.window, "Add TCN file", "", "tcn files (*.tcn)", options=options)

		if fileName != '':
			copyfile(fileName, self.path_dir_tmp + '/ndf.tcn')

		self.load_advanced_tcn_input()

		return fileName


	def save_as_advanced(self):
		# fileName,_ = QFileDialog.getSaveFileName(self.window, 'Save File')
		fileName = QFileDialog.getExistingDirectory(self.window, "Select Folder")
		
		if fileName != '':

			self.path_advanced = fileName
			# self.path_dir_tmp = '/'.join(self.path_advanced.split('/')[:-1]) + '/'
			# self.file = self.path_advanced.split('/')[-1]

			print('Save file...')
			print('Path: %s' %self.path_advanced)

			self.save_advanced()




	def save_advanced(self):
		self.save_state()

		if self.filenames_advanced is None:
			return

		if self.path_advanced is None:
			self.save_as_advanced()
			return

		pairs = {
			self.filenames_advanced['str_files'][0] : self.window.advanced_str_input_field,
			self.filenames_advanced['prf_files'][0] : self.window.advanced_prf_input_field,
			self.filenames_advanced['spc_files'][0] : self.window.advanced_spc_input_field,
			'ndf.tcn': self.window.advanced_tcn_input_field
		}


		for k,field in pairs.items():
			text = field.toPlainText()
			if k != None:
				with open(self.path_advanced + '/' + k, 'w') as file:
					file.write(text)


				print(self.path_advanced + '/' + k, 'saved')


		for geo_path, geo_text in zip(self.filenames_advanced['geo_files'], self.geo_text):
			with open(self.path_advanced + '/' + geo_path, 'w') as file:
				file.write(''.join(geo_text))

			print(self.path_advanced + '/' + geo_path, 'saved')


		for dat in self.filenames_advanced['dataxy_files']:
			try:
				copyfile(self.path_dir_tmp + dat, self.path_advanced + '/' + dat)

				print(self.path_advanced + '/' + dat, 'saved')
			except:
				pass

		self.fit_ids = []
		sample_count = 0
		geo_count = 0
		spc_text = self.window.advanced_spc_input_field.toPlainText().strip().split('\n')
		for line in spc_text:
			entries = line.split()
			n_entries = len(entries)
			if n_entries == 4:
				if entries[-1][-1] in [']', ')', '}']:
					geo_count += 1
				else:
					sample_count += 1
					geo_count = 1
			elif n_entries == 3:
				geo_count += 1

			if geo_count < 10: spacer_g = '0'
			else: spacer_g = ''
			if sample_count < 10: spacer_s = '0'
			else: spacer_s = ''


			self.fit_ids.append('%s%s%s%s' %(spacer_s, sample_count, spacer_g, geo_count))

	def open_folder(self):
		OSname = platform()
		try:
			if 'Linux' in OSname:
				Popen(["xdg-open", self.path_advanced])			
			elif 'Windows' in OSname:
				print('Nothing')
				# startfile(self.path_advanced)
		except Exception as e:
			self.window.error_window.setText('Error: Try saving the files first.\n\n - ' + str(e))
			self.window.error_window.exec_()


	def load_results_advanced(self):
		try:
			self.window.tabAdvanced.setCurrentIndex(1)

			current_id = self.window.comboBox_results_Advanced.currentText().split(':')[0]
			current_id = int(current_id)
			fit_id = self.fit_ids[current_id]

			file = self.filenames_advanced['spc_files'][0]

			# name[:3]gXY x is the sample and Y is the spectra
			pairs = {
					self.window.results_geometry: '%sg%s.geo' %(file[:3], fit_id),
					self.window.results_elements: '%ss%s.str' %(file[:3], fit_id[:2]),
					self.window.results_profile: '%s%s.prf' %(file[:3], fit_id[:2])
					}

			for field, filename in pairs.items():       
				res_filename = self.path_advanced + '/' + filename

				with open(res_filename, 'r') as file:
					data = file.readlines()
				
				field.clear()
				field.insertPlainText(''.join(data))


			self.set_spectra_fit_result_advanced()

			

		except Exception as e:
			if self.window.debug: raise e
			print('Result files not found')
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)

			msg.setText("Result files not found")
			# msg.setInformativeText("Showing IDF raw results instead")
			msg.setWindowTitle("Error")
			# msg.setDetailedText("The details are as follows:")
			msg.setStandardButtons(QMessageBox.Ok)
			# buttonAdd = msg.button(QMessageBox.Open)
			result = msg.exec_()



	def set_spectra_fit_result_advanced(self):
		file = self.filenames_advanced['spc_files'][0]
		current_id = self.window.comboBox_results_Advanced.currentText().split(':')[0]
		current_id = int(current_id)
		fit_id = self.fit_ids[current_id]

		res_filename = '%sf%s.dat' %(file[:3], fit_id)

		data = loadtxt(self.path_advanced + '/' + res_filename, skiprows = 7)

		data_x_given = data_x_fit = data[:,0]
		data_y_given = data[:,1]
		data_y_fit = data[:,2]

		if data_x_fit is None: return

		self.window.figure_result_advanced.clear()

		ax_result = self.window.figure_result_advanced.add_subplot(111)

		ax_result.plot(data_x_given, data_y_given, 'x', label = 'Exp.')
		ax_result.plot(data_x_fit, data_y_fit, label = 'Fit')
		
		ax_result.set_yticklabels([])
		ax_result.set_xlabel('Energy (Channels)')
		ax_result.legend(frameon=False)

		self.window.figure_result_advanced.tight_layout()
		self.window.canvas_result_advanced.draw()

	
	def update_combo_id(self):
			name_list = []

			c = 0
			for i in range(self.window.nspectra):
				name = self.idf_file.get_spectrum_file_name(spectra_id=i)
				reactions = self.idf_file.get_reactions(spectra_id = i)

				if name is None:
					name = 'Spectrum %i' %(i+1)
				else:
					# name += '\t %i: %s' %(i, name.split('.')[0])
					for r in reactions:
						name = '%i: %s' %(i, self.filenames_advanced['geo_files'][c])
						name_list.append(name + ' - ' + r['code'])
						c += 1
					c -= 1
				c += 1

			self.window.comboBox_Advanced.blockSignals(True)
			self.window.comboBox_Advanced.clear()
			self.window.comboBox_Advanced.addItems(name_list)
			self.window.comboBox_Advanced.setCurrentIndex(0)
			self.window.comboBox_Advanced.blockSignals(False)

			self.window.comboBox_results_Advanced.blockSignals(True)
			self.window.comboBox_results_Advanced.clear()
			self.window.comboBox_results_Advanced.addItems(name_list)
			self.window.comboBox_results_Advanced.setCurrentIndex(0)
			self.window.comboBox_results_Advanced.blockSignals(False)

			# self.window.comboReactions_Advanced.blockSignals(True)
			# self.window.comboReactions_Advanced.clear()
			# self.window.comboReactions_Advanced.addItems(reaction_list)
			# self.window.comboReactions_Advanced.blockSignals(False)


	def run_ndf(self):
		self.ndf_window.advanced_tab = self
		self.save_advanced()


		if ~self.ndf_window.isVisible():
			self.ndf_window.show()

			frame = self.window.frameGeometry()
			self.ndf_window.move(frame.x() + frame.width(), frame.y())




class run_ndf_from_ori_files(NDF_Window):
	def tcn_warning(self):
		file = self.advanced_tab.path_advanced + '/ndf.tcn'
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
			copyfile(fileName, self.advanced_tab.path_advanced + '/ndf.tcn')

		return fileName

	def run_ndf(self):
		#save advanced tab state
		options_combo = {
					'fitmethod': self.comboRun_speed,
					'channelcompreesion': self.comboRun_compression,
					'convolute': self.comboRun_FWHM,
					'distribution': self.comboRun_isodist,
					'smooth': self.comboRun_smooth,
					'normalisation': self.comboRun_normalise
		}
		
		self.flags = []						
		for k,o in options_combo.items():
			self.flags.append(o.currentText().split(' - ')[0])

				


		OSname = platform()
		if 'Linux' in OSname:
			self.run_ndf_linux()
		elif 'Windows' in OSname:
			self.run_ndf_windows()


		self.close()

	def run_ndf_linux(self):
		shell = 'gnome-terminal'
		wine = 'wine'
		ndf_path = '/codes/NDF_11_MS/NDF.exe'


		# get flags:
		
		ndf_flags = ' '.join(self.flags)


		path = self.advanced_tab.path_advanced
		file = self.advanced_tab.filenames_advanced['spc_files'][0] 
		
		cwd = osjoin(dirname(__file__), 'pyIBA/pyIBA')
		cmd = wine + ' ' + cwd + ndf_path + ' ' + file + ' ' + ndf_flags
		path_bat = path + 'ndf.bat'

		print(cmd)
		with open(path_bat,'w') as file:
			file.write('echo \'Run started...\' > run_status.res \n')
			file.write('cd ' + path + '\n')
			file.write(cmd + '\n')
			file.write('echo \'Finished\' > ../run_status.res \n')
			file.write('echo \'\n\nPress enter to close:\'\n')
			if self.main_window.settings['Actions'].getboolean('keep_NDF_open'):
				file.write('read line')

		
		run = Popen(shell + ' -- bash ' + path_bat, shell = True)
		
		# self.run_state = run

		# while run.poll() is None:
		# 	sleep(1)


class NDF_Fit_Figure(QMainWindow, Ui_NDF_Fit_Figure):
	def __init__(self, main_window, type = False, parent=None):
		super().__init__(parent)
		self.setupUi(self)

		# self.idf_file = main_window.idf_file
		# self.spectra_id = main_window.spectra_id
		# self.simulation_id = main_window.simulation_id
		# self.debug = main_window.debug
		# self.settings = main_window.settings
		self.filenames_advanced = main_window.filenames_advanced
		self.path_advanced = main_window.path_advanced
		self.window = main_window.window
		self.fit_ids = main_window.fit_ids


		self.figure_result = plt.figure(figsize=(10,6))
		self.canvas_result = FigureCanvas(self.figure_result)
		self.spectra_result_plot.addWidget(self.canvas_result)
		
		self.toolbar = NavigationToolbar(self.canvas_result, self)
		self.spectra_result_plot.addWidget(self.toolbar)


		file = self.filenames_advanced['spc_files'][0]
		current_id = self.window.comboBox_results_Advanced.currentText().split(':')[0]
		current_id = int(current_id)
		fit_id = self.fit_ids[current_id]

		res_filename = '%sf%s.dat' %(file[:3], fit_id)

		data = loadtxt(self.path_advanced + '/' + res_filename, skiprows = 7)

		data_x_given = data_x_fit = data[:,0]
		data_y_given = data[:,1]
		data_y_fit = data[:,2]

		if data_x_fit is None: return


		self.figure_result.clear()
		
		ax_result = self.figure_result.add_subplot(111)

		ax_result.plot(data_x_given, data_y_given, 'x', label = 'Exp.')
		ax_result.plot(data_x_fit, data_y_fit, label = 'Fit')
		
		ax_result.set_yticklabels([])
		ax_result.set_xlabel('Energy (Channels)')
		ax_result.legend(frameon=False)

		self.figure_result.tight_layout()
		self.canvas_result.draw()