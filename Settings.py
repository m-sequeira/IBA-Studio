from configparser import ConfigParser
import os
import sys
import textwrap

class settings():
	def __init__(self):
		self.parser = ConfigParser()

		# Get the path of the executable
		if getattr(sys, 'frozen', False):
			# we are running in a bundle
			folder_exe = os.path.dirname(sys.executable)
		else:
			# we are running in a normal Python environment
			folder_exe = os.path.dirname(os.path.realpath(__file__))

		self.settings_path = os.path.join(folder_exe, 'settings.ini')

		if not os.path.isfile(self.settings_path):
			self.create_new_settings()
		
		self.parser.read(self.settings_path)
		

	def get_settings(self):	
		return self.parser

	def print_settings(self):
		print('\nSettings:' )
		for sec in self.parser.sections():
			print('  ', sec)
			for key in self.parser[sec]:
				print('\t', key, self.parser[sec][key])
		print('\n')


	def create_new_settings(self):
		text = '''
			#################################################################
			##                       General                               ##
			#################################################################

			[Appearance]
			# lower cutoff channel
			cut_off_channel = 50 

			show_elemental_fits = True

			# if set to false, the spectrum x-axis will be shown in channels
			# **beta version**
			energy_scale_keV = False


			[Verbose]
			debug = False

			

			#################################################################
			##                           NDF                               ##
			## The settings below are related to NDF and should eventully  ##
			## be moved to a separate settings file                        ##
			#################################################################

			[Actions]
			# Keeps the NDF command prommt open after job ends

			keep_NDF_open = False

			# Keeps the NDF files after been loaded into the idv file.
			# Note that the run history is stored in the idv file, that is 
			# not deleted. However, calculations such as double scattering 
			# will be deleted and not passed between runs.
			
			keep_NDF_files = True


			[Foils]
			# Materials used as detector foils

			Kapton = C 22 H 10 N 2 O 5
			Mylar = C 10 H 8 O 4
			Aluminium = Al 1
			Silicon Nitride = Si 3 N 4


			[nonRutherford]
			# Path to the *ebsfiles* file pointing to the non-Rutherford 
			# cross-sections of each reaction. See NDF's manual (11.1.4) for 
			# more information. Only the name of the file will be saved in 
			# the idf file.

			ebsfiles = path_to_crosssections.ebs


			[tcn_files]
			thin_film_fitting = path.tcn
			'''


		with open(self.settings_path, 'w') as file:
			file.write(textwrap.dedent(text))

