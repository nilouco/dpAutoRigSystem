# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "AddHandFollow"
TITLE = "m059_addHandFollow"
DESCRIPTION = "m060_addHandFollowDesc"
ICON = "/Icons/dp_addHandFollow.png"


class AddHandFollow():
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
        self.defaultName = self.langDic[self.langName]['m042_default']
        self.chestName = self.langDic[self.langName]['c028_chest']
        
        self.spineChestACtrl = self.spineName+"_"+self.chestName+"A_Ctrl"
        self.globalCtrl = self.globalName+"_Ctrl"
        self.rootCtrl = self.rootName+"_Ctrl"
        self.spineHipsBCtrl = self.spineName+"_"+self.hipsName+"B_Ctrl"
        self.headCtrl = self.headName+"_"+self.headName+"_Ctrl"
        
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
        if not cmds.objExists(self.headCtrl):
            callAction = False
        if callAction:
            self.dpDoAddHandFollow()
    
    
    def dpSetHandFollowSDK(self, *args):
        """ Create the setDrivenKey.
        """
        armWristIkCtrl = args[0]
        cmds.setDrivenKeyframe(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.spineChestACtrl+"W0", currentDriver=armWristIkCtrl+"."+self.langDic[self.langName]['c032_Follow'])
        cmds.setDrivenKeyframe(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.globalCtrl+"W1", currentDriver=armWristIkCtrl+"."+self.langDic[self.langName]['c032_Follow'])
        cmds.setDrivenKeyframe(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.rootCtrl+"W2", currentDriver=armWristIkCtrl+"."+self.langDic[self.langName]['c032_Follow'])
        cmds.setDrivenKeyframe(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.spineHipsBCtrl+"W3", currentDriver=armWristIkCtrl+"."+self.langDic[self.langName]['c032_Follow'])
        cmds.setDrivenKeyframe(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.headCtrl+"W4", currentDriver=armWristIkCtrl+"."+self.langDic[self.langName]['c032_Follow'])
    
    
    def dpDoAddHandFollow(self, *args):
        """ Set attributes and call setDrivenKey method.
        """
        sideList = [self.langDic[self.langName]['p002_left'], self.langDic[self.langName]['p003_right']]
        for side in sideList:
            armWristIkCtrl = side+"_"+self.langDic[self.langName]['c037_arm']+"_"+self.langDic[self.langName]['c004_arm_extrem']+"_Ik_Ctrl"
            
            if cmds.objExists(armWristIkCtrl):
                if cmds.objExists(armWristIkCtrl+"."+self.langDic[self.langName]['c032_Follow']):
                    return
                else:
                    cmds.addAttr(armWristIkCtrl, ln=self.langDic[self.langName]['c032_Follow'], at="enum", en=self.defaultName+":"+self.globalName+":"+self.rootName+":"+self.hipsName+":"+self.headName+":")
                    cmds.setAttr(armWristIkCtrl+"."+self.langDic[self.langName]['c032_Follow'], edit=True, keyable=True)
                    
                    parentConst = cmds.parentConstraint(self.spineChestACtrl, self.globalCtrl, self.rootCtrl, self.spineHipsBCtrl, self.headCtrl, armWristIkCtrl+"_Orient_Grp", mo=True, name=armWristIkCtrl+"_Orient_Grp_ParentConstraint")
                    
                    cmds.setAttr(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.globalCtrl+"W1", 0)
                    cmds.setAttr(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.rootCtrl+"W2", 0)
                    cmds.setAttr(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.spineHipsBCtrl+"W3", 0)
                    cmds.setAttr(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.headCtrl+"W4", 0)
                    self.dpSetHandFollowSDK(armWristIkCtrl)

                    cmds.setAttr(armWristIkCtrl+"."+self.langDic[self.langName]['c032_Follow'], 1)
                    cmds.setAttr(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.spineChestACtrl+"W0", 0)
                    cmds.setAttr(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.globalCtrl+"W1", 1)
                    self.dpSetHandFollowSDK(armWristIkCtrl)

                    cmds.setAttr(armWristIkCtrl+"."+self.langDic[self.langName]['c032_Follow'], 2)
                    cmds.setAttr(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.globalCtrl+"W1", 0)
                    cmds.setAttr(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.rootCtrl+"W2", 1)
                    self.dpSetHandFollowSDK(armWristIkCtrl)

                    cmds.setAttr(armWristIkCtrl+"."+self.langDic[self.langName]['c032_Follow'], 3)
                    cmds.setAttr(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.rootCtrl+"W2", 0)
                    cmds.setAttr(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.spineHipsBCtrl+"W3", 1)
                    self.dpSetHandFollowSDK(armWristIkCtrl)

                    cmds.setAttr(armWristIkCtrl+"."+self.langDic[self.langName]['c032_Follow'], 4)
                    cmds.setAttr(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.spineHipsBCtrl+"W3", 0)
                    cmds.setAttr(armWristIkCtrl+"_Orient_Grp_ParentConstraint."+self.headCtrl+"W4", 1)
                    self.dpSetHandFollowSDK(armWristIkCtrl)
                    
                    cmds.setAttr(armWristIkCtrl+"."+self.langDic[self.langName]['c032_Follow'], 0)

