import os
import json
import maya.OpenMayaUI as omui
import maya.cmds as cmds
from shiboken2 import wrapInstance
import codecs
from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import QWidget, QMainWindow, QVBoxLayout
from PySide2.QtCore import QFile


SCRIPT_LOC = os.path.dirname(__file__)

# ============================================================================================================
def ready_config():
	"""Load the configuration JSON file."""
	json_path = os.path.join(SCRIPT_LOC, 'config.json')
	
	if not os.path.exists(json_path):
		cmds.warning("Config file not found at %s" % json_path)
		return None
	
	try:
		with codecs.open(json_path, 'r', 'utf-8') as file:
			return json.load(file)
	except ValueError as e:  # JSONDecodeError doesn't exist in Python 2.7
		cmds.error("Error parsing config.json: %s" % e)
		return None

# ============================================================================================================
def get_maya_window():
	"""Get Maya's main window as a PySide2 object."""
	main_window_ptr = omui.MQtUtil.mainWindow()
	if not main_window_ptr:
		raise RuntimeError("Failed to obtain Maya's main window.")
	return wrapInstance(long(main_window_ptr), QWidget)  # Use `long` for Python 2.7 compatibility

# ============================================================================================================
class MyWindow(QMainWindow):
	"""Main UI Window."""
	def __init__(self, parent=None):
		super(MyWindow, self).__init__(parent)

		# Main container
		self.container_widget = QWidget()
		self.container_layout = QVBoxLayout()
		self.container_widget.setLayout(self.container_layout)
		self.setCentralWidget(self.container_widget)

		self.setWindowTitle("Dynamic Attribute Controller")
		self.resize(350, 100)

		# Load config and create UI
		self.load_config_and_create_ui()

	def load_config_and_create_ui(self):
		"""Load the configuration data and dynamically create UI."""
		config = ready_config()
		if not config or 'dynamic' not in config:
			cmds.warning("Dynamic data not found in configuration.")
			return

		for row_name, items in config['dynamic'].items():
			for item in items:
				self.create_row(*item)

	def create_row(self, label, line_edit_name, slider_name, button_name, obj_name, default_value, attr_name, reset_button, reset_attr):
		"""Create a row dynamically based on the provided data."""
		row_layout = QtWidgets.QHBoxLayout()

		# Add QLabel
		label_widget = QtWidgets.QLabel("%s:" % label)
		row_layout.addWidget(label_widget)

		# Add QLineEdit
		line_edit = QtWidgets.QLineEdit()
		line_edit.setText(default_value)
		line_edit.setFixedSize(50, 30)
		line_edit.setPlaceholderText("Value")
		row_layout.addWidget(line_edit)

		# Add QSlider
		slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
		slider.setMinimum(0)
		slider.setMaximum(100)
		slider.setValue(int(float(default_value) * 10))  # Map default value (float) to slider
		slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
		slider.setTickInterval(10)
		row_layout.addWidget(slider)

		# Add Reset QPushButton
		reset_button_widget = QtWidgets.QPushButton("Reset")
		row_layout.addWidget(reset_button_widget)

		# Slider value change updates the line edit and attribute
		slider.valueChanged.connect(
			lambda value: self.update_line_edit_and_attribute(line_edit, obj_name, attr_name, value / 10.0)
		)

		# LineEdit value change updates the slider and attribute
		line_edit.editingFinished.connect(
			lambda: self.update_slider_and_attribute(slider, line_edit, obj_name, attr_name)
		)

		# Reset button sets the attribute to its reset value
		reset_button_widget.clicked.connect(
			lambda obj=obj_name, attr=attr_name, reset_value=float(default_value): self.reset_slider_and_line_edit(slider, line_edit, obj, attr, reset_value)
		)

		# Add the row layout to the container
		self.container_layout.addLayout(row_layout)

	def update_line_edit_and_attribute(self, line_edit, obj_name, attr_name, value):
		"""Update the line edit and Maya attribute when the slider is moved."""
		line_edit.setText("%.2f" % value)  # Update the line edit with the float value
		self.update_attribute(obj_name, attr_name, value)  # Update the Maya attribute

	def update_slider_and_attribute(self, slider, line_edit, obj_name, attr_name):
		"""Update the slider and Maya attribute when the line edit value changes."""
		try:
			value = float(line_edit.text())
			slider.setValue(int(value * 10))  # Update the slider position
			self.update_attribute(obj_name, attr_name, value)  # Update the Maya attribute
		except ValueError:
			cmds.warning("Invalid value entered: %s" % line_edit.text())

	def reset_slider_and_line_edit(self, slider, line_edit, obj_name, attr_name, reset_value):
		"""Reset both the slider and the line edit to their default value."""
		slider.setValue(int(reset_value * 10))  # Reset the slider position
		line_edit.setText("%.2f" % reset_value)  # Reset the line edit
		self.update_attribute(obj_name, attr_name, reset_value)  # Reset the Maya attribute

	def update_attribute(self, obj_name, attr_name, value):
		"""Update the Maya attribute based on the given object name and value."""
		if cmds.objExists(obj_name):
			try:
				cmds.setAttr("%s.%s" % (obj_name, attr_name), value)
				print("Updated %s.%s to %s" % (obj_name, attr_name, value))
			except Exception as e:
				cmds.warning("Failed to update attribute %s.%s: %s" % (obj_name, attr_name, e))
		else:
			cmds.warning("Object %s does not exist." % obj_name)


# ============================================================================================================
def show_window():
	"""Show the main UI window."""
	global my_window
	try:
		my_window.close()
		my_window.deleteLater()
	except Exception:
		pass
	
	my_window = MyWindow(parent=get_maya_window())
	my_window.show()
