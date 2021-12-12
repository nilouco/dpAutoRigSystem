# importing libraries:
import maya.cmds as cmds

from Library import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout


# global variables to this module:    
CLASS_NAME = "Chain"
TITLE = "m178_chain"
DESCRIPTION = "m179_chainDesc"
ICON = "/Icons/dp_chain.png"


class Chain(Base.StartClass, Layout.LayoutClass):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        Base.StartClass.__init__(self, *args, **kwargs)
        self.worldRefList = []
        self.worldRefShapeList = []
    
    
    def createModuleLayout(self, *args):
        Base.StartClass.createModuleLayout(self)
        Layout.LayoutClass.basicModuleLayout(self)
        # Custom MODULE LAYOUT:
        # verify if we are creating or re-loading this module instance:
        firstTime = cmds.getAttr(self.moduleGrp+'.nJoints')
        if firstTime == 1:
            try:
                cmds.intField(self.nJointsIF, edit=True, value=5, minValue=5)
            except:
                pass
            self.changeJointNumber(5)
    
    
    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="nJoints", attributeType='long')
        cmds.setAttr(self.moduleGrp+".nJoints", 1)
        
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".flip", 0)
        
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        
        cmds.addAttr(self.moduleGrp, longName="articulation", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".articulation", 0)
        
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
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        
        cmds.parent(self.cvJointLoc, self.moduleGrp)
        cmds.parent(self.jGuideEnd, self.jGuide1)
        cmds.parentConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=False, name=self.jGuide1+"_PaC")
        cmds.parentConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=False, name=self.jGuideEnd+"_PaC")


    def changeJointNumber(self, enteredNJoints, *args):
        """ Edit the number of joints in the guide.
        """
        utils.useDefaultRenderLayer()
        # get the number of joints entered by user:
        if enteredNJoints == 0:
            try:
                self.enteredNJoints = cmds.intField(self.nJointsIF, query=True, value=True)
            except:
                return
        else:
            self.enteredNJoints = enteredNJoints
        if self.enteredNJoints >= 5:
            # get the number of joints existing:
            self.currentNJoints = cmds.getAttr(self.moduleGrp+".nJoints")
            # start analisys the difference between values:
            if self.enteredNJoints != self.currentNJoints:
                # unparent temporarely the Ends:
                self.cvEndJoint = self.guideName+"_JointEnd"
                cmds.parent(self.cvEndJoint, world=True)
                self.jGuideEnd = (self.guideName+"_JGuideEnd")
                cmds.parent(self.jGuideEnd, world=True)
                # verify if the nJoints is greather or less than the current
                if self.enteredNJoints > self.currentNJoints:
                    for n in range(self.currentNJoints+1, self.enteredNJoints+1):
                        # create another N cvJointLoc:
                        self.cvJointLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointLoc"+str(n), r=0.3, d=1, guide=True)
                        # set its nJoint value as n:
                        cmds.setAttr(self.cvJointLoc+".nJoint", n)
                        # parent it to the lastGuide:
                        cmds.parent(self.cvJointLoc, self.guideName+"_JointLoc"+str(n-1), relative=True)
                        cmds.setAttr(self.cvJointLoc+".translateZ", 2)
                        # create a joint to use like an arrowLine:
                        self.jGuide = cmds.joint(name=self.guideName+"_JGuide"+str(n), radius=0.001)
                        cmds.setAttr(self.jGuide+".template", 1)
                        #Prevent a intermidiate node to be added
                        cmds.parent(self.jGuide, self.guideName+"_JGuide"+str(n-1), relative=True)
                        #Do not maintain offset and ensure cv will be at the same place than the joint
                        cmds.parentConstraint(self.cvJointLoc, self.jGuide, maintainOffset=False, name=self.jGuide+"_PaC")
                        cmds.scaleConstraint(self.cvJointLoc, self.jGuide, maintainOffset=False, name=self.jGuide+"_ScC")
                elif self.enteredNJoints < self.currentNJoints:
                    # re-define cvEndJoint:
                    self.cvJointLoc = self.guideName+"_JointLoc"+str(self.enteredNJoints)
                    self.cvEndJoint = self.guideName+"_JointEnd"
                    self.jGuide = self.guideName+"_JGuide"+str(self.enteredNJoints)
                    # re-parent the children guides:
                    childrenGuideBellowList = utils.getGuideChildrenList(self.cvJointLoc)
                    if childrenGuideBellowList:
                        for childGuide in childrenGuideBellowList:
                            cmds.parent(childGuide, self.cvJointLoc)
                    # delete difference of nJoints:
                    cmds.delete(self.guideName+"_JointLoc"+str(self.enteredNJoints+1))
                    cmds.delete(self.guideName+"_JGuide"+str(self.enteredNJoints+1))
                # re-parent cvEndJoint:
                pTempParent = cmds.listRelatives(self.cvEndJoint, p=True)
                cmds.parent(self.cvEndJoint, self.cvJointLoc)

                #Ensure to remove temp parent from the unparenting done on the end joint
                if pTempParent:
                    cmds.delete(pTempParent)
                cmds.setAttr(self.cvEndJoint+".tz", 1.3)
                pTempParent = cmds.listRelatives(self.jGuideEnd, p=True)
                cmds.parent(self.jGuideEnd, self.jGuide, relative=True)
                if pTempParent:
                    cmds.delete(pTempParent)

                cmds.setAttr(self.moduleGrp+".nJoints", self.enteredNJoints)
                self.currentNJoints = self.enteredNJoints
                # re-build the preview mirror:
                Layout.LayoutClass.createPreviewMirror(self)
            cmds.select(self.moduleGrp)
        else:
            self.changeJointNumber(5)
    

    def setupAimLocators(self, side, toUpParent, ikNumb, ikFakeCtrl, toFakeParent, hasFake=True, *args):
        """ Creates the up and fake locators to use in the aimConstraint.
            Return them as a list.
        """
        fakeLoc = None
        # up locator:
        upLoc = cmds.spaceLocator(name=side+self.userGuideName+"_%02d_Up_Loc"%ikNumb)[0]
        cmds.delete(cmds.parentConstraint(toUpParent, upLoc, maintainOffset=False))
        cmds.parent(upLoc, toUpParent, relative=False)
        cmds.setAttr(upLoc+".translateY", 2*self.ctrlRadius)
        cmds.setAttr(upLoc+".visibility", 0)    
        if hasFake:
            # fake aim locator:
            fakeLoc = cmds.spaceLocator(name=side+self.userGuideName+"_%02d_Fake_Loc"%ikNumb)[0]
            cmds.delete(cmds.parentConstraint(ikFakeCtrl, fakeLoc, maintainOffset=False))
            cmds.parent(fakeLoc, toFakeParent, relative=False)
            cmds.setAttr(fakeLoc+".visibility", 0)
        return [upLoc, fakeLoc]
    

    def setupAimConst(self, ikCtrl, ikToAimCtrl, upLoc, fakeLoc, ikCtrlZero, zDir=1, autoOrient=True, *args):
        """ Creates an aim constraint to extrem ik controls use autoOrient attributes.
        """
        # look at aim constraint:
        aimConst = cmds.aimConstraint(ikToAimCtrl, fakeLoc, ikCtrlZero, worldUpType="object", worldUpObject=upLoc, aimVector=(0, 0, zDir), upVector=(0, 1, 0), maintainOffset=True, name=ikCtrlZero+"_AiC")[0]
        if autoOrient:
            cmds.connectAttr(ikCtrl+"."+self.langDic[self.langName]['c033_autoOrient'], aimConst+"."+ikToAimCtrl+"W0", force=True)
            aimRev = cmds.createNode("reverse", name=ikCtrlZero+"_Aim_Rev")
            cmds.connectAttr(ikCtrl+"."+self.langDic[self.langName]['c033_autoOrient'], aimRev+".inputX", force=True)
            cmds.connectAttr(aimRev+".outputX", aimConst+"."+fakeLoc+"W1", force=True)


    def rigModule(self, *args):
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            # articulation joint:
            self.addArticJoint = self.getArticulation()
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
                        if not self.getModuleAttr("flip"):
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
                sideLower = side
                if side:
                    sideLower = side[0].lower()
                self.base = side+self.userGuideName+'_Guide_Base'
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"
                self.ctrlZeroGrp = side+self.userGuideName+"_00_Ctrl_Zero_0_Grp"
                self.skinJointList, self.ikJointList, self.fkJointList = [], [], []
                # get the number of joints to be created:
                self.nJoints = cmds.getAttr(self.base+".nJoints")
                
                # creating joint chains:
                self.chainDic = {}
                self.jSuffixList = ['_Jnt', '_Ik_Jxt', '_Fk_Jxt']
                self.jEndSuffixList = ['_JEnd', '_Ik_JEnd', '_Fk_JEnd']
                for t, suffix in enumerate(self.jSuffixList):
                    self.wipList = []
                    cmds.select(clear=True)
                    for n in range(0, self.nJoints):
                        newJoint = cmds.joint(name=side+self.userGuideName+"_%02d"%n+suffix)
                        self.wipList.append(newJoint)
                    jEndJnt = cmds.joint(name=side+self.userGuideName+self.jEndSuffixList[t], radius=0.5)
                    self.wipList.append(jEndJnt)
                    self.chainDic[suffix] = self.wipList
                # getting jointLists:
                self.skinJointList = self.chainDic[self.jSuffixList[0]]
                self.ikJointList = self.chainDic[self.jSuffixList[1]]
                self.fkJointList = self.chainDic[self.jSuffixList[2]]
                

                # hide not skin joints in order to be more Rigger friendly when working the Skinning:
