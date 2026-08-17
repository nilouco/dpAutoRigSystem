# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:    
CLASS_NAME = "Single"
TITLE = "m073_single"
DESCRIPTION = "m074_singleDesc"
WIKI = "03-‐-Guides#-single"



class Single(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        # returned data from the dictionary
        self.mainJisList = []
        self.aStaticGrpList = []
        self.aCtrlGrpList = []
    
    
#    def create_module_layout(self):
#        standard.BaseStandard.create_module_layout(self)
    
    
    def getHasIndirectSkin(self):
        return cmds.getAttr(self.guide_base + ".indirectSkin")
    
    
    def getHasHolder(self):
        return cmds.getAttr(self.guide_base + ".holder")
        
    
    def getHasSDKLocator(self):
        return cmds.getAttr(self.guide_base + ".sdkLocator")
    
    
    def create_guide(self, *args):
        self.create_guide_base()
        # Custom GUIDE:
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="indirectSkin", attributeType='bool')
        cmds.addAttr(self.guide_base, longName='holder', attributeType='bool')
        cmds.addAttr(self.guide_base, longName='sdkLocator', attributeType='bool')
        cmds.addAttr(self.guide_base, longName="deformedBy", minValue=0, defaultValue=0, maxValue=3, attributeType='long')
        
        self.cvJointLoc = self.ar.ctrls.cvJointLoc(ctrlName=self.name_guide+"_JointLoc1", r=0.3, d=1, guide=True)
        self.jGuide1 = cmds.joint(name=self.name_guide+"_JGuide1", radius=0.001)
        cmds.setAttr(self.jGuide1+".template", 1)
        cmds.parent(self.jGuide1, self.guide_base, relative=True)
        
        self.cvEndJoint = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_JointEnd", r=0.1, d=1, guide=True)
        cmds.parent(self.cvEndJoint, self.cvJointLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        
        cmds.parent(self.cvJointLoc, self.guide_base)
        cmds.parent(self.jGuideEnd, self.jGuide1)
        cmds.parentConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=False, name=self.jGuide1+"_PaC")
        cmds.parentConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=False, name=self.jGuideEnd+"_PaC")
        cmds.scaleConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=False, name=self.jGuide1+"_ScC")
        cmds.scaleConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=False, name=self.jGuideEnd+"_ScC")
        # include nodes into net
        self.add_node_to_guide_net([self.cvJointLoc, self.cvEndJoint], ["JointLoc1", "JointEnd"])
    
    
    def changeIndirectSkin(self, *args):
        """ Set the attribute value for indirectSkin.
        """
        indSkinValue = cmds.checkBox(self.indirectSkinCB, query=True, value=True)
        cmds.setAttr(self.guide_base+".indirectSkin", indSkinValue)
        if indSkinValue == 0:
            cmds.setAttr(self.guide_base+".holder", 0)
            cmds.checkBox(self.holderCB, edit=True, value=False, enable=False)
            cmds.checkBox(self.sdkLocatorCB, edit=True, enable=False)
        else:
            cmds.checkBox(self.holderCB, edit=True, enable=True)
            cmds.checkBox(self.sdkLocatorCB, edit=True, enable=True)
            

    def changeHolder(self, *args):
        """ Set the attribute value for holder.
        """
        cmds.setAttr(self.guide_base+".holder", cmds.checkBox(self.holderCB, query=True, value=True))
    
    
    def changeSDKLocator(self, *args):
        """ Set the attribute value for sdkLocator.
        """
        cmds.setAttr(self.guide_base+".sdkLocator", cmds.checkBox(self.sdkLocatorCB, query=True, value=True))
    
    
    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # run for all sides
            for s, side in enumerate(self.sides):
                self.base = side+self.number_name+'_Guide_Base'
                cmds.select(clear=True)
                # declare guide:
                self.guide = side+self.number_name+"_Guide_JointLoc1"
                self.cvEndJoint = side+self.number_name+"_Guide_JointEnd"
                self.radiusGuide = side+self.number_name+"_Guide_Base_RadiusCtrl"
                # create a joint:
                self.jnt = cmds.joint(name=side+self.number_name+"_Jnt", scaleCompensate=False)
                cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                self.ar.utils.setJointLabel(self.jnt, s+self.joint_label_add, 18, self.number_name)
                # create a control:
                if not self.getHasIndirectSkin():
                    if self.curve_degree == 0:
                        self.curve_degree = 1
                # work with curve shape and rotation cases:
                indirectSkinRot = (0, 0, 0)
                if self.ar.data.lang['c058_main'] in self.number_name:
                    ctrlTypeID = "id_054_SingleMain"
                    if len(self.sides) > 1:
                        if self.ar.data.lang['c041_eyebrow'] in self.number_name:
                            indirectSkinRot = (0, 0, -90)
                        else:
                            indirectSkinRot = (0, 0, 90)
                else:
                    ctrlTypeID = "id_029_SingleIndSkin"
                    if self.ar.data.lang['c045_lower'] in self.number_name:
                        indirectSkinRot=(0, 0, 180)
                    elif self.ar.data.lang['c043_corner'] in self.number_name:
                        if "00" in self.number_name:
                            indirectSkinRot=(0, 0, 90)
                        else:
                            indirectSkinRot=(0, 0, -90)
                self.singleCtrl = self.ar.ctrls.cvControl(ctrlTypeID, side+self.number_name+"_Ctrl", r=self.radius, d=self.curve_degree, rot=indirectSkinRot, headDef=cmds.getAttr(self.base+".deformedBy"), guideSource=self.name_guide+"_JointLoc1")
                self.ar.utils.originedFrom(objName=self.singleCtrl, attrString=self.base+";"+self.guide+";"+self.cvEndJoint+";"+self.radiusGuide)
                # position and orientation of joint and control:
                cmds.delete(cmds.parentConstraint(self.guide, self.jnt, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.guide, self.singleCtrl, maintainOffset=False))
                # zeroOut controls:
                zeroOutCtrlGrp = self.ar.utils.zeroOut([self.singleCtrl], offset=True)[0]
                # hide visibility attribute:
                cmds.setAttr(self.singleCtrl+'.visibility', keyable=False)
                # fixing flip mirror:
                if s == 1:
                    if cmds.getAttr(self.guide_base+".flip") == 1:
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
                    self.ar.utils.clearDpArAttr([jxt])
                    cmds.makeIdentity(self.jnt, apply=True, jointOrient=False)
                    cmds.parent(self.jnt, jxt)
                    for attr in self.ar.data.transform_attrs[:-1]:
                        cmds.connectAttr(self.singleCtrl+'.'+attr, self.jnt+'.'+attr, force=True)
                    # fix mirror issue: Maya 2026 release bug
                    if s == 1:
                        if cmds.getAttr(self.guide_base+".flip") == 1:
                            invMD = cmds.createNode("multiplyDivide", name=jxtName.replace("_Jxt", "_Inv_MD"))
                            for sAxis in self.ar.data.axis:
                                cmds.setAttr(invMD+".input2"+sAxis, -1)
                                cmds.connectAttr(self.singleCtrl+'.translate'+sAxis, invMD+'.input1'+sAxis, force=True)
                                cmds.connectAttr(invMD+'.output'+sAxis, self.jnt+'.translate'+sAxis, force=True)
                    if self.getHasHolder():
                        cmds.delete(self.singleCtrl+"0Shape", shape=True)
                        self.singleCtrl = cmds.rename(self.singleCtrl, self.singleCtrl+"_"+self.ar.data.lang['c046_holder']+"_Grp")
                        self.ar.utils.removeUserDefinedAttr(self.singleCtrl, True)
                        #cmds.addAttr(self.singleCtrl, longName="dpHolder", attributeType="bool", defaultValue=1)
                        #self.ar.custom_attr.addAttr("custom", [self.singleCtrl], "dpHolder")
                        self.ar.utils.addCustomAttr([self.singleCtrl], "dpHolder")
                        self.ar.ctrls.setLockHide([self.singleCtrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
                        self.jnt = cmds.rename(self.jnt, self.jnt.replace("_Jnt", "_"+self.ar.data.lang['c046_holder']+"_Jis"))
                        self.ar.ctrls.setLockHide([self.jnt], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'], True, True)
                    else:
                        if self.getHasSDKLocator():
                            if not self.ar.data.lang['c058_main'] in self.number_name:
                                # this one will be used to receive inputs from sdk locator:
                                sdkJisName = self.jnt.replace("_Jnt", "_SDK_Jis")
                                sdkJis = cmds.duplicate(self.jnt, name=sdkJisName)[0]
                                # sdk locator:
                                sdkLoc = cmds.spaceLocator(name=sdkJis.replace("_Jis", "_Loc"))[0]
                                sdkLocGrp = cmds.group(sdkLoc, name=sdkLoc+"_Grp")
                                cmds.delete(cmds.parentConstraint(self.singleCtrl, sdkLocGrp, maintainOffset=False))
                                cmds.parent(sdkLocGrp, self.singleCtrl, relative=True)
                                sdkLocMD = cmds.createNode("multiplyDivide", name=sdkLoc+"_MD")
                                self.to_ids.append(sdkLocMD)
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
                                for attr in self.ar.data.transform_attrs[:-1]:
                                    cmds.connectAttr(sdkLoc+'.'+attr, sdkJis+'.'+attr)
                                cmds.setAttr(sdkLocGrp+".rotateX", 0)
                                cmds.setAttr(sdkLocGrp+".rotateY", 0)
                                cmds.setAttr(sdkLocGrp+".rotateZ", 0)
                        # rename indirectSkinning joint from Jnt to Jis:
                        self.jnt = cmds.rename(self.jnt, self.jnt.replace("_Jnt", "_Jis"))
                else: # like a fkLine
                    # create parentConstraint from ctrl to jnt:
                    cmds.parentConstraint(self.singleCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_PaC")
                    # create scaleConstraint from ctrl to jnt:
                    cmds.scaleConstraint(self.singleCtrl, self.jnt, maintainOffset=True, name=self.jnt+"_ScC")
                # create end joint:
                cmds.select(self.jnt)
                self.endJoint = cmds.joint(name=side+self.number_name+"_"+self.ar.data.joint_end_attr, radius=0.5)
                self.ar.utils.addJointEndAttr([self.endJoint])
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))
                self.mainJisList.append(self.jnt)
                # create a masterModuleGrp to be checked if this rig exists:
                if self.getHasIndirectSkin():
                    self.create_hook_setup(side, [side+self.number_name+"_Ctrl_Zero_0_Grp"], staticList=[side+self.number_name+"_Jxt"])
                else:
                    self.create_hook_setup(side, [side+self.number_name+"_Ctrl_Zero_0_Grp"], [side+self.number_name+"_Jnt"])
                self.aStaticGrpList.append(self.static_hook_grp)
                self.aCtrlGrpList.append(self.ctrl_hook_grp)
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.number_name+'_'+self.mirror_grp)
                self.ar.custom_attr.addAttr(0, [self.static_hook_grp], descendents=True) #dpID
            # finalize this rig:
            self.serialize_guide()
            self.composing_info()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and module_instance namespace:
        self.delete_guide()
        self.rename_unit_conversion()
        self.ar.custom_attr.addAttr(0, self.to_ids) #dpID
    
    
    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "mainJisList"   : self.mainJisList,
                            "staticGrpList" : self.aStaticGrpList,
                            "ctrlGrpList"   : self.aCtrlGrpList,
                        }
