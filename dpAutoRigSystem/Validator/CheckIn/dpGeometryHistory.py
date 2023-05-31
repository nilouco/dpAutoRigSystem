# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "GeometryHistory"
TITLE = "v071_geometryHistory"
DESCRIPTION = "v072_geometryHistoryDesc"
ICON = "/Icons/dp_geometryHistory.png"

dpGeometryHistory_Version = 1.0

class GeometryHistory(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseValidatorClass.ValidatorStartClass.__init__(self, *args, **kwargs)
    

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
            geoToCleanList = objList
        else:
            shapeList = cmds.ls(selection=False, type='mesh')
            geoList = []
            if shapeList:
                # Get only transform nodes
                transformList = list(set(cmds.listRelatives(shapeList, type="transform", parent=True, fullPath=True)))
                if transformList:
                    for transform in transformList:
                        # Filter which geometry has deformer history and groupLevels to pass through sets and shader
                        historyList = cmds.listHistory(transform, pruneDagObjects=True, groupLevels=True)
                        if historyList:
                            for history in historyList:
                                # Pass through tweak and initialShading nodes
                                if cmds.nodeType(history) != "tweak": 
                                    if history != "initialShadingGroup":
                                        geoList.append(transform)
            # Merge duplicated names
            geoToCleanFullPathList = list(set(geoList))
            # Get shortName to better reading in display log
            geoToCleanList = cmds.ls(geoToCleanFullPathList, long=False)
        if geoToCleanList:
            for geo in geoToCleanList:
                if cmds.objExists(geo):
                    progressAmount = 0
                    maxProcess = len(geoToCleanList)
                    if self.verbose:
                    # Update progress window
                        progressAmount += 1
                        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.langDic[self.dpUIinst.langName][self.title]+': '+repr(progressAmount)))
                    self.checkedObjList.append(geo)
                    self.foundIssueList.append(True)
                    if self.verifyMode:
                        self.resultOkList.append(False)
                    else: #fix
                        try:
                            # Delete history
                            cmds.delete(geo, constructionHistory=True)
                            self.resultOkList.append(True)
                            self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+geo)
                        except:
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+geo)
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