# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "VisibilityIO"
TITLE = "r070_visibilityIO"
DESCRIPTION = "r071_visibilityIODesc"
ICON = "/Icons/dp_visibilityIO.png"
WIKI = "10-‐-Rebuilder#-visibility"

DP_VISIBILITYIO_VERSION = 1.01


class VisibilityIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_VISIBILITYIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_visibilityIO"
        self.startName = "dpVisibility"
        self.ignoreList = ["defaultLayer"]
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If firstMode parameter is False, it'll run in import mode.
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
        # --- rebuilder code --- beginning
        if not cmds.file(query=True, reference=True):
            if self.pipeliner.checkAssetContext():
                self.ioPath = self.getIOPath(self.ioDir)
                if self.ioPath:
                    itemList = None
                    if objList:
                        itemList = objList
                    else:
                        itemList = cmds.ls(selection=False)#, type="transform")
                    if itemList:
                        if self.firstMode: #export
                            self.exportDicToJsonFile(self.getVisibilityDataDic(itemList))
                        else: #import
                            visDic = self.importLatestJsonFile(self.getExportedList())
                            if visDic:
                                self.importVisibilityData(visDic)
                            else:
                                self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])
                    else:
                        self.maybeDoneIO("Ctrls_Grp")
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic


    def getVisibilityDataDic(self, itemList, *args):
        """ Processes the given item list to check the visibility value if it doesn't have input connection.
            Returns the dictionary to export.
        """
        dic = {}
        self.utils.setProgress(max=len(itemList), addOne=False, addNumber=False)
        for item in itemList:
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            if cmds.objExists(item):
                if "visibility" in cmds.listAttr(item):
                    if not cmds.listConnections(item+".visibility", source=True, destination=False):
                        dic[item] = cmds.getAttr(item+".visibility")
        return dic


    def importVisibilityData(self, visDic, *args):
        """ Import visibility attribute values from exported dictionary.
        """
        self.utils.setProgress(max=len(visDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in visDic.keys():
            notFoundNodesList = []
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            # check attribute
            if not cmds.objExists(item):
                item = item[item.rfind("|")+1:] #short name (after last "|")
            if cmds.objExists(item):
                if not cmds.getAttr(item+".visibility", lock=True):
                    if not item in self.ignoreList:
                        try:
                            cmds.setAttr(item+".visibility", visDic[item])
                            if not item in wellImportedList:
                                wellImportedList.append(item)
                        except Exception as e:
                            self.notWorkedWellIO(item+" - "+str(e))
            else:
                notFoundNodesList.append(item)
        if wellImportedList:
            self.wellDoneIO(self.latestDataFile)
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
