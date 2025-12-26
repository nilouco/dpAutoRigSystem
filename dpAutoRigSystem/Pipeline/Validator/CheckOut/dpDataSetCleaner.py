# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "DataSetCleaner"
TITLE = "v144_dataSetCleaner"
DESCRIPTION = "v145_dataSetCleanerDesc"
ICON = "/Icons/dp_dataSetCleaner.png"
WIKI = "07-‐-Validator#-data-set-cleaner"

DP_DATASETCLEANER_VERSION = 1.00


class DataSetCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_DATASETCLEANER_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
    

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
        if not cmds.file(query=True, reference=True):
            if objList:
                dataGrp = objList[0]
            else:
                dataGrp = self.utils.getNodeByMessage("dataGrp")
                if not dataGrp:
                    if cmds.objExists("Data_Grp"):
                        dataGrp = "Data_Grp"
            if dataGrp:
                toCheckList = cmds.listRelatives(dataGrp, children=True, allDescendents=True)
                if toCheckList:
                    self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                    for item in toCheckList:
                        self.utils.setProgress(self.dpUIinst.lang[self.title])
                        plugList = cmds.listConnections(item+".instObjGroups[0]", source=False, destination=True, plugs=True)
                        if plugList:
                            for plug in plugList:
                                if cmds.objectType(plug.split(".")[0]) == "objectSet":
                                    itemDone = False
                                    if item in self.checkedObjList:
                                        itemDone = True
                                    if not itemDone:
                                        self.checkedObjList.append(item)
                                        self.foundIssueList.append(True)
                                    if self.firstMode:
                                        if not itemDone:
                                            self.resultOkList.append(False)
                                    else: #fix
                                        try:
                                            cmds.disconnectAttr(item+".instObjGroups[0]", plug)
                                            if not itemDone:
                                                self.resultOkList.append(True)
                                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                                        except:
                                            self.resultOkList.append(False)
                                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
            else:
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
