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
                cmds.intField(self.nJointsIF, edit=True, value=3, minValue=3)
            except:
                pass
            self.changeJointNumber(3)
    
    
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
        if self.enteredNJoints >= 3:
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
            self.changeJointNumber(3)
    
    
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
                    cmds.parent(self.toParentExtremCtrl, origGrp)
                    if s == 0:
                        cmds.setAttr(self.toParentExtremCtrl+".translateZ", self.ctrlRadius)
                    else:
                        cmds.setAttr(self.toParentExtremCtrl+".translateZ", -self.ctrlRadius)
                    utils.zeroOut([self.toParentExtremCtrl])
                    self.ctrls.setLockHide([self.toParentExtremCtrl], ['v'])

                # invert scale for right side before:
                if s == 1:
                    cmds.setAttr(self.fkCtrlList[0] + ".scaleX", -1)
                    cmds.setAttr(self.fkCtrlList[0] + ".scaleY", -1)
                    cmds.setAttr(self.fkCtrlList[0] + ".scaleZ", -1)

                # working with position, orientation of joints and make an orientConstraint for Fk controls:
                for n in range(0, self.nJoints):
                    cmds.delete(cmds.parentConstraint(side+self.userGuideName+"_Guide_JointLoc"+str(n+1), self.skinJointList[n], maintainOffset=False))
                    cmds.delete(cmds.parentConstraint(side+self.userGuideName+"_Guide_JointLoc"+str(n+1), self.ikJointList[n], maintainOffset=False))

                    # freezeTransformations (rotates):
                    cmds.makeIdentity(self.skinJointList[n], self.ikJointList[n], self.fkJointList[n], apply=True, rotate=True)
                    # fk control leads fk joint:
                    cmds.parentConstraint(self.fkCtrlList[n], self.fkJointList[n], maintainOffset=True, name=side+self.userGuideName+"_%02d_Fk_PaC"%n)
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









                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(self.fkZeroGrpList[0], self.origFromList[0], self.worldRef, name=side+self.userGuideName+"_Control_Grp")
                self.toScalableHookGrp = cmds.group(self.skinJointList[0], self.ikJointList[0], self.fkJointList[0], name=side+self.userGuideName+"_Joint_Grp")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, name=side+self.userGuideName+"_Grp")
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
