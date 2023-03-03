from sys import argv, exit, path as syspath, setrecursionlimit
from os import remove
from shutil import rmtree
from os.path import dirname, realpath, join as osjoin
from glob import glob 
from webbrowser import open_new

from shutil import copyfile
from copy import deepcopy
from pickle import load as pickleLoad
from Settings import settings


from PyQt5.QtWidgets import (
	QApplication, QDialog, QMainWindow, QMessageBox, QListWidget,
	QMenu,
	QFileDialog, QTableWidgetItem, 
	QLineEdit, QComboBox, QWidget, QTableWidget, QPlainTextEdit, QVBoxLayout,
	QCheckBox, QSpacerItem
	)
# from PyQt5.QtCore.Qt import MatchContains
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

#from PyQt5.uic import loadUi


from main_window_ui import Ui_MainWindow
from about_window_ui import Ui_dialog_about
from ndf_spectra_fit_ui import Ui_MainWindow as Ui_NDF_Fit_Figure
from reactions_ui import Ui_Dialog as Ui_Reactions_Dialog
from ndf_run_window import Window as NDF_Window
from ndf_more_options import Window as ndf_more_options_window

syspath.insert(0, osjoin(dirname(__file__), 'pyIBA'))
from pyIBA import IDF
from pyIBA.auxiliar import latex_atom, simplify_atomic_formula, set_element_fit_symbol, pretty_formula_ratio
from NDF_project import project, load as load_project
from NDF_advanced import NDF_advanced

from numpy import loadtxt, savetxt, array as nparray, zeros_like as npzeros_like
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar


# this might lead to system instabilities. A better copy algorithm needs to be implented to handle the deepcopy of large idf files
setrecursionlimit(10000)

