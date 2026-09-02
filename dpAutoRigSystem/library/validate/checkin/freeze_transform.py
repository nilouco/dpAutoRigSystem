# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = 'FreezeTransform'
TITLE = 'v015_freezeTransform'
DESCRIPTION = 'v016_freezeTranformDesc'
WIKI = "07-‐-Validator#-freeze-transform"



class FreezeTransform(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)


    def run_action(self, first_mode=True, inputs=None, *args):
        ''' Main method to process this validator instructions.
            It's in verify mode by default.
            If first_mode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        '''
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start()

        # ---
        # --- validator code --- beginning
        if not self.ar.utils.get_all_grp():
            if not self.ar.utils.get_network_by_attr("dpGuideNet"):
                if not cmds.file(query=True, reference=True):
                    allObjectList = []
                    toFixList = []
                    if inputs:
                        allObjectList = list(filter(lambda obj: cmds.objectType(obj) == 'transform', inputs))
                    if len(allObjectList) == 0:
                        allObjectList = cmds.ls(selection=False, type='transform', long=True)
                    # analisys transformations
                    if len(allObjectList) > 0:
                        self.ar.utils.set_progress(max=len(allObjectList), add_one=False, add_number=False)
                        self.animCurvesList = cmds.ls(type='animCurve')
                        zeroAttrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
                        oneAttrList = ['scaleX', 'scaleY', 'scaleZ']
                        camerasList = ['|persp', '|top', '|side', '|front', '|bottom', '|back', '|left']
                        allValidObjs = list(filter(lambda obj: obj not in camerasList, allObjectList))
                        for idx, obj in enumerate(allValidObjs):
                            self.ar.utils.set_progress(self.ar.data.lang[self.title])
                            if cmds.objExists(obj):
                                # run for translates and rotates
                                frozenTR = self.checkFrozenObject(obj, zeroAttrList, 0)
                                # run for scales
                                frozenS = self.checkFrozenObject(obj, oneAttrList, 1)
                                self.checked_items.append(obj)
                                if frozenTR and frozenS:
                                    self.found_issues.append(False)
                                    self.good_results.append(True)
                                else:
                                    self.found_issues.append(True)
                                    self.good_results.append(False)
                                    self.messages.append(self.ar.data.lang['v018_foundTransform']+obj)
                                    toFixList.append((obj, idx))
                        if not self.first_mode and len(toFixList) > 0: #one item to fix
                            for obj in toFixList:
                                if self.unlockAttributes(obj[0], zeroAttrList) and self.unlockAttributes(obj[0], oneAttrList):
                                    try:
                                        cmds.makeIdentity(obj[0], apply=True, translate=True, rotate=True, scale=True)
                                        if self.checkFrozenObject(obj[0], zeroAttrList, 0) and self.checkFrozenObject(obj[0], oneAttrList, 1):
                                            self.found_issues[obj[1]] = False
                                            self.good_results[obj[1]] = True
                                            self.messages.append(self.ar.data.lang['v019_frozenTransform']+obj[0])
                                        else:
                                            raise Exception('Freeze Tranform Failed')
                                    except:
                                        self.messages.append(self.ar.data.lang['v017_freezeError'] + obj+'.')
                                else:
                                    self.messages.append(self.ar.data.lang['v017_freezeError'] + obj+'.')
                else:
                    self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
            else:
                self.fail_io(self.ar.data.lang['v100_cantExistsGuides'])
        else:
            self.fail_io(self.ar.data.lang['v099_cantExistsAllGrp'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data


    def checkFrozenObject(self, obj, attributes, compValue, *args):
        """ Compare values.
            Return True if equal.
        """
        for attr in attributes:
            if cmds.getAttr(obj+'.'+attr) != compValue:
                return False
        return True


    def unlockAttributes(self, obj, attributes, *args):
        """ Just unlock attributes.
        """
        for attr in attributes:
            if self.animCurvesList:
                if obj+'_'+attr in self.animCurvesList:
                    return False
                else:
                    cmds.setAttr(obj+'.'+attr, lock=False)
            else:
                cmds.setAttr(obj+'.'+attr, lock=False)
        return True
