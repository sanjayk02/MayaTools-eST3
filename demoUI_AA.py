import os
import maya.OpenMayaUI as omui
import maya.cmds as cmds
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLineEdit, QLabel, QPushButton

# Function to get Maya's main window
def get_maya_window():
	"""Get Maya's main window as a PySide2 object."""
	main_window_ptr = omui.MQtUtil.mainWindow()
	if not main_window_ptr:
		raise RuntimeError("Failed to obtain Maya's main window.")
	return wrapInstance(long(main_window_ptr), QWidget)  # Use `long` for Python 2.7 compatibility

class MayaAttributeCallbackManager:
	"""Manages attribute change callbacks for a Maya node."""
	def __init__(self):
		self.script_jobs = {}

	def add_callback(self, node, attribute, callback_function):
		"""Add a scriptJob to monitor changes in a node's attribute."""
		if not cmds.objExists(node):
			cmds.warning("Node %s does not exist." % node)
			return

		if not cmds.attributeQuery(attribute, node=node, exists=True):
			cmds.warning("Attribute %s does not exist on node %s." % (attribute, node))
			return

		attr_full_name = "%s.%s" % (node, attribute)

		if attr_full_name in self.script_jobs:
			cmds.warning("Callback already exists for %s." % attr_full_name)
			return

		job_id = cmds.scriptJob(attributeChange=[attr_full_name, callback_function])
		self.script_jobs[attr_full_name] = job_id
		print("Added callback for %s with scriptJob ID %d." % (attr_full_name, job_id))

	def remove_callback(self, node, attribute):
		"""Remove a scriptJob monitoring a node's attribute."""
		attr_full_name = "%s.%s" % (node, attribute)

		if attr_full_name not in self.script_jobs:
			cmds.warning("No callback exists for %s." % attr_full_name)
			return

		job_id = self.script_jobs.pop(attr_full_name)
		if cmds.scriptJob(exists=job_id):
			cmds.scriptJob(kill=job_id, force=True)
			print("Removed callback for %s with scriptJob ID %d." % (attr_full_name, job_id))

	def remove_all_callbacks(self):
		"""Remove all active scriptJobs managed by this class."""
		for attr_full_name, job_id in list(self.script_jobs.items()):
			if cmds.scriptJob(exists=job_id):
				cmds.scriptJob(kill=job_id, force=True)
				print("Removed callback for %s with scriptJob ID %d." % (attr_full_name, job_id))
		self.script_jobs.clear()

	def __del__(self):
		"""Ensure all scriptJobs are cleaned up on destruction."""
		self.remove_all_callbacks()

# ============================================================================================================
SLIDER_STYLESHEET = """
				QSlider::groove:horizontal {
					border: 1px solid #999;
					height: 6px;
					background: #ccc;
					margin: 0px;
					border-radius: 3px;
				}
				QSlider::handle:horizontal {
					background: #5c5c5c;
					border: 1px solid #444;
					width: 14px;
					margin: -5px 0;
					border-radius: 7px;
				}
				QSlider::handle:horizontal:hover {
					background: #787878;
					border: 1px solid #555;
				}
				QSlider::sub-page:horizontal {
					background: #409eff;
					border: 1px solid #5a9;
					height: 6px;
					border-radius: 3px;
				}
				QSlider::add-page:horizontal {
					background: #ccc;
					border: 1px solid #999;
					height: 6px;
					border-radius: 3px;
				}
				"""

