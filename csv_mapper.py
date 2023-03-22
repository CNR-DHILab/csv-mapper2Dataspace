"""
This is a Python GUI application that allows users to convert CSV files
into a uniform format. It uses Qt to create a GUI window and displays two tables,
one with template fields and the other with the data fields. Users are then able
to map the data fields to the corresponding template fields, and click on the 'Convert'
button to generate a new, uniform CSV file.
Additionally, this application also provides a way to generate
unique UUID values for each data row and also provide mapping to concepts from a JSON file.
"""



from PyQt5.QtCore import QAbstractTableModel,Qt
from PyQt5.QtWidgets import *
from PyQt5.uic import *

import os
import csv
import pandas as pd
import json
import random

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__),  'ui', 'CSV_mapper.ui'))


class CSVMapper(QMainWindow,MAIN_DIALOG_CLASS):
	"""
	This code is defining a class CSVMapper which is a subclass of QMainWindow.
	"""
	CONVERSION=['',
		'Collection_or_Set',
		'Digital_Resources',
		'Group',
		'Instrument',
		'MP_Characterization_Analysis',
		'MP_Conservation_Analysis',
		'MP_Geographical_Context',
		'MP_Object',
		'MP_Sample',
		'Observation',
		'Person',
		'Phisical_Thing',
		'Place',
		'Project'
	]
	def __init__(self, parent=None):



		super(CSVMapper, self).__init__(parent = parent)
		self.setupUi(self)
		self.template_fields = []
		self.data_fields = []
		self.mapping = {}
		self.comboBox_template.currentTextChanged.connect(self.on_template_changed)
		self.custumize_gui()


	def on_template_changed(self,text):
		#lista_valori = [self.comboBox_template.itemText(i) for i in range(self.comboBox_template.count())]
		if text:

			self.template_path = os.path.join('templates/', text+'.csv')
			self.load_template(self.template_path)

	def load_template(self,path):
		self.template_table.clear()
		self.mapping_table.clear()
		with open(path, 'r') as csv_file:
			reader = csv.reader(csv_file)
			self.template_fields = next(reader)
		self.template_table.setHorizontalHeaderLabels(['Template Field'])

		self.template_table.setRowCount(len(self.template_fields))
		#self.template_table.setVerticalHeaderLabels(self.template_fields)
		#self.template_table = QTableWidget(len(header), 1)
		for i, field in enumerate(self.template_fields):
			item = QTableWidgetItem(field)
			self.template_table.setItem(i, 0, item)
		self.mapping_table.setHorizontalHeaderLabels(['Template Field', 'Data Field'])
		self.mapping_table.setRowCount(len(self.template_fields))
		#self.mapping_table.setVerticalHeaderLabels(header)
		self.mapping_table.setAcceptDrops(True)

		for i, field in enumerate(self.template_fields):
			item = QTableWidgetItem(field)
			self.mapping_table.setItem(i, 0, item)
	def custumize_gui(self):
		"""
		In the cutumize_gui() method, it is setting the window title, setting the geometry,
		and opening files for the template and data CSVs.
		"""

		self.comboBox_template.addItems(self.CONVERSION)

		self.setCentralWidget(self.widget)
		# Crea la statusBar e la imposta in alto a destra

		self.statusbar.setSizeGripEnabled(False)
		self.statusbar.showMessage("Barra di stato in alto a destra")
		self.statusbar.setStyleSheet("QStatusBar{border-top: 1px solid grey;}")


	def on_toolButton_load_pressed(self):
		# Open the data CSV file
		data_file, _ = QFileDialog.getOpenFileName(self, 'Open Data CSV', '', 'CSV files (*.csv)')
		if not data_file:
			self.show_error('No data file selected.')
			return

		df = pd.read_csv(data_file, dtype = str)
		self.data_fields = df.columns.tolist()

		self.data_table.setDragEnabled(True)
		model = PandasModel(df)
		self.data_table.setModel(model)
		# Add the data table to the right layout
		#right_layout1 = self.layout().itemAt(1).layout()
		#right_layout1.addWidget(self.data_table)
	def on_add_mapping_pressed(self):
		template_index = self.template_table.currentRow()
		input_dialog = QInputDialog()
		data_field, okPressed = input_dialog.getItem(
			self,
			"Data Field",
			"Select Data Field:",
			self.data_fields,
			0,
			False
		)

		if okPressed:
			self.mapping[self.template_fields[template_index]] = data_field
			item = QTableWidgetItem(data_field)
			self.mapping_table.setItem(template_index, 1, item)

	def on_remove_mapping_pressed(self):
		template_index = self.template_table.currentRow()
		del self.mapping[self.template_fields[template_index]]
		self.mapping_table.setItem(template_index, 1, QTableWidgetItem())

	def on_convert_data_pressed(self):

		self.log_text.clear()
		if self.comboBox_template.currentText()=='':
			self.log_text.append('Waring! You need choose a template')
			pass
		if not self.data_fields:
			self.log_text.append('Waring! You need choose a data table')
			pass
		if self.comboBox_template.currentText()!='' and self.data_fields:

			output_file, _ = QFileDialog.getSaveFileName(self, 'Save Output CSV', '', 'CSV files (*.csv)')
			if not output_file:
				return
			output_fields = self.template_fields.copy()
			output_data = []
			for index, row in self.data_table.model()._data.iterrows():
				new_row = []
				for field in output_fields:
					if field in self.mapping:
						data_field = self.mapping[field]
						new_row.append(row[data_field])
					else:
						new_row.append('')
				output_data.append(new_row)
				self.create_uuids(output_data)
			df = pd.DataFrame(output_data, columns=output_fields)
			df.to_csv(output_file, index=False)
			self.statusbar.showMessage('Output CSV saved successfully.')



			original_csv = output_file

			#flow control of the template
			if self.comboBox_template.currentText()=='Collection_or_Set':

				concepts_file = "resources/Collection or Set_concepts.json"

			if self.comboBox_template.currentText()=='Digital_Resources':

				concepts_file = "resources/Digital Resources_concepts.json"

			if self.comboBox_template.currentText()=='Group':

				concepts_file = "resources/Group_concepts.json"

			#if self.comboBox_template.currentText()=='Instrument':

				#concepts_file = "resources/Collection or Set_concepts.json"

			if self.comboBox_template.currentText() == 'MP_Characterization_Analysis':

				concepts_file = "resources/Characterization Analysis MP_concepts.json"

			if self.comboBox_template.currentText() == 'MP_Conservation_Analysis':

				concepts_file = "resources/Conservation Analysis MP_concepts.json"

			if self.comboBox_template.currentText() == 'MP_Geographical_Context':

				concepts_file = "resources/Geographical Context MP_concepts.json"

			if self.comboBox_template.currentText() == 'MP_Object':

				concepts_file = "resources/Object MP_concepts.json"

			if self.comboBox_template.currentText() == 'MP_Sample':

				concepts_file = "resources/Sample MP_concepts.json"

			if self.comboBox_template.currentText() == 'Observation':

				concepts_file = "resources/Object MP_concepts.json"

			if self.comboBox_template.currentText() == 'Person':

				concepts_file = "resources/Person_concepts.json"

			if self.comboBox_template.currentText() == 'Phisical_Thing':

				concepts_file = "resources/Physical Thing_concepts.json"

			if self.comboBox_template.currentText() == 'Place':

				concepts_file = "resources/Place_concepts.json"

			if self.comboBox_template.currentText() == 'Project':

				concepts_file = "resources/Project_concepts.json"



			objects = self.create_list(original_csv)
			self.map_concepts(objects, concepts_file)



			if self.comboBox_template.currentText() == 'MP_Object':

				self.relate_resource(objects, "Object Project", "Project.csv", "Name_content")

			self.to_csv(objects)
	def create_list(self, objects_file):
		"""Reads the csv and creates a python list to manipulate the data."""
		objects = []

		with open(objects_file, mode = 'r', encoding = 'utf_8') as csv_file:
			csv_reader = csv.DictReader(csv_file)

			for row in csv_reader:
				objects.append(row)

		return objects



	def create_list(self, objects_file):
		"""Reads the csv and creates a python list to manipulate the data."""
		objects = []

		with open(objects_file, mode = 'r', encoding = 'utf_8') as csv_file:
			csv_reader = csv.DictReader(csv_file)

			for row in csv_reader:
				objects.append(row)

		return objects

	def map_concepts(self, objects, concepts_file):
		"""Maps the prefLabel of an object from list in "objects",
		then finds its corresponding UUID in file "concepts_file"."""
		f = open(concepts_file)
		map = json.load(f)
		f.close()

		cont = 0
		for object in objects:
			for attr, concepts in map.items():
				if attr != "Resource to Resource Relationship Types":
					self.log_text.append(f"Attr: {attr}")

					if object[attr]:
						changed = False
						for uuid, concept in concepts.items():

							if object[attr] == concept:
								object[attr] = uuid
								changed = True
								break

						if not changed:
							cont += 1
							self.log_text.append(f"{object[attr]} from {attr} wasn't found.")

		self.log_text.append(f"Items NOT changed (should be 0): {cont}")

	def relate_resource(self, objects, object_name, lookup_csv, lookup_name):
		"""Maps the name "object_name" of an object from list in "objects",
		then finds its corresponding UUID in file "lookup_csv" in the column "lookup_name".
		Then updates list "objects" with UUID in arches format."""
		lookup = []
		with open(lookup_csv, mode = 'r') as csv_file:
			csv_reader = csv.DictReader(csv_file)

			for row in csv_reader:
				tempdict = {}
				tempdict['ResourceID'] = row['ResourceID']
				tempdict[object_name] = row[lookup_name]

				lookup.append(tempdict)

			for object in objects:
				found_uuid = False
				if object[object_name]:
					for uuid in lookup:
						if uuid[object_name] == object[object_name]:
							text_to_update = "[{'resourceId': '"
							text_to_update += uuid['ResourceID']
							text_to_update += "', 'ontologyProperty': '', "
							text_to_update += "'resourceXresourceId': '', "
							text_to_update += "'inverseOntologyProperty': ''}]"

							object[object_name] = text_to_update
							found_uuid = True
					if not found_uuid:
						self.log_text.append(f"{object_name} for {object[object_name]} not found.")

	def to_csv(self, objects):
		fieldnames = []
		for key in objects[0]:
			fieldnames.append(key)

		with open("dataspace.csv", mode = 'w') as csv_file:
			writer = csv.DictWriter(csv_file, fieldnames = fieldnames)

			writer.writeheader()
			for row in objects:
				writer.writerow(row)

	def create_uuids(self,objects):
		"""Generates random UUIDS."""
		groups = [8, 4, 4, 4, 12]
		vars = "abcdef1234567890"

		for object in objects:
			resource_id = ""

			for group in groups:
				for char in range(group):
					resource_id += random.choice(vars)
				if group != 12:
					resource_id += '-'

			object[0] = resource_id

	def show_error(self, message):
		dialog = QMessageBox(self)
		dialog.setIcon(QMessageBox.Critical)
		dialog.setText(message)
		dialog.setWindowTitle('Error')
		dialog.setStandardButtons(QMessageBox.Ok)
		dialog.show()

