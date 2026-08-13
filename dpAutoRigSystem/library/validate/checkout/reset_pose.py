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
        self.nonDynZeroAttrList = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]
        self.nonDynOneAttrList = ["scaleX", "scaleY", "scaleZ", "visibility"]
    

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
                check_items = self.ar.ctrls.getControlList()
            if check_items:
                self.ar.utils.setProgress(max=len(check_items), add_one=False, add_number=False)
                for item in check_items:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    # conditional to check here
                    if cmds.objExists(item+".dpControl"):
                        self.checked_items.append(item)

                        editedAttrList = []
                        attrData = self.getAttrDefaultValueData(item)
                        for attr in list(attrData):
                            # get attribute type to use in the variables comparation
                            attrType = self.getAttrType(attrData[attr][2])
                            if attrType == 0: #boolean
                                if not bool(attrData[attr][0]) == bool(attrData[attr][1]): #defaultValue vs currentValue
                                    editedAttrList.append(attr)
                            elif attrType == 1: #integer
                                if not int(attrData[attr][0]) == int(attrData[attr][1]):
                                    editedAttrList.append(attr)
                            elif attrType == 2: #float
                                if not float(format(attrData[attr][0],".3f")) == float(format(attrData[attr][1],".3f")):
                                    editedAttrList.append(attr)
                        
                        if editedAttrList:
                            self.found_issues.append(True)
                            for a, attr in enumerate(editedAttrList):
                                if a == 0:
                                    attrString = "."
                                else:
                                    attrString += "/"
                                attrString += attr
                            self.checked_items[-1] = item+attrString
                        else:
                            self.found_issues.append(False)
                        
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            for attr in editedAttrList:
                                try:
                                    attrType = self.getAttrType(attrData[attr][2])
                                    if attrType == 0: #boolean
                                        cmds.setAttr(item+"."+attr, bool(attrData[attr][0]))
                                    elif attrType == 1: #integer
                                        cmds.setAttr(item+"."+attr, int(attrData[attr][0]))
                                    elif attrType == 2: #float
                                        cmds.setAttr(item+"."+attr, float(format(attrData[attr][0],".3f")))
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


    def getSetupAttrList(self, item, ignoreAttrList=TO_IGNORE, *args):
        """ Returns the desired attribute list to work with set or reset default values.
        """
        cleanAttrList = []
        attributes = cmds.listAttr(item, channelBox=True)
        if not attributes:
            attributes = []
        if attributes:
            for attr_name in attributes:
                if not cmds.attributeQuery(attr_name, node=item, attributeType=True) == "bool":
                    cleanAttrList.append(attr_name)
        allAttrList = cmds.listAttr(item)
        animAttrList = cmds.listAnimatable(item)
        if allAttrList and animAttrList:
            orderedAttrs = [attr for attr in allAttrList for animAttr in animAttrList if animAttr.endswith(attr) and not attr in cleanAttrList]
            cleanAttrList.extend(orderedAttrs)
        if ignoreAttrList:
            for ignoreAttr in ignoreAttrList:
                if ignoreAttr in cleanAttrList:
                    cleanAttrList.remove(ignoreAttr)
        return cleanAttrList
    

    def getAttrDefaultValueData(self, item, *args):
        """ Returns a dictionary with a list of default and current values for each attribute of the given node.
            index 0 = default value
            index 1 = current value
            index 2 = attribute type
        """
        attrData = {}
        attributes = self.getSetupAttrList(item)
        if attributes:
            for attr in attributes:
                attrType = cmds.attributeQuery(attr, node=item, attributeType=True)
                currentValue = cmds.getAttr(item+"."+attr)
                if attr in self.nonDynZeroAttrList: #translate and rotate
                    attrData[attr] = [0.0, currentValue, attrType]
                elif attr in self.nonDynOneAttrList: #scale
                    attrData[attr] = [1.0, currentValue, attrType]
                else: #custom and visibility
                    attrData[attr] = [cmds.addAttr(item+"."+attr, query=True, defaultValue=True), currentValue, attrType]
        return attrData


    def getAttrType(self, inputData, *args):
        """ Just return the attribute type number for the given attribute name based in the Maya's attribute types from documentation.
            Return:
                0 = boolean
                1 = integer
                2 = float
        """
        if inputData:
            return ATTR_TYPE[inputData]