class Window(QMainWindow, Ui_MainWindow):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.spacerItem = QSpacerItem(20, 30)
		self.spacerItem_result = QSpacerItem(20, 40)


		self.connectSignalsSlots()

		self.settings = settings().get_settings()
		self.debug = self.settings['Verbose'].getboolean('debug')

		if self.debug: settings().print_settings()
		

		self.inicialize()

	def add_menu_to_button(self, button):
		menu = QMenu()
		button.setMenu(menu)

		if button.objectName() == 'copyGeometry_button':
			menu.triggered.connect(lambda x: self.copy_geooutput2input(x.text()))
			menu_items = ['All', 'Energy', 'FWHM', 'Angle In', 'Angle Out', 'Charge', 'Calibration']

		elif button.objectName() == 'copyElements_button':
			menu.triggered.connect(lambda x: self.copy_elements_output2input(x.text()))
			nrows = self.elements_table.rowCount()
			menu_items = ['All']
			for i in range(0,nrows):
				element = self.elements_table_fit_result.item(i,0)
				if element is not None:
					element = element.text()
					element = simplify_atomic_formula(element)
				else:
					element = ''

				menu_items.append('%i: %s' %(i+1, element))
		elif button.objectName() == 'copySpectra_button':
			menu.triggered.connect(lambda x: self.copy_geo_spectra(x.text().split(':')[0] ))
			menu_items = ['All']
			menu_items += self.idf_file.get_all_spectra_filenames()
			menu_items = [name.split('.')[0] for name in menu_items]

			current_spectrum = self.comboSpectrum_id.currentText()
			try:
				menu_items.remove(current_spectrum)
			except:
				pass
		elif button.objectName() == 'copyNDFparam_button':
			menu.triggered.connect(lambda x: self.copy_model_spectra(x.text().split(':')[0] ))
			menu_items = ['All']
			menu_items += self.idf_file.get_all_spectra_filenames()
			menu_items = [name.split('.')[0] for name in menu_items]

			current_spectrum = self.comboSpectrum_id.currentText()
			try:
				menu_items.remove(current_spectrum)
			except:
				pass


			

		for item in menu_items:
			menu.addAction(item)

			# submenu = QMenu()
			# item_menu.addMenu(submenu)

			# submenu.addAction('All')
			# submenu.addAction('Energy')

			


		return menu

	def copy_geo_spectra(self, target_spectra_id):
		if target_spectra_id == 'All':
			target_spectra_id = range(self.nspectra)
			for spectra_id in target_spectra_id:
				self.save_geometry_box(target_spectra_id = spectra_id)

		else:
			target_spectra_id = int(target_spectra_id)
			self.save_geometry_box(target_spectra_id = target_spectra_id)

	def copy_model_spectra(self, target_spectra_id):
		if target_spectra_id == 'All':
			for spectra_id in range(self.nspectra):
				for simulation_id in range(len(self.idf_file.get_reactions(spectra_id = spectra_id))):
					self.save_fit_methods_box(target_spectra_id = spectra_id, target_simulation_id = simulation_id)
					self.save_geometry_box_fits(target_spectra_id = spectra_id, target_simulation_id = simulation_id)
		else:
			target_spectra_id = int(target_spectra_id)
			for simulation_id in range(len(self.idf_file.get_reactions(spectra_id = target_spectra_id))):
				self.save_fit_methods_box(target_spectra_id = target_spectra_id, target_simulation_id = simulation_id)
				self.save_geometry_box_fits(target_spectra_id = target_spectra_id, target_simulation_id = simulation_id)


	def copy_elements_output2input(self, element):
		if element == 'All':
			id_elements = range(self.elements_table_fit_result.rowCount())
		else:
			id_elements = [int(element.split(':')[0]) - 1]

		for id_element in id_elements:
			# initial_value = self.elements_table_fit_result_initial.item(id_element, 0).text()
			final_value = self.elements_table_fit_result.item(id_element, 0).text()

			# if '?=' in initial_value:
			# 	final_value = set_element_fit_symbol(final_value)
			self.elements_table.item(id_element, 0).setText(final_value)

	def copy_geooutput2input(self, element):
		pairs = {
			'energy':{
						'field_in': self.geo_energy_fit_result,
						'field_out': self.geo_energy
					},
			'fwhm'  :{
						'field_in': self.geo_fwhm_fit_result,
						'field_out': self.geo_fwhm
					},
			'angle in':{
						'field_in': self.geo_angle_in_fit_result,
						'field_out': self.geo_angle_in
					},
			'angle out':{
						'field_in': self.geo_angle_out_fit_result,
						'field_out': self.geo_angle_out
					},
			'charge':{
						'field_in': self.geo_charge_fit_result,
						'field_out': self.geo_charge
					},
			'calibration':{
						'field_in': [self.geo_calibration_m_fit_result, self.geo_calibration_b_fit_result],
						'field_out': [self.geo_calibration_m, self.geo_calibration_b]
					},
			}


		if element == 'All':
			elements = ['Energy', 'FWHM', 'Angle In', 'Angle Out', 'Charge', 'Calibration']
		else:
			elements = [element]

		for element in elements:
			fields_in = pairs[element.lower()]['field_in']
			fields_out = pairs[element.lower()]['field_out'] 

			if isinstance(fields_in, list):
				for fi, fo in zip(fields_in, fields_out):
					fo.setText(fi.text())	
			else:
				fields_out.setText(fields_in.text())

	def copy_profile_output2input(self):
		nrows = self.profile_table_fit_result.rowCount()
		ncols = self.profile_table_fit_result.columnCount()

		self.profile_table.setRowCount(nrows)

		for r in range(nrows):
			for c in range(ncols):
				new_value = self.profile_table_fit_result.item(r, c).clone()
				self.profile_table.setItem(r,c, new_value)



	def inicialize(self):
		self._nspectra = 0
		self._spectra_id = 0
		self.nsims = 0
		self._simulation_id = 0

		# resize the element table columns with
		horizontalHeader = self.elements_table.horizontalHeader()
		# resize the first column to 100 pixels
		horizontalHeader.resizeSection(0, 135)
		horizontalHeader.resizeSection(1, 70)

		#self.executable_dir = dirname(realpath(__file__)) + '/'
		self.executable_dir = osjoin(dirname(__file__), 'pyIBA') + '/'

		self.error_window = self.message_window()

		self.about_window = About_Window()
		self.ndf_more_options_window = ndf_more_options_window(self)
		self.new_windows = []

		self.figure_exp_spectra = plt.figure(figsize=(5,2))
		self.canvas_exp_spectra = FigureCanvas(self.figure_exp_spectra)
		self.spectra_plot.addWidget(self.canvas_exp_spectra)
		self.canvas_exp_spectra.mpl_connect('button_press_event', self.onclick_spectrum)
		self.canvas_exp_spectra.setToolTip('Click to enlarge')

		self.figure_result = plt.figure(figsize=(8.5,2.5))
		self.canvas_result = FigureCanvas(self.figure_result)
		self.spectra_result_plot.addWidget(self.canvas_result)
		self.canvas_result.mpl_connect('button_press_event', self.onclick_spectra_fit_result)
		self.canvas_result.setToolTip('Click to enlarge')

		self.figure_profile = plt.figure(figsize=(8.5,2.))
		self.canvas_profile = FigureCanvas(self.figure_profile)
		self.profile_fit_result_plot.addWidget(self.canvas_profile)
		self.tab_5.mousePressEvent = self.onclick_profile
		# self.canvas_profile.mpl_connect('button_press_event', self.onclick_profile)
		# self.canvas_profile.setToolTip('Click to enlarge')
		self.profile_fit_result_plot_frame.setVisible(False)

		self.figure_result_advanced = plt.figure(figsize=(4,4))
		self.canvas_result_advanced = FigureCanvas(self.figure_result_advanced)
		self.spectra_result_plot_advanced.addWidget(self.canvas_result_advanced)
		# self.canvas_result_advanced.mpl_connect('button_press_event', self.onclick_spectra_fit_result_advanced)
		# self.canvas_result_advanced.setToolTip('Click to enlarge')		

		self.new()

		self.open()

		self.advanced_tab = NDF_advanced(self)

		
	def new(self):
		self.idf_file = IDF()
		self.project = project(self.idf_file)
		self.ndf_window = NDF_Window(self)
		self.path = None
		self.path_dir = None
		self.file = None

		self.setWindowTitle('IDF Viewer: New file')
		self.reset_window()
		self.update_runList()
		



	def connectSignalsSlots(self):
		# file menu
		self.actionNew.triggered.connect(self.new)
		self.actionOpen.triggered.connect(self.open)
		self.actionSave.triggered.connect(self.save)
		self.actionSave_As.triggered.connect(self.save_as)
		self.actionExit.triggered.connect(self.quit)
		self.actionSpectrum.triggered.connect(self.export_spectrum)

		# edit menu
		self.actionAdd_RBS_reactions.triggered.connect(self.edit_reactions_window)

		# tools menu
		self.actionClear_Files.triggered.connect(self.clear_files)
		self.actionRemove_results_from_IDF.triggered.connect(self.remove_results_from_IDF)
		self.actionClear_idv_file.triggered.connect(self.clear_idv_file)
		self.actionExport_fit.triggered.connect(self.export_fit)

		# about menu
		self.actionAbout.triggered.connect(self.about_window)
		self.actionOpen_NDF_Manual.triggered.connect(About_Window.open_NDF_manual)

		# window top banner
		self.actionReload_file.triggered.connect(self.reload_button)

		# window buttons
		self.loadSpectrumButton.clicked.connect(self.load_spectrum)
		self.appendSpectrumButton.clicked.connect(self.append_spectrum)
		self.deleteSpectrumButton.clicked.connect(self.delete_spectrum)
		self.run_NDF_button.clicked.connect(self.run_ndf)
		self.pushLoad_results.clicked.connect(self.load_results)
		# self.pushLoad_results_advanced.clicked.connect(self.load_results)
		self.copyProfile_button.clicked.connect(self.copy_profile_output2input)
		self.calibration_button.clicked.connect(self.onclick_calibration_button)
		self.ndfMoreButton.clicked.connect(self.onclick_ndfMoreButton)

		# run history
		self.runList.currentRowChanged.connect(self.change_idf_version)

		# window dynamics
		self.elements_nelements.valueChanged.connect(self.resize_elements_table)
		self.elements_nelements.valueChanged.connect(self.set_sample_fit_box)
		self.elements_table.itemChanged.connect(self.set_sample_fit_box)
		self.elements_table.itemChanged.connect(self.tidy_elements_table)
		self.profile_nlayers.valueChanged.connect(self.resize_profile_table)
		self.profile_table.itemChanged.connect(self.tidy_profile_table)
		
		self.comboSpectrum_id.currentIndexChanged.connect(self.onchange_spectrum_combo)
		self.comboTechnique.currentIndexChanged.connect(self.reload_technique)
		# self.comboReactions.currentIndexChanged.connect(self.onchange_reaction)
		self.comboReactions.activated.connect(self.onchange_reaction)
		self.comboSimulation.currentIndexChanged.connect(self.onchange_comboSimulation)
		self.geo_projectile_in.textChanged.connect(self.reload_geoprojout)

		self.comboSpectrum_id_results.currentIndexChanged.connect(self.onchange_spectrum_combo_results)

		# self.tabWidget.currentChanged.connect(self.set_sample_fit_box)



		# save states
		self.comboSpectrum_id.view().pressed.connect(self.save_state)
		self.comboSpectrum_id_results.view().pressed.connect(self.save_state)
		self.comboSimulation.view().pressed.connect(self.save_state)
		self.comboTechnique.view().pressed.connect(self.save_state)
		self.comboReactions.view().pressed.connect(self.save_state)
		# self.tabWidget.currentChanged.connect(self.save_state)



	def onclick_profile(self,event):
		self.new_windows.append(NDF_Fit_Figure(self, type = 'profile'))
		self.new_windows[-1].show()

		if self.runList.currentItem() is not None:
			self.new_windows[-1].setWindowTitle('Profile:', self.runList.currentItem().text())


	def onclick_spectra_fit_result(self,event):
		self.new_windows.append(NDF_Fit_Figure(self))
		self.new_windows[-1].show()
		if self.runList.currentItem() is not None:
			self.new_windows[-1].setWindowTitle('Fit: %s' %self.runList.currentItem().text())

	def onclick_spectrum(self,event):
		self.new_windows.append(IDF_spectrum_Figure(self))
		self.new_windows[-1].show()
		if self.comboSpectrum_id.currentItem() is not None:
			self.new_windows[-1].setWindowTitle('Spectrum %s' %str(self.comboSpectrum_id.currentText()))

	def onclick_elements_table(self, event):
		self.set_sample_fit_box()


	def onclick_calibration_button(self):
		options = QFileDialog.Options()
		filePath, _ = QFileDialog.getOpenFileName(self, "Add calibration file", "", "All files (*)", options=options)

		if filePath != '':
			fileName = filePath.split('/')[-1]
			try:
				copyfile(filePath, self.idf_file.path_dir + fileName)
			except:
				pass

			self.geo_calibration_m.setText(fileName)
			self.idf_file.set_energy_calibration_file(filePath, spectra_id=self.spectra_id)




	def save_state(self):
		try:
			self.save_elements_box()
			self.save_profile_box()		

			self.save_geometry_box()
			self.save_geometry_box_fits()
			self.save_fit_methods_box()

			self.save_user_notes()
		except Exception as e:
			if self.debug: raise e
			print('State not saved')


	def onchange_spectrum_combo(self):
		curr_index = self.comboSpectrum_id.currentIndex()
		self.comboSpectrum_id_results.setCurrentIndex(curr_index)
		
		if self.spectra_id != curr_index:
			self.spectra_id = curr_index

	def onchange_reaction(self):
		if self.comboReactions.currentText() == 'Edit reactions...':
			self.edit_reactions_window()

		reaction_id = self.comboReactions.currentIndex()

		if reaction_id < self.comboReactions.count() - 2:
			try:
				m, b = self.idf_file.get_energy_calibration(spectra_id = self.spectra_id, reaction_id = reaction_id)

				if m is None: m = ''
				if b is None: b = ''

				self.geo_calibration_m.setText(str(m))
				self.geo_calibration_b.setText(str(b))
			except:
				pass

	def onchange_spectrum_combo_results(self):
		curr_index = self.comboSpectrum_id_results.currentIndex()
		self.comboSpectrum_id.setCurrentIndex(curr_index)

		if self.spectra_id != curr_index:
			self.spectra_id = curr_index
		
		self.simulation_id = 0

	def onchange_comboSimulation(self):
		self.simulation_id = self.comboSimulation.currentIndex()

	def onclick_ndfMoreButton(self):
		self.ndf_more_options_window.show()
		self.ndf_more_options_window.activateWindow()

		self.new_windows.append(self.ndf_more_options_window)

		frame = self.frameGeometry()
		self.ndf_more_options_window.move(frame.x(), frame.y() + frame.height() + 15)


	@property
	def nspectra(self):
		return self._nspectra

	@nspectra.setter
	def nspectra(self, newvalue):
		self._nspectra = newvalue

		if self._nspectra > 0:
			self.appendSpectrumButton.setEnabled(True)
		else:
			self.appendSpectrumButton.setEnabled(False)

		if self._nspectra <= 1:
			self.deleteSpectrumButton.setEnabled(False)
		else:
			self.deleteSpectrumButton.setEnabled(True)



	@property
	def spectra_id(self):
		return self._spectra_id

	@spectra_id.setter
	def spectra_id(self, newvalue):
		if newvalue >= self.nspectra:
			newvalue = self.nspectra - 1
		if newvalue < 0:
			newvalue = 0

		self._spectra_id = newvalue


		if newvalue != self.comboSpectrum_id.currentIndex():
			self.comboSpectrum_id.setCurrentIndex(newvalue)
			self.comboSpectrum_id_results.setCurrentIndex(newvalue)

		try:
			self.update_comboSimulations()
			self.reload_spectra_box()       
			# self.reload_models_box()
			self.reload_technique()
			self.add_menu_to_button(self.copySpectra_button)
			self.add_menu_to_button(self.copyNDFparam_button)


		except Exception as e:
			if self.debug: raise e


	@property
	def simulation_id(self):
		return self._simulation_id

	@simulation_id.setter
	def simulation_id(self, newvalue):
		if newvalue >= self.nsims:
			newvalue = self.nsims - 1
		if newvalue < 0:
			newvalue = 0

		self._simulation_id = newvalue

		self.comboSimulation.setCurrentIndex(newvalue)
		self.set_models_box()
		self.set_geometry_fit_box()
		self.set_results_box()


	def update_comboSpectrum_id(self):
		name_list = []

		for i in range(self.nspectra):
			name = self.idf_file.get_spectrum_file_name(spectra_id=i)
			if name is None:
				name = 'Spectrum %i' %(i+1)
			else:
				name = '%i: %s' %(i, name.split('.')[0])
			
			name_list.append(name)

		self.comboSpectrum_id.blockSignals(True)
		self.comboSpectrum_id.clear()
		self.comboSpectrum_id.addItems(name_list)
		self.comboSpectrum_id.blockSignals(False)

		self.comboSpectrum_id_results.blockSignals(True)
		self.comboSpectrum_id_results.clear()
		self.comboSpectrum_id_results.addItems(name_list)
		self.comboSpectrum_id_results.blockSignals(False)



	def update_comboSimulations(self):
		self.nsims = self.idf_file.get_number_of_simulations(spectra_id = self.spectra_id)
		reactions = self.idf_file.get_reactions(spectra_id = self.spectra_id)
		technique = self.idf_file.get_technique(spectra_id = self.spectra_id)


		name_list = []
		if reactions is None:
			if self.nsims == 0: self.nsims = 1
			name_list = ['Simulation %i' %i for i in range(1, 1 + self.nsims)]
		else:
			if technique in ['RBS', 'NRA', 'ERDA']:
				name_list = [technique + ': ' + r['code'] for r in reactions]
			else:
				name_list = [technique + ': Simulation %i' %i for i in range(1, 1 + self.nsims)]


		self.comboSimulation.blockSignals(True)
		self.comboSimulation.clear()
		self.comboSimulation.addItems(name_list)
		self.comboSimulation.blockSignals(False)


	def update_comboReactions(self):
		try:
			reactions = self.idf_file.get_reactions(spectra_id = self.spectra_id)
		except Exception as e:
			if self.debug: raise e
			return

		name_list = []

		if reactions is not None:
			name_list = [r['code'] for r in reactions]
			name_list.append('--------')
		name_list.append('Edit reactions...')

		self.comboReactions.blockSignals(True)
		self.comboReactions.clear()
		self.comboReactions.addItems(name_list)
		self.comboReactions.blockSignals(False)


	def update_runList(self):
		prev_names = self.project.get_version_names()
		
		self.runList.blockSignals(True)
		self.runList.clear()
		self.runList.addItems(prev_names)
		self.runList.blockSignals(False)

		run_states = self.project.check_simulations_running()
		if True not in run_states:
			self.pushLoad_results.setEnabled(False)
		else:
			self.pushLoad_results.setEnabled(True)
		

	
	def edit_reactions_window(self):
		reactions = self.idf_file.get_reactions(spectra_id=self.spectra_id)
		if reactions is None:
			reactions = [
				{'initialtargetparticle':'',
				  'incidentparticle': self.geo_projectile_in.text(),
				  'exitparticle': '',
				  'finaltargetparticle': '',
				  'reactionQ': '',
				  'code': ''},]
	
		for i,r in enumerate(reactions):
			r['calibration'] = self.idf_file.get_energy_calibration(spectra_id = self.spectra_id, reaction_id = i)

		input_reaction = Reactions_Dialog(reactions, technique = self.comboTechnique.currentText())
		reactions = input_reaction.get_values()
		if reactions is None:
			return

		self.idf_file.set_reactions(reactions[0], append = False, spectra_id = self.spectra_id)
		m, b = reactions[0]['calibration']
		self.idf_file.set_energy_calibration(m, b, append = False, spectra_id = self.spectra_id, reaction_id = 0)
		for i, r in enumerate(reactions[1:]):
			self.idf_file.set_reactions(r, spectra_id = self.spectra_id)
			m, b = r['calibration']
			self.idf_file.set_energy_calibration(m, b, append = False, spectra_id = self.spectra_id, reaction_id = i + 1)
			

		self.idf_file.set_technique(self.comboTechnique.currentText(), spectra_id=self.spectra_id)
		self.update_comboReactions()
		self.reload_technique()
		# for i in range(self.idf_file.get_number_of_simulations(spectra_id = self.spectra_id)):
		# 	self.idf_file.remove_simulation_entry(self.spectra_id, i)

		self.idf_file.append_simulation_entry(len(reactions), spectra_id = self.spectra_id)
		self.update_comboSimulations()

		self.geo_projectile_in.setText(reactions[0]['incidentparticle'])
		self.geo_projectile_out.setText(reactions[0]['exitparticle'])



	def open(self, fileName = ''):
		if fileName == False:
			if self.ndf_window.isVisible():
				self.ndf_window.close()

			options = QFileDialog.Options()
			fileName, _ = QFileDialog.getOpenFileName(self, "Open IDF file...", "", "IDF Files (*.xml)", options=options)


		if fileName != '':
			self.path = fileName
			self.path_dir = '/'.join(self.path.split('/')[:-1]) + '/'
			if self.path_dir == '/':
				self.path_dir = ''
			self.file = self.path.split('/')[-1]

			print('Opening file...')
			print('Path: %s' %self.path_dir)
			print('File: %s' %self.file)

			## try loading idv
			try:
				pickle_filename = self.path[:-3] + 'idv'
				self.project = load_project(pickle_filename)
				# self.idf_file = self.project.sim_version_history[-1]
				self.idf_file = IDF(self.path)

				self.reload_window()                

				# self.runList.blockSignals(True)
				self.update_runList()
				self.runList.setCurrentRow(self.runList.count()-1)
				# self.runList.blockSignals(False)

				print('Pickle Loaded')

			except Exception as e:
				# raise e
				try:
					self.idf_file = IDF(self.path)
					self.project = project(self.idf_file)
					self.reload_window()
					self.update_runList()
				except Exception as e:
					msg = QMessageBox()
					msg.setIcon(QMessageBox.Information)

					msg.setText("File not recognised")
					msg.setWindowTitle("Error")
					msg.setStandardButtons(QMessageBox.Ok)
					result = msg.exec_()
					if self.debug: raise e
			
			
	def quit(self):
		for window in self.new_windows:
			window.close()
		self.ndf_window.close_window()
		self.close()

	def save_as(self, givenFileName = ''):
		if self.debug: print('NDF_gui, save_as path', givenFileName)
		if givenFileName in ['', False] :
			fileName,_ = QFileDialog.getSaveFileName(self, 'Save File')
			if fileName == '':
				return
		else:
			fileName = givenFileName

		## check if fileName ends with .xml
		if fileName[-4:] != '.xml':
			fileName = fileName + '.xml'

		if fileName != '':
			self.setWindowTitle('IDF Viewer: ' + fileName)

			self.path = fileName
			self.path_dir = '/'.join(self.path.split('/')[:-1]) + '/'
			self.file = self.path.split('/')[-1]

			self.save()
			self.open(fileName)


	def save(self):
		if self.debug: print('NDF_gui, save, path', self.path, '-')
		if self.path is None or self.path == '':
			self.save_as()
			return

		try:
			self.save_geometry_box()
			self.save_elements_box()
			self.save_profile_box()
			self.save_user_notes()      
		except Exception as e:
			if self.debug: raise e
			print('Not saved, check input')
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)

			msg.setText("Not saved, check input")
			msg.setWindowTitle("Error")
			msg.setStandardButtons(QMessageBox.Ok)
			result = msg.exec_()

			return

		self.save_geometry_box_fits()
		self.save_fit_methods_box()

		self.idf_file.save_idf(self.path)
	
	def export_spectrum(self, spectra_id = 0):
		fileName,_ = QFileDialog.getSaveFileName(self, 'Export Spectrum')

		if fileName != '':
			self.idf_file.write_dataxy(fileName)

	def export_fit(self, spectra_id = 0):
		fileName,_ = QFileDialog.getSaveFileName(self, 'Export Spectrum')

		if fileName != '':
			xx, yy = self.idf_file.get_dataxy_fit(spectra_id = 0)
			data = nparray([xx, yy])
			data = data.T

			savetxt(fileName, data)


	
	def about_window(self):
		# about = About_Window()
		self.about_window.show()






	def run_ndf(self):
		if self.debug: print('NDF_gui, run_ndf - main window button clicked')
		if self.idf_file.file_name == '':
			self.save()
		
		if self.idf_file.file_name == '':
			return
				

		# else:
		# 	self.save_state()

		self.ndf_window.update_idf_file_version()

		if ~self.ndf_window.isVisible():
			self.ndf_window.show()

			frame = self.frameGeometry()
			self.ndf_window.move(frame.x() + frame.width(), frame.y())

		self.ndf_window.activateWindow()





	def clear_files(self):
		print('Files cleared')
		ext_toclear = ['.geo','.str', '.prf' ,'.spc', '.bat', 
						'.dat', '.res', '.11', '.01', '.pe',
						'.ord', '.log', '.spx', '.res'
				]

		ext_dir_toclear = ['_idv']

		name = self.file.split('.')[0]

		for ext in ext_toclear:
			files = glob(self.path_dir + name + '*' + ext)
			for f in files:
				remove(f)

		for ext in ext_dir_toclear:
			dirs = glob(self.path_dir + name + '*' + ext)
			for d in dirs:
				rmtree(d)
		
	def clear_idv_file(self):
		name = self.file.split('.')[0] + '.idv'
		files = glob(self.path_dir + name)
		for f in files:
			remove(f)

		self.reload_button()



	def remove_results_from_IDF(self):
		for spectra in range(self.nspectra):
			self.idf_file.remove_results_from_IDF(spectra_id = spectra)

		self.reset_results_box()



	def resize_elements_table(self):
		nrows = self.elements_nelements.value()
		self.elements_table.setRowCount(nrows)
		self.profile_table.setColumnCount(nrows+1)

		labels = ['Thickness']
		for i in range(1,nrows+1):
			labels.append('Conc. Ele. %i' %i)
		self.profile_table.setHorizontalHeaderLabels(labels)

	def resize_profile_table(self):
		ncols = self.profile_nlayers.value()
		self.profile_table.setRowCount(ncols)

	def reload_button(self):
		if self.ndf_window.isVisible():
			self.ndf_window.close()
		
		self.idf_file = IDF(self.path)
		self.open(fileName = self.idf_file.file_path)

		self.runList.setCurrentRow(self.runList.count()-1)
		
	def reload_window(self):
		if self.debug: print('NDF_gui, reload_window - reset_window begins')
		self.reset_window()

		if self.debug: print('NDF_gui, reload_window - reloading begins')
		if self.path != None:
			self.setWindowTitle('IDF Viewer: ' + self.path.split('/')[-1])

			self.notes_user.setText(self.idf_file.user)
			self.notes_note.insertPlainText('\n\n'.join(self.idf_file.description))
			
			self.nspectra = self.idf_file.get_number_of_spectra()
			self.spectra_id = 0
			self.nsims = self.idf_file.get_number_of_simulations(spectra_id = self.spectra_id)

			self.update_comboSpectrum_id()

			technique = self.idf_file.get_technique(spectra_id=self.spectra_id)
			combo_index = self.comboTechnique.findText(technique, flags = Qt.MatchContains)
			self.comboTechnique.setCurrentIndex(combo_index)

			self.set_spectra_box()
			self.set_elements_box()
			self.set_profile_box()

			self.set_geometry_fit_box()
			self.set_models_box()
			try:
				self.set_results_box()
				self.add_menu_to_button(self.copyElements_button)
			except Exception as e:
				if self.debug: raise e
				pass


			self.add_menu_to_button(self.copySpectra_button)
			self.add_menu_to_button(self.copyNDFparam_button)
			self.add_menu_to_button(self.copyGeometry_button)


		if self.debug: print('NDF_gui, reload_window - reloading ends')




	def reset_window(self):
		if self.debug: print('NDF_gui, reset_window - begins')
		# self.inicialize()
		for widget in QApplication.allWidgets():
			for ele2reset in [QLineEdit, QPlainTextEdit]:
				if isinstance(widget, ele2reset):
					widget.clear()
					break
			# if isinstance(widget, QComboBox):
				# widget.setCurrentIndex(-1)
			if isinstance(widget, QTableWidget):
				# print(widget)
				widget.clearContents()

			elif isinstance(widget, QCheckBox):
				widget.setChecked(False)

			# print('aa', widget, isinstance(widget, QWidget))
			# if not isinstance(widget, QWidget):
			#   print('bb', widget)
			#   widget.clear()


			widget.setStyleSheet('QLineEdit' +
								"{"
								"}")

		while self.fitElementLayout.count():
			child = self.fitElementLayout.takeAt(0)
			if child.widget():
				child.widget().deleteLater()

		labels = ['Thickness'] + ['']*self.profile_table_fit_result.columnCount()
		self.profile_table_fit_result.setHorizontalHeaderLabels(labels)

		# set defaults
		if self.debug: print('NDF_gui, reset_window - set all to 0')
		self.comboTechnique.blockSignals(True)
		self.nspectra = 0
		self.spectra_id = 0
		self.nsims = 0
		self.simulation_id = 0
		self.comboTechnique.blockSignals(False)

		if self.debug: print('NDF_gui, reset_window - reset combos')
		self.comboReactions.setVisible(False)
		self.update_comboSpectrum_id()
		self.update_comboReactions()

		self.comboTechnique.blockSignals(True)
		self.comboTechnique.setCurrentIndex(0)
		self.comboTechnique.blockSignals(False)

		self.pileup_param.setText('1e-6')
		self.doublescatter_scaleparam.setText('1')
		self.straggling_scaleparam.setText('1')
		# self.profile_min_thickness.setText('0')
		self.checkCalibration.setChecked(True)
		self.checkCharge.setChecked(True)
		self.checkWindow.setChecked(False)

		if self.debug: print('NDF_gui, reset_window - reset figs')

		try:
			# self.canvas.close()
			self.figure_exp_spectra.clear()
			self.canvas_exp_spectra.draw()
		except Exception as e:
			pass

		try:
			# self.canvas_result.close()
			self.figure_result.clear()
			self.canvas_result.draw()
		except Exception as e:
			pass

		try:
			# self.canvas_profile.close()
			self.figure_profile.clear()
			self.canvas_profile.draw()
		except Exception as e:
			pass

		try:
			# self.canvas_profile.close()
			self.figure_result_advanced.clear()
			self.figure_result_advanced.draw()
		except Exception as e:
			pass


	def reset_results_box(self):
		try:
			self.canvas_result.close()
		except Exception as e:
			pass

		for widget_grand in self.tabResults.children():
			for widget_parent in widget_grand.children():
				for widget in widget_parent.children():
					if isinstance(widget, QLineEdit):
						widget.clear()
					elif isinstance(widget, QTableWidget):
						# widget.clear()
						widget.clearContents()
		
		labels = ['Thickness'] + ['']*self.profile_table_fit_result.columnCount()
		self.profile_table_fit_result.setHorizontalHeaderLabels(labels)


	def convert_window_energy(self, value, channel2energy = True):
		value = int(float(value))

		if self.settings['Appearance'].getboolean('energy_scale_keV'):
			# m, b = 1, 0
			calib = self.idf_file.get_energy_calibration(spectra_id = self.spectra_id) 
			if None not in calib:
				m, b = calib[0], calib[1]

				if channel2energy == False:
					value = (value - b)/m
				else:
					value = m*value + b

				value = '%0.1f'%value

		return value


	def set_geometry_box(self):
		try:
			params = self.idf_file.get_geo_parameters(spectra_id=self.spectra_id) 
			params['window'][0] = self.convert_window_energy(params['window'][0])
			params['window'][1] = self.convert_window_energy(params['window'][1])

		except Exception as e:
			if self.debug: raise e
			return


		pairs_params = {
			'beam_energy' : self.geo_energy,
			'beam_FWHM'   : self.geo_fwhm,
			'window'      : [self.geo_window_min, self.geo_window_max],
			'projectile'  : self.geo_projectile_in,
			'angles'      : [self.geo_angle_in, self.geo_angle_out],
			'dect_solid'  : self.geo_solid_angle,
			'energy_calib': [self.geo_calibration_m, self.geo_calibration_b]
		}       

		for key,element in pairs_params.items():
			if isinstance(element, list):
				if params[key][0]:
					element[0].setText(str(params[key][0]))
					element[1].setText(str(params[key][1]))
				else:
					element[0].setText('')
					element[0].setText('')
					self.set_element_color(element[0], "QLineEdit")
					self.set_element_color(element[1], "QLineEdit")
			else:
				if params[key]:
					element.setText(str(params[key]))
				else:
					element.setText('')
					self.set_element_color(element, "QLineEdit")

		combo_index = self.geo_geometry.findText(params['geometry'], flags = Qt.MatchContains)
		self.geo_geometry.setCurrentIndex(combo_index)          

		if combo_index == -1:
			self.set_element_color(self.geo_geometry, 'QComboBox')

		if params[key]:
			self.geo_charge.setText(self.idf_file.get_charge(self.spectra_id))
		else:
			self.geo_charge.setText('')
			self.set_element_color(self.geo_charge, "QLineEdit")

		technique = self.comboTechnique.currentText()

		if technique == 'RBS':
			self.geo_projectile_out.setText(params['projectile'])
		elif technique == 'PIXE':
			self.geo_projectile_out.setText('X-Ray')
		elif technique == 'SIMS':
			particles = self.idf_file.get_SIMS_particles(spectra_id=self.spectra_id)
			if particles is not None:
				self.geo_projectile_out.setText(' '.join(particles))
		elif technique == 'ERDA':
			reactions = self.idf_file.get_reactions(spectra_id=self.spectra_id)

			if reactions is not None:
				exitparticle = reactions[0]['exitparticle']
				if exitparticle is None:
					exitparticle = ''
				
				self.geo_projectile_out.setText(exitparticle)



	
	
	def set_geometry_fit_box(self):
		pairs = {
			'energy':{
				'check' : self.checkEnergy,
				'field' : self.geo_energy_fit,
				'method': self.idf_file.get_beam_energy_fitparam},
			'fwhm'  :{
				'check' : self.checkFWHM,
				'field' : self.geo_fwhm_fit,
				'method': self.idf_file.get_beam_energy_spread_fitparam},
			'window_min': {
				'check' : self.checkWindow,
				'field' : self.geo_window_min,
				'method': self.idf_file.get_window_min},
			'window_max': {
				'check' : self.checkWindow,
				'field' : self.geo_window_max,
				'method': self.idf_file.get_window_max},
			# 'angle_in'  :{
			# 	'check' : self.checkAngles,
			# 	'field' : self.geo_angle_in_fit,
			# 	'method': self.idf_file.get_incident_angle_fitparam},
			# 'angle_out' :{
			# 	'check' : self.checkAngles,
			# 	'field' : self.geo_angle_out_fit,
			# 	'method': self.idf_file.get_scattering_angle_fitparam},
			'angles':{
					'check': self.checkAngles,
					'field': [self.geo_angle_in_fit, self.geo_angle_out_fit],
					'method': self.idf_file.get_angles_fitparam},
			'charge'    :{
				'check' : self.checkCharge,
				'field' : None, 
				'method': self.idf_file.get_charge_fitparam},
			'calibration':{
				'check' : self.checkCalibration,
				'field' : None, 
				'method': self.idf_file.get_energy_calibration_fitparam},
			'foil':{
				'check': self.ndf_more_options_window.checkFoil,
				'field': [self.ndf_more_options_window.foilMaterialCombo, self.ndf_more_options_window.foilMaterialThickness],
				'method': self.idf_file.get_detector_foil},
			'rutherford':{
				'check': self.ndf_more_options_window.checkRutherford,
				'field': None,
				'method': self.idf_file.get_rutherford_cross},

		}

		# self.ndf_more_options_window.checkFoil.setChecked(True)

		for k, p in pairs.items():
			value = p['method'](spectra_id = self.spectra_id, simulation_id=self.simulation_id)

			if 'window' in k:
				value = self.convert_window_energy(value)

			if k == 'calibration':
				p['check'].setChecked(value == ['True', 'True'])
			elif k == 'charge':
				p['check'].setChecked(value == 'True')
			elif k == 'foil':
				if value[0] == '': value[0] = None
				p['check'].setChecked(value[0] != None)
				p['field'][0].setEnabled(value[0] != None)
				p['field'][1].setEnabled(value[0] != None)

				if value[0] != None:
					combo_index = p['field'][0].findText(value[0].capitalize(), flags = Qt.MatchContains)
					p['field'][0].setCurrentIndex(combo_index)
					p['field'][1].setText(value[1])
			elif k == 'rutherford':
				if value[0] != None:
					p['check'].setChecked(not value[0])


			elif isinstance(value, list):
				if None in value or '' in value:
					p['check'].setChecked(False)
					p['field'][0].setEnabled(False)
					p['field'][1].setEnabled(False)

				else:
					p['check'].setChecked(True)
					p['field'][0].setEnabled(True)
					p['field'][1].setEnabled(True)

					if not isinstance(value[0], str): value[0] = str(value[0])
					if not isinstance(value[1], str): value[1] = str(value[1])
					
					p['field'][0].setText(value[0])
					p['field'][1].setText(value[1])

			elif value is None:
				p['check'].setChecked(False)
				p['field'].setEnabled(False)

			else:
				p['check'].setChecked(True)
				p['field'].setEnabled(True)
				if not isinstance(value, str): value = str(value)
				p['field'].setText(value) 


	def set_models_box(self):
		pairs = {
			'pileup':{
				'check': self.checkPileup,
				'model': self.comboPileup,
				'param': self.pileup_param,
				'method': self.idf_file.get_model_pileup
			},
			'doublescattering':{
				'check': self.checkDoublescatter,
				'model': self.comboDoublescatter,
				'param': self.doublescatter_scaleparam,
				'method': self.idf_file.get_model_doublescatter
			},
			'straggling':{
				'check': self.checkStraggling,
				'model': self.comboStraggling,
				'param': self.straggling_scaleparam,
				'method': self.idf_file.get_model_straggling
			},
			'energyloss':{
				'check': self.checkEnergyloss,
				'model': self.comboEnergyloss,
				'param': None,
				'method': self.idf_file.get_model_energyloss
			},
			'adhoc_corection':{
				'check': self.checkAdhoc_correction,
				'model': self.adhoc_element,
				'param': self.adhoc_parameters,
				'method': self.idf_file.get_model_adhoc_correction
			},

		}

		for k, p in pairs.items():
			code, param, model = p['method'](spectra_id=self.spectra_id, simulation_id = self.simulation_id)

			if None in [code, param, model]:
				p['check'].setChecked(False)
				p['model'].setEnabled(False)
				if p['param'] is not None: p['param'].setEnabled(False)
			else:
				p['check'].setChecked(True)
				p['model'].setEnabled(True)
				if p['param'] is not None: p['param'].setEnabled(True)

				if isinstance(p['model'], QComboBox):
					combo_index = p['model'].findText(model.capitalize(), flags = Qt.MatchContains)
					p['model'].setCurrentIndex(combo_index)
				else:
					p['model'].setText(model)

				if p['param'] is not None: 
					if not isinstance(param, str): param = str(param)
					p['param'].setText(param)


	def set_sample_fit_box(self):
		self.fitElementArea.setWidgetResizable(True)

		fit_checked = []
		while self.fitElementLayout.count():
			child = self.fitElementLayout.takeAt(0)
			if child.widget():
				if child.widget().isChecked():
					fit_checked.append(True)
				else:
					fit_checked.append(False)

				child.widget().deleteLater()


		nrows = self.elements_table.rowCount()

		for i in range(nrows):
			name = self.elements_table.item(i,0)
			if name is None: 
				name = ''
			else:
				name = name.text().strip()
			# if name.strip() != '':
			checkBox = QCheckBox(name)
			self.fitElementLayout.addWidget(checkBox)


		for i in range(min(len(fit_checked), self.fitElementLayout.count())):
			self.fitElementLayout.itemAt(i).widget().setChecked(fit_checked[i])


	def load_results(self, index_run = None):
		if self.debug: print('NDF_gui, load_results - begins')
		self.update_runList()		

		try:
			# need to reload the file from the disk because IDF2NDF (of NDF) changes 
			# the file (adds the file ids used for output)
			if index_run is None:
				index_run = 0

			self.idf_file  = self.project.reload_idf_file(-(index_run + 1))

			self.runList.blockSignals(True)
			self.runList.setCurrentRow(index_run)
			self.runList.blockSignals(False)

			for i in range(self.idf_file.get_number_of_spectra()):
				self.idf_file.set_spectra_result(spectra_id = i)
				self.idf_file.set_geometry_result(spectra_id = i)
				self.idf_file.set_elements_result(spectra_id = i)
				self.idf_file.set_profile_result(spectra_id  = i)
			
			self.set_results_box()

			self.idf_file.save_idf(self.idf_file.file_path)
			self.project.save()

			run_states = self.project.check_simulations_running()
			if True not in run_states:
				self.pushLoad_results.setEnabled(False)
				if not self.settings['Actions'].getboolean('keep_NDF_files'):			
					self.clear_files()


		except Exception as e:
			if self.debug: raise e
			print('Result files not found')
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)

			msg.setText("Result files not found")
			# msg.setInformativeText("This is additional information")
			msg.setWindowTitle("Error")
			# msg.setDetailedText("The details are as follows:")
			msg.setStandardButtons(QMessageBox.Ok)
			# buttonAdd = msg.button(QMessageBox.Open)
			result = msg.exec_()
		

	def change_idf_version(self):
		if self.path == None:
			return

		if self.debug: print('NDF_gui, change_idf_version - begins')


		index_run = self.runList.currentRow()
		text_run = self.runList.currentItem().text()


		if 'In xml file' == text_run:
			self.idf_file = IDF(self.path)
		else:
			if self.debug: print('NDF_gui, change_idf_version - deep copy made of i:', index_run)

			if '[R]' in text_run:
				self.load_results(index_run = index_run)
			else:
				self.idf_file = deepcopy(self.project.sim_version_history[-(index_run + 1)])
		

		if self.debug: print('NDF_gui, change_idf_version - ',  self.idf_file.path_dir)

		spectra_id_old = self.spectra_id
		if self.debug: print('NDF_gui, change_idf_version - reload window')
		self.reload_window()
		if self.debug: print('NDF_gui, change_idf_version - change spectra_id')
		self.spectra_id = spectra_id_old

		if self.ndf_window.isVisible():
			self.ndf_window.update_idf_file_version()



	def set_results_box(self):
		self.set_spectra_fit_result_tab()
		self.set_geometry_fit_result_tab()
		self.set_elements_fit_result_tab()
		self.set_profile_fit_result_tab()

	def set_spectra_fit_result_tab(self):
		self.figure_result.clear()

		data_y_list = []
		reactions = self.idf_file.get_reactions(spectra_id = self.spectra_id)
		if reactions is None:
			nreactions = 1
			reactions = [{'code':''}]
		else:
			nreactions = len(reactions)

		for i in range(nreactions):
			data_x_fit, data_y_fit = self.idf_file.get_dataxy_fit(spectra_id = self.spectra_id, simulation_id = i)
			data_y_list.append(data_y_fit)

		data_x_given, data_y_given = self.idf_file.get_dataxy(spectra_id = self.spectra_id)

		if data_x_fit is None or len(data_x_given) == 0:
			data_x_given, data_y_given = [], []

		self.ax_result = self.figure_result.add_subplot(111)

		if 'PIXE' == self.idf_file.get_technique(spectra_id=self.spectra_id):
			self.ax_result.stem(data_x_given, data_y_given, basefmt = ' ', label = 'Exp.')
			self.ax_result.scatter(data_x_fit, data_y_fit, marker = '_', s = 250, color = 'r', label = 'Fit')
			self.ax_result.set_xlabel('Element/Line')
			self.ax_result.set_ylabel('Line Area')
			self.ax_result.legend(frameon=False)
			self.ax_result.set_yscale('log')


		elif 'SIMS' == self.idf_file.get_technique(spectra_id=self.spectra_id):
			for particle, profile in data_y_given.items():
				self.ax_result.plot(data_x_given, profile, label = r'%s'%latex_atom(particle))
			for particle, profile in data_y_fit.items():
				self.ax_result.plot(data_x_fit, profile, '--', color = (0.2,0.2,0.2))

			self.ax_result.plot([],[], '--', color = (0.2,0.2,0.2), label = 'Fit')

			self.ax_result.set_yscale('log')
			self.ax_result.set_xlabel(r'Depth ($\mu$m)')
			self.ax_result.legend(frameon = False, ncol= 2, loc='center left', bbox_to_anchor=(1, 0.5))

		else:
			cut_channel_min = int(self.settings['Appearance']['cut_off_channel'])
			cut_channel_max = len(data_x_given)
			# to account for pure simulation cases
			if cut_channel_max == 0: cut_channel_max = len(data_y_fit)
			
			m = 1
			b = 0
			data_y_sum = npzeros_like(data_y_list[0])

			for i in range(nreactions):
				## get calibration
				if self.settings['Appearance'].getboolean('energy_scale_keV'):
					calib = self.idf_file.get_energy_calibration_fit_result(spectra_id = self.spectra_id, simulation_id = i) 
					if calib is not None:
						m, b = calib[0], calib[1]
					else:
						m, b = 1, 0
				
				# get the fit for this reaction
				data_y_fit = data_y_list[i]
				# add to the total (this will be wrong if different calibrations are used and the plot is in energy)
				data_y_sum = data_y_sum + data_y_fit


				if i == 0:			
					self.ax_result.plot(m*nparray(data_x_given[cut_channel_min:cut_channel_max]) + b, data_y_given[cut_channel_min:cut_channel_max], 'o', ms = 2, label = 'Exp.')

				self.ax_result.plot(m*nparray(data_x_fit[cut_channel_min:cut_channel_max]) + b, data_y_fit[cut_channel_min:cut_channel_max], label = 'Fit ' + reactions[i]['code'])

				# this condition is separeted from the one above so that the plot looks more organized
				# if i == nreactions - 1 and i != 0:
				# 	self.ax_result.plot(m*nparray(data_x_fit[cut_channel_min:cut_channel_max]) + b, data_y_sum[cut_channel_min:cut_channel_max], ms = 2, label = 'Fit. Total')
				
				if self.settings['Appearance'].getboolean('show_elemental_fits'):
					try:
						data_ele = self.idf_file.get_elemental_dataxy_fit(spectra_id = self.spectra_id, simulation_id = i)

						for name, y in data_ele.items():
							if name == 'x':
								continue
							self.ax_result.plot(m*nparray(data_ele['x'][cut_channel_min:cut_channel_max]) + b, y[cut_channel_min:cut_channel_max], '--', label = name + ' ' + reactions[i]['code'])
					except Exception as e:
						if self.debug: raise e							
						pass

			if self.settings['Appearance'].getboolean('energy_scale_keV'):
				self.ax_result.set_xlabel('Energy (keV)')
			else:
				self.ax_result.set_xlabel('Energy (Channels)')
			self.ax_result.legend(frameon=False, ncol = 2)



		
		
		self.ax_result.set_yticklabels([])
		self.figure_result.tight_layout()

		self.canvas_result.draw()

	def set_geometry_fit_result_tab(self):
		pairs = {
			'energy':{
						'field' : self.geo_energy_fit_result, 
						'method': self.idf_file.get_beam_energy_fit_result
					},
			'fwhm'  :{
						'field' : self.geo_fwhm_fit_result,
						'method': self.idf_file.get_beam_energy_spread_fit_result
					},
			'angle_in':{
						'field' : self.geo_angle_in_fit_result,
						'method': self.idf_file.get_incident_angle_fit_result
					},
			'angle_out':{
						'field' : self.geo_angle_out_fit_result,
						'method': self.idf_file.get_scattering_angle_fit_result
					},
			'charge':{
						'field' : self.geo_charge_fit_result,
						'method': self.idf_file.get_charge_fit_result
					},
			'calibration':{
						'field' : [self.geo_calibration_m_fit_result, self.geo_calibration_b_fit_result],
						'method': self.idf_file.get_energy_calibration_fit_result
					},
			}


		for k,p in pairs.items():
			value = p['method'](spectra_id = self.spectra_id, simulation_id = self.simulation_id)

			if isinstance(value, list):
				for v,f in zip(value, p['field']):
					f.setText(str(v))
			elif value is not None:
				value = float(value)
				p['field'].setText(str(value))





	def set_elements_fit_result_tab(self):
		elements = self.idf_file.get_elements_fit_result(spectra_id=self.spectra_id, simulation_id=self.simulation_id)
		elements_initial = self.idf_file.get_elements()

		if (elements is None) or (elements['nelements'] is None):
			return

		self.elements_table_fit_result.setRowCount(int(elements['nelements']))
		self.elements_table_fit_result_initial.setRowCount(int(elements['nelements']))


		i = 0
		for key, param in elements.items():
			if key != 'nelements':
				param = param.replace('?=', '')
				param = pretty_formula_ratio(param)
				item = QTableWidgetItem(param)
				self.elements_table_fit_result.setItem(i,0,item)                
				i += 1
		
		i = 0
		for key, param in elements_initial.items():
			if key != 'nelements':
				param['name'] = param['name'].replace('?=', '')
				item = QTableWidgetItem(param['name']) 
				self.elements_table_fit_result_initial.setItem(i,0,item)
				i += 1   

		self.add_menu_to_button(self.copyElements_button)                               
	
	def set_profile_fit_result_tab(self):
		if self.debug: print('NDF_gui, set_profile_fit_result_tab begins')
		profile_params = self.idf_file.get_profile_fit_result(spectra_id=self.spectra_id, simulation_id=self.simulation_id)

		if (profile_params is None) or (profile_params['nlayers'] in [None, '0']):
			return

		self.nlayers_fit_result.setText(profile_params['nlayers'])
		self.profile_table_fit_result.setRowCount(int(profile_params['nlayers']))
		self.profile_table_fit_result.setColumnCount(len(profile_params['names']) + 1)

		names = [simplify_atomic_formula(n) for n in profile_params['names']]
		labels = ['Thickness', *names]
		self.profile_table_fit_result.setHorizontalHeaderLabels(labels)


		col = 0
		row = 0
		i = 0
		for key, param in profile_params.items():
			if key in ['nlayers', 'names']:
				continue
			item = QTableWidgetItem(param['thickness']) 
			self.profile_table_fit_result.setItem(i,0,item)

			for j,conc in enumerate(param['concentrations']):
				item = QTableWidgetItem(conc) 
				self.profile_table_fit_result.setItem(i,j+1,item)


									
			i+=1

		self.set_profile_fit_result_plot(profile_params)

	def set_profile_fit_result_plot(self, profile_params):
		# try:
		#   self.profile_fit_result_plot.removeWidget(self.canvas_profile)
		# except:
		#   pass
		self.figure_profile.clear()
		

		self.ax_profile = self.figure_profile.add_subplot(111)
		

		for i,name in enumerate(profile_params['names']):
			xx = [0]
			yy = [0]

			for k,p in profile_params.items():
				if k in ['nlayers', 'names']:
					continue
				if k != int(profile_params['nlayers'])-1:
					xx.append(float(p['thickness']) + xx[-1])
					yy.append(float(p['concentrations'][i]))
				else:
					xx.append(1.2*xx[-1])
					yy.append(float(p['concentrations'][i]))

			yy[0] = yy[1]
			xx_step = [xx[0]]*2
			yy_step = [yy[0]]*2
			for x,y in zip(xx[1:], yy[1:]):
				xx_step.append(x)
				xx_step.append(x)
				yy_step[-1] = y
				yy_step.append(y)
				yy_step.append(y)
			
			self.ax_profile.plot(xx_step, yy_step,'o--', label = r'%s'%simplify_atomic_formula(name))

		self.ax_profile.legend(ncol=7, loc = 'upper center', frameon=False)
		self.ax_profile.set_ylim(-5, 180)
		self.ax_profile.set_xlabel(r'Thickness (1$\times 10^{15}$ at/cm$^2$)')
		self.ax_profile.set_ylabel('Fraction (%)')
		self.figure_profile.tight_layout(rect = (0,-0.05,1,1.05))


		# self.canvas_profile = FigureCanvas(self.figure_profile)
		# self.profile_fit_result_plot.addWidget(self.canvas_profile)
		self.canvas_profile.draw()

		# this try here to permit the reuse of this method in the NDF_Fit_Figure class
		try:
			if self.radio_profile_graph.isChecked():
				self.profile_fit_result_plot_frame.setVisible(True)
			else:
				self.profile_fit_result_plot_frame.setVisible(False)
		except:
			pass


	
	
	def delete_spectrum(self):
		if self.ndf_window.isVisible():
			self.ndf_window.close()

		oldIndex = self.comboSpectrum_id.currentIndex()

		self.idf_file.delete_spectrum(spectra_id=self.spectra_id)
		self.nspectra = self.idf_file.get_number_of_spectra()       
		self.update_comboSpectrum_id()

		self.spectra_id = oldIndex
		
		self.set_spectra_box()
	

	def append_spectrum(self):
		if self.ndf_window.isVisible():
			self.ndf_window.close()

		self.save_geometry_box()

		options = QFileDialog.Options()
		file_names, _ = QFileDialog.getOpenFileNames(self, "Open spectrum file...", ""	, "All Files (*)", options=options)
		

		for file in file_names:
			self.nspectra +=1
			self.idf_file.append_spectrum_entry(self.nspectra)
			self.load_spectrum(spectra_id = self.nspectra - 1, fileName = file)


		# to change the window to the last spectrum, i.e. the appended one
		self.spectra_id = self.nspectra - 1



	def load_spectrum(self, spectra_id=False, fileName = False):
		if fileName == False:
			options = QFileDialog.Options()
			fileName, _ = QFileDialog.getOpenFileName(self, "Open spectrum file...", ""	, "All Files (*)", options=options)
		

		if spectra_id == False:
			spectra_id = self.spectra_id


		if fileName != '':
			try:
				with open(fileName, 'r') as file:
					line1 = file.readline()

				if 'GUPIX' in line1:
					self.idf_file.load_pixe_data_from_file(fileName, spectra_id=spectra_id)
					# self.idf_file.set_technique('PIXE', spectra_id=spectra_id)
					# self.comboTechnique.setCurrentIndex(2)
					technique = 'PIXE'
					technique_id = 2
				elif 'SIMS' in fileName:
					self.idf_file.set_SIMS_from_file(fileName, spectra_id=spectra_id)
					# self.idf_file.set_technique('SIMS', spectra_id=spectra_id)
					# self.comboTechnique.setCurrentIndex(4)
					technique = 'SIMS'
					technique_id = 4
				else:
					if len(line1.split()) == 8:
						mode = '8 columns'
						technique = 'RBS'
						technique_id = 0
					elif '[DISPLAY]' in line1:
						mode = 'potku'
						technique = 'ERDA'
						technique_id = 3
					else:
						mode = 'channels vs yield'
						technique = 'RBS'
						technique_id = 0


					self.idf_file.set_spectrum_data_from_file(fileName, mode = mode, spectra_id=spectra_id)
			
				# set technique to RBS since it will be the most commonly used
				self.idf_file.set_technique(technique, spectra_id=spectra_id)                   
				self.comboTechnique.setCurrentIndex(technique_id)      
				# self.reload_technique()


				if self.nspectra == 0: self.nspectra = 1


				self.set_spectrum_box()
				self.update_comboSpectrum_id()

				## set initial window
				datax, _ = self.idf_file.get_dataxy(spectra_id = spectra_id)
				self.idf_file.set_window_min(datax.min(), spectra_id = spectra_id)
				self.idf_file.set_window_max(datax.max(), spectra_id = spectra_id)
				self.geo_window_min.setText(str(datax.min()))
				self.geo_window_max.setText(str(datax.max()))



			except Exception as e:
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Information)

				msg.setText("File not recognised")
				msg.setWindowTitle("Error")
				msg.setStandardButtons(QMessageBox.Ok)
				result = msg.exec_()

				if self.debug: raise e


	def reload_technique(self):
		try:
			reactions = self.idf_file.get_reactions(spectra_id=self.spectra_id)
		except Exception as e:
			reactions = None
			# if self.debug: raise e

		text_fields = [self.geo_energy, self.geo_fwhm,  self.geo_projectile_in, self.geo_projectile_out,
					   self.geo_charge, self.geo_geometry,  self.geo_angle_in, self.geo_angle_out,
					   self.geo_solid_angle, self.geo_calibration_m, self.geo_calibration_b,
					   self.label_geo_charge, self.label_geo_geometry,  self.label_geo_angles
			]

		invisible_list = [self.comboReactions, 
						  self.geo_charge, self.geo_geometry, self.geo_angle_in, self.geo_angle_out, 
						  self.label_geo_charge, self.label_geo_geometry, self.label_geo_angles,
						  self.checkAngles, self.checkCharge, self.geo_angle_in_fit, self.geo_angle_out_fit
						  ]


		for field in text_fields:
			field.setEnabled(True)
			field.setVisible(True)
		for widget in invisible_list:
			widget.setVisible(True)

		self.geo_calibration_m.setFixedWidth(83)
		self.geo_calibration_m.setReadOnly(False)
		self.geo_projectile_out.setEnabled(False)


		if self.comboTechnique.currentText() == 'SIMS':
			for widget in invisible_list:
				widget.setVisible(False)

			# self.gridLayout.removeWidget(self.geo_charge)
			# self.gridLayout.removeWidget(self.geo_geometry)
			# self.gridLayout.removeWidget(self.geo_angle_in)
			# self.gridLayout.removeWidget(self.geo_angle_out)

			# self.gridLayout.removeWidget(self.label_geo_charge)
			# self.gridLayout.removeWidget(self.label_geo_geometry)
			# self.gridLayout.removeWidget(self.label_geo_angles)

			# self.gridLayout.addWidget(self.geo_projectile_out, 4,1,1,-1)

			self.label_geo_fwhm.setText('Resolution')
			self.checkFWHM.setText('Resolution')


			# self.gridLayout.addItem(self.spacerItem)
			self.gridLayout_3.addItem(self.spacerItem_result)
			

		elif self.comboTechnique.currentText() == 'RBS':
			self.geo_projectile_in.setReadOnly(False)
			self.geo_projectile_out.setReadOnly(True)
			# self.geo_projectile_in.setText(reactions[0]['incidentparticle'])
			# self.geo_projectile_out.setText(self.geo_projectile_in.text())

			if reactions is not None:
				if len(reactions)>2:
					self.comboReactions.setVisible(True)
					self.update_comboReactions()
				else:
					self.comboReactions.setVisible(False)	
			else:
				self.comboReactions.setVisible(False)



		elif self.comboTechnique.currentText() == 'NRA':
			self.comboReactions.setVisible(True)
			
			self.update_comboReactions()
			# if len(reactions)>1:
			#   self.comboReactions.setText('Reactions')
			# else:
			#   self.comboReactions.setText(reactions[0]['code'])

			self.geo_projectile_in.setReadOnly(True)
			self.geo_projectile_out.setReadOnly(True)
			# self.geo_projectile_in.setText(reactions[0]['incidentparticle'])
			self.geo_projectile_out.setText('-')


		elif self.comboTechnique.currentText() == 'PIXE':
			self.comboReactions.setVisible(False)
			self.geo_projectile_in.setReadOnly(False)
			self.geo_projectile_out.setReadOnly(True)
			self.geo_projectile_out.setText('X-Ray')
			self.geo_calibration_b.setVisible(False)
			self.geo_calibration_m.setFixedWidth(140)
			self.geo_calibration_m.setReadOnly(True)



		elif self.comboTechnique.currentText() == 'ERDA':
			self.geo_projectile_in.setReadOnly(False)
			self.geo_projectile_out.setReadOnly(True)
			self.comboReactions.setVisible(True)
			self.update_comboReactions()


		# self.save_geometry_box()



	def reload_geoprojout(self):
		# schedule for deletion
		if self.comboTechnique.currentText() =='RBS':
			self.geo_projectile_out.setText(self.geo_projectile_in.text())





	

	def reload_spectra_box(self):
		technique = self.idf_file.get_technique(spectra_id=self.spectra_id)
		if technique in ['RBS', 'NRA', 'PIXE', 'ERDA', 'SIMS']:
			combo_index = self.comboTechnique.findText(technique, flags = Qt.MatchContains)
		else:
			combo_index = -1
		self.comboTechnique.setCurrentIndex(combo_index)

		self.set_spectra_box()

	def reload_models_box(self):
		self.update_comboSimulations()

	def set_spectra_box(self):
		self.set_spectrum_box()
		self.set_geometry_box()

	def set_spectrum_box(self):
		self.figure_exp_spectra.clear()

		# self.figure = plt.figure(figsize=(5,2))
		self.ax = self.figure_exp_spectra.add_subplot(111)


		try:
			data_x, data_y = self.idf_file.get_dataxy(spectra_id=self.spectra_id)
		except Exception as e:
			print('Something wrong with the data')
			if self.debug: raise e
			return


		if 'PIXE' in [self.comboTechnique.currentText(), self.idf_file.get_technique(spectra_id=self.spectra_id)]:
			self.ax.stem(data_x, data_y, basefmt = ' ')
			self.ax.set_xlabel('Element/Line')
			self.ax.set_ylabel('Line Area')
			self.ax.set_yscale('log')

		elif 'SIMS' in [self.comboTechnique.currentText(), self.idf_file.get_technique(spectra_id=self.spectra_id)]:
			for particle, profile in data_y.items():
				self.ax.plot(data_x, profile, label = r'%s'%latex_atom(particle))

			self.ax.set_yscale('log')
			self.ax.set_xlabel(r'Depth ($\mu$m)')
			self.ax.legend(frameon = False, loc='center left', bbox_to_anchor=(1, 0.5))

		else:
			cut_channel = int(self.settings['Appearance']['cut_off_channel'])

			m = 1
			b = 0
			if self.settings['Appearance'].getboolean('energy_scale_keV'):
				calib = self.idf_file.get_energy_calibration(spectra_id = self.spectra_id) 
				if None not in calib:
					m, b = calib[0], calib[1]


			self.ax.plot(m*data_x[cut_channel:] + b, data_y[cut_channel:])
			if self.settings['Appearance'].getboolean('energy_scale_keV'):
				self.ax.set_xlabel('Energy (keV)')
			else:
				self.ax.set_xlabel('Energy (Channels)')

		self.ax.set_yticklabels([])
		self.figure_exp_spectra.tight_layout()


		# self.canvas = FigureCanvas(self.figure)
		# self.spectra_plot.addWidget(self.canvas)
		self.canvas_exp_spectra.draw()

	def set_elements_box(self): 
		if self.debug: print('NDF_gui, set_elements_box begins')
		nelements = self.idf_file.get_nelements()

		if nelements:
			self.elements_nelements.setValue(nelements)
		else:
			self.set_element_color(self.elements_nelements, "QSpinBox")


		elements = self.idf_file.get_elements()

		if elements is None:
			self.set_element_color(self.elements_table, "QTableWidget")
			return

		i= 0
		fitted = False
		for key, param in elements.items():
			if key == 'nelements':
				continue

			if '?=' in param['name']:
				param['name'] = param['name'].replace('?=','')
				fitted = True

			item = QTableWidgetItem(param['name'])
			self.elements_table.setItem(i,0,item)
			item = QTableWidgetItem(str(param['density'])) 
			self.elements_table.setItem(i,1,item)
			item = QTableWidgetItem(str(param['concentration'][0])) 
			self.elements_table.setItem(i,2,item)
			item = QTableWidgetItem(str(param['concentration'][1])) 
			self.elements_table.setItem(i,3,item)
			item = QTableWidgetItem(str(param['depth'][0])) 
			self.elements_table.setItem(i,4,item)
			item = QTableWidgetItem(str(param['depth'][1])) 
			self.elements_table.setItem(i,5,item)
	
			if fitted:
				self.fitElementLayout.itemAt(i).widget().setChecked(True)
				fitted = False


			i+=1

	def tidy_elements_table(self):
		font = QFont()
		font.setBold(True)
		
		for i in range(self.elements_table.rowCount()):
			for j in range(self.elements_table.columnCount()):
				item = self.elements_table.item(i, j)
				if item is not None:
					if j == 0:
						item.setFont(font)
					item.setTextAlignment(Qt.AlignCenter)


	
	def set_profile_box(self):
		if self.debug: print('NDF_gui, set_profile_box begins')
		nlayers = self.idf_file.get_nlayers()

		if nlayers:
			self.profile_nlayers.setValue(nlayers)
		else:
			self.set_element_color(self.profile_nlayers, "QSpinBox")
		
		try:
			layers = self.idf_file.get_profile()
			elements = self.idf_file.get_elements()
		except:
			return


		ele_ids = [0]*elements['nelements']
		for key, params in elements.items():
			if key == 'nelements':
				continue

			params['name'] = params['name'].replace('?=', '')
			ele_ids[key] = params['name']

		if layers:
			i= 0
			for key, param in layers.items():
				if key in ['nlayers', 'names']:
					continue

				item = QTableWidgetItem(str(param['thickness'])) 
				self.profile_table.setItem(i,0,item)

				for j, conc in enumerate(param['concentrations']):
					if str(conc) == None:
						conc = 0
					item = QTableWidgetItem(str(conc))

					ele_name = layers['names'][j]
					ele_id = ele_ids.index(ele_name)
					
					self.profile_table.setItem(i, ele_id+1, item)                         

				i+=1
		else:           
			self.set_element_color(self.profile_table, "QTableWidget")


		self.profile_min_thickness.setText(self.idf_file.get_min_thickness())
		self.profile_max_thickness.setText(self.idf_file.get_max_thickness())

	def tidy_profile_table(self):		
		for i in range(self.profile_table.rowCount()):
			for j in range(self.profile_table.columnCount()):
				item = self.profile_table.item(i, j)
				if item is not None:
					item.setTextAlignment(Qt.AlignCenter)

			
	def set_element_color(self, qElement, qType):
		# qElement.setStyleSheet(qType +
		#                       "{"
		#                       "border : 1px solid red;"
		#                       # "background-color : lightgreen;"
		#                       "}")
		pass

	
	def save_user_notes(self):
		user = self.notes_user.text()
		notes = self.notes_note.toPlainText()

		self.idf_file.set_user(user)
		self.idf_file.set_note(notes)

	def save_geometry_box(self, target_spectra_id = ''):
		pairs = [
			{'field': self.geo_energy, 'method': self.idf_file.set_beam_energy},
			{'field': self.geo_fwhm, 'method': self.idf_file.set_beam_energy_spread},
			{'field': self.geo_charge, 'method': self.idf_file.set_charge},
			{'field': self.geo_angle_in, 'method': self.idf_file.set_incident_angle},
			{'field': self.geo_angle_out, 'method': self.idf_file.set_scattering_angle},
			{'field': self.geo_solid_angle, 'method': self.idf_file.set_detector_solid_angle},
		]

		for pair in pairs:
			try:
				text = pair['field'].text()
				if text not in ['', None]:
					_  = float(text)
			except Exception as e:
				print(e)
				self.error_window.setText('Check geometry input\n' + str(e))
				self.error_window.exec_()

		pairs.append({'field': self.geo_projectile_in, 'method': self.idf_file.set_beam_particles})

		if target_spectra_id == '':
			spectra_id = self.spectra_id
		else:
			spectra_id = target_spectra_id


		for p in pairs:
			value = p['field'].text()
			if value != '-':
				p['method'](value, spectra_id=spectra_id)
		
		
		geometry = self.geo_geometry.currentText()
		self.idf_file.set_geometry_type(geometry, spectra_id=spectra_id)
		

		technique = self.comboTechnique.currentText()
		self.idf_file.set_technique(technique, spectra_id=spectra_id)


		if technique == 'RBS':
			reaction = {
				'initialtargetparticle': '',
				'incidentparticle': self.geo_projectile_in.text(),
				'exitparticle': self.geo_projectile_in.text(),
				'finaltargetparticle': '',
				'reactionQ': '',
				'code':'(%s, %s)' %(self.geo_projectile_in.text(), self.geo_projectile_out.text())
				}
			self.idf_file.set_reactions(reaction, append = False, spectra_id=spectra_id)
		
		elif technique == 'PIXE':
			reaction = {
				'initialtargetparticle': '',
				'incidentparticle': self.geo_projectile_in.text(),
				'exitparticle': 'X',
				'finaltargetparticle': '',
				'reactionQ': '',
				'code':''
				}
			self.idf_file.set_reactions(reaction, append = False, spectra_id=spectra_id, linked_calibrations = False)
		
		
		if technique in ['RBS', 'NRA', 'ERDA']:
			reaction_id = self.comboReactions.currentIndex()
			if reaction_id is None:
				reaction_id = 0

			m_calib = self.geo_calibration_m.text()
			b_calib = self.geo_calibration_b.text()
			self.idf_file.set_energy_calibration(m_calib, b_calib, spectra_id=spectra_id, reaction_id = reaction_id)



	def save_elements_box(self):
		nrows = self.elements_table.rowCount()
		ncols = self.elements_table.columnCount()

		molecules = {'nelements': nrows}
		col_params = []

		# delete empty rows
		rows_del = []
		for i in range(nrows):
			col_params = []

			for j in range(ncols):
				param = self.elements_table.item(i,j)
				if param is None:
					param_text = ''
				else:
					param_text = param.text()
				col_params.append(param_text)

			if col_params == ['', '', '', '', '', '']:
				rows_del.append(i)
				
				
		for row in rows_del:
			self.elements_table.removeRow(row)

		nrows = nrows - len(rows_del)
		if nrows < 1:
			nrows = 1

		self.elements_nelements.setValue(nrows)
		self.resize_elements_table()	

		for i in range(nrows):
			col_params = []

			for j in range(ncols):
				param = self.elements_table.item(i,j)
				if param is None:
					param = ''
				else:
					param = param.text()
				col_params.append(param)

			name = col_params[0]

			

			if name == '':
				self.set_element_color(self.elements_table, 'QTableWidget')
				# self.error_window.setText('Elements not well defined')
				# self.error_window.exec_()

			else:
				# introduce spaces between elements and numbers
				full_name = name[0]
				for k in range(1, len(name)):
					if name[k].isnumeric() and name[k-1].isalpha():
						full_name += ' ' + name[k]
					else:
						full_name += name[k]

				name = full_name
				name = name.split()

				# check if every other 2 entry is a number and add one if not
				full_name = [name[0]]
				for k in range(1, len(name)):
					if name[k].isalpha() and name[k-1].isalpha():
							full_name.append('1')
					full_name.append(name[k])
						
				if full_name[-1].isalpha():
					full_name.append('1')

				# write formulas in NDF way (with '?=')
				if self.fitElementLayout.itemAt(i).widget().isChecked():
					name = full_name

					full_name = []
					for n in name:
						full_name.append(n)
						if n.isalpha():
							full_name.append('?=')

				col_params[0] = ' '.join(full_name)
				col_params[0] = col_params[0].replace('= ', '=')



			mol = {
				'name'		   : col_params[0],
				'density'	   : col_params[1],
				'concentration': [col_params[2], col_params[3]],
				'depth': [col_params[4], col_params[5]]
			}

			molecules[i] = mol


		self.idf_file.set_elements(molecules)

	def save_profile_box(self):
		if self.debug: print('NDF_gui, save_profile_box begins')
		# self.save_elements_box()
		elements = self.idf_file.get_elements()

		nrows = self.profile_table.rowCount()
		ncols = self.profile_table.columnCount()

		names = []

		for key, param in elements.items():
			if key == 'nelements':
				continue

			name = param['name'].replace('?=','')
			names.append(name)

		profile_dic = {'nlayers': nrows}
		profile_dic['names'] = names

		for i in range(nrows):
			thickness = self.profile_table.item(i,0)
			if thickness is None: continue 
			else: thickness = thickness.text()

			concentrations = []

			for j in range(1,ncols):
				concentration = self.profile_table.item(i, j)

				if concentration is None: concentration = 0
				else: concentration = concentration.text()

				concentrations.append(concentration)


			profile_dic[i] = {'thickness':thickness, 'concentrations':concentrations}



		self.idf_file.set_profile(profile_dic)

		# save minimum thickness
		self.idf_file.set_min_thickness(self.profile_min_thickness.text())
		self.idf_file.set_max_thickness(self.profile_max_thickness.text())



	   #           'elements':[{'name': 'Au', 'concentration':1}]
				# }
	   #          }

	   #          ,
	   #          {'layerthickness':'2000', 
	   #           'layerdensity':6.6, 
	   #           'elements':[
	   #               {'name':'Si', 'concentration':1/3},
	   #               {'name':'O', 'concentration':2/3},]
	   #          },
	   #          {'layerthickness':'30000',  
	   #           'elements':[{'name': 'Si', 'concentration':1},]
	   #          }, 
	   #      ]


	def save_geometry_box_fits(self, target_spectra_id = '', target_simulation_id = ''):
		pairs = {
			'energy':{
				'check': self.checkEnergy,
				'field': self.geo_energy_fit,
				'method': self.idf_file.set_beam_energy_fitparam},
			'fwhm': {
				'check': self.checkFWHM,
				'field': self.geo_fwhm_fit,
				'method': self.idf_file.set_beam_energy_spread_fitparam},
			'window_min': {
				'check': self.checkWindow,
				'field': self.geo_window_min,
				'method': self.idf_file.set_window_min},
			'window_max': {
				'check': self.checkWindow,
				'field': self.geo_window_max,
				'method': self.idf_file.set_window_max},
			'angle_in':{
				'check': self.checkAngles,
				'field': self.geo_angle_in_fit,
				'method': self.idf_file.set_incident_angle_fitparam},
			'angle_out':{
				'check': self.checkAngles,
				'field': self.geo_angle_out_fit,
				'method': self.idf_file.set_scattering_angle_fitparam},
			'charge':{
				'check': self.checkCharge,
				'field': None,  #self.geo_solid_angle_fit,
				'method': self.idf_file.set_charge_fitparam},
			'calibration':{
				'check': self.checkCalibration,
				'field': None, #[self.geo_calibration_m_fit, self.geo_calibration_b_fit],
				'method': self.idf_file.set_energy_calibration_fitparam},
			'foil':{
				'check': self.ndf_more_options_window.checkFoil,
				'field': [self.ndf_more_options_window.foilMaterialCombo, self.ndf_more_options_window.foilMaterialThickness],
				'method': self.idf_file.set_detector_foil},
			'rutherford':{
				'check': self.ndf_more_options_window.checkRutherford,
				'field': None,
				'method': self.idf_file.set_rutherford_cross},
		}

		if target_spectra_id == '':
			spectra_id = self.spectra_id
		else:
			spectra_id = target_spectra_id

		if target_simulation_id == '':
			simulation_id = self.simulation_id
		else:
			simulation_id = target_simulation_id


		for k, p in pairs.items():
			if k == 'calibration':
				p['method'](p['check'].isChecked(), p['check'].isChecked(), spectra_id = spectra_id, simulation_id = simulation_id)
			elif k == 'charge':
				p['method'](p['check'].isChecked(), spectra_id = spectra_id, simulation_id = simulation_id)
			elif k == 'rutherford':
				p['method'](not p['check'].isChecked(), self.settings['nonRutherford']['ebsfiles'], spectra_id = spectra_id, simulation_id = simulation_id)
			elif k == 'foil':
				if p['check'].isChecked():
					p['method'](p['field'][0].currentText(), p['field'][1].text(), spectra_id = spectra_id, simulation_id = simulation_id)
				else:
					p['method']('', '', spectra_id = spectra_id, simulation_id = simulation_id)


			elif p['check'].isChecked():
				if isinstance(p['field'], list):
					p['method'](p['field'][0].text(), p['field'][1].text(), spectra_id = spectra_id, simulation_id = simulation_id)				
				else:
					value = p['field'].text()
					if 'window' in k:
						value = self.convert_window_energy(value, channel2energy = False)

					p['method'](value,  spectra_id=spectra_id, simulation_id = simulation_id)
			else:
				if isinstance(p['field'], list):
					p['method']('','',  spectra_id=spectra_id, simulation_id = simulation_id)
				else:
					p['method']('',  spectra_id=spectra_id, simulation_id = simulation_id)



	def save_fit_methods_box(self, target_spectra_id = '', target_simulation_id = ''):
		pairs = {
			'pileup':{
				'check': self.checkPileup,
				'model': self.comboPileup,
				'param': self.pileup_param,
				'method': self.idf_file.set_model_pileup
			},
			'doublescattering':{
				'check': self.checkDoublescatter,
				'model': self.comboDoublescatter,
				'param': self.doublescatter_scaleparam,
				'method': self.idf_file.set_model_doublescatter
			},
			'straggling':{
				'check': self.checkStraggling,
				'model': self.comboStraggling,
				'param': self.straggling_scaleparam,
				'method': self.idf_file.set_model_straggling
			},
			'energyloss':{
				'check' : self.checkEnergyloss,
				'model' : self.comboEnergyloss,
				'param' : None,
				'method': self.idf_file.set_model_energyloss
			},
			'adhoc_corection':{
				'check': self.checkAdhoc_correction,
				'model': self.adhoc_element,
				'param': self.adhoc_parameters,
				'method': self.idf_file.set_model_adhoc_correction
			},
		}

		if target_spectra_id == '':
			spectra_id = self.spectra_id
		else:
			spectra_id = target_spectra_id

		if target_simulation_id == '':
			simulation_id = self.simulation_id
		else:
			simulation_id = target_simulation_id

		for k, p in pairs.items():
			if p['check'].isChecked():
				if isinstance(p['model'], QComboBox):
					model = p['model'].currentText()
				else:
					model = p['model'].text()

				if p['param'] is not None: 
					param = p['param'].text()
					p['method'](model, param,  spectra_id=spectra_id, simulation_id = simulation_id)
				else: 
					p['method'](model,  spectra_id=spectra_id, simulation_id = simulation_id)

			else:
				if p['param'] is not None:
					p['method']('','',  spectra_id=spectra_id, simulation_id = simulation_id)
				else:
					p['method']('',  spectra_id=spectra_id, simulation_id = simulation_id)

	def message_window(self):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Information)
		msg.setWindowTitle("Error")
		msg.setStandardButtons(QMessageBox.Ok)
		# result = msg.exec_()

		return msg


