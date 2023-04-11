# importing libraries:
from maya import cmds

# global variables to this module:    
CLASS_NAME = "LimbSpaceSwitch"
TITLE = "m059_limbSpaceSwitch"
DESCRIPTION = "m060_limbSpaceSwitchDesc"
ICON = "/Icons/dp_limbSpaceSwitch.png"

DPLSS_VERSION = "2.0"

class LimbSpaceSwitch(object):
    def __init__(self, dpUIinst, langDic, langName, *args):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        
        self.globalName = "Global"
        self.rootName = "Root"
        self.spineName = self.langDic[self.langName]['m011_spine']
        self.hipsName = self.langDic[self.langName]['c027_hips']
        self.headName = self.langDic[self.langName]['c024_head']
        self.chestName = self.langDic[self.langName]['c028_chest']
        
        self.globalCtrl = self.globalName+"_Ctrl"
        self.rootCtrl = self.rootName+"_Ctrl"
        self.spineHipsACtrl = self.spineName+"_"+self.hipsName+"A_Ctrl"
        self.spineHipsBCtrl = self.spineName+"_"+self.hipsName+"B_Ctrl"
        self.spineChestACtrl = self.spineName+"_"+self.chestName+"A_Ctrl"
        self.spineChestBCtrl = self.spineName+"_"+self.chestName+"B_Ctrl"
        self.headSubCtrl = self.headName+"_"+self.headName+"_Sub_Ctrl"

        self.followAttr = self.langDic[self.langName]['c032_follow']
        
        # call main function
        self.dpMain(self)
    
    
    def dpMain(self, *args):
        """ Main function.
            Check existen nodes and call the scripted function.
        """
        callAction = True
        if not cmds.objExists(self.spineChestACtrl):
            callAction = False
        if not cmds.objExists(self.globalCtrl):
            callAction = False
        if not cmds.objExists(self.rootCtrl):
            callAction = False
        if not cmds.objExists(self.spineHipsBCtrl):
            callAction = False
        if not cmds.objExists(self.headSubCtrl):
            callAction = False
        if callAction:
            self.dpDoAddHandFollow()
    
    
    def dpSetHandFollowSDK(self, *args):
        """ Create the setDrivenKey.
        """
        ikCtrl = args[0]
        cmds.setDrivenKeyframe(self.pac+"."+self.globalCtrl+"W0", currentDriver=ikCtrl+"."+self.followAttr)
        cmds.setDrivenKeyframe(self.pac+"."+self.rootCtrl+"W1", currentDriver=ikCtrl+"."+self.followAttr)
        cmds.setDrivenKeyframe(self.pac+"."+self.spineHipsACtrl+"W2", currentDriver=ikCtrl+"."+self.followAttr)
        cmds.setDrivenKeyframe(self.pac+"."+self.spineHipsBCtrl+"W3", currentDriver=ikCtrl+"."+self.followAttr)
        cmds.setDrivenKeyframe(self.pac+"."+self.spineChestACtrl+"W4", currentDriver=ikCtrl+"."+self.followAttr)
        cmds.setDrivenKeyframe(self.pac+"."+self.spineChestBCtrl+"W5", currentDriver=ikCtrl+"."+self.followAttr)
        cmds.setDrivenKeyframe(self.pac+"."+self.headSubCtrl+"W6", currentDriver=ikCtrl+"."+self.followAttr)
    
    
    def dpDoAddHandFollow(self, *args):
        """ Set attributes and call setDrivenKey method.
        """
        sideList = [self.langDic[self.langName]['p002_left'], self.langDic[self.langName]['p003_right']]
        limbList = [self.langDic[self.langName]['c037_arm']+"_"+self.langDic[self.langName]['c004_arm_extrem'], self.langDic[self.langName]['c006_leg_main']+"_"+self.langDic[self.langName]['c009_leg_extrem']]
        for side in sideList:
            for x, limbNode in enumerate(limbList):
                ikCtrl = side+"_"+limbNode+"_Ik_Ctrl"
                
                if cmds.objExists(ikCtrl):
                    if cmds.objExists(ikCtrl+"."+self.followAttr):
                        return
                    else:
                        if x == 0: #arm
                            followValue = 4 #chestB
                        else: #leg
                            followValue = 1 #root

                        cmds.addAttr(ikCtrl, ln=self.followAttr, at="enum", en=self.globalName+":"+self.rootName+":"+self.hipsName+"A:"+self.hipsName+"B:"+self.chestName+"A:"+self.chestName+"B:"+self.headName+":", defaultValue=followValue)
                        cmds.setAttr(ikCtrl+"."+self.followAttr, edit=True, keyable=True)
                        
                        self.pac = cmds.parentConstraint(self.globalCtrl, self.rootCtrl, self.spineHipsACtrl, self.spineHipsBCtrl, self.spineChestACtrl, self.spineChestBCtrl, self.headSubCtrl, ikCtrl+"_Orient_Grp", maintainOffset=True, name=ikCtrl+"_Orient_Grp_PaC")[0]
                        
                        cmds.setAttr(ikCtrl+"."+self.followAttr, 0)
                        cmds.setAttr(self.pac+"."+self.globalCtrl+"W0", 1)
                        cmds.setAttr(self.pac+"."+self.rootCtrl+"W1", 0)
                        cmds.setAttr(self.pac+"."+self.spineHipsACtrl+"W2", 0)
                        cmds.setAttr(self.pac+"."+self.spineHipsBCtrl+"W3", 0)
                        cmds.setAttr(self.pac+"."+self.spineChestACtrl+"W4", 0)
                        cmds.setAttr(self.pac+"."+self.spineChestBCtrl+"W5", 0)
                        cmds.setAttr(self.pac+"."+self.headSubCtrl+"W6", 0)
                        self.dpSetHandFollowSDK(ikCtrl)

                        cmds.setAttr(ikCtrl+"."+self.followAttr, 1)
                        cmds.setAttr(self.pac+"."+self.globalCtrl+"W0", 0)
                        cmds.setAttr(self.pac+"."+self.rootCtrl+"W1", 1)
                        self.dpSetHandFollowSDK(ikCtrl)

                        cmds.setAttr(ikCtrl+"."+self.followAttr, 2)
                        cmds.setAttr(self.pac+"."+self.rootCtrl+"W1", 0)
                        cmds.setAttr(self.pac+"."+self.spineHipsACtrl+"W2", 1)
                        self.dpSetHandFollowSDK(ikCtrl)

                        cmds.setAttr(ikCtrl+"."+self.followAttr, 3)
                        cmds.setAttr(self.pac+"."+self.spineHipsACtrl+"W2", 0)
                        cmds.setAttr(self.pac+"."+self.spineHipsBCtrl+"W3", 1)
                        self.dpSetHandFollowSDK(ikCtrl)

                        cmds.setAttr(ikCtrl+"."+self.followAttr, 4)
                        cmds.setAttr(self.pac+"."+self.spineHipsBCtrl+"W3", 0)
                        cmds.setAttr(self.pac+"."+self.spineChestACtrl+"W4", 1)
                        self.dpSetHandFollowSDK(ikCtrl)
                        
                        cmds.setAttr(ikCtrl+"."+self.followAttr, 5)
                        cmds.setAttr(self.pac+"."+self.spineChestACtrl+"W4", 0)
                        cmds.setAttr(self.pac+"."+self.spineChestBCtrl+"W5", 1)
                        self.dpSetHandFollowSDK(ikCtrl)

                        cmds.setAttr(ikCtrl+"."+self.followAttr, 6)
                        cmds.setAttr(self.pac+"."+self.spineChestBCtrl+"W5", 0)
                        cmds.setAttr(self.pac+"."+self.headSubCtrl+"W6", 1)
                        self.dpSetHandFollowSDK(ikCtrl)

                        cmds.setAttr(ikCtrl+"."+self.followAttr, followValue)
