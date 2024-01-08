# importing libraries:
from maya import cmds
from ... import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "ResetPose"
TITLE = "v032_resetPose"
DESCRIPTION = "v033_resetPoseDesc"
ICON = "/Icons/dp_resetPose.png"

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

DP_RESETPOSE_VERSION = 1.4


class ResetPose(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_RESETPOSE_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.nonDynZeroAttrList = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]
        self.nonDynOneAttrList = ["scaleX", "scaleY", "scaleZ", "visibility"]
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If firstMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()

        # ---
        # --- validator code --- beginning
        if objList:
            toCheckList = objList
        else:
            toCheckList = self.dpUIinst.ctrls.getControlList()
        if toCheckList:
            progressAmount = 0
            maxProcess = len(toCheckList)
            for item in toCheckList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                # conditional to check here
                if cmds.objExists(item+".dpControl"):
                    self.checkedObjList.append(item)

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
                        self.foundIssueList.append(True)
                        for a, attr in enumerate(editedAttrList):
                            if a == 0:
                                attrString = "."
                            else:
                                attrString += "/"
                            attrString += attr
                        self.checkedObjList[-1] = item+attrString
                    else:
                        self.foundIssueList.append(False)
                    
                    if self.firstMode:
                        self.resultOkList.append(False)
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
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item+"."+attr)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item+"."+attr)
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic


    def getSetupAttrList(self, item, ignoreAttrList=TO_IGNORE, *args):
        """ Returns the desired attribute list to work with set or reset default values.
        """
        cleanAttrList = []
        attrList = cmds.listAttr(item, channelBox=True)
        if not attrList:
            attrList = []
        if attrList:
            for attrName in attrList:
                if not cmds.attributeQuery(attrName, node=item, attributeType=True) == "bool":
                    cleanAttrList.append(attrName)
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
        attrList = self.getSetupAttrList(item)
        if attrList:
            for attr in attrList:
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