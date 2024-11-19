# importing libraries:
from maya import cmds
from . import dpBaseClass
from . import dpLayoutClass

# global variables to this module:    
CLASS_NAME = "Single"
TITLE = "m073_single"
DESCRIPTION = "m074_singleDesc"
ICON = "/Icons/dp_single.png"

DP_SINGLE_VERSION = 2.3


class Single(dpBaseClass.StartClass, dpLayoutClass.LayoutClass):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseClass.StartClass.__init__(self, *args, **kwargs)
        #Returned data from the dictionnary
        self.mainJisList = []
        self.aStaticGrpList = []
        self.aCtrlGrpList = []
    
    
    def createModuleLayout(self, *args):
        dpBaseClass.StartClass.createModuleLayout(self)
        dpLayoutClass.LayoutClass.basicModuleLayout(self)
    
    
    def getHasIndirectSkin(self):
        return cmds.getAttr(self.moduleGrp + ".indirectSkin")
    
    
    def getHasHolder(self):
        return cmds.getAttr(self.moduleGrp + ".holder")
        
    
    def getHasSDKLocator(self):
        return cmds.getAttr(self.moduleGrp + ".sdkLocator")
    
    
    def createGuide(self, *args):
        dpBaseClass.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName="indirectSkin", attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName='holder', attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName='sdkLocator', attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName="deformedBy", minValue=0, defaultValue=0, maxValue=3, attributeType='long')
        
        self.cvJointLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLoc1", r=0.3, d=1, guide=True)
        self.jGuide1 = cmds.joint(name=self.guideName+"_JGuide1", radius=0.001)
        cmds.setAttr(self.jGuide1+".template", 1)
        cmds.parent(self.jGuide1, self.moduleGrp, relative=True)
        
        self.cvEndJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1, d=1, guide=True)
        cmds.parent(self.cvEndJoint, self.cvJointLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        
        cmds.parent(self.cvJointLoc, self.moduleGrp)
        cmds.parent(self.jGuideEnd, self.jGuide1)
        cmds.parentConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=False, name=self.jGuide1+"_PaC")
        cmds.parentConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=False, name=self.jGuideEnd+"_PaC")
        cmds.scaleConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=False, name=self.jGuide1+"_ScC")
        cmds.scaleConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=False, name=self.jGuideEnd+"_ScC")
        # include nodes into net
        self.addNodeToGuideNet([self.cvJointLoc, self.cvEndJoint], ["JointLoc1", "JointEnd"])
    
    
    def changeIndirectSkin(self, *args):
        """ Set the attribute value for indirectSkin.
        """
        indSkinValue = cmds.checkBox(self.indirectSkinCB, query=True, value=True)
        cmds.setAttr(self.moduleGrp+".indirectSkin", indSkinValue)
        if indSkinValue == 0:
            cmds.setAttr(self.moduleGrp+".holder", 0)
            cmds.checkBox(self.holderCB, edit=True, value=False, enable=False)
            cmds.checkBox(self.sdkLocatorCB, edit=True, enable=False)
        else:
            cmds.checkBox(self.holderCB, edit=True, enable=True)
            cmds.checkBox(self.sdkLocatorCB, edit=True, enable=True)
            

    def changeHolder(self, *args):
        """ Set the attribute value for holder.
        """
        cmds.setAttr(self.moduleGrp+".holder", cmds.checkBox(self.holderCB, query=True, value=True))
    
    
    def changeSDKLocator(self, *args):
        """ Set the attribute value for sdkLocator.
        """
        cmds.setAttr(self.moduleGrp+".sdkLocator", cmds.checkBox(self.sdkLocatorCB, query=True, value=True))
    
    
    def rigModule(self, *args):
        dpBaseClass.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            # run for all sides
            for s, side in enumerate(self.sideList):
                self.base = side+self.userGuideName+'_Guide_Base'
                cmds.select(clear=True)
                # declare guide:
                self.guide = side+self.userGuideName+"_Guide_JointLoc1"
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"
                # create a joint:
                self.jnt = cmds.joint(name=side+self.userGuideName+"_Jnt", scaleCompensate=False)
                cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                self.utils.setJointLabel(self.jnt, s+self.jointLabelAdd, 18, self.userGuideName)
                # create a control:
                if not self.getHasIndirectSkin():
                    if self.curveDegree == 0:
                        self.curveDegree = 1
                # work with curve shape and rotation cases:
                indirectSkinRot = (0, 0, 0)
                if self.dpUIinst.lang['c058_main'] in self.userGuideName:
                    ctrlTypeID = "id_054_SingleMain"
                    if len(self.sideList) > 1:
                        if self.dpUIinst.lang['c041_eyebrow'] in self.userGuideName:
                            indirectSkinRot = (0, 0, -90)
                        else:
                            indirectSkinRot = (0, 0, 90)
                else:
                    ctrlTypeID = "id_029_SingleIndSkin"
                    if self.dpUIinst.lang['c045_lower'] in self.userGuideName:
                        indirectSkinRot=(0, 0, 180)
                    elif self.dpUIinst.lang['c043_corner'] in self.userGuideName:
                        if "00" in self.userGuideName:
                            indirectSkinRot=(0, 0, 90)
                        else:
                            indirectSkinRot=(0, 0, -90)
                self.singleCtrl = self.ctrls.cvControl(ctrlTypeID, side+self.userGuideName+"_Ctrl", r=self.ctrlRadius, d=self.curveDegree, rot=indirectSkinRot, headDef=cmds.getAttr(self.base+".deformedBy"), guideSource=self.guideName+"_JointLoc1")
                self.utils.originedFrom(objName=self.singleCtrl, attrString=self.base+";"+self.guide+";"+self.cvEndJoint+";"+self.radiusGuide)
                # position and orientation of joint and control:
                cmds.delete(cmds.parentConstraint(self.guide, self.jnt, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.guide, self.singleCtrl, maintainOffset=False))
                # zeroOut controls:
                zeroOutCtrlGrp = self.utils.zeroOut([self.singleCtrl], offset=True)[0]
                # hide visibility attribute:
                cmds.setAttr(self.singleCtrl+'.visibility', keyable=False)
                # fixing flip mirror:
                if s == 1:
                    if cmds.getAttr(self.moduleGrp+".flip") == 1:
                        cmds.setAttr(zeroOutCtrlGrp+".scaleX", -1)
                        cmds.setAttr(zeroOutCtrlGrp+".scaleY", -1)
                        cmds.setAttr(zeroOutCtrlGrp+".scaleZ", -1)
                if not self.getHasIndirectSkin():
                    cmds.addAttr(self.singleCtrl, longName='scaleCompensate', attributeType="short", minValue=0, maxValue=1, defaultValue=1, keyable=False)
                    cmds.setAttr(self.singleCtrl+".scaleCompensate", channelBox=True)
                    cmds.connectAttr(self.singleCtrl+".scaleCompensate", self.jnt+".segmentScaleCompensate", force=True)
                if self.getHasIndirectSkin():
                    # create fatherJoints in order to zeroOut the skinning joint:
                    cmds.select(clear=True)
                    jxtName = self.jnt.replace("_Jnt", "_Jxt")
                    jxt = cmds.duplicate(self.jnt, name=jxtName)[0]
                    self.utils.clearDpArAttr([jxt])
                    cmds.makeIdentity(self.jnt, apply=True, jointOrient=False)
                    cmds.parent(self.jnt, jxt)
                    attrList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
                    for attr in attrList:
                        cmds.connectAttr(self.singleCtrl+'.'+attr, self.jnt+'.'+attr)
                    if self.getHasHolder():
                        cmds.delete(self.singleCtrl+"0Shape", shape=True)
                        self.singleCtrl = cmds.rename(self.singleCtrl, self.singleCtrl+"_"+self.dpUIinst.lang['c046_holder']+"_Grp")
                        self.utils.removeUserDefinedAttr(self.singleCtrl, True)
                        self.ctrls.setLockHide([self.singleCtrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
                        self.jnt = cmds.rename(self.jnt, self.jnt.replace("_Jnt", "_"+self.dpUIinst.lang['c046_holder']+"_Jis"))
                        self.ctrls.setLockHide([self.jnt], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'], True, True)
                    else:
                        if self.getHasSDKLocator():
                            if not self.dpUIinst.lang['c058_main'] in self.userGuideName:
                                # this one will be used to receive inputs from sdk locator:
                                sdkJisName = self.jnt.replace("_Jnt", "_SDK_Jis")
                                sdkJis = cmds.duplicate(self.jnt, name=sdkJisName)[0]
                                # sdk locator:
                                sdkLoc = cmds.spaceLocator(name=sdkJis.replace("_Jis", "_Loc"))[0]
                                sdkLocGrp = cmds.group(sdkLoc, name=sdkLoc+"_Grp")
                                cmds.delete(cmds.parentConstraint(self.singleCtrl, sdkLocGrp, maintainOffset=False))
                                cmds.parent(sdkLocGrp, self.singleCtrl, relative=True)
                                sdkLocMD = cmds.createNode("multiplyDivide", name=sdkLoc+"_MD")
                                cmds.addAttr(sdkLoc, longName="intensityX", attributeType="float", defaultValue=-1, keyable=False)
                                cmds.addAttr(sdkLoc, longName="intensityY", attributeType="float", defaultValue=-1, keyable=False)
                                cmds.addAttr(sdkLoc, longName="intensityZ", attributeType="float", defaultValue=-1, keyable=False)
                                cmds.connectAttr(sdkLoc+".translateX", sdkLocMD+".input1X", force=True)
                                cmds.connectAttr(sdkLoc+".translateY", sdkLocMD+".input1Y", force=True)
                                cmds.connectAttr(sdkLoc+".translateZ", sdkLocMD+".input1Z", force=True)
                                cmds.connectAttr(sdkLoc+".intensityX", sdkLocMD+".input2X", force=True)
                                cmds.connectAttr(sdkLoc+".intensityY", sdkLocMD+".input2Y", force=True)
                                cmds.connectAttr(sdkLoc+".intensityZ", sdkLocMD+".input2Z", force=True)
                                cmds.connectAttr(sdkLocMD+".outputX", sdkLocGrp+".translateX", force=True)
                                cmds.connectAttr(sdkLocMD+".outputY", sdkLocGrp+".translateY", force=True)
                                cmds.connectAttr(sdkLocMD+".outputZ", sdkLocGrp+".translateZ", force=True)
                                cmds.addAttr(self.singleCtrl, longName="displayLocator", attributeType="bool", keyable=False)
                                cmds.setAttr(self.singleCtrl+".displayLocator", 0, channelBox=True)
                                cmds.connectAttr(self.singleCtrl+".displayLocator", sdkLoc+".visibility", force=True)
                                cmds.setAttr(sdkLoc+".visibility", lock=True)
                                for attr in attrList:
                                    cmds.connectAttr(sdkLoc+'.'+attr, sdkJis+'.'+attr)
                                cmds.setAttr(sdkLocGrp+".rotateX", 0)
                                cmds.setAttr(sdkLocGrp+".rotateY", 0)
                                cmds.setAttr(sdkLocGrp+".rotateZ", 0)
                        # rename indirectSkinning joint from Jnt to Jis:
                        self.jnt = cmds.rename(self.jnt, self.jnt.replace("_Jnt", "_Jis"))
                    # fix mirror issue:
                    if s == 1:
                        if cmds.getAttr(self.moduleGrp+".flip") == 1:
                            cmds.setAttr(jxt+".scaleX", -1)
                            cmds.setAttr(jxt+".scaleY", -1)
                            cmds.setAttr(jxt+".scaleZ", -1)
                else: # like a fkLine
                    # create parentConstraint from ctrl to jnt:
                    cmds.parentConstraint(self.singleCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_PaC")
                    # create scaleConstraint from ctrl to jnt:
                    cmds.scaleConstraint(self.singleCtrl, self.jnt, maintainOffset=True, name=self.jnt+"_ScC")
                # create end joint:
                cmds.select(self.jnt)
                self.endJoint = cmds.joint(name=side+self.userGuideName+"_JEnd", radius=0.5)
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))
                self.mainJisList.append(self.jnt)
                # create a masterModuleGrp to be checked if this rig exists:
                if self.getHasIndirectSkin():
                    locScale = cmds.spaceLocator(name=side+self.userGuideName+"_Scalable_DO_NOT_DELETE_PLEASE_Loc")[0]
                    cmds.setAttr(locScale+".visibility", 0)
                    self.hookSetup(side, [side+self.userGuideName+"_Ctrl_Zero_0_Grp"], [locScale], [side+self.userGuideName+"_Jxt"])
                else:
                    self.hookSetup(side, [side+self.userGuideName+"_Ctrl_Zero_0_Grp"], [side+self.userGuideName+"_Jnt"])
                self.aStaticGrpList.append(self.toStaticHookGrp)
                self.aCtrlGrpList.append(self.toCtrlHookGrp)
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)
            # finalize this rig:
            self.serializeGuide()
            self.integratingInfo()
            self.dpUIinst.customAttr.addAttr(0, [self.toStaticHookGrp], descendents=True) #dpID
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and moduleInstance namespace:
        self.deleteModule()
        self.renameUnitConversion()
    
    
    def integratingInfo(self, *args):
        dpBaseClass.StartClass.integratingInfo(self)
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.integratedActionsDic = {
                                    "module": {
                                                "mainJisList"   : self.mainJisList,
                                                "staticGrpList" : self.aStaticGrpList,
                                                "ctrlGrpList"   : self.aCtrlGrpList,
                                              }
                                    }
