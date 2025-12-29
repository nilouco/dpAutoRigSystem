# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "UnusedDeformerCleaner"
TITLE = "v148_unusedDeformerCleaner"
DESCRIPTION = "v149_unusedDeformerCleanerDesc"
ICON = "/Icons/dp_unusedDeformerCleaner.png"
WIKI = "07-‐-Validator#-unused-deformer-cleaner"

DP_UNUSEDDEFORMERCLEANER_VERSION = 1.00


class UnusedDeformerCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_UNUSEDDEFORMERCLEANER_VERSION
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
        
        #mel.eval('scOpt_performOneCleanup({"deformerOption"});')

        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            unusedList = []
            #cmds.findDeformers("*")
            deformerList = cmds.ls(type="geometryFilter") #deformers
            intermedList = cmds.ls(type="controlPoint", intermediateObjects=True)
            if objList:
                toCheckList = objList
            else:
                toCheckList = deformerList.copy()
                toCheckList.extend(intermedList.copy())
            if toCheckList:
                self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                if deformerList:
                    for defNode in deformerList:
                        self.utils.setProgress(self.dpUIinst.lang[self.title])
                        hasTags = False
                        indicesList = cmds.getAttr(defNode+".input", multiIndices=True)
                        if indicesList:
                            for i in indicesList:
                                if not cmds.getAttr(defNode+".input["+str(i)+"].groupId"):
                                    if cmds.getAttr(defNode+".input["+str(i)+"].componentTagExpression"):
                                        hasTags = True
                                        break
                        if not hasTags:
                            defSetList = cmds.listConnections(defNode+".message", type="objectSet")
                            if not defSetList:
                                unusedList.append(defNode)
                            else:
                                memberList = cmds.sets(defSetList[0], query=True)
                                if not memberList:
                                    unusedList.append(defNode)
                if intermedList:
                    for intermedObj in intermedList:
                        self.utils.setProgress(self.dpUIinst.lang[self.title])
                        outputList = cmds.listConnections(intermedObj, source=False, destination=True, plugs=True)
                        if not outputList:
                            unusedList.append(intermedObj)
                # conditional to check here
                if unusedList:
                    self.checkedObjList.append("\n".join(unusedList))
                    self.foundIssueList.append(True)
                    if self.firstMode:
                        self.resultOkList.append(False)
                    else: #fix
                        try:
                            # delete them
                            cmds.lockNode(unusedList, lock=False)
                            cmds.delete(unusedList)
                            self.resultOkList.append(True)
                            self.messageList.append(self.dpUIinst.lang['v004_fixed']+": nodes = "+str(len(unusedList)))
                        except:
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": nodes = "+str(len(unusedList)))
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
