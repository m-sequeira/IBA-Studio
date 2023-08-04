from ui.reactions_ui import Ui_Dialog as Ui_Reactions_Dialog


from PyQt5.QtWidgets import QDialog


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