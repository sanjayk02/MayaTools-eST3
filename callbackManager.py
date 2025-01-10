import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
from shiboken2 import wrapInstance, isValid

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