class IDF_spectrum_Figure(QMainWindow, Ui_NDF_Fit_Figure):
	def __init__(self, main_window, parent=None):
		super().__init__(parent)
		self.setupUi(self)

		self.setWindowTitle('Experimental Data')

		self.idf_file = main_window.idf_file
		self.spectra_id = main_window.spectra_id
		self.simulation_id = main_window.simulation_id
		self.comboTechnique = main_window.comboTechnique
		self.settings = main_window.settings

		self.figure_exp_spectra = plt.figure(figsize=(8, 6))
		self.canvas_exp_spectra = FigureCanvas(self.figure_exp_spectra)
		self.spectra_result_plot.addWidget(self.canvas_exp_spectra)

		self.toolbar = NavigationToolbar(self.canvas_exp_spectra, self)
		self.spectra_result_plot.addWidget(self.toolbar)

		Window.set_spectrum_box(self)


class NDF_Fit_Figure(QMainWindow, Ui_NDF_Fit_Figure):
	def __init__(self, main_window, type = False, parent=None):
		super().__init__(parent)
		self.setupUi(self)

		self.idf_file = main_window.idf_file
		self.spectra_id = main_window.spectra_id
		self.simulation_id = main_window.simulation_id
		self.debug = main_window.debug
		self.settings = main_window.settings

		if type == False:
			self.figure_result = plt.figure(figsize=(10,6))
			self.canvas_result = FigureCanvas(self.figure_result)
			self.spectra_result_plot.addWidget(self.canvas_result)
			
			self.toolbar = NavigationToolbar(self.canvas_result, self)
			self.spectra_result_plot.addWidget(self.toolbar)

			Window.set_spectra_fit_result_tab(self)
		elif type == 'profile':
			profile_params = main_window.idf_file.get_profile_fit_result(spectra_id=main_window.spectra_id, 
																		 simulation_id=main_window.simulation_id)

			self.figure_profile = plt.figure(figsize=(10,6))
			self.canvas_profile = FigureCanvas(self.figure_profile)
			self.spectra_result_plot.addWidget(self.canvas_profile)
			
			self.toolbar = NavigationToolbar(self.canvas_profile, self)
			self.spectra_result_plot.addWidget(self.toolbar)

			Window.set_profile_fit_result_plot(self, profile_params)
			self.ax_profile.set_ylim(-5, 120)
			self.figure_profile.tight_layout()

