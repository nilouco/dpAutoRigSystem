# importing libraries:
from maya import cmds
from maya import mel
from ....library.base import action

# global variables to this module:
CLASS_NAME = "Envelope"
TITLE = "v094_envelope"
DESCRIPTION = "v095_envelopeDesc"
WIKI = "07-‐-Validator#-envelope-checker"



class Envelope(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)


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
                allNodesList = inputs
            else:
                allNodesList = cmds.ls()
            allEnvelopedNodes = list(filter(self.nodeHasEnvelope, allNodesList))
            allValidEnvelopeNodes = list(filter(self.envelopeIsValid, allEnvelopedNodes))
            self.checked_items.extend(allValidEnvelopeNodes)
            if self.checked_items:
                self.ar.utils.setProgress(max=len(self.checked_items), add_one=False, add_number=False)

                for node in self.checked_items:
                    self.found_issues.append(self.verifyEnvelope(node))

                if not self.first_mode:
                    for idx, issue in enumerate(self.checked_items):
                        self.ar.utils.setProgress(self.ar.data.lang[self.title])
                        if issue:
                            try:
                                cmds.setAttr(f"{self.checked_items[idx]}.envelope", 1)
                                self.found_issues[idx] = False
                            except Exception as e:
                                mel.eval('print \"dpAR: '+e+'\\n\";')
            else:
                self.found_issues.append(False)

            self.good_results.append(not True in self.found_issues)
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data
