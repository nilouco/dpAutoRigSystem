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
                    transforms, to_fix_items = [], []
                    if inputs:
                        transforms = list(filter(lambda item: cmds.objectType(item) == 'transform', inputs))
                    if len(transforms) == 0:
                        transforms = cmds.ls(selection=False, type='transform', long=True)
                    # analisys transformations
                    if len(transforms) > 0:
                        self.ar.utils.set_progress(max=len(transforms), add_one=False, add_number=False)
                        self.anim_curves = cmds.ls(type='animCurve')
                        zero_attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
                        one_attrs = ['scaleX', 'scaleY', 'scaleZ']
                        cameras = ['|persp', '|top', '|side', '|front', '|bottom', '|back', '|left']
                        valid_items = list(filter(lambda item: item not in cameras, transforms))
                        for idx, item in enumerate(valid_items):
                            self.ar.utils.set_progress(self.ar.data.lang[self.title])
                            if cmds.objExists(item):
                                # run for translates and rotates
                                frozen_tr = self.check_frozen_item(item, zero_attrs, 0)
                                # run for scales
                                frozen_s = self.check_frozen_item(item, one_attrs, 1)
                                self.checked_items.append(item)
                                if frozen_tr and frozen_s:
                                    self.found_issues.append(False)
                                    self.good_results.append(True)
                                else:
                                    self.found_issues.append(True)
                                    self.good_results.append(False)
                                    self.messages.append(self.ar.data.lang['v018_foundTransform']+item)
                                    to_fix_items.append((item, idx))
                        if not self.first_mode and len(to_fix_items) > 0: #one item to fix
                            for item in to_fix_items:
                                self.locked_attrs = cmds.listAttr(item[0], locked=True)
                                if self.unlock_attrs(item[0], zero_attrs) and self.unlock_attrs(item[0], one_attrs):
                                    try:
                                        cmds.makeIdentity(item[0], apply=True, translate=True, rotate=True, scale=True)
                                        if self.check_frozen_item(item[0], zero_attrs, 0) and self.check_frozen_item(item[0], one_attrs, 1):
                                            self.found_issues[item[1]] = False
                                            self.good_results[item[1]] = True
                                            self.messages.append(self.ar.data.lang['v019_frozenTransform']+item[0])
                                        else:
                                            raise Exception('Freeze Tranform Failed')
                                    except:
                                        self.messages.append(self.ar.data.lang['v017_freezeError'] + item+'.')
                                else:
                                    self.messages.append(self.ar.data.lang['v017_freezeError'] + item+'.')
                                if self.locked_attrs:
                                    for attr in self.locked_attrs:
                                        cmds.setAttr(item[0]+'.'+attr, lock=True)
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


    def check_frozen_item(self, item, attributes, comp_value):
        """ Compare values.
            Return True if equal.
        """
        cmds.lockNode(item, lock=False, lockUnpublished=False)
        for attr in attributes:
            if cmds.getAttr(item+'.'+attr) != comp_value:
                return False
        return True


    def unlock_attrs(self, item, attributes):
        """ Just unlock attributes.
        """
        for attr in attributes:
            if self.anim_curves:
                if item+'_'+attr in self.anim_curves:
                    return False
                else:
                    cmds.setAttr(item+'.'+attr, lock=False)
            else:
                cmds.setAttr(item+'.'+attr, lock=False)
        return True