class About_Window(QMainWindow, Ui_dialog_about):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.executable_dir = osjoin(dirname(__file__), 'pyIBA') + '/'

		self.push_openNDFManual.clicked.connect(self.open_NDF_manual)


	def open_NDF_manual(self):
		executable_dir = dirname(realpath(__file__)) + '/'
		# print(realpath('aux_files/MANUAL_100a.pdf'))
		open_new('file://' + realpath(executable_dir + 'pyIBA/pyIBA/aux_files/MANUAL_100a.pdf'))


class Reactions_Dialog(QDialog, Ui_Reactions_Dialog):
	def __init__(self, reactions, technique = 'NRA'):
		super(Reactions_Dialog, self).__init__()
		self.setupUi(self)

		self.connectSignalsSlots()

		if reactions is None:
			reactions = [{
				'initialtargetparticle': '',
				'incidentparticle': '',
				'exitparticle': '',
				'finaltargetparticle': '',
				'reactionQ': '',
				'code':''
			}]

		self.reactions = reactions


		if technique == 'ERDA':
			self.initial_target_label.setEnabled(False)
			self.final_target_label.setEnabled(False)
			self.QEnergy_label.setEnabled(False)
			self.initial_target_atom.setEnabled(False)
			self.final_target_atom.setEnabled(False)
			self.qenergy.setEnabled(False)


		self.update_comboReactions()
		self.onchange_reaction()

	def connectSignalsSlots(self):
		self.add_button.clicked.connect(self.add_reaction)
		self.save_button.clicked.connect(self.save_reaction)
		self.delete_button.clicked.connect(self.delete_reaction)

		self.comboReactions.currentIndexChanged.connect(self.onchange_reaction)


	def onchange_reaction(self):
		index = self.comboReactions.currentIndex()
		reaction = self.reactions[index]

		self.initial_target_atom.setText(reaction['initialtargetparticle'])
		self.incident_ion.setText(reaction['incidentparticle'])
		self.exit_ion.setText(reaction['exitparticle'])
		self.final_target_atom.setText(reaction['finaltargetparticle'])
		self.qenergy.setText(reaction['reactionQ'])

	def save_reaction(self):
		index = self.comboReactions.currentIndex()

		self.edit_reaction(index)
		self.update_comboReactions()
		self.comboReactions.setCurrentIndex(index)      

	def add_reaction(self):
		curr_index = self.comboReactions.currentIndex()
		if self.reactions[curr_index]['code'] != '':
			index = len(self.reactions)
			reaction = self.reactions[curr_index].copy()
			self.reactions.append(reaction)
		else:
			index = curr_index

		self.edit_reaction(index)
		self.update_comboReactions()
		self.comboReactions.setCurrentIndex(index)

	def delete_reaction(self):
		index = self.comboReactions.currentIndex()

		if len(self.reactions) == 1:
			return

		self.reactions.pop(index)
		self.update_comboReactions()
		if index >0:
			self.comboReactions.setCurrentIndex(index-1)
		else:
			self.comboReactions.setCurrentIndex(0) 
		self.onchange_reaction()


	def edit_reaction(self, index):
		reaction = self.reactions[index]
		
		reaction['initialtargetparticle'] = self.initial_target_atom.text()
		reaction['incidentparticle'] = self.incident_ion.text()
		reaction['exitparticle'] = self.exit_ion.text()
		reaction['finaltargetparticle'] = self.final_target_atom.text()
		reaction['reactionQ'] = self.qenergy.text()

	
		try:
			energy_code = '%0.2f' %(float(reaction['reactionQ']))
		except:
			energy_code = ''

		for key, item in reaction.items():
			if item is None:
				reaction[key] = ''


		reaction['code'] = '%s(%s, %s)%s %s' %(
						reaction['initialtargetparticle'], reaction['incidentparticle'], reaction['exitparticle'], 
						reaction['finaltargetparticle'], energy_code)

		self.reactions[index] = reaction



	def update_comboReactions(self):
		name_list = []

		if self.reactions is not None:
			name_list = [r['code'] for r in self.reactions]

		self.comboReactions.blockSignals(True)
		self.comboReactions.clear()
		self.comboReactions.addItems(name_list)
		self.comboReactions.blockSignals(False)


	



	def get_values(self):
		if self.exec_() == QDialog.Accepted:
			self.save_reaction()
			return self.reactions
		else:
			return None





if __name__ == "__main__":
	app = QApplication(argv)

	from PyQt5.QtCore import pyqtRemoveInputHook
	pyqtRemoveInputHook()

	win = Window()

	if len(argv)>1:
		if '--debug' in argv:
			win.debug = True
		if '-' != argv[-1][0]:
			win.open(fileName = argv[-1])

	win.show()

	exit(app.exec())


