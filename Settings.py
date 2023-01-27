from configparser import ConfigParser


class settings():
	def __init__(self):
		self.parser = ConfigParser()
		self.parser.read('settings.ini')

	def get_settings(self):	
		return self.parser

	def print_settings(self):
		print('\nSettings:' )
		for sec in self.parser.sections():
			print('  ', sec)
			for key in self.parser[sec]:
				print('\t', key, self.parser[sec][key])
		print('\n')




