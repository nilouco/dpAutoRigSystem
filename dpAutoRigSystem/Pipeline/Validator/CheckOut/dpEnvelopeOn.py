# importing libraries:
from maya import cmds
from maya import mel
from ... import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "EnvelopeChecker"
TITLE = "v094_envelopeChecker"
DESCRIPTION = "v095_envelopeCheckerDesc"
ICON = "/Icons/dp_envelopeChecker.png"

DP_ENVELOPECHECKER_VERSION = 1.0


class EnvelopeChecker(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_ENVELOPECHECKER_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)


    def nodeHasEnvelope(self, node):
        return cmds.attributeQuery('envelope', node=node, exists=True)


    def verifyEnvelope(self, node):
        envelopeValue = cmds.getAttr(f"{node}.envelope")
        return envelopeValue < 1
    

    def runAction(self, firstMode=True, objList=None, *args):
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
        self.firstMode = firstMode
        self.verbose = True
        self.cleanUpToStart()

        # ---
        # --- validator code --- beginning
        if objList:
            allNodesList = objList
        else:
            allNodesList = cmds.ls()
        allEnvelopedNodes = filter(self.nodeHasEnvelope, allNodesList)
        self.checkedObjList.extend(list(allEnvelopedNodes))
        if self.checkedObjList:
            self.utils.setProgress(max=len(self.checkedObjList), addOne=False, addNumber=False)

            for node in self.checkedObjList:
                self.foundIssueList.append(self.verifyEnvelope(node))

            if not self.firstMode:
                for idx, issue in enumerate(self.checkedObjList):
                    #self.utils.setProgress(self.dpUIinst.lang[self.title])
                    notConnected =  not cmds.listConnections(self.checkedObjList[idx]+".envelope", source=True, destination=False)
                    nodeStateNormal = cmds.getAttr(self.checkedObjList[idx]+".nodeState") == 0
                    notUserDefined = "envelope" in cmds.listAttr(self.checkedObjList[idx], userDefined=False)
                    if issue and notConnected and nodeStateNormal and notUserDefined:
                        try:
                            cmds.setAttr(f"{self.checkedObjList[idx]}.envelope", 1)
                        except Exception as e:
                            mel.eval('print \"dpAR: '+e+'\\n\";')

        self.resultOkList.append(True in self.foundIssueList)

        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
