# importing libraries:
import maya.cmds as cmds

from Library import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout


# global variables to this module:    
CLASS_NAME = "Suspension"
TITLE = "m153_suspension"
DESCRIPTION = "m154_suspensionDesc"
ICON = "/Icons/dp_suspension.png"


class Suspension(Base.StartClass, Layout.LayoutClass):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        Base.StartClass.__init__(self, *args, **kwargs)
    
    
    def createModuleLayout(self, *args):
        Base.StartClass.createModuleLayout(self)
        Layout.LayoutClass.basicModuleLayout(self)
    
    
    def getModuleAttr(self, moduleAttr, *args):
        return cmds.getAttr(self.moduleGrp + "." + moduleAttr)
        
    
    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".flip", 0)
        cmds.addAttr(self.moduleGrp, longName="fatherB", dataType='string')
        
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        
        self.cvALoc, shapeSizeCH = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLocA", r=0.3, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        self.jAGuide = cmds.joint(name=self.guideName+"_jAGuide", radius=0.001)
        cmds.setAttr(self.jAGuide+".template", 1)
        cmds.parent(self.jAGuide, self.moduleGrp, relative=True)
        
        self.cvBLoc, shapeSizeCH = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLocB", r=0.3, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvBLoc, self.cvALoc)
        cmds.setAttr(self.cvBLoc+".tz", 3)
        cmds.setAttr(self.cvBLoc+".rotateX", 180)
        self.jBGuide = cmds.joint(name=self.guideName+"_jBGuide", radius=0.001)
        cmds.setAttr(self.jBGuide+".template", 1)
        cmds.transformLimits(self.cvBLoc, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvBLoc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        
        cmds.parent(self.cvALoc, self.moduleGrp)
        cmds.parent(self.jBGuide, self.jAGuide)
        cmds.parentConstraint(self.cvALoc, self.jAGuide, maintainOffset=False, name=self.jAGuide+"_ParentConstraint")
        cmds.parentConstraint(self.cvBLoc, self.jBGuide, maintainOffset=False, name=self.jBGuide+"_ParentConstraint")
        cmds.scaleConstraint(self.cvALoc, self.jAGuide, maintainOffset=False, name=self.jAGuide+"_ScaleConstraint")
        cmds.scaleConstraint(self.cvBLoc, self.jBGuide, maintainOffset=False, name=self.jBGuide+"_ScaleConstraint")
    
    
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
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            # declare lists to store names and attributes:
            self.suspensionBCtrlGrpList, self.fatherBList, self.ctrlHookGrpList = [], [], []
            # start as no having mirror:
            sideList = [""]
            # analisys the mirror module:
            self.mirrorAxis = cmds.getAttr(self.moduleGrp+".mirrorAxis")
            if self.mirrorAxis != 'off':
                # get rigs names:
                self.mirrorNames = cmds.getAttr(self.moduleGrp+".mirrorName")
                # get first and last letters to use as side initials (prefix):
                sideList = [ self.mirrorNames[0]+'_', self.mirrorNames[len(self.mirrorNames)-1]+'_' ]
                for s, side in enumerate(sideList):
                    duplicated = cmds.duplicate(self.moduleGrp, name=side+self.userGuideName+'_Guide_Base')[0]
                    allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                    for item in allGuideList:
                        cmds.rename(item, side+self.userGuideName+"_"+item)
                    self.mirrorGrp = cmds.group(name="Guide_Base_Grp", empty=True)
                    cmds.parent(side+self.userGuideName+'_Guide_Base', self.mirrorGrp, absolute=True)
                    # re-rename grp:
                    cmds.rename(self.mirrorGrp, side+self.userGuideName+'_'+self.mirrorGrp)
                    # do a group mirror with negative scaling:
                    if s == 1:
                        if cmds.getAttr(self.moduleGrp+".flip") == 0:
                            for axis in self.mirrorAxis:
                                gotValue = cmds.getAttr(side+self.userGuideName+"_Guide_Base.translate"+axis)
                                flipedValue = gotValue*(-2)
                                cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.translate'+axis, flipedValue)
                        else:
                            for axis in self.mirrorAxis:
                                cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.scale'+axis, -1)
                # joint labelling:
                jointLabelAdd = 1
            else: # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_Guide_Base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(self.userGuideName+'_Guide_Base', name="Guide_Base_Grp", relative=True)
                #for Maya2012: self.userGuideName+'_'+self.moduleGrp+"_Grp"
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
                # joint labelling:
                jointLabelAdd = 0
            # store the number of this guide by module type
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # run for all sides
            for s, side in enumerate(sideList):
                # declare guide:
                self.base = side+self.userGuideName+'_Guide_Base'
                self.cvALoc = side+self.userGuideName+"_Guide_JointLocA"
                self.cvBLoc = side+self.userGuideName+"_Guide_JointLocB"
                self.locatorsGrp = cmds.group(name=side+self.userGuideName+"_Loc_Grp", empty=True)
                # calculate distance between guide and end:
                self.dist = self.ctrls.distanceBet(self.cvALoc, self.cvBLoc)[0] * 0.2
                self.jointList, self.mainCtrlList, self.ctrlZeroList, self.ctrlList, self.aimLocList, self.upLocList = [], [], [], [], [], []
                for p, letter in enumerate(["A", "B"]):
                    # create joints:
                    cmds.select(clear=True)
                    jnt = cmds.joint(name=side+self.userGuideName+"_"+letter+"_1_Jnt", scaleCompensate=False)
                    endJoint = cmds.joint(name=side+self.userGuideName+"_"+letter+"_JEnd", scaleCompensate=False)
                    cmds.addAttr(jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    cmds.setAttr(endJoint+".translateZ", self.dist)
                    # joint labelling:
                    utils.setJointLabel(jnt, s+jointLabelAdd, 18, self.userGuideName+"_"+letter)
                    self.jointList.append(jnt)
                    
                    # create a control:
                    mainCtrl = self.ctrls.cvControl("id_055_SuspensionMain", side+self.userGuideName+"_"+self.langDic[self.langName]["c058_main"]+"_"+letter+"_Ctrl", r=self.ctrlRadius, d=self.curveDegree)
                    ctrl = self.ctrls.cvControl("id_056_SuspensionAB", side+self.userGuideName+"_"+letter+"_Ctrl", r=self.ctrlRadius*0.5, d=self.curveDegree)
                    upLocCtrl = self.ctrls.cvControl("id_057_SuspensionUpLoc", side+self.userGuideName+"_"+letter+"_UpLoc_Ctrl", r=self.ctrlRadius*0.1, d=self.curveDegree)
                    self.ctrls.setLockHide([ctrl], ['tx', 'ty', 'tz', 'v'])
                    self.ctrls.setLockHide([upLocCtrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                    # position and orientation of joint and control:
                    cmds.parent(ctrl, upLocCtrl, mainCtrl)
                    cmds.parentConstraint(ctrl, jnt, maintainOffset=False, name=jnt+"_ParentConstraint")
                    cmds.scaleConstraint(ctrl, jnt, maintainOffset=False, name=jnt+"_ScaleConstraint")
                    self.ctrlList.append(ctrl)
                    # zeroOut controls:
                    zeroOutCtrlGrp = utils.zeroOut([mainCtrl, ctrl, upLocCtrl])
                    self.mainCtrlList.append(zeroOutCtrlGrp[0])
                    self.ctrlZeroList.append(zeroOutCtrlGrp[1])
                    cmds.setAttr(zeroOutCtrlGrp[2]+".translateX", self.dist)
                    # origined from data:
                    if p == 0:
                        utils.originedFrom(objName=mainCtrl, attrString=self.base+";"+self.cvALoc)
                        utils.originedFrom(objName=ctrl, attrString=self.base+";"+self.cvALoc)
                        cmds.delete(cmds.parentConstraint(self.cvALoc, zeroOutCtrlGrp[0], maintainOffset=False))
                    else:
                        utils.originedFrom(objName=mainCtrl, attrString=self.cvBLoc)
                        utils.originedFrom(objName=ctrl, attrString=self.cvBLoc)
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
                    cmds.addAttr(ctrl, longName='scaleCompensate', attributeType="bool", keyable=False)
                    cmds.setAttr(ctrl+".scaleCompensate", 1, channelBox=True)
                    cmds.connectAttr(ctrl+".scaleCompensate", jnt+".segmentScaleCompensate", force=True)
                    
                    # working with aim setup:
                    cmds.addAttr(ctrl, longName="active", attributeType="bool", defaultValue=1, keyable=True)
                    aimLoc = cmds.spaceLocator(name=side+self.userGuideName+"_"+letter+"_Aim_Loc")[0]
                    upLoc = cmds.spaceLocator(name=side+self.userGuideName+"_"+letter+"_Up_Loc")[0]
                    locGrp = cmds.group(aimLoc, upLoc, name=side+self.userGuideName+"_"+letter+"_Loc_Grp")
                    cmds.parent(locGrp, self.locatorsGrp, relative=True)
                    cmds.delete(cmds.parentConstraint(ctrl, locGrp, maintainOffset=False))
                    cmds.parentConstraint(upLocCtrl, upLoc, maintainOffset=False, name=upLoc+"_ParentConstraint")
                    cmds.parentConstraint(mainCtrl, locGrp, maintainOffset=True, name=locGrp+"_ParentConstraint")
                    cmds.setAttr(locGrp+".visibility", 0)
                    self.aimLocList.append(aimLoc)
                    self.upLocList.append(upLoc)

                # aim constraints:
                # B to A:
                aAimConst = cmds.aimConstraint(self.aimLocList[1], self.ctrlZeroList[0], aimVector=(0, 0, 1), upVector=(1, 0, 0), worldUpType="object", worldUpObject=self.upLocList[0], maintainOffset=True, name=self.ctrlZeroList[0]+"_AimConstraint")[0]
                cmds.connectAttr(self.ctrlList[0]+".active", aAimConst+"."+self.aimLocList[1]+"W0", force=True)
                # A to B:
                bAimConst = cmds.aimConstraint(self.aimLocList[0], self.ctrlZeroList[1], aimVector=(0, 0, 1), upVector=(1, 0, 0), worldUpType="object", worldUpObject=self.upLocList[1], maintainOffset=True, name=self.ctrlZeroList[0]+"_AimConstraint")[0]
                cmds.connectAttr(self.ctrlList[1]+".active", bAimConst+"."+self.aimLocList[0]+"W0", force=True)
                
                # integrating data:
                self.loadedFatherB = cmds.getAttr(self.moduleGrp+".fatherB")
                if self.loadedFatherB:
                    self.fatherBList.append(self.loadedFatherB)
                else:
                    self.fatherBList.append(None)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(self.mainCtrlList, name=side+self.userGuideName+"_Control_Grp")
                self.toScalableHookGrp = cmds.group(self.jointList, name=side+self.userGuideName+"_Joint_Grp")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, self.locatorsGrp, name=side+self.userGuideName+"_Grp")
                # add hook attributes to be read when rigging integrated modules:
                utils.addHook(objName=self.toCtrlHookGrp, hookType='ctrlHook')
                utils.addHook(objName=self.toScalableHookGrp, hookType='scalableHook')
                utils.addHook(objName=self.toStaticHookGrp, hookType='staticHook')
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_name", dataType="string")
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_type", dataType="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_name", self.userGuideName, type="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_type", CLASS_NAME, type="string")
                # add module type counter value
                cmds.addAttr(self.toStaticHookGrp, longName='dpAR_count', attributeType='long', keyable=False)
                cmds.setAttr(self.toStaticHookGrp+'.dpAR_count', dpAR_count)
                self.ctrlHookGrpList.append(self.toCtrlHookGrp)
                if hideJoints:
                    cmds.setAttr(self.toScalableHookGrp+".visibility", 0)
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)
            # finalize this rig:
            self.integratingInfo()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and moduleInstance namespace:
        self.deleteModule()
    
    
    def integratingInfo(self, *args):
        Base.StartClass.integratingInfo(self)
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.integratedActionsDic = {
                                    "module": {
                                                "suspensionBCtrlGrpList" : self.suspensionBCtrlGrpList,
                                                "fatherBList"        : self.fatherBList,
                                                "ctrlHookGrpList"    : self.ctrlHookGrpList,
                                              }
                                    }