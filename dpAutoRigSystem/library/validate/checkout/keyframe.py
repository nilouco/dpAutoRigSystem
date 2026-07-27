# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "Keyframe"
TITLE = "v040_keyframe"
DESCRIPTION = "v041_keyframeDesc"
WIKI = "07-‐-Validator#-keyframe-cleaner"



class Keyframe(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

    def runAction(self, first_mode=True, objList=None, *args):
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
            if objList:
                toCheckList = objList
            else:
                toCheckList = cmds.ls(selection=False)
            if toCheckList:
                # get animation node list
                animCurveList = cmds.ls(type="animCurve")
                if animCurveList:
                    animatedList = []
                    for animCrv in animCurveList:
                        connectionList = cmds.ls(cmds.listConnections(animCrv), type=["transform", "blendShape", "nonLinear"])
                        if connectionList and not connectionList[0] in animatedList:
                            animatedList.append(connectionList[0])
                    if animatedList:
                        self.ar.utils.setProgress(max=len(animatedList), addOne=False, addNumber=False)
                        for item in animatedList:
                            self.ar.utils.setProgress(self.ar.data.lang[self.title])
                            if item in toCheckList:
                                if cmds.objExists(item):
                                    crvList = cmds.listConnections(item, source=True, destination=False, type="animCurve") #blendWeighted/pairBlend
                                    if crvList:
                                        foundKey = False
                                        for crv in crvList:
                                            # conditional to check here
                                            if len(cmds.listConnections(crv, source=True)) >= 2:
                                                pass #drivenKey
                                            else: #normal key
                                                foundKey = True
                                                break
                                        if foundKey:
                                            self.checked_items.append(item)
                                            self.found_issues.append(True)
                                            if self.first_mode:
                                                self.good_results.append(False)
                                            else: #fix
                                                reported = False
                                                for crv in crvList:
                                                    if len(cmds.listConnections(crv, source=True)) < 2:
                                                        try:
                                                            # delete animation curve (keyframe)
                                                            cmds.delete(crv)
                                                            if not reported:
                                                                self.good_results.append(True)
                                                                self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
                                                                reported = True
                                                        except:
                                                            if not reported:
                                                                self.good_results.append(False)
                                                                self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
                                                                reported = True
            else:
                self.not_found_node()
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.endProgress()
        return self.log_data