#                cmds.setAttr(self.ikJointList[0]+".visibility", 0)
#                cmds.setAttr(self.fkJointList[0]+".visibility", 0)

                



                for o, skinJoint in enumerate(self.skinJointList):
                    if o < len(self.skinJointList) - 1:
                        cmds.addAttr(skinJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                        utils.setJointLabel(skinJoint, s+jointLabelAdd, 18, self.userGuideName+"_%02d"%o)

                self.fkCtrlList, self.fkZeroGrpList, self.origFromList = [], [], []
                for n in range(0, self.nJoints):
                    cmds.select(clear=True)
                    # declare guide:
                    self.guide = side+self.userGuideName+"_Guide_JointLoc"+str(n+1)
                    
                    # create a Fk control:
                    self.fkCtrl = self.ctrls.cvControl("id_082_ChainFk", side+self.userGuideName+"_%02d_Fk_Ctrl"%n, r=self.ctrlRadius, d=self.curveDegree)
                    self.fkCtrlList.append(self.fkCtrl)
                    # position and orientation of joint and control:
                    cmds.delete(cmds.parentConstraint(self.guide, self.fkJointList[n], maintainOffset=False))
                    cmds.delete(cmds.parentConstraint(self.guide, self.fkCtrl, maintainOffset=False))
                    # zeroOut controls:
                    self.zeroOutCtrlGrp = utils.zeroOut([self.fkCtrl])[0]
                    self.fkZeroGrpList.append(self.zeroOutCtrlGrp)
                    # hide visibility attribute:
                    cmds.setAttr(self.fkCtrl+'.visibility', keyable=False)

                    # creating the originedFrom attributes (in order to permit integrated parents in the future):
                    origGrp = cmds.group(empty=True, name=side+self.userGuideName+"_%02d_OrigFrom_Grp"%n)
                    self.origFromList.append(origGrp)
                    if n == 0:
                        utils.originedFrom(objName=origGrp, attrString=self.guide[self.guide.find("__") + 1:].replace(":", "_")+";"+self.cvEndJoint+";"+self.radiusGuide)
                    elif n == (self.nJoints-1):
                        utils.originedFrom(objName=origGrp, attrString=self.guide[self.guide.find("__") + 1:].replace(":", "_")+";"+self.base)
                    else:
                        utils.originedFrom(objName=origGrp, attrString=self.guide[self.guide.find("__") + 1:].replace(":", "_"))
                    cmds.parentConstraint(self.skinJointList[n], origGrp, maintainOffset=False, name=origGrp+"_PaC")
                    
                    if n > 0:
                        cmds.parent(self.fkZeroGrpList[n], self.fkCtrlList[n - 1])
                        cmds.parent(origGrp, self.origFromList[n - 1])

                # add extrem_toParent_Ctrl
                if n == (self.nJoints-1):
                    self.toParentExtremCtrl = self.ctrls.cvControl("id_083_ChainToParent", ctrlName=side+self.userGuideName+"_ToParent_Ctrl", r=(self.ctrlRadius * 0.1), d=self.curveDegree)
                    cmds.addAttr(self.toParentExtremCtrl, longName="stretchable", minValue=0, maxValue=1, attributeType="float", defaultValue=1, keyable=True)
                    cmds.addAttr(self.toParentExtremCtrl, longName=self.langDic[self.langName]['c031_volumeVariation'], attributeType="float", minValue=0, defaultValue=1, keyable=True)
                    cmds.addAttr(self.toParentExtremCtrl, longName="min"+self.langDic[self.langName]['c031_volumeVariation'].capitalize(), attributeType="float", minValue=0, defaultValue=0.01, maxValue=1, keyable=True)
                    cmds.addAttr(self.toParentExtremCtrl, longName="active"+self.langDic[self.langName]['c031_volumeVariation'].capitalize(), attributeType="bool", defaultValue=1, keyable=True)
                    cmds.parent(self.toParentExtremCtrl, origGrp)
                    cmds.setAttr(self.toParentExtremCtrl+".translateZ", self.ctrlRadius)
                    if s == 1:
                        if self.getModuleAttr("flip"):
                            cmds.setAttr(self.toParentExtremCtrl+".translateZ", -self.ctrlRadius)
                    utils.zeroOut([self.toParentExtremCtrl])
                    self.ctrls.setLockHide([self.toParentExtremCtrl], ['v'])

                # invert scale for right side before:
                if s == 1:
                    cmds.setAttr(self.fkCtrlList[0] + ".scaleX", -1)
                    cmds.setAttr(self.fkCtrlList[0] + ".scaleY", -1)
                    cmds.setAttr(self.fkCtrlList[0] + ".scaleZ", -1)
                    # fix flipping issue for right side:
                    for f in range(1, len(self.fkCtrlList)):
                        attrList = ["tx", "ty", "tz", "rx", "ry", "rz"]
                        for attr in attrList:
                            attrValue = cmds.getAttr(self.fkZeroGrpList[f]+"."+attr)
                            cmds.setAttr(self.fkZeroGrpList[f]+"."+attr, -1*attrValue)
                
                # working with position, orientation of joints and make an orientConstraint for Fk controls:
                for n in range(0, self.nJoints):
                    cmds.delete(cmds.parentConstraint(side+self.userGuideName+"_Guide_JointLoc"+str(n+1), self.skinJointList[n], maintainOffset=False))
                    cmds.delete(cmds.parentConstraint(side+self.userGuideName+"_Guide_JointLoc"+str(n+1), self.ikJointList[n], maintainOffset=False))
                    
                    # freezeTransformations (rotates):
                    cmds.makeIdentity(self.skinJointList[n], self.ikJointList[n], self.fkJointList[n], apply=True, rotate=True)
                    # fk control leads fk joint:
                    cmds.parentConstraint(self.fkCtrlList[n], self.fkJointList[n], maintainOffset=True, name=side+self.userGuideName+"_%02d_Fk_PaC"%n)
                    if n == self.nJoints-1:
                        cmds.connectAttr(self.fkCtrlList[n]+".scaleX", self.fkJointList[n]+".scaleX", force=True)
                        cmds.connectAttr(self.fkCtrlList[n]+".scaleY", self.fkJointList[n]+".scaleY", force=True)
                        cmds.connectAttr(self.fkCtrlList[n]+".scaleZ", self.fkJointList[n]+".scaleZ", force=True)
                    else:
                        self.ctrls.setLockHide([self.fkCtrlList[n]], ['sx', 'sy', 'sz'])
                
                # puting endJoints in the correct position:
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.skinJointList[-1], maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.ikJointList[-1], maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.fkJointList[-1], maintainOffset=False))

                # add articulationJoint:
                if n > 0:
                    if self.addArticJoint:
                        artJntList = utils.articulationJoint(self.skinJointList[n-1], self.skinJointList[n]) #could call to create corrective joints. See parameters to implement it, please.
                        utils.setJointLabel(artJntList[0], s+jointLabelAdd, 18, self.userGuideName+"_%02d_Jar"%n)
                cmds.select(self.skinJointList[n])
                
                # creating a group reference to recept the attributes:
                self.worldRef = self.ctrls.cvControl("id_084_ChainWorldRef", side+self.userGuideName+"_WorldRef_Ctrl", r=self.ctrlRadius, d=self.curveDegree, dir="+Z")
                cmds.addAttr(self.worldRef, longName=sideLower+self.userGuideName+'_ikFkBlend', attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                if not cmds.objExists(self.worldRef+'.globalStretch'):
                    cmds.addAttr(self.worldRef, longName='globalStretch', attributeType='float', minValue=0, maxValue=1, defaultValue=1, keyable=True)
                self.worldRefList.append(self.worldRef)
                self.worldRefShape = cmds.listRelatives(self.worldRef, children=True, type='nurbsCurve')[0]
                self.worldRefShapeList.append(self.worldRefShape)

                # create constraint in order to blend ikFk:
                self.ikFkRevList = []
                for n in range(0, self.nJoints):
                    parentConst = cmds.parentConstraint(self.ikJointList[n], self.fkJointList[n], self.skinJointList[n], maintainOffset=True, name=self.skinJointList[n]+"_IkFkBlend_PaC")[0]
                    cmds.setAttr(parentConst+".interpType", 2) #shortest
                    if n == 0:
                        revNode = cmds.createNode('reverse', name=side+self.userGuideName+"_IkFkBlend_Rev")
                        cmds.connectAttr(self.worldRef+"."+sideLower+self.userGuideName+'_ikFkBlend', revNode+".inputX", force=True)
                    else:
                        revNode = side+self.userGuideName+"_IkFkBlend_Rev"
                    self.ikFkRevList.append(revNode)
                    # connecting ikFkBlend using the reverse node:
                    cmds.connectAttr(self.worldRef+"."+sideLower+self.userGuideName+'_ikFkBlend', parentConst+"."+self.fkJointList[n]+"W1", force=True)
                    cmds.connectAttr(revNode+".outputX", parentConst+"."+self.ikJointList[n]+"W0", force=True)

                # ik spline:
                ikSplineList = cmds.ikHandle(startJoint=self.ikJointList[0], endEffector=self.ikJointList[-2], name=side+self.userGuideName+"_IkH", solver="ikSplineSolver", parentCurve=False, numSpans=4) #[Handle, Effector, Curve]
                ikSplineList[1] = cmds.rename(ikSplineList[1], side+self.userGuideName+"_Eff")
                ikSplineList[2] = cmds.rename(ikSplineList[2], side+self.userGuideName+"_IkC")
                self.ikSplineHandle = ikSplineList[0]
                self.ikSplineCurve = ikSplineList[2]
                # ik clusters:
                self.ikClusterList = []
                self.ikClusterList.append(cmds.cluster(self.ikSplineCurve+".cv[0:1]", name=side+self.userGuideName+"_Ik_0_Cls")[1]) #[Deform, Handle]
                self.ikClusterList.append(cmds.cluster(self.ikSplineCurve+".cv[2]", name=side+self.userGuideName+"_Ik_1_Cls")[1]) #[Deform, Handle]
                self.ikClusterList.append(cmds.cluster(self.ikSplineCurve+".cv[3]", name=side+self.userGuideName+"_Ik_2_Cls")[1]) #[Deform, Handle]
                self.ikClusterList.append(cmds.cluster(self.ikSplineCurve+".cv[4]", name=side+self.userGuideName+"_Ik_3_Cls")[1]) #[Deform, Handle]
                self.ikClusterList.append(cmds.cluster(self.ikSplineCurve+".cv[5:6]", name=side+self.userGuideName+"_Ik_4_Cls")[1]) #[Deform, Handle]
                # ik cluster positions:
                firstIkJointPos = cmds.xform(self.ikJointList[0], query=True, worldSpace=True, rotatePivot=True)
                cmds.xform(self.ikClusterList[0], worldSpace=True, rotatePivot=firstIkJointPos)
                endIkJointPos = cmds.xform(self.ikJointList[-2], query=True, worldSpace=True, rotatePivot=True)
                cmds.xform(self.ikClusterList[-1], worldSpace=True, rotatePivot=endIkJointPos)
                # ik cluster group:
                self.ikClusterGrp = cmds.group(self.ikClusterList, name=side+self.userGuideName+"_Ik_Cluster_Grp")

                # ik controls:
                self.ikCtrlList, self.ikCtrlZeroList = [], []
                self.ikCtrlGrp = cmds.group(name=side+self.userGuideName+"_Ik_Ctrl_Grp", empty=True)
                for c, clusterNode in enumerate(self.ikClusterList):
                    if c == 0: #first
                        self.ikCtrlMain = self.ctrls.cvControl("id_086_ChainIkMain", ctrlName=side+self.userGuideName+"_Ik_Main_Ctrl", r=self.ctrlRadius, d=self.curveDegree)
                        cmds.delete(cmds.parentConstraint(clusterNode, self.ikCtrlMain, maintainOffset=False))
                        ikCtrlMainZero = utils.zeroOut([self.ikCtrlMain])[0]
                        cmds.parent(ikCtrlMainZero, self.ikCtrlGrp)
                        # loading Maya matrix node
                        loadedQuatNode = utils.checkLoadedPlugin("quatNodes", self.langDic[self.langName]['e014_cantLoadQuatNode'])
                        loadedMatrixPlugin = utils.checkLoadedPlugin("decomposeMatrix", "matrixNodes", self.langDic[self.langName]['e002_decomposeMatrixNotFound'])
                        if loadedQuatNode and loadedMatrixPlugin:
                            # setup extract rotateZ from ikCtrlMain using worldSpace matrix by quaternion:
                            ikMainLoc = cmds.spaceLocator(name=side+self.userGuideName+"_Ik_Main_Loc")[0]
                            ikMainLocGrp = cmds.group(ikMainLoc, name=side+self.userGuideName+"_Ik_MainLoc_Grp")
                            # need to keep ikMainLocGrp at the world without any transformation to use it to extract ikMainCtrl rotateZ properly:
                            cmds.setAttr(ikMainLocGrp+".inheritsTransform", 0)
                            cmds.setAttr(ikMainLocGrp+".visibility", 0)
                            self.ctrls.setLockHide([ikMainLocGrp], ['rx', 'ry', 'rz'], l=True, k=True)
                            cmds.parentConstraint(self.ikCtrlMain, ikMainLoc, maintainOffset=False, skipTranslate=("x", "y", "z"), name=ikMainLoc+"_PaC")
                            mainTwistMatrixMD = utils.twistBoneMatrix(ikMainLocGrp, ikMainLoc, "ikCtrlMain_TwistMatrix")
                            cmds.setAttr(mainTwistMatrixMD+".input1Z", 1)
                            # connect output of rotate in Z to ikSplineHandle roll attribute:
                            cmds.connectAttr(mainTwistMatrixMD+".outputZ", self.ikSplineHandle+".roll", force=True)

                    ikCtrl = self.ctrls.cvControl("id_085_ChainIk", ctrlName=side+self.userGuideName+"_Ik_"+str(c)+"_Ctrl", r=self.ctrlRadius, d=self.curveDegree)
                    self.ikCtrlList.append(ikCtrl)
                    cmds.delete(cmds.parentConstraint(clusterNode, ikCtrl, maintainOffset=False))
                    cmds.parentConstraint(ikCtrl, clusterNode, maintainOffset=True, name=clusterNode+"_PaC")
                    ikCtrlZero = utils.zeroOut([ikCtrl])[0]
                    self.ikCtrlZeroList.append(ikCtrlZero)
                    cmds.parent(ikCtrlZero, self.ikCtrlMain)
                    if c == 4: #last
                        cmds.addAttr(ikCtrl, longName=self.langDic[self.langName]['c033_autoOrient'], attributeType="float", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                        self.ctrls.setLockHide([ikCtrl], ["sx", "sy", "sz", "v"])
                        # last ik control:
                        self.ikCtrlLast = self.ctrls.cvControl("id_087_ChainIkLast", ctrlName=side+self.userGuideName+"_Ik_Last_Ctrl", r=0.75*self.ctrlRadius, d=self.curveDegree)
                        self.ctrls.colorShape([self.ikCtrlLast], 'cyan')
                        cmds.delete(cmds.parentConstraint(clusterNode, self.ikCtrlLast, maintainOffset=False))
                        ikCtrlLastZero = utils.zeroOut([self.ikCtrlLast])[0]
                        cmds.parent(ikCtrlLastZero, self.ikCtrlMain)
                        cmds.parent(ikCtrlZero, self.ikCtrlLast)
                        self.ctrls.setLockHide([self.ikCtrlLast], ["v"])
                        cmds.orientConstraint(self.ikCtrlLast, self.ikJointList[-2], maintainOffset=True, name=self.ikJointList[-2]+"_OrC")
                        cmds.connectAttr(self.ikCtrlLast+".scaleX", self.ikJointList[-2]+".scaleX", force=True)
                        cmds.connectAttr(self.ikCtrlLast+".scaleY", self.ikJointList[-2]+".scaleY", force=True)
                        cmds.connectAttr(self.ikCtrlLast+".scaleZ", self.ikJointList[-2]+".scaleZ", force=True)
                    elif not c == 0:
                        if c == 2:
                            self.ctrls.setLockHide([ikCtrl], ["rx", "ry", "sx", "sy", "sz", "v"])
                        else:
                            self.ctrls.setLockHide([ikCtrl], ["rx", "ry", "rz", "sx", "sy", "sz", "v"])
                    else: #first
                        cmds.addAttr(ikCtrl, longName=self.langDic[self.langName]['c033_autoOrient'], attributeType="float", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                        self.ctrls.setLockHide([ikCtrl], ["sx", "sy", "sz", "v"])

                # ik controls position:
                cmds.pointConstraint(self.ikCtrlMain, self.ikCtrlList[2], self.ikCtrlZeroList[1], maintainOffset=True, name=self.ikCtrlZeroList[1]+"_PoC")
                cmds.pointConstraint(self.ikCtrlMain, self.ikCtrlLast, self.ikCtrlZeroList[2], maintainOffset=True, name=self.ikCtrlZeroList[2]+"_PoC")
                cmds.pointConstraint(self.ikCtrlList[2], self.ikCtrlLast, self.ikCtrlZeroList[3], maintainOffset=True, name=self.ikCtrlZeroList[3]+"_PoC")
                
                # ik controls orientation:
                firstUpLoc, firstFakeLoc = self.setupAimLocators(side, self.ikCtrlMain, 0, self.ikCtrlList[1], self.ikCtrlMain)
                lastUpLoc, lastFakeLoc = self.setupAimLocators(side, self.ikCtrlLast, 4, self.ikCtrlList[-2], self.ikCtrlLast)
                self.setupAimConst(self.ikCtrlList[0], self.ikCtrlList[1], firstUpLoc, firstFakeLoc, self.ikCtrlZeroList[0], 1)
                self.setupAimConst(self.ikCtrlList[-1], self.ikCtrlList[-2], lastUpLoc, lastFakeLoc, self.ikCtrlZeroList[-1], -1)
                midUpLoc, midFakeLoc = self.setupAimLocators(side, self.ikCtrlList[2], 13, self.ikCtrlList[2], self.ikCtrlList[2], False)
                self.setupAimConst(self.ikCtrlList[1], self.ikCtrlList[2], midUpLoc, midFakeLoc, self.ikCtrlZeroList[1], 1, False)
                self.setupAimConst(self.ikCtrlList[3], self.ikCtrlList[2], midUpLoc, midFakeLoc, self.ikCtrlZeroList[3], -1, False)
                lastMidLoc = cmds.duplicate(lastFakeLoc, name=lastFakeLoc.replace("Fake", "Middle"))[0]
                cmds.setAttr(lastMidLoc+".translateZ", 0)
                cmds.aimConstraint(lastMidLoc, self.ikCtrlZeroList[2], worldUpType="object", worldUpObject=lastUpLoc, aimVector=(0, 0, 1), upVector=(0, 1, 0), maintainOffset=True, name=self.ikCtrlZeroList[2]+"_AiC")

                self.ikStaticDataGrp = cmds.group(ikSplineList[0], ikSplineList[2], name=side+self.userGuideName+"_IkH_Grp")

                # ik stretch:
                curveInfoNode = cmds.arclen(ikSplineList[2], constructionHistory=True)
                curveInfoNode = cmds.rename(curveInfoNode, side+self.userGuideName+"_Ik_CurveInfo")
                # create stretch nodes:
                ikNormalizeMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_Normalize_MD")
                globalStretchBC = cmds.createNode("blendColors", name=side+self.userGuideName+"_GlobalStretch_BC")
                stretchableBC = cmds.createNode("blendColors", name=side+self.userGuideName+"_Stretchable_BC")
                stretchBC = cmds.createNode("blendColors", name=side+self.userGuideName+"_Stretch_BC")
                ikStretchRevNode = cmds.createNode("reverse", name=side+self.userGuideName+"_Stretch_Rev")
                # get and set stretch attribute values:
                initialDistance = cmds.getAttr(curveInfoNode+".arcLength")
                cmds.setAttr(ikNormalizeMD+".operation", 2)
                cmds.setAttr(ikNormalizeMD+".input2X", initialDistance)
                # connect stretch attributes:
                cmds.connectAttr(curveInfoNode+".arcLength", ikNormalizeMD+".input1X", force=True)
                cmds.connectAttr(ikNormalizeMD+".outputX", globalStretchBC+".color1.color1R", force=True)
                cmds.connectAttr(globalStretchBC+".output.outputR", stretchableBC+".color1.color1R", force=True)
                cmds.connectAttr(stretchableBC+".output.outputR", stretchBC+".color1.color1R", force=True)
                cmds.connectAttr(self.toParentExtremCtrl+".stretchable", stretchableBC+".blender", force=True)
                cmds.connectAttr(ikStretchRevNode+".outputX", stretchBC+".blender", force=True)
                # work with worldRef node:
                if cmds.objExists(self.worldRef):
                    cmds.connectAttr(self.worldRef+"."+sideLower+self.userGuideName+'_ikFkBlend', ikStretchRevNode+".inputX", force=True)
                    cmds.connectAttr(self.worldRef+".globalStretch", globalStretchBC+".blender", force=True)
                    cmds.connectAttr(self.worldRef+".scaleX", globalStretchBC+".color2.color2R", force=True)
                    cmds.connectAttr(self.worldRef+".scaleX", stretchableBC+".color2.color2R", force=True)
                    cmds.connectAttr(self.worldRef+".scaleX", stretchBC+".color2.color2R", force=True)
                # output stretch values to joint scale:
                for j in range(0, len(self.ikJointList)-2):
                    cmds.connectAttr(stretchBC+".output.outputR", self.ikJointList[j]+".scaleZ", force=True)
                    cmds.connectAttr(stretchBC+".output.outputR", self.skinJointList[j]+".scaleZ", force=True)

                # volumeVariation:
                vvBC = cmds.createNode('blendColors', name=side+self.userGuideName+"_VV_BC")
                vvCond = cmds.createNode('condition', name=side+self.userGuideName+'_VV_Cond')
                vvMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_VV_MD")
                vvScaleCompensateMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_VV_ScaleCompensate_MD")
                vvClp = cmds.createNode('clamp', name=side+self.userGuideName+"_VV_Clp")
                cmds.setAttr(vvClp+".maxR", 1000)
                cmds.connectAttr(self.toParentExtremCtrl+'.'+self.langDic[self.langName]['c031_volumeVariation'], vvBC+'.blender', force=True)
                cmds.connectAttr(self.toParentExtremCtrl+".active"+self.langDic[self.langName]['c031_volumeVariation'].capitalize(), vvCond+'.firstTerm', force=True)
                cmds.connectAttr(self.toParentExtremCtrl+".min"+self.langDic[self.langName]['c031_volumeVariation'].capitalize(), vvClp+'.min.minR', force=True)
                cmds.connectAttr(vvBC+'.outputR', vvClp+'.input.inputR', force=True)
                cmds.connectAttr(vvClp+'.output.outputR', vvCond+'.colorIfTrueR', force=True)
                cmds.connectAttr(vvScaleCompensateMD+".outputX", vvBC+'.color1R', force=True)
                cmds.connectAttr(vvMD+".outputX", vvScaleCompensateMD+'.input1X', force=True)
                cmds.connectAttr(self.worldRef+".scaleX", vvMD+'.input1X', force=True)
                cmds.connectAttr(self.worldRef+".scaleX", vvCond+'.colorIfFalseR', force=True)
                cmds.connectAttr(self.worldRef+".scaleX", vvScaleCompensateMD+'.input2X', force=True)
                cmds.connectAttr(stretchBC+".output.outputR", vvMD+'.input2X', force=True)
                cmds.setAttr(vvMD+'.operation', 2)
                cmds.setAttr(vvBC+'.color2R', 1)
                cmds.setAttr(vvCond+".secondTerm", 1)
                #output volumeVariation values to joint scale axis:
                for j in range(0, len(self.skinJointList)-2):
                    cmds.connectAttr(vvCond+".outColorR", self.skinJointList[j]+".scaleX", force=True)
                    cmds.connectAttr(vvCond+".outColorR", self.skinJointList[j]+".scaleY", force=True)

                # connecting visibilities:
                cmds.connectAttr(self.worldRef+"."+sideLower+self.userGuideName+'_ikFkBlend', self.fkZeroGrpList[0] + ".visibility", force=True)
                cmds.connectAttr(self.ikFkRevList[0]+".outputX", self.ikCtrlGrp+".visibility", force=True)
                self.ctrls.setLockHide(self.fkCtrlList, ['v'], l=False)
                self.ctrls.setLockHide(self.ikCtrlList, ['v'], l=False)
                
                # last controls drive scale of last joints:
                fkLastScaleCompensateMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_LastScale_Fk_MD")
                ikLastScaleCompensateMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_LastScale_Ik_MD")
                lastScaleBC = cmds.createNode("blendColors", name=side+self.userGuideName+"_LastScale_BC")
                cmds.connectAttr(self.worldRef+"."+sideLower+self.userGuideName+'_ikFkBlend', lastScaleBC+".blender", force=True)
                cmds.connectAttr(self.fkJointList[-2]+".scaleX", fkLastScaleCompensateMD+'.input1X', force=True)
                cmds.connectAttr(self.fkJointList[-2]+".scaleY", fkLastScaleCompensateMD+'.input1Y', force=True)
                cmds.connectAttr(self.fkJointList[-2]+".scaleZ", fkLastScaleCompensateMD+'.input1Z', force=True)
                cmds.connectAttr(self.ikJointList[-2]+".scaleX", ikLastScaleCompensateMD+'.input1X', force=True)
                cmds.connectAttr(self.ikJointList[-2]+".scaleY", ikLastScaleCompensateMD+'.input1Y', force=True)
                cmds.connectAttr(self.ikJointList[-2]+".scaleZ", ikLastScaleCompensateMD+'.input1Z', force=True)
                cmds.connectAttr(self.worldRef+".scaleX", fkLastScaleCompensateMD+'.input2X', force=True)
                cmds.connectAttr(self.worldRef+".scaleX", fkLastScaleCompensateMD+'.input2Y', force=True)
                cmds.connectAttr(self.worldRef+".scaleX", fkLastScaleCompensateMD+'.input2Z', force=True)
                cmds.connectAttr(self.worldRef+".scaleX", ikLastScaleCompensateMD+'.input2X', force=True)
                cmds.connectAttr(self.worldRef+".scaleX", ikLastScaleCompensateMD+'.input2Y', force=True)
                cmds.connectAttr(self.worldRef+".scaleX", ikLastScaleCompensateMD+'.input2Z', force=True)
                cmds.connectAttr(fkLastScaleCompensateMD+".outputX", lastScaleBC+'.color1R', force=True)
                cmds.connectAttr(fkLastScaleCompensateMD+".outputY", lastScaleBC+'.color1G', force=True)
                cmds.connectAttr(fkLastScaleCompensateMD+".outputZ", lastScaleBC+'.color1B', force=True)
                cmds.connectAttr(ikLastScaleCompensateMD+".outputX", lastScaleBC+'.color2R', force=True)
                cmds.connectAttr(ikLastScaleCompensateMD+".outputY", lastScaleBC+'.color2G', force=True)
                cmds.connectAttr(ikLastScaleCompensateMD+".outputZ", lastScaleBC+'.color2B', force=True)
                cmds.connectAttr(lastScaleBC+".outputR", self.skinJointList[-2]+'.scaleX', force=True)
                cmds.connectAttr(lastScaleBC+".outputG", self.skinJointList[-2]+'.scaleY', force=True)
                cmds.connectAttr(lastScaleBC+".outputB", self.skinJointList[-2]+'.scaleZ', force=True)

                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(self.fkZeroGrpList[0], self.ikCtrlGrp, self.origFromList[0], self.worldRef, name=side+self.userGuideName+"_Control_Grp")
                self.toScalableHookGrp = cmds.group(self.skinJointList[0], self.ikJointList[0], self.fkJointList[0], self.ikClusterGrp, name=side+self.userGuideName+"_Joint_Grp")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, self.ikStaticDataGrp, ikMainLocGrp, name=side+self.userGuideName+"_Grp")
                # create a locator in order to avoid delete static group
                loc = cmds.spaceLocator(name=side+self.userGuideName+"_DO_NOT_DELETE_PLEASE_Loc")[0]
                cmds.parent(loc, self.toStaticHookGrp, absolute=True)
                cmds.setAttr(loc+".visibility", 0)
                self.ctrls.setLockHide([loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
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
                "worldRefList": self.worldRefList,
                "worldRefShapeList": self.worldRefShapeList,
            }
        }