class PandasModel(QAbstractTableModel):
	def __init__(self, data):
		QAbstractTableModel.__init__(self)
		self._data = data

	def rowCount(self, parent=None):
		return self._data.shape[0]

	def columnCount(self, parent=None):
		return self._data.shape[1]

	def data(self, index, role=Qt.DisplayRole):
		if index.isValid():

			if role == Qt.DisplayRole:
				return str(self._data.iloc[index.row(), index.column()])

			column_count = self.columnCount()

			for column in range(0, column_count):

				if (index.column() == column and role == Qt.TextAlignmentRole):
					return Qt.AlignHCenter | Qt.AlignVCenter

		return None

	def headerData(self, section, orientation, role=Qt.DisplayRole):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return self._data.columns[section]
		return None

	def setData(self, index, value, role):
		if not index.isValid():
			return False

		if role != Qt.EditRole:
			return False

		row = index.row()

		if row < 0 or row >= self._data.shape[0]:
			return False

		column = index.column()

		if column < 0 or column >= self._data.shape[1]:
			return False

		self._data.iloc[row, column] = value
		self.dataChanged.emit(index, index)

		return True

	def flags(self, index):
		return Qt.ItemIsEnabled


if __name__ == '__main__':
	app = QApplication([])
	mapper = CSVMapper()
	mapper.show()
	app.exec_()