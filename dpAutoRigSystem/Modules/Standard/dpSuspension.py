# importing libraries:
from maya import cmds
from ..Base import dpBaseStandard
from ..Base import dpBaseLayout

# global variables to this module:    
CLASS_NAME = "Suspension"
TITLE = "m153_suspension"
DESCRIPTION = "m154_suspensionDesc"
ICON = "/Icons/dp_suspension.png"
WIKI = "03-‐-Guides#-suspension"

DP_SUSPENSION_VERSION = 2.04


class Suspension(dpBaseStandard.BaseStandard, dpBaseLayout.BaseLayout):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseStandard.BaseStandard.__init__(self, *args, **kwargs)
    
    
    def createModuleLayout(self, *args):
        dpBaseStandard.BaseStandard.createModuleLayout(self)
        dpBaseLayout.BaseLayout.basicModuleLayout(self)
    
    
    def getModuleAttr(self, moduleAttr, *args):
        return cmds.getAttr(self.moduleGrp + "." + moduleAttr)
        
    
    def createGuide(self, *args):
        dpBaseStandard.BaseStandard.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName="fatherB", dataType='string')
        
        self.cvALoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLocA", r=0.3, d=1, guide=True)
        self.jAGuide = cmds.joint(name=self.guideName+"_jAGuide", radius=0.001)
        cmds.setAttr(self.jAGuide+".template", 1)
        cmds.parent(self.jAGuide, self.moduleGrp, relative=True)
        
        self.cvBLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLocB", r=0.3, d=1, guide=True)
        cmds.parent(self.cvBLoc, self.cvALoc)
        cmds.setAttr(self.cvBLoc+".tz", 3)
        cmds.setAttr(self.cvBLoc+".rotateX", 180)
        self.jBGuide = cmds.joint(name=self.guideName+"_jBGuide", radius=0.001)
        cmds.setAttr(self.jBGuide+".template", 1)
        cmds.transformLimits(self.cvBLoc, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvBLoc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        
        cmds.parent(self.cvALoc, self.moduleGrp)
        cmds.parent(self.jBGuide, self.jAGuide)
        cmds.parentConstraint(self.cvALoc, self.jAGuide, maintainOffset=False, name=self.jAGuide+"_PaC")
        cmds.parentConstraint(self.cvBLoc, self.jBGuide, maintainOffset=False, name=self.jBGuide+"_PaC")
        cmds.scaleConstraint(self.cvALoc, self.jAGuide, maintainOffset=False, name=self.jAGuide+"_ScC")
        cmds.scaleConstraint(self.cvBLoc, self.jBGuide, maintainOffset=False, name=self.jBGuide+"_ScC")
        # include nodes into net
        self.addNodeToGuideNet([self.cvALoc, self.cvBLoc], ["JointLocA", "JointLocB"])
    
    
    def loadFatherB(self, *args):
        """ Loads the selected node to fatherBTextField in selectedModuleLayout.
        """
        selList = cmds.ls(selection=True)
        if selList:
            if cmds.objExists(selList[0]):
                cmds.textField(self.fatherBTF, edit=True, text=selList[0])
                cmds.setAttr(self.moduleGrp+".fatherB", selList[0], type='string')
    
    
    def changeFatherB(self, *args):
        """ Update moduleGrp fatherB attribute from UI textField.
        """
        newFatherBValue = cmds.textField(self.fatherBTF, query=True, text=True)
        cmds.setAttr(self.moduleGrp+".fatherB", newFatherBValue, type='string')
    
    
    def rigModule(self, *args):
        dpBaseStandard.BaseStandard.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            # declare lists to store names and attributes:
            self.suspensionBCtrlGrpList, self.fatherBList, self.ctrlHookGrpList = [], [], []
            # run for all sides
            for s, side in enumerate(self.sideList):
                # declare guide:
                self.base = side+self.userGuideName+'_Guide_Base'
                self.cvALoc = side+self.userGuideName+"_Guide_JointLocA"
                self.cvBLoc = side+self.userGuideName+"_Guide_JointLocB"
                self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"
                self.locatorsGrp = cmds.group(name=side+self.userGuideName+"_Loc_Grp", empty=True)
                # calculate distance between guide and end:
                self.dist = self.utils.distanceBet(self.cvALoc, self.cvBLoc)[0] * 0.2
                self.jointList, self.mainCtrlList, self.ctrlZeroList, self.ctrlList, self.aimLocList, self.upLocList = [], [], [], [], [], []
                for p, letter in enumerate(["A", "B"]):
                    # create joints:
                    cmds.select(clear=True)
                    jnt = cmds.joint(name=side+self.userGuideName+"_"+letter+"_1_Jnt", scaleCompensate=False)
                    endJoint = cmds.joint(name=side+self.userGuideName+"_"+letter+"_"+self.dpUIinst.jointEndAttr, scaleCompensate=False, radius=0.5)
                    self.utils.addJointEndAttr([endJoint])
                    cmds.addAttr(jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    cmds.setAttr(endJoint+".translateZ", self.dist)
                    # joint labelling:
                    self.utils.setJointLabel(jnt, s+self.jointLabelAdd, 18, self.userGuideName+"_"+letter)
                    self.jointList.append(jnt)
                    
                    # create a control:
                    mainCtrl = self.ctrls.cvControl("id_055_SuspensionMain", side+self.userGuideName+"_"+self.dpUIinst.lang["c058_main"]+"_"+letter+"_Ctrl", r=self.ctrlRadius, d=self.curveDegree, guideSource=self.guideName+"_JointLoc"+letter)
                    ctrl = self.ctrls.cvControl("id_056_SuspensionAB", side+self.userGuideName+"_"+letter+"_Ctrl", r=self.ctrlRadius*0.5, d=self.curveDegree, guideSource=self.guideName+"_JointLoc"+letter, parentTag=mainCtrl)
                    upLocCtrl = self.ctrls.cvControl("id_057_SuspensionUpLoc", side+self.userGuideName+"_"+letter+"_UpLoc_Ctrl", r=self.ctrlRadius*0.1, d=self.curveDegree, guideSource=self.guideName+"_JointLoc"+letter, parentTag=ctrl)
                    self.ctrls.setLockHide([ctrl], ['tx', 'ty', 'tz', 'v'])
                    self.ctrls.setLockHide([upLocCtrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
                    # position and orientation of joint and control:
                    cmds.parent(ctrl, upLocCtrl, mainCtrl)
                    cmds.parentConstraint(ctrl, jnt, maintainOffset=False, name=jnt+"_PaC")
                    cmds.scaleConstraint(ctrl, jnt, maintainOffset=False, name=jnt+"_ScC")
                    self.ctrlList.append(ctrl)
                    # zeroOut controls:
                    zeroOutCtrlGrp = self.utils.zeroOut([mainCtrl, ctrl, upLocCtrl])
                    self.mainCtrlList.append(zeroOutCtrlGrp[0])
                    self.ctrlZeroList.append(zeroOutCtrlGrp[1])
                    cmds.setAttr(zeroOutCtrlGrp[2]+".translateX", self.dist)
                    # origined from data:
                    if p == 0:
                        self.utils.originedFrom(objName=mainCtrl, attrString=self.base+";"+self.cvALoc+";"+self.radiusGuide)
                        cmds.delete(cmds.parentConstraint(self.cvALoc, zeroOutCtrlGrp[0], maintainOffset=False))
                    else:
                        self.utils.originedFrom(objName=mainCtrl, attrString=self.cvBLoc)
                        cmds.delete(cmds.parentConstraint(self.cvBLoc, zeroOutCtrlGrp[0], maintainOffset=False))
                        # integrating data:
                        self.suspensionBCtrlGrpList.append(zeroOutCtrlGrp[0])
                    # hide visibility attribute:
                    cmds.setAttr(mainCtrl+'.visibility', keyable=False)
                    # fixing flip mirror:
                    if s == 1:
                        if cmds.getAttr(self.moduleGrp+".flip") == 1:
                            cmds.setAttr(zeroOutCtrlGrp[0]+".scaleX", -1)
                            cmds.setAttr(zeroOutCtrlGrp[0]+".scaleY", -1)
                            cmds.setAttr(zeroOutCtrlGrp[0]+".scaleZ", -1)
                    cmds.addAttr(ctrl, longName='scaleCompensate', attributeType="short", minValue=0, maxValue=1, defaultValue=1, keyable=False)
                    cmds.setAttr(ctrl+".scaleCompensate", channelBox=True)
                    cmds.connectAttr(ctrl+".scaleCompensate", jnt+".segmentScaleCompensate", force=True)
                    
                    # working with aim setup:
                    cmds.addAttr(ctrl, longName=self.dpUIinst.lang['c118_active'], attributeType="short", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                    aimLoc = cmds.spaceLocator(name=side+self.userGuideName+"_"+letter+"_Aim_Loc")[0]
                    upLoc = cmds.spaceLocator(name=side+self.userGuideName+"_"+letter+"_Up_Loc")[0]
                    locGrp = cmds.group(aimLoc, upLoc, name=side+self.userGuideName+"_"+letter+"_Loc_Grp")
                    cmds.parent(locGrp, self.locatorsGrp, relative=True)
                    cmds.delete(cmds.parentConstraint(ctrl, locGrp, maintainOffset=False))
                    cmds.parentConstraint(upLocCtrl, upLoc, maintainOffset=False, name=upLoc+"_PaC")
                    cmds.parentConstraint(mainCtrl, locGrp, maintainOffset=True, name=locGrp+"_PaC")
                    cmds.setAttr(locGrp+".visibility", 0)
                    self.aimLocList.append(aimLoc)
                    self.upLocList.append(upLoc)

                # aim constraints:
                # B to A:
                aAimConst = cmds.aimConstraint(self.aimLocList[1], self.ctrlZeroList[0], aimVector=(0, 0, 1), upVector=(1, 0, 0), worldUpType="object", worldUpObject=self.upLocList[0], maintainOffset=True, name=self.ctrlZeroList[0]+"_AiC")[0]
                cmds.connectAttr(self.ctrlList[0]+"."+self.dpUIinst.lang['c118_active'], aAimConst+"."+self.aimLocList[1]+"W0", force=True)
                # A to B:
                bAimConst = cmds.aimConstraint(self.aimLocList[0], self.ctrlZeroList[1], aimVector=(0, 0, 1), upVector=(1, 0, 0), worldUpType="object", worldUpObject=self.upLocList[1], maintainOffset=True, name=self.ctrlZeroList[1]+"_AiC")[0]
                cmds.connectAttr(self.ctrlList[1]+"."+self.dpUIinst.lang['c118_active'], bAimConst+"."+self.aimLocList[0]+"W0", force=True)
                
                # integrating data:
                self.loadedFatherB = cmds.getAttr(self.moduleGrp+".fatherB")
                if self.loadedFatherB:
                    self.fatherBList.append(self.loadedFatherB)
                else:
                    self.fatherBList.append(None)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.hookSetup(side, self.mainCtrlList, self.jointList, [self.locatorsGrp])
                self.ctrlHookGrpList.append(self.toCtrlHookGrp)
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)
                self.dpUIinst.customAttr.addAttr(0, [self.toStaticHookGrp], descendents=True) #dpID
            # finalize this rig:
            self.serializeGuide()
            self.integratingInfo()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and moduleInstance namespace:
        self.deleteModule()
        self.renameUnitConversion()
    
    
    def integratingInfo(self, *args):
        dpBaseStandard.BaseStandard.integratingInfo(self)
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.integratedActionsDic = {
                                    "module": {
                                                "suspensionBCtrlGrpList" : self.suspensionBCtrlGrpList,
                                                "fatherBList"        : self.fatherBList,
                                                "ctrlHookGrpList"    : self.ctrlHookGrpList,
                                              }
                                    }