# ============================================================================================================
class MyWindow(QMainWindow):
	"""Main UI Window."""
	def __init__(self, parent=None):
		super(MyWindow, self).__init__(parent)

		self.callback_manager = MayaAttributeCallbackManager()

		# Example UI setup
		self.container_widget = QWidget()
		self.container_layout = QVBoxLayout()
		self.container_widget.setLayout(self.container_layout)
		self.setCentralWidget(self.container_widget)

		self.setWindowTitle("Dynamic Attribute Controller")
		self.resize(350, 100)

		# Example dynamic configuration
		self.dynamic_config = {
			"row1": [
				["Label1", "LineEdit1", "Slider1", "Button1", "pSphere1", "1.0", "translateX", "resetBtn1", "resetAttr1"],
				["Label2", "LineEdit2", "Slider2", "Button2", "pSphere1", "0.0", "translateY", "resetBtn2", "resetAttr2"]
			],
			"row2": [
				["Label3", "LineEdit3", "Slider3", "Button3", "pSphere2", "0.5", "translateX", "resetBtn3", "resetAttr3"]
			]
		}

		# Dynamically create rows from the configuration
		self.create_dynamic_rows()

	def create_dynamic_rows(self):
		"""Create UI rows based on the dynamic configuration."""
		for row_name, items in self.dynamic_config.items():
			for item in items:
				self.create_row(*item)

	def create_row(self, label, line_edit_name, slider_name, button_name, 
				obj_name, default_value, attr_name, reset_button, reset_attr):
		"""Create a row dynamically based on the provided data."""
		
		row_layout = QHBoxLayout()

		# Add QLabel for value
		label_widget = QLabel("Value: %s" % label)
		row_layout.addWidget(label_widget)

		# Add QLineEdit for inputting the value
		line_edit = QLineEdit()
		line_edit.setText(default_value)
		line_edit.setFixedSize(40, 30)
		line_edit.setPlaceholderText("Value")
		row_layout.addWidget(line_edit)

		# Add QSlider for adjusting the value		
		slider = QSlider(QtCore.Qt.Horizontal)
		slider.setMinimum(0)
		slider.setMaximum(100)
		slider.setValue(int(float(default_value) * 10))  # Assuming default_value is normalized
		slider.setTickPosition(QSlider.TicksBelow)
		slider.setTickInterval(10)
		slider.setStyleSheet(SLIDER_STYLESHEET)

		row_layout.addWidget(slider)

		# Add Reset button
		reset_button_widget = QPushButton("Reset")
		row_layout.addWidget(reset_button_widget)

		# Connect slider to line edit and update attribute
		slider.valueChanged.connect(lambda value: self.update_slider_and_attribute(slider, line_edit, obj_name, attr_name))
		line_edit.editingFinished.connect(lambda: self.update_line_edit_and_attribute(slider, line_edit, obj_name, attr_name))

		# Reset button sets the attribute to its reset value
		reset_button_widget.clicked.connect(lambda: self.reset_attribute_value(slider, line_edit, obj_name, attr_name, default_value))

		# Add the row layout to the container
		# Set spacing between the widgets in the row
		row_layout.setSpacing(6)  # Set spacing to 10 pixels between widgets

		# Stretch the line edit more than other widgets (e.g., slider, button)
		row_layout.setStretch(1, 2)  # Make the line edit widget (index 1) take more space (stretch factor 2)
		row_layout.setStretch(2, 1)  # Keep the slider widget (index 2) with default stretch factor 1

		# Add the row layout to the main container layout
		self.container_layout.addLayout(row_layout)

		# Set up the callback manager to listen for changes to the attribute in Maya
		def on_attribute_change():
			if cmds.objExists(obj_name):
				value = cmds.getAttr("%s.%s" % (obj_name, attr_name))
				slider.setValue(int(value * 10))  # Example scaling
				line_edit.setText("%.2f" % value)

		self.callback_manager.add_callback(obj_name, attr_name, on_attribute_change)

	def update_slider_and_attribute(self, slider, line_edit, obj_name, attr_name):
		"""Update the attribute in Maya when the slider value changes."""
		value = slider.value() / 10.0  # Scale back to the actual value
		cmds.setAttr("%s.%s" % (obj_name, attr_name), value)
		line_edit.setText("%.2f" % value)
		print("Updated %s.%s to %.2f" % (obj_name, attr_name, value))

	def update_line_edit_and_attribute(self, slider, line_edit, obj_name, attr_name):
		"""Update the attribute in Maya when the line edit value changes."""
		try:
			value = float(line_edit.text())
			cmds.setAttr("%s.%s" % (obj_name, attr_name), value)
			slider.setValue(int(value * 10))  # Scale the slider
			print("Updated %s.%s to %.2f" % (obj_name, attr_name, value))
		except ValueError:
			cmds.warning("Invalid value entered.")

	def reset_attribute_value(self, slider, line_edit, obj_name, attr_name, default_value):
		"""Reset the attribute to its default value."""
		value = float(default_value)
		cmds.setAttr("%s.%s" % (obj_name, attr_name), value)
		slider.setValue(int(value * 10))  # Scale the slider
		line_edit.setText(default_value)  # Reset the line edit text
		print("Reset %s.%s to %s" % (obj_name, attr_name, default_value))

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
