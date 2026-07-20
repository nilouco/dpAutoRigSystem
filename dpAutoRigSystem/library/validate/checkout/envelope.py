# importing libraries:
from maya import cmds
from maya import mel
from ....library.base import action

# global variables to this module:
CLASS_NAME = "Envelope"
TITLE = "v094_envelope"
DESCRIPTION = "v095_envelopeDesc"
WIKI = "07-‐-Validator#-envelope-checker"



class Envelope(action.ActionStartClass):
    def __init__(self, ar):
        action.ActionStartClass.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)


    def nodeHasEnvelope(self, node):
        return cmds.attributeQuery('envelope', node=node, exists=True)
    
    def envelopeIsValid(self, node):
        notConnected =  not cmds.listConnections(node+".envelope", source=True, destination=False)
        nodeStateNormal = cmds.getAttr(node+".nodeState") == 0
        notUserDefined = not "envelope" in (cmds.listAttr(node, userDefined=True) or [])
        return notConnected and nodeStateNormal and notUserDefined


    def verifyEnvelope(self, node):
        envelopeValue = cmds.getAttr(f"{node}.envelope")
        return envelopeValue < 1
    

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
                allNodesList = objList
            else:
                allNodesList = cmds.ls()
            allEnvelopedNodes = list(filter(self.nodeHasEnvelope, allNodesList))
            allValidEnvelopeNodes = list(filter(self.envelopeIsValid, allEnvelopedNodes))
            self.checkedObjList.extend(allValidEnvelopeNodes)
            if self.checkedObjList:
                self.ar.utils.setProgress(max=len(self.checkedObjList), addOne=False, addNumber=False)

                for node in self.checkedObjList:
                    self.foundIssueList.append(self.verifyEnvelope(node))

                if not self.firstMode:
                    for idx, issue in enumerate(self.checkedObjList):
                        self.ar.utils.setProgress(self.ar.data.lang[self.title])
                        if issue:
                            try:
                                cmds.setAttr(f"{self.checkedObjList[idx]}.envelope", 1)
                                self.foundIssueList[idx] = False
                            except Exception as e:
                                mel.eval('print \"dpAR: '+e+'\\n\";')
            else:
                self.foundIssueList.append(False)

            self.resultOkList.append(not True in self.foundIssueList)
        else:
            self.notWorkedWellIO(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
