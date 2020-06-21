# Thanks to Andrew Christophersen
# Maya Wheel Rig with World Vectors video tutorial
# https://youtu.be/QpDc93br3dM


# importing libraries:
import maya.cmds as cmds

from Library import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout


# global variables to this module:    
CLASS_NAME = "Wheel"
TITLE = "m156_wheel"
DESCRIPTION = "m157_wheelDesc"
ICON = "/Icons/dp_wheel.png"


class Wheel(Base.StartClass, Layout.LayoutClass):
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
    
    
    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName="geo", dataType='string')
        cmds.addAttr(self.moduleGrp, longName="startFrame", attributeType='long', defaultValue=1)
        cmds.addAttr(self.moduleGrp, longName="showControls", attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName="steering", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".flip", 0)
        cmds.setAttr(self.moduleGrp+".showControls", 1)
        cmds.setAttr(self.moduleGrp+".steering", 0)
        
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        
        self.cvCenterLoc, shapeSizeCH = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_CenterLoc", r=0.6, d=1, rot=(90, 0, 90), guide=True)
        self.connectShapeSize(shapeSizeCH)
        self.jGuideCenter = cmds.joint(name=self.guideName+"_JGuideCenter", radius=0.001)
        cmds.setAttr(self.jGuideCenter+".template", 1)
        cmds.parent(self.jGuideCenter, self.moduleGrp, relative=True)
        
        self.cvFrontLoc = self.ctrls.cvControl("id_059_AimLoc", ctrlName=self.guideName+"_FrontLoc", r=0.3, d=1, rot=(0, 0, 90))
        self.ctrls.colorShape([self.cvFrontLoc], "blue")
        shapeSizeCH = self.ctrls.shapeSizeSetup(self.cvFrontLoc)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvFrontLoc, self.cvCenterLoc)
        cmds.setAttr(self.cvFrontLoc+".tx", 1.3)
        self.jGuideFront = cmds.joint(name=self.guideName+"_JGuideFront", radius=0.001)
        cmds.setAttr(self.jGuideFront+".template", 1)
        cmds.transformLimits(self.cvFrontLoc, translationX=(1, 1), enableTranslationX=(True, False))
        radiusCtrl = self.moduleGrp+"_RadiusCtrl"
        cvFrontLocPosNode = cmds.createNode("plusMinusAverage", name=self.cvFrontLoc+"_Pos_PMA")
        cmds.setAttr(cvFrontLocPosNode+".input1D[0]", -0.5)
        cmds.connectAttr(radiusCtrl+".translateX", cvFrontLocPosNode+".input1D[1]")
        cmds.connectAttr(cvFrontLocPosNode+".output1D", self.cvFrontLoc+".tx")
        self.ctrls.setLockHide([self.cvCenterLoc, self.cvFrontLoc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        
        self.cvInsideLoc, shapeSizeCH = self.ctrls.cvLocator(ctrlName=self.guideName+"_InsideLoc", r=0.2, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvInsideLoc, self.cvCenterLoc)
        cmds.setAttr(self.cvInsideLoc+".tz", 0.3)
        self.jGuideInside = cmds.joint(name=self.guideName+"_JGuideInside", radius=0.001)
        cmds.setAttr(self.jGuideInside+".template", 1)
        cmds.transformLimits(self.cvInsideLoc, tz=(0.01, 1), etz=(True, False))
        inverseRadius = cmds.createNode("multiplyDivide", name=self.moduleGrp+"_Radius_Inv_MD")
        cmds.setAttr(inverseRadius+".input2X", -1)
        cmds.connectAttr(radiusCtrl+".translateX", inverseRadius+".input1X")
        cmds.connectAttr(inverseRadius+".outputX", self.cvInsideLoc+".translateY")
        self.ctrls.setLockHide([self.cvInsideLoc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        
        self.cvOutsideLoc, shapeSizeCH = self.ctrls.cvLocator(ctrlName=self.guideName+"_OutsideLoc", r=0.2, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvOutsideLoc, self.cvCenterLoc)
        cmds.setAttr(self.cvOutsideLoc+".tz", -0.3)
        self.jGuideOutside = cmds.joint(name=self.guideName+"_JGuideOutside", radius=0.001)
        cmds.setAttr(self.jGuideOutside+".template", 1)
        cmds.transformLimits(self.cvOutsideLoc, tz=(-1, 0.01), etz=(False, True))
        cmds.connectAttr(inverseRadius+".outputX", self.cvOutsideLoc+".translateY")
        self.ctrls.setLockHide([self.cvOutsideLoc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        
        cmds.parent(self.cvCenterLoc, self.moduleGrp)
        cmds.parent(self.jGuideFront, self.jGuideInside, self.jGuideOutside, self.jGuideCenter)
        cmds.parentConstraint(self.cvCenterLoc, self.jGuideCenter, maintainOffset=False, name=self.jGuideCenter+"_ParentConstraint")
        cmds.parentConstraint(self.cvFrontLoc, self.jGuideFront, maintainOffset=False, name=self.jGuideFront+"_ParentConstraint")
        cmds.parentConstraint(self.cvInsideLoc, self.jGuideInside, maintainOffset=False, name=self.cvInsideLoc+"_ParentConstraint")
        cmds.parentConstraint(self.cvOutsideLoc, self.jGuideOutside, maintainOffset=False, name=self.cvOutsideLoc+"_ParentConstraint")
    
    
    def changeStartFrame(self, *args):
        """ Update moduleGrp startFrame attribute from UI.
        """
        newStartFrameValue = cmds.intField(self.startFrameIF, query=True, value=True)
        cmds.setAttr(self.moduleGrp+".startFrame", newStartFrameValue)
    
    
    def changeSteering(self, *args):
        """ Update moduleGrp steering attribute from UI.
        """
        newSterringValue = cmds.checkBox(self.steeringCB, query=True, value=True)
        cmds.setAttr(self.moduleGrp+".steering", newSterringValue)
        
        
    def changeShowControls(self, *args):
        """ Update moduleGrp showControls attribute from UI.
        """
        newShowControlsValue = cmds.checkBox(self.showControlsCB, query=True, value=True)
        cmds.setAttr(self.moduleGrp+".showControls", newShowControlsValue)
    
    
    def changeGeo(self, *args):
        """ Update moduleGrp geo attribute from UI textField.
        """
        newGeoValue = cmds.textField(self.geoTF, query=True, text=True)
        cmds.setAttr(self.moduleGrp+".geo", newGeoValue, type='string')
    
        
    def rigModule(self, *args):
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            # declare lists to store names and attributes:
            self.mainCtrlList, self.wheelCtrlList, self.steeringGrpList, self.ctrlHookGrpList = [], [], [], []
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
                # declare guides:
                self.base = side+self.userGuideName+'_Guide_Base'
                self.cvCenterLoc = side+self.userGuideName+"_Guide_CenterLoc"
                self.cvFrontLoc = side+self.userGuideName+"_Guide_FrontLoc"
                self.cvInsideLoc = side+self.userGuideName+"_Guide_InsideLoc"
                self.cvOutsideLoc = side+self.userGuideName+"_Guide_OutsideLoc"
                
                # create a joint:
                cmds.select(clear=True)
                # center joint:
                self.centerJoint = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['m156_wheel']+"_Jnt", scaleCompensate=False)
                cmds.addAttr(self.centerJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                utils.setJointLabel(self.centerJoint, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['m156_wheel'])
                # create end joint:
                self.endJoint = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['m156_wheel']+"_JEnd")
                # main joint:
                cmds.select(clear=True)
                self.mainJoint = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c058_main']+"_Jnt", scaleCompensate=False)
                cmds.addAttr(self.mainJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                utils.setJointLabel(self.mainJoint, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c058_main'])
                # create end joint:
                self.mainEndJoint = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c058_main']+"_JEnd")
                
                # create controls:
                self.wheelCtrl = self.ctrls.cvControl("id_060_WheelCenter", side+self.userGuideName+"_"+self.langDic[self.langName]['m156_wheel']+"_Ctrl", r=self.ctrlRadius, d=self.curveDegree)
                self.mainCtrl = self.ctrls.cvControl("id_061_WheelMain", side+self.userGuideName+"_"+self.langDic[self.langName]['c058_main']+"_Ctrl", r=self.ctrlRadius*0.4, d=self.curveDegree)
                self.insideCtrl = self.ctrls.cvControl("id_062_WheelPivot", side+self.userGuideName+"_"+self.langDic[self.langName]['c011_RevFoot_B'].capitalize()+"_Ctrl", r=self.ctrlRadius*0.2, d=self.curveDegree, rot=(0, 90, 0))
                self.outsideCtrl = self.ctrls.cvControl("id_062_WheelPivot", side+self.userGuideName+"_"+self.langDic[self.langName]['c010_RevFoot_A'].capitalize()+"_Ctrl", r=self.ctrlRadius*0.2, d=self.curveDegree, rot=(0, 90, 0))
                self.mainCtrlList.append(self.mainCtrl)
                self.wheelCtrlList.append(self.wheelCtrl)
                
                # origined from attributes:
                utils.originedFrom(objName=self.mainCtrl, attrString=self.base+";"+self.cvCenterLoc+";"+self.cvFrontLoc+";"+self.cvInsideLoc+";"+self.cvOutsideLoc)
                #utils.originedFrom(objName=self.wheelCtrl, attrString=self.cvCenterLoc)
                
                # prepare group to receive steering wheel connection:
                self.toSteeringGrp = cmds.group(self.insideCtrl, name=side+self.userGuideName+"_"+self.langDic[self.langName]['c070_steering'].capitalize()+"_Grp")
                cmds.addAttr(self.toSteeringGrp, longName=self.langDic[self.langName]['c070_steering'], attributeType='bool', keyable=True)
                cmds.addAttr(self.toSteeringGrp, longName=self.langDic[self.langName]['c070_steering']+self.langDic[self.langName]['m151_invert'], attributeType='bool', keyable=True)
                cmds.setAttr(self.toSteeringGrp+"."+self.langDic[self.langName]['c070_steering'], 1)
                self.steeringGrpList.append(self.toSteeringGrp)
                
                # position and orientation of joint and control:
                cmds.delete(cmds.parentConstraint(self.cvCenterLoc, self.centerJoint, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvFrontLoc, self.endJoint, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvCenterLoc, self.wheelCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvCenterLoc, self.mainCtrl, maintainOffset=False))
                cmds.parentConstraint(self.mainCtrl, self.mainJoint, maintainOffset=False)
                cmds.delete(cmds.parentConstraint(self.cvFrontLoc, self.mainEndJoint, maintainOffset=False))
                if s == 1 and cmds.getAttr(self.moduleGrp+".flip") == 1:
                    cmds.move(self.ctrlRadius, self.mainCtrl, moveY=True, relative=True, objectSpace=True, worldSpaceDistance=True)
                else:
                    cmds.move(-self.ctrlRadius, self.mainCtrl, moveY=True, relative=True, objectSpace=True, worldSpaceDistance=True)
                cmds.delete(cmds.parentConstraint(self.cvInsideLoc, self.toSteeringGrp, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvOutsideLoc, self.outsideCtrl, maintainOffset=False))
                
                # zeroOut controls:
                zeroGrpList = utils.zeroOut([self.mainCtrl, self.wheelCtrl, self.toSteeringGrp, self.outsideCtrl])
                wheelAutoGrp = utils.zeroOut([self.wheelCtrl])
                wheelAutoGrp = cmds.rename(wheelAutoGrp, side+self.userGuideName+"_"+self.langDic[self.langName]['m156_wheel']+"_Auto_Grp")
                
                # fixing flip mirror:
                if s == 1:
                    if cmds.getAttr(self.moduleGrp+".flip") == 1:
                        for zeroOutGrp in zeroGrpList:
                            cmds.setAttr(zeroOutGrp+".scaleX", -1)
                            cmds.setAttr(zeroOutGrp+".scaleY", -1)
                            cmds.setAttr(zeroOutGrp+".scaleZ", -1)
                
                cmds.addAttr(self.wheelCtrl, longName='scaleCompensate', attributeType="bool", keyable=False)
                cmds.setAttr(self.wheelCtrl+".scaleCompensate", 1, channelBox=True)
                cmds.connectAttr(self.wheelCtrl+".scaleCompensate", self.centerJoint+".segmentScaleCompensate", force=True)
                cmds.addAttr(self.mainCtrl, longName='scaleCompensate', attributeType="bool", keyable=False)
                cmds.setAttr(self.mainCtrl+".scaleCompensate", 1, channelBox=True)
                cmds.connectAttr(self.mainCtrl+".scaleCompensate", self.mainJoint+".segmentScaleCompensate", force=True)
                # hide visibility attributes:
                self.ctrls.setLockHide([self.mainCtrl, self.insideCtrl, self.outsideCtrl], ['v'])
                self.ctrls.setLockHide([self.wheelCtrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'sx', 'sy', 'sz', 'v'])
                
                # grouping:
                cmds.parentConstraint(self.wheelCtrl, self.centerJoint, maintainOffset=False, name=self.centerJoint+"_ParentConstraint")
                cmds.scaleConstraint(self.wheelCtrl, self.centerJoint, maintainOffset=True, name=self.centerJoint+"_ScaleConstraint")
                cmds.parent(zeroGrpList[1], self.mainCtrl, absolute=True)
                cmds.parent(zeroGrpList[0], self.outsideCtrl, absolute=True)
                cmds.parent(zeroGrpList[3], self.insideCtrl, absolute=True)
                
                # add attributes:
                cmds.addAttr(self.wheelCtrl, longName=self.langDic[self.langName]['c047_autoRotate'], attributeType="bool", defaultValue=1, keyable=True)
                cmds.addAttr(self.wheelCtrl, longName=self.langDic[self.langName]['c068_startFrame'], attributeType="long", defaultValue=1, keyable=False)
                cmds.addAttr(self.wheelCtrl, longName=self.langDic[self.langName]['c067_radius'], attributeType="float", min=0.01, defaultValue=self.ctrlRadius, keyable=True)
                cmds.addAttr(self.wheelCtrl, longName=self.langDic[self.langName]['c069_radiusScale'], attributeType="float", defaultValue=1, keyable=False)
                cmds.addAttr(self.wheelCtrl, longName=self.langDic[self.langName]['c021_showControls'], attributeType="long", min=0, max=1, defaultValue=0, keyable=True)
                cmds.addAttr(self.wheelCtrl, longName=self.langDic[self.langName]['c070_steering'], attributeType="bool", defaultValue=0, keyable=True)
                cmds.addAttr(self.wheelCtrl, longName=self.langDic[self.langName]['i037_to']+self.langDic[self.langName]['c070_steering'].capitalize(), attributeType="float", defaultValue=0, keyable=False)
                cmds.addAttr(self.wheelCtrl, longName=self.langDic[self.langName]['c070_steering']+self.langDic[self.langName]['c053_invert'].capitalize(), attributeType="long", min=0, max=1, defaultValue=1, keyable=False)
                cmds.addAttr(self.wheelCtrl, longName=self.langDic[self.langName]['c093_tryKeepUndo'], attributeType="long", min=0, max=1, defaultValue=1, keyable=False)
                
                # get stored values by user:
                startFrameValue = cmds.getAttr(self.moduleGrp+".startFrame")
                steeringValue = cmds.getAttr(self.moduleGrp+".steering")
                showControlsValue = cmds.getAttr(self.moduleGrp+".showControls")
                cmds.setAttr(self.wheelCtrl+"."+self.langDic[self.langName]['c068_startFrame'], startFrameValue, channelBox=True)
                cmds.setAttr(self.wheelCtrl+"."+self.langDic[self.langName]['c070_steering'], steeringValue, channelBox=True)
                cmds.setAttr(self.wheelCtrl+"."+self.langDic[self.langName]['c021_showControls'], showControlsValue, channelBox=True)
                cmds.setAttr(self.wheelCtrl+"."+self.langDic[self.langName]['c070_steering']+self.langDic[self.langName]['c053_invert'].capitalize(), 1, channelBox=True)
                cmds.setAttr(self.wheelCtrl+"."+self.langDic[self.langName]['c093_tryKeepUndo'], 1, channelBox=True)
                if s == 1:
                    if cmds.getAttr(self.moduleGrp+".flip") == 1:
                        cmds.setAttr(self.wheelCtrl+"."+self.langDic[self.langName]['c070_steering']+self.langDic[self.langName]['c053_invert'].capitalize(), 0)
                
                # automatic rotation wheel setup:
                receptSteeringMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_"+self.langDic[self.langName]['c070_steering']+"_MD")
                inverseSteeringMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_"+self.langDic[self.langName]['c070_steering']+"_Inv_MD")
                steeringInvCnd = cmds.createNode('condition', name=side+self.userGuideName+"_"+self.langDic[self.langName]['c070_steering']+"_Inv_Cnd")
                cmds.setAttr(steeringInvCnd+".colorIfTrueR", 1)
                cmds.setAttr(steeringInvCnd+".colorIfFalseR", -1)
                cmds.connectAttr(self.wheelCtrl+"."+self.langDic[self.langName]['i037_to']+self.langDic[self.langName]['c070_steering'].capitalize(), receptSteeringMD+".input1X", force=True)
                cmds.connectAttr(self.wheelCtrl+"."+self.langDic[self.langName]['c070_steering'], receptSteeringMD+".input2X", force=True)
                cmds.connectAttr(receptSteeringMD+".outputX", inverseSteeringMD+".input1X", force=True)
                cmds.connectAttr(steeringInvCnd+".outColorR", inverseSteeringMD+".input2X", force=True)
                cmds.connectAttr(self.wheelCtrl+"."+self.langDic[self.langName]['c070_steering']+self.langDic[self.langName]['c053_invert'].capitalize(), steeringInvCnd+".firstTerm", force=True)
                cmds.connectAttr(inverseSteeringMD+".outputX", self.toSteeringGrp+".rotateY", force=True)
                # create locators (frontLoc to get direction and oldLoc to store wheel old position):
                self.frontLoc = cmds.spaceLocator(name=side+self.userGuideName+"_"+self.langDic[self.langName]['m156_wheel']+"_Front_Loc")[0]
                self.oldLoc = cmds.spaceLocator(name=side+self.userGuideName+"_"+self.langDic[self.langName]['m156_wheel']+"_Old_Loc")[0]
                cmds.delete(cmds.parentConstraint(self.cvFrontLoc, self.frontLoc, maintainOffset=False))
                cmds.parent(self.frontLoc, self.mainCtrl)
                cmds.delete(cmds.parentConstraint(self.cvCenterLoc, self.oldLoc, maintainOffset=False))
                cmds.setAttr(self.frontLoc+".visibility", 0, lock=True)
                cmds.setAttr(self.oldLoc+".visibility", 0, lock=True)
                # this wheel auto group locator could be replaced by a decomposeMatrix to get the translation in world space of the Wheel_Auto_Ctrl_Grp instead:
                self.wheelAutoGrpLoc = cmds.spaceLocator(name=side+self.userGuideName+"_"+self.langDic[self.langName]['m156_wheel']+"_Auto_Loc")[0]
                cmds.pointConstraint(wheelAutoGrp, self.wheelAutoGrpLoc, maintainOffset=False, name=self.wheelAutoGrpLoc+"_PointConstraint")
                cmds.setAttr(self.wheelAutoGrpLoc+".visibility", 0, lock=True)
                expString = "if ("+self.wheelCtrl+"."+self.langDic[self.langName]['c047_autoRotate']+" == 1) {"+\
                        "\nif ("+self.wheelCtrl+"."+self.langDic[self.langName]['c093_tryKeepUndo']+" == 1) { undoInfo -stateWithoutFlush 0; };"+\
                        "\nfloat $radius = "+self.wheelCtrl+"."+self.langDic[self.langName]['c067_radius']+" * "+self.wheelCtrl+"."+self.langDic[self.langName]['c069_radiusScale']+\
                        ";\nvector $moveVectorOld = `xform -q -ws -t \""+self.oldLoc+\
                        "\"`;\nvector $moveVector = << "+self.wheelAutoGrpLoc+".translateX, "+self.wheelAutoGrpLoc+".translateY, "+self.wheelAutoGrpLoc+".translateZ >>;"+\
                        "\nvector $dirVector = `xform -q -ws -t \""+self.frontLoc+\
                        "\"`;\nvector $wheelVector = ($dirVector - $moveVector);"+\
                        "\nvector $motionVector = ($moveVector - $moveVectorOld);"+\
                        "\nfloat $distance = mag($motionVector);"+\
                        "\n$dot = dotProduct($motionVector, $wheelVector, 1);\n"+\
                        wheelAutoGrp+".rotateZ = "+wheelAutoGrp+".rotateZ - 360 / (6.283*$radius) * ($dot*$distance);"+\
                        "\nxform -t ($moveVector.x) ($moveVector.y) ($moveVector.z) "+self.oldLoc+\
                        ";\nif (frame == "+self.wheelCtrl+"."+self.langDic[self.langName]['c068_startFrame']+") { "+wheelAutoGrp+".rotateZ = 0; };"+\
                        "\nif ("+self.wheelCtrl+"."+self.langDic[self.langName]['c093_tryKeepUndo']+" == 1) { undoInfo -stateWithoutFlush 1; };};"
                # expression:
                cmds.expression(name=side+self.userGuideName+"_"+self.langDic[self.langName]['m156_wheel']+"_Exp", object=self.frontLoc, string=expString)
                self.ctrls.setLockHide([self.frontLoc, self.wheelAutoGrpLoc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                
                # deformers:
                self.loadedGeo = cmds.getAttr(self.moduleGrp+".geo")
                
                # geometry holder:
                self.geoHolder = cmds.polyCube(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c046_holder']+"_Geo", constructionHistory=False)[0]
                cmds.delete(cmds.parentConstraint(self.cvCenterLoc, self.geoHolder, maintainOffset=False))
                cmds.setAttr(self.geoHolder+".visibility", 0, lock=True)
                
                # skinning:
                cmds.skinCluster(self.centerJoint, self.geoHolder, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=side+self.userGuideName+"_"+self.langDic[self.langName]['c046_holder']+"_SC")
                if self.loadedGeo:
                    if cmds.objExists(self.loadedGeo):
                        baseName = utils.extractSuffix(self.loadedGeo)
                        skinClusterName = baseName+"_SC"
                        if "|" in skinClusterName:
                            skinClusterName = skinClusterName[skinClusterName.rfind("|")+1:]
                        try:
                            cmds.skinCluster(self.centerJoint, self.loadedGeo, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=skinClusterName)
                        except:
                            childList = cmds.listRelatives(self.loadedGeo, children=True, allDescendents=True)
                            if childList:
                                for item in childList:
                                    itemType = cmds.objectType(item)
                                    if itemType == "mesh" or itemType == "nurbsSurface":
                                        try:
                                            skinClusterName = utils.extractSuffix(item)+"_SC"
                                            cmds.skinCluster(self.centerJoint, item, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=skinClusterName)
                                        except:
                                            pass
                
                # lattice:
                latticeList = cmds.lattice(self.geoHolder, divisions=(6, 6, 6), outsideLattice=2, outsideFalloffDistance=1, position=(0, 0, 0), scale=(self.ctrlRadius*2, self.ctrlRadius*2, self.ctrlRadius*2), name=side+self.userGuideName+"_FFD") #[deformer, lattice, base]
                cmds.scale(self.ctrlRadius*2, self.ctrlRadius*2, self.ctrlRadius*2, latticeList[2])
                # clusters:
                upperClusterList = cmds.cluster(latticeList[1]+".pt[0:5][4:5][0:5]", relative=True, name=side+self.userGuideName+"_"+self.langDic[self.langName]['c044_upper']+"_Cls") #[deform, handle]
                middleClusterList = cmds.cluster(latticeList[1]+".pt[0:5][2:3][0:5]", relative=True, name=side+self.userGuideName+"_"+self.langDic[self.langName]['m033_middle']+"_Cls") #[deform, handle]
                lowerClusterList = cmds.cluster(latticeList[1]+".pt[0:5][0:1][0:5]", relative=True, name=side+self.userGuideName+"_"+self.langDic[self.langName]['c045_lower']+"_Cls") #[deform, handle]
                clusterGrpList = utils.zeroOut([upperClusterList[1], middleClusterList[1], lowerClusterList[1]])
                clustersGrp = cmds.group(clusterGrpList, name=side+self.userGuideName+"_Clusters_Grp")
                
                # deform controls:
                upperDefCtrl = self.ctrls.cvControl("id_063_WheelDeform", side+self.userGuideName+"_"+self.langDic[self.langName]['c044_upper']+"_Ctrl", r=self.ctrlRadius*0.5, d=self.curveDegree)
                middleDefCtrl = self.ctrls.cvControl("id_064_WheelMiddle", side+self.userGuideName+"_"+self.langDic[self.langName]['m033_middle']+"_Ctrl", r=self.ctrlRadius*0.5, d=self.curveDegree)
                lowerDefCtrl = self.ctrls.cvControl("id_063_WheelDeform", side+self.userGuideName+"_"+self.langDic[self.langName]['c045_lower']+"_Ctrl", r=self.ctrlRadius*0.5, d=self.curveDegree, rot=(0, 0, 180))
                defCtrlGrpList = utils.zeroOut([upperDefCtrl, middleDefCtrl, lowerDefCtrl])
                defCtrlGrp = cmds.group(defCtrlGrpList, name=side+self.userGuideName+"_Ctrl_Grp")
                
                # positions:
                cmds.delete(cmds.parentConstraint(upperClusterList[1], defCtrlGrpList[0], maintainOffset=False))
                cmds.delete(cmds.parentConstraint(middleClusterList[1], defCtrlGrpList[1], maintainOffset=False))
                cmds.delete(cmds.parentConstraint(lowerClusterList[1], defCtrlGrpList[2], maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvCenterLoc, latticeList[1], maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvCenterLoc, latticeList[2], maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvCenterLoc, clustersGrp, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvCenterLoc, defCtrlGrp, maintainOffset=False))
                outsideDist = cmds.getAttr(self.cvOutsideLoc+".tz")
                if s == 1:
                    if cmds.getAttr(self.moduleGrp+".flip") == 1:
                        outsideDist = -outsideDist
                cmds.move(outsideDist, defCtrlGrp, moveZ=True, relative=True, objectSpace=True, worldSpaceDistance=True)
                self.ctrls.directConnect(upperDefCtrl, upperClusterList[1])
                self.ctrls.directConnect(middleDefCtrl, middleClusterList[1])
                self.ctrls.directConnect(lowerDefCtrl, lowerClusterList[1])
                # grouping deformers:
                if self.loadedGeo:
                    if cmds.objExists(self.loadedGeo):
                        cmds.lattice(latticeList[0], edit=True, geometry=self.loadedGeo)
                defGrp = cmds.group(latticeList[1], latticeList[2], clustersGrp, name=side+self.userGuideName+"_Deform_Grp")
                cmds.parentConstraint(self.mainCtrl, defGrp, maintainOffset=True, name=defGrp+"_ParentConstraint")
                cmds.scaleConstraint(self.mainCtrl, defGrp, maintainOffset=True, name=defGrp+"_ScaleConstraint")
                cmds.parent(defCtrlGrp, self.mainCtrl)
                cmds.connectAttr(self.wheelCtrl+"."+self.langDic[self.langName]['c021_showControls'], defCtrlGrp+".visibility", force=True)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(zeroGrpList[2], name=side+self.userGuideName+"_Control_Grp")
                self.toScalableHookGrp = cmds.group(self.centerJoint, self.mainJoint, defGrp, name=side+self.userGuideName+"_Joint_Grp")
                self.toStaticHookGrp = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, self.oldLoc, self.wheelAutoGrpLoc, self.geoHolder, name=side+self.userGuideName+"_Grp")
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
                                                "mainCtrlList"    : self.mainCtrlList,
                                                "wheelCtrlList"   : self.wheelCtrlList,
                                                "steeringGrpList" : self.steeringGrpList,
                                                "ctrlHookGrpList" : self.ctrlHookGrpList,
                                              }
                                    }


###
#
# Wheel Auto Rotation Expression:
#
# if (WHEEL_CTRL.AUTO_ROTATE == 1) {
# if (WHEEL_CTRL.TRYKEEPUNDO == 1) { undoInfo -stateWithoutFlush 0; };
# float $radius = WHEEL_CTRL.RADIUS * WHEEL_CTRL.RADIUSSCALE;
# vector $moveVectorOld = `xform -q -ws -t "OLD_LOC"`;
# vector $moveVector = << AUTO_GRP_LOC.translateX, AUTO_GRP_LOC.translateY, AUTO_GRP_LOC.translateZ >>;
# vector $dirVector = `xform -q -ws -t "FRONT_LOC"`;
# vector $wheelVector = ($dirVector - $moveVector);
# vector $motionVector = ($moveVector - $moveVectorOld);
# float $distance = mag($motionVector);
# $dot = dotProduct($motionVector, $wheelVector, 1);
# AUTO_GRP.rotateZ = AUTO_GRP.rotateZ - 360 / (6.283*$radius) * ($dot*$distance);
# xform -t ($moveVector.x) ($moveVector.y) ($moveVector.z) OLD_LOC;
# if (frame == WHEEL_CTRL.START_FRAME) { AUTO_GRP.rotateZ = 0; };
# if (WHEEL_CTRL.TRYKEEPUNDO == 1) { undoInfo -stateWithoutFlush 1; };};
# 
###