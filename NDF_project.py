from pyIBA import IDF

from pickle import dump, load as pickleLoad
from copy import deepcopy


class project():
	def __init__(self, idf_file):
		self.idf_file = idf_file
		self.sim_version_history = [self.idf_file]

		self.path_dir = self.idf_file.path_dir
		self.name = self.idf_file.name
		self.file_path = self.path_dir + self.name + '.idv'

	def reload_idf_file(self, index):
		path = self.sim_version_history[index].file_path
		self.sim_version_history[index] = IDF(path)


	def get_version_names(self):
		prev_names = []
		size_oriname = len(self.idf_file.name)
		for idf in self.sim_version_history[::-1]:
			name = idf.path_dir.split('/')[-2]
			name = name[size_oriname + 1:]
			name = name.replace('_', ' ')
			if name == '':
				name = 'Initial'
			prev_names.append(name)

		return prev_names


	def save(self):
		dump(self, open(self.file_path, 'wb'))

def load(pickle_filename):
	return pickleLoad(open(pickle_filename, 'rb'))





