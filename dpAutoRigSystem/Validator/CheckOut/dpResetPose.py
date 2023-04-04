# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "ResetPose"
TITLE = "v032_resetPose"
DESCRIPTION = "v033_resetPoseDesc"
ICON = "/Icons/dp_resetPose.png"

dpResetPose_Version = 1.0

TO_IGNORE = ["rotateOrder", "scaleCompensate"]
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

class ResetPose(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseValidatorClass.ValidatorStartClass.__init__(self, *args, **kwargs)
        self.nonDynZeroAttrList = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]
        self.nonDynOneAttrList = ["scaleX", "scaleY", "scaleZ", "visibility"]
    

    def runValidator(self, verifyMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If verifyMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.verifyMode = verifyMode
        self.startValidation()
        
        

        # ---
        # --- validator code --- beginning
        if objList:
            toCheckList = objList
        else:
            toCheckList = cmds.ls(selection=False, type='transform')
        if toCheckList:
            progressAmount = 0
            maxProcess = len(toCheckList)
            for item in toCheckList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.langDic[self.dpUIinst.langName][self.title]+': '+repr(progressAmount)))
                # conditional to check here
                if cmds.objExists(item+".dpControl"):
                    self.checkedObjList.append(item)

                    editedAttrData = {}
                    attrData = self.getAttrDefaultValueData(item)
                    for attr in list(attrData):
                        
                        attrType = self.getAttrType(attrData[attr][2])
                        
                        if attrType == 0: #boolean
                            if not bool(attrData[attr][0]) == bool(attrData[attr][1]):
                                editedAttrData[attr] = attrData[attr][0]
                        elif attrType == 1: #integer
                            if not int(attrData[attr][0]) == int(attrData[attr][1]):
                                editedAttrData[attr] = attrData[attr][0]
                        elif attrType == 2: #float
                            if not float(attrData[attr][0]) == float(attrData[attr][1]):
                                editedAttrData[attr] = attrData[attr][0]
                    
                    if editedAttrData:
                        self.foundIssueList.append(True)
                        #self.messageList.append(str(editedAttrData.keys()))
                    else:
                        self.foundIssueList.append(False)
                    
                    if self.verifyMode:
                        self.resultOkList.append(False)
                    else: #fix
                        for attr in list(editedAttrData):
                            try:
                                cmds.setAttr(item+"."+attr, editedAttrData[attr][0])
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+item+"."+attr)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+item+"."+attr)
        else:
            self.checkedObjList.append("")
            self.foundIssueList.append(False)
            self.resultOkList.append(True)
            self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v014_notFoundNodes'])
        # --- validator code --- end
        # ---



        # finishing
        self.finishValidation()
        return self.dataLogDic


    def startValidation(self, *args):
        """ Procedures to start the validation cleaning old data.
        """
        dpBaseValidatorClass.ValidatorStartClass.cleanUpToStart(self)


    def finishValidation(self, *args):
        """ Call main base methods to finish the validation of this class.
        """
        dpBaseValidatorClass.ValidatorStartClass.updateButtonColors(self)
        dpBaseValidatorClass.ValidatorStartClass.reportLog(self)
        dpBaseValidatorClass.ValidatorStartClass.endProgressBar(self)

    
    def getAttrDefaultValueData(self, item, ignoreAttrList=TO_IGNORE, *args):
        """ Returns a dictionary with a list of default and current values for each attribute of the given node.
        """
        attrData = {}
        attrList = cmds.listAttr(item, channelBox=True)
        if not attrList:
            attrList = []
        allAttrList = cmds.listAttr(item)
        animAttrList = cmds.listAnimatable(item)
        if allAttrList and animAttrList:
            orderedAttrs = [attr for attr in allAttrList for animAttr in animAttrList if animAttr.endswith(attr) and not attr in attrList]
            attrList.extend(orderedAttrs)
        if ignoreAttrList:
            for ignoreAttr in ignoreAttrList:
                if ignoreAttr in attrList:
                    attrList.remove(ignoreAttr)
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
        """
        if inputData:
            return ATTR_TYPE[inputData]