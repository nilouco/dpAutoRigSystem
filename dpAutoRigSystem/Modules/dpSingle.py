# importing libraries:
import maya.cmds as cmds
import maya.OpenMaya as om

from Library import dpControls as ctrls
from Library import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout


# global variables to this module:    
CLASS_NAME = "Single"
TITLE = "m073_single"
DESCRIPTION = "m074_singleDesc"
ICON = "/Icons/dp_single.png"


class Single(Base.StartClass, Layout.LayoutClass):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        Base.StartClass.__init__(self, *args, **kwargs)
        #Returned data from the dictionnary
        self.mainJisList = []
        self.aStaticGrpList = []
        self.aCtrlGrpList = []
        self.detectedBug = False
    
    
    def createModuleLayout(self, *args):
        Base.StartClass.createModuleLayout(self)
        Layout.LayoutClass.basicModuleLayout(self)
    
    
    def getHasIndirectSkin(self):
        return cmds.getAttr(self.moduleGrp + ".indirectSkin")
    
    
    def getHasHolder(self):
        return cmds.getAttr(self.moduleGrp + "." + self.langDic[self.langName]['c_holder'])
        
        
    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".flip", 0)
        
        cmds.addAttr(self.moduleGrp, longName="indirectSkin", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".indirectSkin", 0)
        cmds.addAttr(self.moduleGrp, longName=self.langDic[self.langName]['c_holder'], attributeType='bool')
        cmds.setAttr(self.moduleGrp+"."+self.langDic[self.langName]['c_holder'], 0)
        
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        
        self.cvJointLoc, shapeSizeCH = ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLoc1", r=0.3)
        self.connectShapeSize(shapeSizeCH)
        self.jGuide1 = cmds.joint(name=self.guideName+"_JGuide1", radius=0.001)
        cmds.setAttr(self.jGuide1+".template", 1)
        cmds.parent(self.jGuide1, self.moduleGrp, relative=True)
        
        self.cvEndJoint, shapeSizeCH = ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvEndJoint, self.cvJointLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        
        cmds.parent(self.cvJointLoc, self.moduleGrp)
        cmds.parent(self.jGuideEnd, self.jGuide1)
        cmds.parentConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=False, name=self.jGuide1+"_ParentConstraint")
        cmds.parentConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=False, name=self.jGuideEnd+"_ParentConstraint")
        cmds.scaleConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=False, name=self.jGuide1+"_ScaleConstraint")
        cmds.scaleConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=False, name=self.jGuideEnd+"_ScaleConstraint")
    
    
    def changeIndirectSkin(self, *args):
        """ Set the attribute value for indirectSkin.
        """
        indSkinValue = cmds.checkBox(self.indirectSkinCB, query=True, value=True)
        cmds.setAttr(self.moduleGrp+".indirectSkin", indSkinValue)
        if indSkinValue == 0:
            cmds.setAttr(self.moduleGrp+"."+self.langDic[self.langName]['c_holder'], 0)
            cmds.checkBox(self.holderCB, edit=True, value=False, enable=False)
        else:
            cmds.checkBox(self.holderCB, edit=True, enable=True)
            

    def changeHolder(self, *args):
        """ Set the attribute value for holder.
        """
        cmds.setAttr(self.moduleGrp+"."+self.langDic[self.langName]['c_holder'], cmds.checkBox(self.holderCB, query=True, value=True))
    
    
    def rigModule(self, *args):
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
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
            else: # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_Guide_Base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(self.userGuideName+'_Guide_Base', name="Guide_Base_Grp", relative=True)
                #for Maya2012: self.userGuideName+'_'+self.moduleGrp+"_Grp"
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
            # store the number of this guide by module type
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # run for all sides
            for s, side in enumerate(sideList):
                self.base = side+self.userGuideName+'_Guide_Base'
                cmds.select(clear=True)
                # declare guide:
                self.guide = side+self.userGuideName+"_Guide_JointLoc1"
                # create a joint:
                self.jnt = cmds.joint(name=side+self.userGuideName+"_Jnt", scaleCompensate=False)
                cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                # create a control:
                if self.getHasIndirectSkin():
                    self.ctrl = cmds.circle(name=side+self.userGuideName+"_Ctrl", degree=3, normal=(0, 0, 1), r=self.ctrlRadius, s=8, ch=False)[0]
                else:
                    self.ctrl = cmds.circle(name=side+self.userGuideName+"_Ctrl", degree=1, normal=(0, 0, 1), r=self.ctrlRadius, s=8, ch=False)[0]
                # edit circle shape to Upper or Lower controls:
                if "Upper" in self.userGuideName:
                    cmds.setAttr(self.ctrl+"Shape.controlPoints[4].yValue", 0)
                    cmds.setAttr(self.ctrl+"Shape.controlPoints[5].yValue", 0)
                    cmds.setAttr(self.ctrl+"Shape.controlPoints[6].yValue", 0)
                    if not self.getHasIndirectSkin():
                        cmds.setAttr(self.ctrl+"Shape.controlPoints[3].yValue", 0)
                elif "Lower" in self.userGuideName:
                    cmds.setAttr(self.ctrl+"Shape.controlPoints[0].yValue", 0)
                    cmds.setAttr(self.ctrl+"Shape.controlPoints[1].yValue", 0)
                    cmds.setAttr(self.ctrl+"Shape.controlPoints[2].yValue", 0)
                    if not self.getHasIndirectSkin():
                        cmds.setAttr(self.ctrl+"Shape.controlPoints[7].yValue", 0)
                        cmds.setAttr(self.ctrl+"Shape.controlPoints[8].yValue", 0)
                utils.originedFrom(objName=self.ctrl, attrString=self.base+";"+self.guide)
                # position and orientation of joint and control:
                cmds.delete(cmds.parentConstraint(self.guide, self.jnt, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.guide, self.ctrl, maintainOffset=False))
                # zeroOut controls:
                zeroOutCtrlGrp = utils.zeroOut([self.ctrl])[0]
                # hide visibility attribute:
                cmds.setAttr(self.ctrl+'.visibility', keyable=False)
                # fixing flip mirror:
                if s == 1:
                    if cmds.getAttr(self.moduleGrp+".flip") == 1:
                        cmds.setAttr(zeroOutCtrlGrp+".scaleX", -1)
                        cmds.setAttr(zeroOutCtrlGrp+".scaleY", -1)
                        cmds.setAttr(zeroOutCtrlGrp+".scaleZ", -1)
                cmds.addAttr(self.ctrl, longName='scaleCompensate', attributeType="bool", keyable=True)
                cmds.setAttr(self.ctrl+".scaleCompensate", 1)
                cmds.connectAttr(self.ctrl+".scaleCompensate", self.jnt+".segmentScaleCompensate", force=True)
                if self.getHasIndirectSkin():
                    # create a fatherJoint in order to zeroOut the skinning joint:
                    cmds.select(clear=True)
                    jxtName = self.jnt.replace("_Jnt", "_Jxt")
                    self.jxt = cmds.duplicate(self.jnt, name=jxtName)[0]
                    cmds.deleteAttr(self.jxt, attribute="dpAR_joint")
                    cmds.parent(self.jnt, self.jxt)
                    cmds.makeIdentity(self.jnt, apply=True, jointOrient=False)
                    attrList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
                    for attr in attrList:
                        cmds.connectAttr(self.ctrl+'.'+attr, self.jnt+'.'+attr)
                    if s == 1:
                        if cmds.getAttr(self.moduleGrp+".flip") == 1:
                            cmds.setAttr(self.jxt+".scaleX", -1)
                            cmds.setAttr(self.jxt+".scaleY", -1)
                            cmds.setAttr(self.jxt+".scaleZ", -1)
                    if self.getHasHolder():
                        cmds.delete(self.ctrl+"Shape", shape=True)
                        self.ctrl = cmds.rename(self.ctrl, self.ctrl+"_"+self.langDic[self.langName]['c_holder']+"_Grp")
                        ctrls.setLockHide([self.ctrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'scaleCompensate'])
                        self.jnt = cmds.rename(self.jnt, self.jnt.replace("_Jnt", "_"+self.langDic[self.langName]['c_holder']+"_Jis"))
                        ctrls.setLockHide([self.jnt], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], True, True)
                    else:
                        self.jnt = cmds.rename(self.jnt, self.jnt.replace("_Jnt", "_Jis"))
                else: # like a fkLine
                    # create parentConstraint from ctrl to jnt:
                    cmds.parentConstraint(self.ctrl, self.jnt, maintainOffset=False, name=self.jnt+"_ParentConstraint")
                    # create scaleConstraint from ctrl to jnt:
                    cmds.scaleConstraint(self.ctrl, self.jnt, maintainOffset=True, name=self.jnt+"_ScaleConstraint")
                # create end joint:
                cmds.select(self.jnt)
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                self.endJoint = cmds.joint(name=side+self.userGuideName+"_JEnd")
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))
                self.mainJisList.append(self.jnt)
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp = cmds.group(side+self.userGuideName+"_Ctrl_Zero", name=side+self.userGuideName+"_Control_Grp")
                if self.getHasIndirectSkin():
                    locScale = cmds.spaceLocator(name=side+self.userGuideName+"_Scalable_DO_NOT_DELETE")[0]
                    cmds.setAttr(locScale+".visibility", 0)
                    self.toScalableHookGrp = cmds.group(locScale, name=side+self.userGuideName+"_IndirectSkin_Grp")
                    jxtGrp = cmds.group(side+self.userGuideName+"_Jxt", name=side+self.userGuideName+"_Joint_Grp")
                    self.toStaticHookGrp   = cmds.group(jxtGrp, self.toScalableHookGrp, self.toCtrlHookGrp, name=side+self.userGuideName+"_Grp")
                else:
                    self.toScalableHookGrp = cmds.group(side+self.userGuideName+"_Jnt", name=side+self.userGuideName+"_Joint_Grp")
                    self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, name=side+self.userGuideName+"_Grp")
                # create a locator in order to avoid delete static or scalable group
                loc = cmds.spaceLocator(name=side+self.userGuideName+"_DO_NOT_DELETE")[0]
                cmds.parent(loc, self.toStaticHookGrp, absolute=True)
                cmds.setAttr(loc+".visibility", 0)
                ctrls.setLockHide([loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                # add hook attributes to be read when rigging integrated modules:
                utils.addHook(objName=self.toCtrlHookGrp, hookType='ctrlHook')
                utils.addHook(objName=self.toScalableHookGrp, hookType='scalableHook')
                utils.addHook(objName=self.toStaticHookGrp, hookType='staticHook')
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_name", dataType="string")
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_type", dataType="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_name", self.userGuideName, type="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_type", CLASS_NAME, type="string")
                self.aStaticGrpList.append(self.toStaticHookGrp)
                self.aCtrlGrpList.append(self.toCtrlHookGrp)
                # add module type counter value
                cmds.addAttr(self.toStaticHookGrp, longName='dpAR_count', attributeType='long', keyable=False)
                cmds.setAttr(self.toStaticHookGrp+'.dpAR_count', dpAR_count)
                if hideJoints:
                    cmds.setAttr(self.toScalableHookGrp+".visibility", 0)
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)
            # check mirror indirectSkin bug in Maya2018:
            if (int(cmds.about(version=True)[:4]) == 2018):
                if self.mirrorAxis != 'off':
                    if self.getHasIndirectSkin():
                        meshList = cmds.ls(selection=False, type="mesh")
                        if meshList:
                            self.detectedBug = True
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
                                                "mainJisList"   : self.mainJisList,
                                                "staticGrpList" : self.aStaticGrpList,
                                                "ctrlGrpList"   : self.aCtrlGrpList,
                                                "detectedBug"   : self.detectedBug,
                                              }
                                    }
