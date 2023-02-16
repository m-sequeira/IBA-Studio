from pyIBA import IDF

from pickle import dump, load as pickleLoad
from copy import deepcopy


class project():
	def __init__(self, idf_file):
		self.idf_file = idf_file
		self.sim_version_history = []#[self.idf_file]

		self.path_dir = self.idf_file.path_dir
		self.name = self.idf_file.name
		self.file_path = self.path_dir + self.name + '.idv'


		self.debug = False

	def reload_idf_file(self, index = None):
		if index is None:
			for i,version in enumerate(self.sim_version_history):
				path = version.file_path
				self.sim_version_history[i] = IDF(path)

			return None
		else:
			path = self.sim_version_history[index].file_path
			self.sim_version_history[index] = IDF(path)
			return self.sim_version_history[index]


	def get_version_names(self):
		prev_names = []
		size_oriname = len(self.idf_file.name)
		for idf in self.sim_version_history[::-1]:
			name = idf.path_dir.split('/')[-2]
			name = name[size_oriname + 1:-4]
			name = name.replace('_', ' ')
			# if name == '':
			# 	name = 'Initial'
			with open(idf.path_dir + 'run_status.res') as file:
				status = file.readline()
				if 'Run' in status:
					name = '[R] ' + name
				

			prev_names.append(name)

		prev_names.append('In xml file')



		return prev_names


	def save(self):
		with open(self.file_path, 'wb') as file:
			dump(self, file)

def load(pickle_filename):
	return pickleLoad(open(pickle_filename, 'rb'))





