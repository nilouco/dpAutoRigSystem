# importing libraries:
from maya import cmds
from maya import mel
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "UnusedNodeCleaner"
TITLE = "v084_unusedNodeCleaner"
DESCRIPTION = "v085_unusedNodeCleanerDesc"
ICON = "/Icons/dp_unusedNodeCleaner.png"

DP_UNUSEDNODECLEANER_VERSION = 1.1


class UnusedNodeCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_UNUSEDNODECLEANER_VERSION
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
        if objList:
            toCheckList = objList
        else:
            toCheckList = cmds.ls(selection=False, materials=True)
        if toCheckList:
            if len(toCheckList) > 3: #discarding default materials
                # getting data to analyse
                defaultMatList = ['lambert1', 'standardSurface1', 'particleCloud1']
                allMatList = list(set(toCheckList) - set(defaultMatList))
                usedMatList = list(set(self.getUsedMaterialList()) - set(defaultMatList))
                # conditional to check here
                if not len(allMatList) == len(usedMatList):
                    self.utils.setProgress(max=len(allMatList), addOne=False, addNumber=False)
                    self.utils.setProgress(self.dpUIinst.lang[self.title])
                    issueMatList = sorted(list(set(allMatList) - set(usedMatList)))
                    self.checkedObjList.append(str(", ".join(issueMatList)))
                    self.foundIssueList.append(True)
                    if self.firstMode:
                        self.resultOkList.append(False)
                    else: #fix
                        try:
                            fixResult = mel.eval("MLdeleteUnused;")
                            self.resultOkList.append(True)
                            self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+str(fixResult)+" nodes = "+str(len(issueMatList))+" materials")
                        except:
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": materials")
            else:
                self.notFoundNodes()
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic


    def getUsedMaterialList(self, *args):
        """ List all materials used by geometry in the scene.
            https://discourse.techart.online/t/list-all-materials-used-in-scene/10185
        """
        usedMaterialList = []
        shadingEngineList = cmds.ls(type='shadingEngine')
        for shadEng in shadingEngineList:
            # if an shadingEngine has 'sets' members, it is used in the scene
            if cmds.sets(shadEng, query=True):
                matList = cmds.listConnections('{}.surfaceShader'.format(shadEng))
                if matList:
                    usedMaterialList.extend(matList)
        return list(set(usedMaterialList))
