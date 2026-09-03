# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ResetPose"
TITLE = "v032_resetPose"
DESCRIPTION = "v033_resetPoseDesc"
WIKI = "07-‐-Validator#-reset-pose"

TO_IGNORE = ["rotateOrder", "pinGuide", "editMode"]
ATTR_TYPE = {
                # boolean
                "bool" : 0,
                # integer
                "long" : 1,
                "short" : 1,
                "byte" : 1,
                "enum" : 1,
                # float
                "float" : 2,
                "double" : 2,
                "doubleAngle" : 2,
                "doubleLinear" : 2
            }



class ResetPose(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.non_dyn_zero_attrs = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]
        self.non_dyn_one_attrs = ["scaleX", "scaleY", "scaleZ", "visibility"]
    

    def run_action(self, first_mode=True, inputs=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If first_mode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start()

        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if inputs:
                check_items = inputs
            else:
                check_items = self.ar.ctrls.get_controllers()
            if check_items:
                self.ar.utils.set_progress(max=len(check_items), add_one=False, add_number=False)
                for item in check_items:
                    self.ar.utils.set_progress(self.ar.data.lang[self.title])
                    # conditional to check here
                    if cmds.objExists(item+".dpControl"):
                        self.checked_items.append(item)
                        edited_attrs = []
                        attr_data = self.get_attr_default_value_data(item)
                        for attr in list(attr_data):
                            # get attribute type to use in the variables comparation
                            attr_type = self.get_attr_type(attr_data[attr][2])
                            if attr_type == 0: #boolean
                                if not bool(attr_data[attr][0]) == bool(attr_data[attr][1]): #defaultValue vs current_value
                                    edited_attrs.append(attr)
                            elif attr_type == 1: #integer
                                if not int(attr_data[attr][0]) == int(attr_data[attr][1]):
                                    edited_attrs.append(attr)
                            elif attr_type == 2: #float
                                if not float(format(attr_data[attr][0],".3f")) == float(format(attr_data[attr][1],".3f")):
                                    edited_attrs.append(attr)
                        
                        if edited_attrs:
                            self.found_issues.append(True)
                            for a, attr in enumerate(edited_attrs):
                                if a == 0:
                                    attr_string = "."
                                else:
                                    attr_string += "/"
                                attr_string += attr
                            self.checked_items[-1] = item+attr_string
                        else:
                            self.found_issues.append(False)
                        
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            for attr in edited_attrs:
                                try:
                                    attr_type = self.get_attr_type(attr_data[attr][2])
                                    if attr_type == 0: #boolean
                                        cmds.setAttr(item+"."+attr, bool(attr_data[attr][0]))
                                    elif attr_type == 1: #integer
                                        cmds.setAttr(item+"."+attr, int(attr_data[attr][0]))
                                    elif attr_type == 2: #float
                                        cmds.setAttr(item+"."+attr, float(format(attr_data[attr][0],".3f")))
                                    self.good_results.append(True)
                                    self.messages.append(self.ar.data.lang['v004_fixed']+": "+item+"."+attr)
                                except:
                                    self.good_results.append(False)
                                    self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item+"."+attr)
            else:
                self.not_found_node()
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data


    def get_setup_attrs(self, item, ignore_attrs=TO_IGNORE):
        """ Returns the desired attribute list to work with set or reset default values.
        """
        clean_attrs = []
        attributes = cmds.listAttr(item, channelBox=True)
        if not attributes:
            attributes = []
        if attributes:
            for attr_name in attributes:
                if not cmds.attributeQuery(attr_name, node=item, attributeType=True) == "bool":
                    clean_attrs.append(attr_name)
        all_attrs = cmds.listAttr(item)
        anim_attrs = cmds.listAnimatable(item)
        if all_attrs and anim_attrs:
            ordered_attrs = [attr for attr in all_attrs for animAttr in anim_attrs if animAttr.endswith(attr) and not attr in clean_attrs]
            clean_attrs.extend(ordered_attrs)
        if ignore_attrs:
            for ignore_attr in ignore_attrs:
                if ignore_attr in clean_attrs:
                    clean_attrs.remove(ignore_attr)
        return clean_attrs
    

    def get_attr_default_value_data(self, item):
        """ Returns a dictionary with a list of default and current values for each attribute of the given node.
            index 0 = default value
            index 1 = current value
            index 2 = attribute type
        """
        attr_data = {}
        attributes = self.get_setup_attrs(item)
        if attributes:
            for attr in attributes:
                attr_type = cmds.attributeQuery(attr, node=item, attributeType=True)
                current_value = cmds.getAttr(item+"."+attr)
                if attr in self.non_dyn_zero_attrs: #translate and rotate
                    attr_data[attr] = [0.0, current_value, attr_type]
                elif attr in self.non_dyn_one_attrs: #scale
                    attr_data[attr] = [1.0, current_value, attr_type]
                else: #custom and visibility
                    attr_data[attr] = [cmds.addAttr(item+"."+attr, query=True, defaultValue=True), current_value, attr_type]
        return attr_data


    def get_attr_type(self, input_data):
        """ Just return the attribute type number for the given attribute name based in the Maya's attribute types from documentation.
            Return:
                0 = boolean
                1 = integer
                2 = float
        """
        if input_data:
            return ATTR_TYPE[input_data]
