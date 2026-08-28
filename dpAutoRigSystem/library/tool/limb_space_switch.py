# importing libraries:
from maya import cmds
from ..base import base
from importlib import reload

# global variables to this module:    
CLASS_NAME = "LimbSpaceSwitch"
TITLE = "m059_limbSpaceSwitch"
DESCRIPTION = "m060_limbSpaceSwitchDesc"
WIKI = "06-‐-Tools#-limb-space-switch"



class LimbSpaceSwitch(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        
        
    def build_tool(self, *args):
        # find nodes
        all_grp = self.ar.utils.getAllGrp()
        if all_grp:
            self.root_ctrl = self.ar.utils.getNodeByMessage("ctrlsVisibilityGrp", all_grp)
            self.global_ctrl = self.ar.utils.getNodeByMessage("globalCtrl", all_grp)
            self.to_ids = []

            self.global_name = "Global"
            self.root_name = "Root"

            self.spine_name = self.ar.data.lang['m011_spine']
            self.hips_name = self.ar.data.lang['c027_hips']
            self.head_name = self.ar.data.lang['c024_head']
            self.chest_name = self.ar.data.lang['c028_chest']
            
            self.spine_hips_a_ctrl = self.spine_name+"_"+self.hips_name+"A_Ctrl"
            self.spine_hips_b_ctrl = self.spine_name+"_"+self.hips_name+"B_Ctrl"
            self.spine_chest_a_ctrl = self.spine_name+"_"+self.chest_name+"A_Ctrl"
            self.spine_chest_b_ctrl = self.spine_name+"_"+self.chest_name+"B_Ctrl"
            self.head_sub_ctrl = self.head_name+"_"+self.head_name+"_Sub_Ctrl"
            self.follow_attr = self.ar.data.lang['c032_follow']

            # call main function
            self.run_limb_space_switch(self)
    
    
    def run_limb_space_switch(self, *args):
        """ Main function.
            Check existen nodes and call the scripted function.
        """
        call_action = True
        if not cmds.objExists(self.spine_chest_a_ctrl):
            call_action = False
        if not cmds.objExists(self.global_ctrl):
            call_action = False
        if not cmds.objExists(self.root_ctrl):
            call_action = False
        if not cmds.objExists(self.spine_hips_b_ctrl):
            call_action = False
        if not cmds.objExists(self.head_sub_ctrl):
            call_action = False
        if call_action:
            self.do_add_hand_follow()
    
    
    def set_hand_follow_sdk(self, *args):
        """ Create the setDrivenKey.
        """
        ik_ctrl = args[0]
        cmds.setDrivenKeyframe(self.pac+"."+self.global_ctrl+"W0", currentDriver=ik_ctrl+"."+self.follow_attr)
        cmds.setDrivenKeyframe(self.pac+"."+self.root_ctrl+"W1", currentDriver=ik_ctrl+"."+self.follow_attr)
        cmds.setDrivenKeyframe(self.pac+"."+self.spine_hips_a_ctrl+"W2", currentDriver=ik_ctrl+"."+self.follow_attr)
        cmds.setDrivenKeyframe(self.pac+"."+self.spine_hips_b_ctrl+"W3", currentDriver=ik_ctrl+"."+self.follow_attr)
        cmds.setDrivenKeyframe(self.pac+"."+self.spine_chest_a_ctrl+"W4", currentDriver=ik_ctrl+"."+self.follow_attr)
        cmds.setDrivenKeyframe(self.pac+"."+self.spine_chest_b_ctrl+"W5", currentDriver=ik_ctrl+"."+self.follow_attr)
        cmds.setDrivenKeyframe(self.pac+"."+self.head_sub_ctrl+"W6", currentDriver=ik_ctrl+"."+self.follow_attr)
    
    
    def do_add_hand_follow(self, *args):
        """ Set attributes and call setDrivenKey method.
        """
        old_drivenkeys = cmds.ls(selection=False, type=self.ar.data.drivenkey_types)
        side_items = [self.ar.data.lang['p002_left'], self.ar.data.lang['p003_right']]
        limb_items = [
                    self.ar.data.lang['c037_arm']+"_"+self.ar.data.lang['c004_arm_extrem'],
                    self.ar.data.lang['c006_leg_main']+"_"+self.ar.data.lang['c009_leg_extrem'],
                    self.ar.data.lang['c006_leg_main']+self.ar.data.lang['c056_front']+"_"+self.ar.data.lang['c009_leg_extrem'],
                    self.ar.data.lang['c006_leg_main']+self.ar.data.lang['c057_back']+"_"+self.ar.data.lang['c009_leg_extrem']
                    ]
        for side in side_items:
            for x, limb_node in enumerate(limb_items):
                ik_ctrl = side+"_"+limb_node+"_Ik_Ctrl"
                
                if cmds.objExists(ik_ctrl):
                    if self.follow_attr in cmds.listAttr(ik_ctrl):
                        pass
                    else:
                        if x == 0: #arm
                            follow_value = 4 #chestB
                        else: #leg
                            follow_value = 1 #root

                        cmds.addAttr(ik_ctrl, ln=self.follow_attr, at="enum", en=self.global_name+":"+self.root_name+":"+self.hips_name+"A:"+self.hips_name+"B:"+self.chest_name+"A:"+self.chest_name+"B:"+self.head_name+":", defaultValue=follow_value)
                        cmds.setAttr(ik_ctrl+"."+self.follow_attr, edit=True, keyable=True)
                        
                        self.pac = cmds.parentConstraint(self.global_ctrl, self.root_ctrl, self.spine_hips_a_ctrl, self.spine_hips_b_ctrl, self.spine_chest_a_ctrl, self.spine_chest_b_ctrl, self.head_sub_ctrl, ik_ctrl+"_Orient_Grp", maintainOffset=True, name=ik_ctrl+"_Orient_Grp_PaC")[0]
                        self.to_ids.append(self.pac)

                        cmds.setAttr(ik_ctrl+"."+self.follow_attr, 0)
                        cmds.setAttr(self.pac+"."+self.global_ctrl+"W0", 1)
                        cmds.setAttr(self.pac+"."+self.root_ctrl+"W1", 0)
                        cmds.setAttr(self.pac+"."+self.spine_hips_a_ctrl+"W2", 0)
                        cmds.setAttr(self.pac+"."+self.spine_hips_b_ctrl+"W3", 0)
                        cmds.setAttr(self.pac+"."+self.spine_chest_a_ctrl+"W4", 0)
                        cmds.setAttr(self.pac+"."+self.spine_chest_b_ctrl+"W5", 0)
                        cmds.setAttr(self.pac+"."+self.head_sub_ctrl+"W6", 0)
                        self.set_hand_follow_sdk(ik_ctrl)

                        cmds.setAttr(ik_ctrl+"."+self.follow_attr, 1)
                        cmds.setAttr(self.pac+"."+self.global_ctrl+"W0", 0)
                        cmds.setAttr(self.pac+"."+self.root_ctrl+"W1", 1)
                        self.set_hand_follow_sdk(ik_ctrl)

                        cmds.setAttr(ik_ctrl+"."+self.follow_attr, 2)
                        cmds.setAttr(self.pac+"."+self.root_ctrl+"W1", 0)
                        cmds.setAttr(self.pac+"."+self.spine_hips_a_ctrl+"W2", 1)
                        self.set_hand_follow_sdk(ik_ctrl)

                        cmds.setAttr(ik_ctrl+"."+self.follow_attr, 3)
                        cmds.setAttr(self.pac+"."+self.spine_hips_a_ctrl+"W2", 0)
                        cmds.setAttr(self.pac+"."+self.spine_hips_b_ctrl+"W3", 1)
                        self.set_hand_follow_sdk(ik_ctrl)

                        cmds.setAttr(ik_ctrl+"."+self.follow_attr, 4)
                        cmds.setAttr(self.pac+"."+self.spine_hips_b_ctrl+"W3", 0)
                        cmds.setAttr(self.pac+"."+self.spine_chest_a_ctrl+"W4", 1)
                        self.set_hand_follow_sdk(ik_ctrl)
                        
                        cmds.setAttr(ik_ctrl+"."+self.follow_attr, 5)
                        cmds.setAttr(self.pac+"."+self.spine_chest_a_ctrl+"W4", 0)
                        cmds.setAttr(self.pac+"."+self.spine_chest_b_ctrl+"W5", 1)
                        self.set_hand_follow_sdk(ik_ctrl)

                        cmds.setAttr(ik_ctrl+"."+self.follow_attr, 6)
                        cmds.setAttr(self.pac+"."+self.spine_chest_b_ctrl+"W5", 0)
                        cmds.setAttr(self.pac+"."+self.head_sub_ctrl+"W6", 1)
                        self.set_hand_follow_sdk(ik_ctrl)

                        cmds.setAttr(ik_ctrl+"."+self.follow_attr, follow_value)

        current_drivenkeys = cmds.ls(selection=False, type=self.ar.data.drivenkey_types)
        new_drivenkeys = current_drivenkeys
        if old_drivenkeys:
            new_drivenkeys = list(set(current_drivenkeys) - set(old_drivenkeys))
        self.to_ids.extend(new_drivenkeys)
        self.ar.custom_attr.add_attr(0, self.to_ids) #dpID
