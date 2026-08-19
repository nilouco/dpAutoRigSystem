# importing libraries:
from maya import cmds
from maya import mel
from ..base import standard
from importlib import reload


# global variables to this module:    
CLASS_NAME = "Chain"
TITLE = "m178_chain"
DESCRIPTION = "m179_chainDesc"
WIKI = "03-‐-Guides#-chain"



class Chain(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(standard)
        self.worldRefList = []
        self.worldRefShapeList = []
        self.currentNJoints = 5
    
    
    def create_guide(self, *args):
        self.create_guide_base()
        # Custom GUIDE:
        cmds.addAttr(self.guide_base, longName="nJoints", attributeType='long')
        cmds.setAttr(self.guide_base+".nJoints", 1)
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="dynamic", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="mainControls", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="nMain", minValue=1, defaultValue=1, attributeType='long')
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
        # include nodes into net
        self.add_node_to_guide_net([self.cvJointLoc, self.cvEndJoint], ["JointLoc1", "JointEnd"])
        self.changeJointNumber(5)


    def changeJointNumber(self, enteredNJoints, *args):
        """ Edit the number of joints in the guide.
        """
        self.ar.opt.check_use_default_render_layer()
        # get the number of joints entered by user:
        if enteredNJoints == 0:
            if self.ar.data.ui_state:
                self.enteredNJoints = cmds.intField("edit_guide_n_joints_if", query=True, value=True)
            else:
                return
        else:
            self.enteredNJoints = enteredNJoints
        if self.enteredNJoints >= 5:
            # get the number of joints existing:
            self.currentNJoints = cmds.getAttr(self.guide_base+".nJoints")
            # start analisys the difference between values:
            if self.enteredNJoints != self.currentNJoints:
                # unparent temporarely the Ends:
                self.cvEndJoint = self.name_guide+"_JointEnd"
                cmds.parent(self.cvEndJoint, world=True)
                self.jGuideEnd = (self.name_guide+"_JGuideEnd")
                cmds.parent(self.jGuideEnd, world=True)
                # verify if the nJoints is greather or less than the current
                if self.enteredNJoints > self.currentNJoints:
                    for n in range(self.currentNJoints+1, self.enteredNJoints+1):
                        # create another N cvJointLoc:
                        self.cvJointLoc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_JointLoc"+str(n), r=0.3, d=1, guide=True)
                        # set its nJoint value as n:
                        cmds.setAttr(self.cvJointLoc+".nJoint", n)
                        # parent it to the lastGuide:
                        cmds.parent(self.cvJointLoc, self.name_guide+"_JointLoc"+str(n-1), relative=True)
                        cmds.setAttr(self.cvJointLoc+".translateZ", 2)
                        # create a joint to use like an arrowLine:
                        self.jGuide = cmds.joint(name=self.name_guide+"_JGuide"+str(n), radius=0.001)
                        cmds.setAttr(self.jGuide+".template", 1)
                        #Prevent a intermidiate node to be added
                        cmds.parent(self.jGuide, self.name_guide+"_JGuide"+str(n-1), relative=True)
                        #Do not maintain offset and ensure cv will be at the same place than the joint
                        cmds.parentConstraint(self.cvJointLoc, self.jGuide, maintainOffset=False, name=self.jGuide+"_PaC")
                        cmds.scaleConstraint(self.cvJointLoc, self.jGuide, maintainOffset=False, name=self.jGuide+"_ScC")
                        self.add_node_to_guide_net([self.cvJointLoc], ["JointLoc"+str(n)])
                elif self.enteredNJoints < self.currentNJoints:
                    # re-define cvEndJoint:
                    self.cvJointLoc = self.name_guide+"_JointLoc"+str(self.enteredNJoints)
                    self.cvEndJoint = self.name_guide+"_JointEnd"
                    self.jGuide = self.name_guide+"_JGuide"+str(self.enteredNJoints)
                    # re-parent the children guides:
                    childrenGuideBellowList = self.ar.utils.getGuideChildrenList(self.cvJointLoc)
                    if childrenGuideBellowList:
                        for childGuide in childrenGuideBellowList:
                            cmds.parent(childGuide, self.cvJointLoc)
                    # delete difference of nJoints:
                    cmds.delete(self.name_guide+"_JointLoc"+str(self.enteredNJoints+1))
                    cmds.delete(self.name_guide+"_JGuide"+str(self.enteredNJoints+1))
                    for j in range(self.enteredNJoints+1, self.currentNJoints+1):
                        self.remove_attr_from_guide_net(["JointLoc"+str(j)])
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

                cmds.setAttr(self.guide_base+".nJoints", self.enteredNJoints)
                self.currentNJoints = self.enteredNJoints
                self.change_main_ctrls_number(0)
                # re-build the preview mirror:
                self.create_mirror_preview()
            cmds.select(self.guide_base)
        else:
            self.changeJointNumber(5)


    def setupAimLocators(self, side, toUpParent, ikNumb, ikFakeCtrl, toFakeParent, hasFake=True, *args):
        """ Creates the up and fake locators to use in the aimConstraint.
            Return them as a list.
        """
        fakeLoc = None
        # up locator:
        upLoc = cmds.spaceLocator(name=side+self.number_name+"_%02d_Up_Loc"%ikNumb)[0]
        cmds.delete(cmds.parentConstraint(toUpParent, upLoc, maintainOffset=False))
        cmds.parent(upLoc, toUpParent, relative=False)
        cmds.setAttr(upLoc+".translateY", 2*self.radius)
        cmds.setAttr(upLoc+".visibility", 0)    
        if hasFake:
            # fake aim locator:
            fakeLoc = cmds.spaceLocator(name=side+self.number_name+"_%02d_Fake_Loc"%ikNumb)[0]
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
            cmds.connectAttr(ikCtrl+"."+self.ar.data.lang['c033_autoOrient'], aimConst+"."+ikToAimCtrl+"W0", force=True)
            aimRev = cmds.createNode("reverse", name=ikCtrlZero+"_Aim_Rev")
            cmds.connectAttr(ikCtrl+"."+self.ar.data.lang['c033_autoOrient'], aimRev+".inputX", force=True)
            cmds.connectAttr(aimRev+".outputX", aimConst+"."+fakeLoc+"W1", force=True)
            self.to_ids.append(aimRev)


    def clearRenameJointChain(self, jntList, fromName, toName, clear=True, *args):
        """ Clean up joint chain and rename it as well.
            Return the renamed list.
        """
        renamedList = []
        for item in reversed(jntList):
            if cmds.objectType(item) == "joint":
                if self.ar.data.joint_end_attr in cmds.listAttr(item):
                    newName = cmds.rename(item, item[item.rfind("|")+1:].replace("_"+self.ar.data.joint_end_attr, toName+"_"+self.ar.data.joint_end_attr))
                    renamedList.append(newName)
                    continue
                elif "_Jax" in item:
                    if clear:
                        cmds.delete(item)
                    continue
                if not toName in item[item.rfind("|")+1:]:
                    newName = cmds.rename(item, item[item.rfind("|")+1:].replace(fromName, toName))
                    renamedList.append(newName)
            else:
                if clear:
                    cmds.delete(item)
        return list(reversed(renamedList))


    def createDynamicChain(self, dynName, rebuildCrvSpans=20, *args):
        """ This is like a patch to add a dynamic setup to the Chain.
        """
        dynNameLower = dynName[0].lower()+dynName[1:]
        if dynNameLower[1] == "_":
            dynNameLower = dynName[0].lower()+dynName[2:]
        # curve
        mainCrv = cmds.duplicate(self.ikSplineList[2], name=dynName+"_Main_Crv")[0]
        cmds.delete(mainCrv+"ShapeOrig")
        cmds.rebuildCurve(mainCrv, constructionHistory=False, replaceOriginal=True, rebuildType=False, endKnots=True, keepRange=False, keepControlPoints=False, keepEndPoints=True, keepTangents=False, spans=rebuildCrvSpans, degree=3, tolerance=0.01)
        cmds.skinCluster(self.skinJointList, mainCrv, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=dynName+"_Main_Crv_SC")

        # dynamic joints
        firstDynJnt = dynName+"_00_Dyn_Jnt"
        dynJntList = cmds.duplicate(dynName+"_00_Fk_Jxt", name=firstDynJnt, fullPath=True)
        newSkinJntList = cmds.duplicate(dynName+"_00_Jnt", name=dynName+"_00_Jnt_First", fullPath=True)
        skinJntList = cmds.ls(self.skinJointList[0], long=True)
        skinJntChildrenList = cmds.listRelatives(self.skinJointList[0], children=True, allDescendents=True, fullPath=True, type="joint")
        skinJntList.extend(sorted(skinJntChildrenList))
        dynJntList = self.clearRenameJointChain(dynJntList, "_Fk", "_Dyn")
        dynJntList.insert(0, firstDynJnt)
        self.skinJointList = self.clearRenameJointChain(skinJntList, "_Jn", "_IkFk_Jx", False)
        self.ar.utils.addJointEndAttr([self.skinJointList[-1]])
        cmds.rename(self.skinJointList[-1], dynName+"_IkFk_"+self.ar.data.joint_end_attr)
        self.ar.utils.removeUserDefinedAttr(self.skinJointList[:-1])
        newSkinJntList = self.clearRenameJointChain(newSkinJntList, "", "")
        cmds.rename(dynName+"_00_Jnt_First", dynName+"_00_Jnt")
        newSkinJntList = [dynName+"_00_Jnt"]
        newSkinJntList.extend(sorted(cmds.listRelatives(dynName+"_00_Jnt", children=True, allDescendents=True)))
        self.ar.utils.clearJointLabel(self.skinJointList)
        cmds.setAttr(self.skinJointList[0]+".visibility", 0)
        
        # setup new blend joints
        self.ar.utils.createJointBlend(self.skinJointList[:-1], dynJntList[:-1], newSkinJntList[:-1], "Dyn_ikFkBlend", dynNameLower, self.worldRef, False)
        dynStretchBC = cmds.createNode("blendColors", name=dynName+"_DynStretch_BC")
        self.to_ids.append(dynStretchBC)
        cmds.connectAttr(dynJntList[0]+".scaleX", dynStretchBC+".color1R", force=True)
        cmds.connectAttr(dynJntList[0]+".scaleY", dynStretchBC+".color1G", force=True)
        cmds.connectAttr(dynJntList[0]+".scaleZ", dynStretchBC+".color1B", force=True)
        cmds.connectAttr(self.skinJointList[0]+".scaleX", dynStretchBC+".color2R", force=True)
        cmds.connectAttr(self.skinJointList[0]+".scaleY", dynStretchBC+".color2G", force=True)
        cmds.connectAttr(self.skinJointList[0]+".scaleZ", dynStretchBC+".color2B", force=True)
        cmds.connectAttr(self.worldRef+"."+dynNameLower+"Dyn_ikFkBlend", dynStretchBC+".blender", force=True)
        for j, jnt in enumerate(newSkinJntList[:-1]):
            cmds.connectAttr(dynStretchBC+".outputR", newSkinJntList[j]+".scaleX", force=True)
            cmds.connectAttr(dynStretchBC+".outputG", newSkinJntList[j]+".scaleY", force=True)
            cmds.connectAttr(dynStretchBC+".outputB", newSkinJntList[j]+".scaleZ", force=True)

        # hairSystem
        mel.eval("DynCreateHairMenu MayaWindow|mainHairMenu; HairAssignHairSystemMenu MayaWindow|mainHairMenu|hairAssignHairSystemItem;")
        cmds.select(mainCrv+"Shape")
        dpHairSystemNode = None
        allTransfList = cmds.ls(selection=False, type="transform")
        if allTransfList:
            for transform in allTransfList:
                if cmds.objExists(transform+".dpHairSystem"):
                    dpHairSystemNode = transform
                    break
        if not dpHairSystemNode:
            mel.eval("assignNewHairSystem;")
            # rename nodes
            if cmds.objExists("hairSystem1"):
                cmds.rename("hairSystem1", "dpHairSystem")
            dpHairSystemNode = "dpHairSystemShape"
            cmds.addAttr(dpHairSystemNode, longName="dpHairSystem", attributeType="bool", defaultValue=1)
            if cmds.objExists("nucleus1"):
                cmds.rename("nucleus1", "dpNucleus")
                cmds.addAttr(dpHairSystemNode, longName="dpNucleus", attributeType="bool", defaultValue=1)
            if cmds.objExists("hairSystem1OutputCurves"):
                cmds.rename("hairSystem1OutputCurves", "dpHairSystemOutputCurves")
            # parent nodes
            fxGrp = self.ar.utils.getNodeByMessage("fxGrp")
            if fxGrp:
                cmds.parent("dpNucleus", "dpHairSystem", "dpHairSystemOutputCurves", fxGrp)
                self.ar.ctrls.colorShape([fxGrp], [0.9, 0.6, 1], outliner=True)
            if cmds.objExists("hairSystem1Follicles"):
                cmds.delete("hairSystem1Follicles")
        else:
            mel.eval('assignHairSystem '+dpHairSystemNode+';')
            if cmds.objExists("dpHairSystemFollicles"):
                cmds.delete("dpHairSystemFollicles")
        cmds.rename(cmds.listRelatives(cmds.listRelatives(self.ikStaticDataGrp, children=True, allDescendents=True, type="follicle")[0], parent=True)[0], dynName+"_Dyn_Fol")
        dynCrv = cmds.rename("dpHairSystemOutputCurves|curve1", dynName+"_Dyn_Crv")
        # ikHandle
        ikSplineList = cmds.ikHandle(startJoint=firstDynJnt, endEffector=dynJntList[-2], name=dynName+"_Dyn_IkH", solver="ikSplineSolver", parentCurve=False, curve=dynCrv, createCurve=False) #[Handle, Effector]
        ikSplineList[1] = cmds.rename(ikSplineList[1], dynName+"_Dyn_Eff")
        cmds.parent(ikSplineList[0], self.ikStaticDataGrp)
        cmds.select(clear=True)


    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # run for all sides
            for s, side in enumerate(self.sides):
                attrNameLower = self.ar.utils.getAttrNameLower(side, self.number_name)
                self.base = side+self.number_name+'_Guide_Base'
                self.cvEndJoint = side+self.number_name+"_Guide_JointEnd"
                self.radiusGuide = side+self.number_name+"_Guide_Base_RadiusCtrl"
                self.ctrlZeroGrp = side+self.number_name+"_00_Ctrl_Zero_0_Grp"
                self.skinJointList, self.ikJointList, self.fkJointList = [], [], []
                # get the number of joints to be created:
                self.nJoints = cmds.getAttr(self.base+".nJoints")
                self.headDefValue = cmds.getAttr(self.base+".deformedBy")
                
                # creating joint chains:
                self.chainDic = {}
                self.jSuffixList = ['_Jnt', '_Ik_Jxt', '_Fk_Jxt']
                self.jEndSuffixList = ['_'+self.ar.data.joint_end_attr, '_Ik_'+self.ar.data.joint_end_attr, '_Fk_'+self.ar.data.joint_end_attr]
                for t, suffix in enumerate(self.jSuffixList):
                    self.wipList = []
                    cmds.select(clear=True)
                    for n in range(0, self.nJoints):
                        newJoint = cmds.joint(name=side+self.number_name+"_%02d"%n+suffix)
                        self.wipList.append(newJoint)
                    jEndJnt = cmds.joint(name=side+self.number_name+self.jEndSuffixList[t], radius=0.5)
                    self.ar.utils.addJointEndAttr([jEndJnt])
                    self.wipList.append(jEndJnt)
                    self.chainDic[suffix] = self.wipList
                # getting jointLists:
                self.skinJointList = self.chainDic[self.jSuffixList[0]]
                self.ikJointList = self.chainDic[self.jSuffixList[1]]
                self.fkJointList = self.chainDic[self.jSuffixList[2]]
                
                # hide not skin joints in order to be more Rigger friendly when working the Skinning:
                cmds.setAttr(self.ikJointList[0]+".visibility", 0)
                cmds.setAttr(self.fkJointList[0]+".visibility", 0)

                for o, skinJoint in enumerate(self.skinJointList):
                    if o < len(self.skinJointList) - 1:
                        cmds.addAttr(skinJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                        self.ar.utils.setJointLabel(skinJoint, s+self.joint_label_add, 18, self.number_name+"_%02d"%o)

                self.fkCtrlList, self.fkZeroGrpList, self.origFromList = [], [], []
                for n in range(0, self.nJoints):
                    cmds.select(clear=True)
                    # declare guide:
                    self.guide = side+self.number_name+"_Guide_JointLoc"+str(n+1)
                    
                    # create a Fk control:
                    self.fkCtrl = self.ar.ctrls.cvControl("id_082_ChainFk", side+self.number_name+"_%02d_Fk_Ctrl"%n, r=self.radius, d=self.curve_degree, headDef=self.headDefValue, guideSource=self.name_guide+"_JointLoc"+str(n+1), parentTag=self.get_parent_to_tag(self.fkCtrlList))
                    self.fkCtrlList.append(self.fkCtrl)
                    # position and orientation of joint and control:
                    cmds.delete(cmds.parentConstraint(self.guide, self.fkJointList[n], maintainOffset=False))
                    cmds.delete(cmds.parentConstraint(self.guide, self.fkCtrl, maintainOffset=False))
                    # zeroOut controls:
                    self.zeroOutCtrlGrp = self.ar.utils.zeroOut([self.fkCtrl])[0]
                    self.fkZeroGrpList.append(self.zeroOutCtrlGrp)
                    # hide visibility attribute:
                    cmds.setAttr(self.fkCtrl+'.visibility', keyable=False)

                    # creating the originedFrom attributes (in order to permit composed parents in the future):
                    origGrp = cmds.group(empty=True, name=side+self.number_name+"_%02d_OrigFrom_Grp"%n)
                    self.origFromList.append(origGrp)
                    if n == 0:
                        self.ar.utils.originedFrom(objName=origGrp, attrString=self.guide[self.guide.find("__") + 1:].replace(":", "_")+";"+self.cvEndJoint+";"+self.radiusGuide)
                    elif n == (self.nJoints-1):
                        self.ar.utils.originedFrom(objName=origGrp, attrString=self.guide[self.guide.find("__") + 1:].replace(":", "_")+";"+self.base)
                    else:
                        self.ar.utils.originedFrom(objName=origGrp, attrString=self.guide[self.guide.find("__") + 1:].replace(":", "_"))
                    self.to_ids.extend(cmds.parentConstraint(self.skinJointList[n], origGrp, maintainOffset=False, name=origGrp+"_PaC"))
                    
                    if n > 0:
                        cmds.parent(self.fkZeroGrpList[n], self.fkCtrlList[n - 1])
                        cmds.parent(origGrp, self.origFromList[n - 1])

                # add extrem_toParent_Ctrl
                if n == (self.nJoints-1):
                    self.toParentExtremCtrl = self.ar.ctrls.cvControl("id_083_ChainToParent", ctrlName=side+self.number_name+"_ToParent_Ctrl", r=(self.radius * 0.1), d=self.curve_degree, headDef=self.headDefValue, guideSource=self.name_guide+"_JointEnd", parentTag=self.fkCtrlList[-1])
                    cmds.addAttr(self.toParentExtremCtrl, longName="stretchable", minValue=0, maxValue=1, attributeType="float", defaultValue=1, keyable=True)
                    cmds.addAttr(self.toParentExtremCtrl, longName=self.ar.data.lang['c031_volumeVariation'], attributeType="float", minValue=0, defaultValue=1, keyable=True)
                    cmds.addAttr(self.toParentExtremCtrl, longName="min"+self.ar.data.lang['c031_volumeVariation'], attributeType="float", minValue=0, defaultValue=0.01, maxValue=1, keyable=True)
                    cmds.addAttr(self.toParentExtremCtrl, longName=self.ar.data.lang['c118_active']+self.ar.data.lang['c031_volumeVariation'], attributeType="short", minValue=0, defaultValue=1, maxValue=1, keyable=True)
                    cmds.parent(self.toParentExtremCtrl, origGrp)
                    cmds.setAttr(self.toParentExtremCtrl+".translateZ", self.radius)
                    if s == 1:
                        if self.flip:
                            cmds.setAttr(self.toParentExtremCtrl+".translateZ", -self.radius)
                    self.ar.utils.zeroOut([self.toParentExtremCtrl])
                    self.ar.ctrls.setLockHide([self.toParentExtremCtrl], ['v'])

                # invert scale for right side before:
                if s == 1:
                    if self.flip:
                        # fix flipping issue for FK right side:
                        for f in range(1, len(self.fkCtrlList)):
                            cmds.setAttr(self.fkZeroGrpList[0]+".scaleX", -1)
                            cmds.setAttr(self.fkZeroGrpList[0]+".scaleY", -1)
                            cmds.setAttr(self.fkZeroGrpList[0]+".scaleZ", -1)
                            attributes = ["tx", "ty", "tz", "rx", "ry", "rz"]
                            for attr in attributes:
                                attr_value = cmds.getAttr(self.fkZeroGrpList[f]+"."+attr)
                                cmds.setAttr(self.fkZeroGrpList[f]+"."+attr, -1*attr_value)
                
                # working with position, orientation of joints and make an orientConstraint for Fk controls:
                for n in range(0, self.nJoints):
                    cmds.delete(cmds.parentConstraint(side+self.number_name+"_Guide_JointLoc"+str(n+1), self.skinJointList[n], maintainOffset=False))
                    cmds.delete(cmds.parentConstraint(side+self.number_name+"_Guide_JointLoc"+str(n+1), self.ikJointList[n], maintainOffset=False))
                    # freezeTransformations (rotates):
                    cmds.makeIdentity(self.skinJointList[n], self.ikJointList[n], self.fkJointList[n], apply=True, rotate=True)
                    # fk control leads fk joint:
                    cmds.parentConstraint(self.fkCtrlList[n], self.fkJointList[n], maintainOffset=True, name=side+self.number_name+"_%02d_Fk_PaC"%n)
                    if n == self.nJoints-1:
                        cmds.connectAttr(self.fkCtrlList[n]+".scaleX", self.fkJointList[n]+".scaleX", force=True)
                        cmds.connectAttr(self.fkCtrlList[n]+".scaleY", self.fkJointList[n]+".scaleY", force=True)
                        cmds.connectAttr(self.fkCtrlList[n]+".scaleZ", self.fkJointList[n]+".scaleZ", force=True)
                    else:
                        self.ar.ctrls.setLockHide([self.fkCtrlList[n]], ['sx', 'sy', 'sz'])

                if self.mirror_axis == "Z":
                    cmds.setAttr(self.ikJointList[0]+".rotateZ", 180)
                # puting endJoints in the correct position:
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.skinJointList[-1], maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.ikJointList[-1], maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.fkJointList[-1], maintainOffset=False))
                
                # creating a group reference to recept the attributes:
                self.worldRef = self.ar.ctrls.cvControl("id_084_ChainWorldRef", side+self.number_name+"_WorldRef_Ctrl", r=self.radius, d=self.curve_degree, dir="+Z", headDef=self.headDefValue, guideSource=self.name_guide+"_Base")
                if not cmds.objExists(self.worldRef+'.globalStretch'):
                    cmds.addAttr(self.worldRef, longName='globalStretch', attributeType='float', minValue=0, maxValue=1, defaultValue=1, keyable=True)
                self.worldRefList.append(self.worldRef)
                self.worldRefShape = cmds.listRelatives(self.worldRef, children=True, type='nurbsCurve')[0]
                self.worldRefShapeList.append(self.worldRefShape)

                # create constraint in order to blend ikFk:
                self.ar.utils.createJointBlend(self.ikJointList, self.fkJointList, self.skinJointList, "Fk_ikFkBlend", attrNameLower, self.worldRef)

                # ik spline:
                self.ikSplineList = cmds.ikHandle(startJoint=self.ikJointList[0], endEffector=self.ikJointList[-2], name=side+self.number_name+"_IkH", solver="ikSplineSolver", parentCurve=False, numSpans=4) #[Handle, Effector, Curve]
                self.ikSplineList[1] = cmds.rename(self.ikSplineList[1], side+self.number_name+"_Eff")
                self.ikSplineList[2] = cmds.rename(self.ikSplineList[2], side+self.number_name+"_IkC")
                self.ikSplineHandle = self.ikSplineList[0]
                self.ikSplineCurve = self.ikSplineList[2]
                # ik clusters:
                self.ikClusterList = []
                for p, i in zip(["0:1", "2", "3", "4", "5:6"], range(0,5)):
                    clusterList = cmds.cluster(self.ikSplineCurve+".cv["+p+"]", name=side+self.number_name+"_Ik_"+str(i)+"_Cls") #[Deform, Handle]
                    self.to_ids.append(clusterList[0]) #Deformer
                    self.ikClusterList.append(clusterList[1]) #Handle
                # ik cluster positions:
                firstIkJointPos = cmds.xform(self.ikJointList[0], query=True, worldSpace=True, rotatePivot=True)
                cmds.xform(self.ikClusterList[0], worldSpace=True, rotatePivot=firstIkJointPos)
                endIkJointPos = cmds.xform(self.ikJointList[-2], query=True, worldSpace=True, rotatePivot=True)
                cmds.xform(self.ikClusterList[-1], worldSpace=True, rotatePivot=endIkJointPos)
                # ik cluster group:
                self.ikClusterGrp = cmds.group(self.ikClusterList, name=side+self.number_name+"_Ik_Cluster_Grp")
                optionCtrl = self.ar.utils.getNodeByMessage("optionCtrl")
                if optionCtrl:
                    for axis in ['X', 'Y', 'Z']:
                        cmds.connectAttr(optionCtrl+".rigScaleOutput", self.ikClusterGrp+".scale"+axis)

                # ik controls:
                self.ikCtrlList, self.ikCtrlZeroList = [], []
                self.ikCtrlGrp = cmds.group(name=side+self.number_name+"_Ik_Ctrl_Grp", empty=True)
                for c, clusterNode in enumerate(self.ikClusterList):
                    if c == 0: #first
                        self.ikCtrlMain = self.ar.ctrls.cvControl("id_086_ChainIkMain", ctrlName=side+self.number_name+"_Ik_Main_Ctrl", r=self.radius, d=self.curve_degree, headDef=self.headDefValue, guideSource=self.name_guide+"_Base")
                        cmds.delete(cmds.parentConstraint(clusterNode, self.ikCtrlMain, maintainOffset=False))
                        ikCtrlMainZero = self.ar.utils.zeroOut([self.ikCtrlMain])[0]
                        cmds.parent(ikCtrlMainZero, self.ikCtrlGrp)
                        
                        # orienting controls
                        if s == 1:
                            cmds.parent(self.base, world=True)
                        guideBaseRX = cmds.getAttr(self.base+".rotateX")
                        guideBaseRY = cmds.getAttr(self.base+".rotateY")
                        guideBaseRZ = cmds.getAttr(self.base+".rotateZ")
                        cmds.setAttr(ikCtrlMainZero+".rotateX", guideBaseRX)
                        cmds.setAttr(ikCtrlMainZero+".rotateY", guideBaseRY)
                        cmds.setAttr(ikCtrlMainZero+".rotateZ", guideBaseRZ)
                        self.fixMirrorFlipping(ikCtrlMainZero, s, -1)

                        # loading Maya matrix node
                        loaded_quaternion_plugin = self.ar.utils.checkLoadedPlugin("quatNodes", self.ar.data.lang['e014_cantLoadQuatNode'])
                        loaded_matrix_plugin = self.ar.utils.checkLoadedPlugin("matrixNodes", self.ar.data.lang['e002_matrixPluginNotFound'])
                        if loaded_quaternion_plugin and loaded_matrix_plugin:
                            # setup extract rotateZ from ikCtrlMain using worldSpace matrix by quaternion:
                            ikMainLoc = cmds.spaceLocator(name=side+self.number_name+"_Ik_Main_Loc")[0]
                            ikMainLocGrp = cmds.group(ikMainLoc, name=side+self.number_name+"_Ik_MainLoc_Grp")
                            # need to keep ikMainLocGrp at the world without any transformation to use it to extract ikMainCtrl rotateZ properly:
                            cmds.setAttr(ikMainLocGrp+".inheritsTransform", 0)
                            cmds.setAttr(ikMainLocGrp+".visibility", 0)
                            cmds.delete(cmds.parentConstraint(self.ikCtrlMain, ikMainLocGrp, maintainOffset=False, skipTranslate=("x", "y", "z")))
                            self.ar.ctrls.setLockHide([ikMainLocGrp], ['rx', 'ry', 'rz'], l=True, k=True)
                            cmds.parentConstraint(self.ikCtrlMain, ikMainLoc, maintainOffset=False, skipTranslate=("x", "y", "z"), name=ikMainLoc+"_PaC")
                            mainTwistMatrixMD = self.ar.utils.twistBoneMatrix(ikMainLocGrp, ikMainLoc, "ikCtrlMain_TwistMatrix")
                            cmds.setAttr(mainTwistMatrixMD+".input1Z", 1)
                            if s == 1:
                                cmds.setAttr(mainTwistMatrixMD+".input1Z", -1)
                            # connect output of rotate in Z to ikSplineHandle roll attribute:
                            cmds.connectAttr(mainTwistMatrixMD+".outputZ", self.ikSplineHandle+".roll", force=True)

                    ikCtrl = self.ar.ctrls.cvControl("id_085_ChainIk", ctrlName=side+self.number_name+"_Ik_"+str(c)+"_Ctrl", r=self.radius, d=self.curve_degree, headDef=self.headDefValue, guideSource=self.name_guide+"_JointLoc"+str(c), parentTag=self.get_parent_to_tag(self.ikCtrlList, self.ikCtrlMain))
                    self.ikCtrlList.append(ikCtrl)
                    cmds.delete(cmds.parentConstraint(clusterNode, ikCtrl, maintainOffset=False))
                    ikCtrlZero = self.ar.utils.zeroOut([ikCtrl])[0]
                    self.ikCtrlZeroList.append(ikCtrlZero)
                    cmds.parent(ikCtrlZero, self.ikCtrlMain)
                    cmds.rotate(0, 0, 0, ikCtrlZero)
                    cmds.parentConstraint(ikCtrl, clusterNode, maintainOffset=True, name=clusterNode+"_PaC")
                    self.fixMirrorFlipping(ikCtrlZero, s, 1)

                    if c == 4: #last
                        cmds.addAttr(ikCtrl, longName=self.ar.data.lang['c033_autoOrient'], attributeType="float", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                        self.ar.ctrls.setLockHide([ikCtrl], ["sx", "sy", "sz", "v"])
                        # last ik control:
                        self.ikCtrlLast = self.ar.ctrls.cvControl("id_087_ChainIkLast", ctrlName=side+self.number_name+"_Ik_"+self.ar.data.lang['c125_last']+"_Ctrl", r=0.75*self.radius, d=self.curve_degree, headDef=self.headDefValue, guideSource=self.name_guide+"_JointEnd", parentTag=self.ikCtrlList[-1])
                        self.ar.ctrls.colorShape([self.ikCtrlLast], 'cyan')
                        cmds.delete(cmds.parentConstraint(ikCtrl, self.ikCtrlLast, maintainOffset=False))
                        ikCtrlLastZero = self.ar.utils.zeroOut([self.ikCtrlLast])[0]
                        cmds.parent(ikCtrlLastZero, self.ikCtrlMain)
                        self.ar.ctrls.setLockHide([self.ikCtrlLast], ["v"])
                        cmds.orientConstraint(self.ikCtrlLast, self.ikJointList[-2], maintainOffset=True, name=self.ikJointList[-2]+"_OrC")
                        cmds.connectAttr(self.ikCtrlLast+".scaleX", self.ikJointList[-2]+".scaleX", force=True)
                        cmds.connectAttr(self.ikCtrlLast+".scaleY", self.ikJointList[-2]+".scaleY", force=True)
                        cmds.connectAttr(self.ikCtrlLast+".scaleZ", self.ikJointList[-2]+".scaleZ", force=True)
                        self.fixMirrorFlipping(ikCtrlLastZero, s, -1, "X")
                        self.fixMirrorFlipping(ikCtrlLastZero, s, -1, "Y")
                        self.fixMirrorFlipping(ikCtrlLastZero, s, 1, "Z")
                        if self.mirror_axis == "Y":
                            self.fixMirrorFlipping(ikCtrlLastZero, s, -1, "Z")
                        cmds.parent(ikCtrlZero, self.ikCtrlLast)
                    elif not c == 0:
                        if c == 2:
                            self.ar.ctrls.setLockHide([ikCtrl], ["rx", "ry", "sx", "sy", "sz", "v", "ro"])
                        else:
                            self.ar.ctrls.setLockHide([ikCtrl], ["rx", "ry", "rz", "sx", "sy", "sz", "v", "ro"])
                    else: #first
                        cmds.addAttr(ikCtrl, longName=self.ar.data.lang['c033_autoOrient'], attributeType="float", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                        self.ar.ctrls.setLockHide([ikCtrl], ["sx", "sy", "sz", "v"])
                        # first ik control:
                        self.ikCtrlFirst = self.ar.ctrls.cvControl("id_087_ChainIkLast", ctrlName=side+self.number_name+"_Ik_"+self.ar.data.lang['c114_first']+"_Ctrl", r=0.75*self.radius, d=self.curve_degree, headDef=self.headDefValue, guideSource=self.name_guide+"_Base", parentTag=self.ikCtrlMain)
                        self.ar.ctrls.colorShape([self.ikCtrlFirst], 'cyan')
                        cmds.delete(cmds.parentConstraint(ikCtrl, self.ikCtrlFirst, maintainOffset=False))
                        ikCtrlFirstZero = self.ar.utils.zeroOut([self.ikCtrlFirst])[0]
                        cmds.parent(ikCtrlFirstZero, self.ikCtrlMain)
                        self.ar.ctrls.setLockHide([self.ikCtrlFirst], ["v"])
                        cmds.connectAttr(self.ikCtrlFirst+".scaleX", self.ikJointList[0]+".scaleX", force=True)
                        cmds.connectAttr(self.ikCtrlFirst+".scaleY", self.ikJointList[0]+".scaleY", force=True)
                        cmds.connectAttr(self.ikCtrlFirst+".scaleZ", self.ikJointList[0]+".scaleZ", force=True)
                        self.fixMirrorFlipping(ikCtrlFirstZero, s, -1, "X")
                        self.fixMirrorFlipping(ikCtrlFirstZero, s, -1, "Y")
                        self.fixMirrorFlipping(ikCtrlFirstZero, s, 1, "Z")
                        if self.mirror_axis == "Y":
                            self.fixMirrorFlipping(ikCtrlFirstZero, s, -1, "Z")
                        cmds.parent(ikCtrlZero, self.ikCtrlFirst)
                cmds.connectAttr(self.ikCtrlFirst+".message", self.ikCtrlList[0]+".parentTag", force=True)
                
                # ik controls position:
                cmds.pointConstraint(self.ikCtrlFirst, self.ikCtrlList[2], self.ikCtrlZeroList[1], maintainOffset=True, name=self.ikCtrlZeroList[1]+"_PoC")
                cmds.pointConstraint(self.ikCtrlFirst, self.ikCtrlLast, self.ikCtrlZeroList[2], maintainOffset=True, name=self.ikCtrlZeroList[2]+"_PoC")
                cmds.pointConstraint(self.ikCtrlList[2], self.ikCtrlLast, self.ikCtrlZeroList[3], maintainOffset=True, name=self.ikCtrlZeroList[3]+"_PoC")
                
                # ik controls orientation:
                firstUpLoc, firstFakeLoc = self.setupAimLocators(side, self.ikCtrlFirst, 0, self.ikCtrlList[1], self.ikCtrlFirst)
                lastUpLoc, lastFakeLoc = self.setupAimLocators(side, self.ikCtrlLast, 4, self.ikCtrlList[-2], self.ikCtrlLast)
                midUpLoc, midFakeLoc = self.setupAimLocators(side, self.ikCtrlList[2], 13, self.ikCtrlList[2], self.ikCtrlList[2], False)
                lastMidLoc = cmds.duplicate(lastFakeLoc, name=lastFakeLoc.replace("Fake", "Middle"))[0]
                cmds.setAttr(lastMidLoc+".translateZ", 0)
                if s == 0:
                    self.setupAimConst(self.ikCtrlList[0], self.ikCtrlList[1], firstUpLoc, firstFakeLoc, self.ikCtrlZeroList[0], 1)
                    self.setupAimConst(self.ikCtrlList[-1], self.ikCtrlList[-2], lastUpLoc, lastFakeLoc, self.ikCtrlZeroList[-1], -1)
                    self.setupAimConst(self.ikCtrlList[1], self.ikCtrlList[2], midUpLoc, midFakeLoc, self.ikCtrlZeroList[1], 1, False)
                    self.setupAimConst(self.ikCtrlList[3], self.ikCtrlList[2], midUpLoc, midFakeLoc, self.ikCtrlZeroList[3], -1, False)
                    cmds.aimConstraint(lastMidLoc, self.ikCtrlZeroList[2], worldUpType="object", worldUpObject=lastUpLoc, aimVector=(0, 0, 1), upVector=(0, 1, 0), maintainOffset=True, name=self.ikCtrlZeroList[2]+"_AiC")
                else:
                    self.setupAimConst(self.ikCtrlList[0], self.ikCtrlList[1], firstUpLoc, firstFakeLoc, self.ikCtrlZeroList[0], -1)
                    self.setupAimConst(self.ikCtrlList[-1], self.ikCtrlList[-2], lastUpLoc, lastFakeLoc, self.ikCtrlZeroList[-1], -1)
                    self.setupAimConst(self.ikCtrlList[1], self.ikCtrlList[2], midUpLoc, midFakeLoc, self.ikCtrlZeroList[1], -1, False)
                    self.setupAimConst(self.ikCtrlList[3], self.ikCtrlList[2], midUpLoc, midFakeLoc, self.ikCtrlZeroList[3], 1, False)
                    cmds.aimConstraint(lastMidLoc, self.ikCtrlZeroList[2], worldUpType="object", worldUpObject=lastUpLoc, aimVector=(0, 0, -1), upVector=(0, 1, 0), maintainOffset=True, name=self.ikCtrlZeroList[2]+"_AiC")
                
                self.ikStaticDataGrp = cmds.group(self.ikSplineList[0], self.ikSplineList[2], name=side+self.number_name+"_IkH_Grp")

                # ik stretch:
                curveInfoNode = cmds.arclen(self.ikSplineList[2], constructionHistory=True)
                curveInfoNode = cmds.rename(curveInfoNode, side+self.number_name+"_Ik_CurveInfo")
                # create stretch nodes:
                ikNormalizeMD = cmds.createNode("multiplyDivide", name=side+self.number_name+"_Normalize_MD")
                globalStretchBC = cmds.createNode("blendColors", name=side+self.number_name+"_GlobalStretch_BC")
                stretchableBC = cmds.createNode("blendColors", name=side+self.number_name+"_Stretchable_BC")
                stretchBC = cmds.createNode("blendColors", name=side+self.number_name+"_Stretch_BC")
                ikStretchRevNode = cmds.createNode("reverse", name=side+self.number_name+"_Stretch_Rev")
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
                    cmds.connectAttr(self.worldRef+"."+attrNameLower+"Fk_ikFkBlend", ikStretchRevNode+".inputX", force=True)
                    cmds.connectAttr(self.worldRef+".globalStretch", globalStretchBC+".blender", force=True)
                    cmds.connectAttr(self.worldRef+".scaleX", globalStretchBC+".color2.color2R", force=True)
                    cmds.connectAttr(self.worldRef+".scaleX", stretchableBC+".color2.color2R", force=True)
                    cmds.connectAttr(self.worldRef+".scaleX", stretchBC+".color2.color2R", force=True)
                # output stretch values to joint scale:
                for j in range(0, len(self.ikJointList)-2):
                    cmds.connectAttr(stretchBC+".output.outputR", self.ikJointList[j]+".scaleX", force=True)
                    cmds.connectAttr(stretchBC+".output.outputR", self.ikJointList[j]+".scaleY", force=True)
                    cmds.connectAttr(stretchBC+".output.outputR", self.ikJointList[j]+".scaleZ", force=True)
                    cmds.connectAttr(stretchBC+".output.outputR", self.skinJointList[j]+".scaleZ", force=True)

                # volumeVariation:
                vvBC = cmds.createNode('blendColors', name=side+self.number_name+"_VV_BC")
                vvCond = cmds.createNode('condition', name=side+self.number_name+'_VV_Cond')
                vvMD = cmds.createNode('multiplyDivide', name=side+self.number_name+"_VV_MD")
                vvScaleCompensateMD = cmds.createNode('multiplyDivide', name=side+self.number_name+"_VV_ScaleCompensate_MD")
                vvClp = cmds.createNode('clamp', name=side+self.number_name+"_VV_Clp")
                cmds.setAttr(vvClp+".maxR", 1000)
                cmds.connectAttr(self.toParentExtremCtrl+'.'+self.ar.data.lang['c031_volumeVariation'], vvBC+'.blender', force=True)
                cmds.connectAttr(self.toParentExtremCtrl+"."+self.ar.data.lang['c118_active']+self.ar.data.lang['c031_volumeVariation'], vvCond+'.firstTerm', force=True)
                cmds.connectAttr(self.toParentExtremCtrl+".min"+self.ar.data.lang['c031_volumeVariation'], vvClp+'.min.minR', force=True)
                cmds.connectAttr(vvBC+'.outputR', vvClp+'.input.inputR', force=True)
                cmds.connectAttr(vvClp+'.output.outputR', vvCond+'.colorIfTrueR', force=True)
                cmds.connectAttr(vvScaleCompensateMD+".outputX", vvBC+'.color1R', force=True)
                cmds.connectAttr(vvMD+".outputX", vvScaleCompensateMD+'.input1X', force=True)
                cmds.connectAttr(self.worldRef+".scaleX", vvMD+'.input1X', force=True)
                cmds.connectAttr(self.worldRef+".scaleX", vvCond+'.colorIfFalseR', force=True)
                cmds.connectAttr(self.worldRef+".scaleX", vvScaleCompensateMD+'.input2X', force=True)
                cmds.connectAttr(self.worldRef+".scaleX", vvBC+'.color2.color2R', force=True)
                cmds.connectAttr(stretchBC+".output.outputR", vvMD+'.input2X', force=True)
                cmds.setAttr(vvMD+'.operation', 2)
                cmds.setAttr(vvCond+".secondTerm", 1)
                #output volumeVariation values to joint scale axis:
                for j in range(0, len(self.skinJointList)-2):
                    cmds.connectAttr(vvCond+".outColorR", self.skinJointList[j]+".scaleX", force=True)
                    cmds.connectAttr(vvCond+".outColorR", self.skinJointList[j]+".scaleY", force=True)

                # connecting visibilities:
                cmds.connectAttr(self.worldRef+"."+attrNameLower+"Fk_ikFkBlend", self.fkZeroGrpList[0] + ".visibility", force=True)
                cmds.connectAttr(self.worldRef+"."+attrNameLower+"Fk_ikFkBlendRevOutputX", self.ikCtrlGrp+".visibility", force=True)
                self.ar.ctrls.setLockHide(self.fkCtrlList, ['v'], l=False)
                self.ar.ctrls.setLockHide(self.ikCtrlList, ['v'], l=False)
                
                # last controls drive scale of last joints:
                fkLastScaleCompensateMD = cmds.createNode("multiplyDivide", name=side+self.number_name+"_LastScale_Fk_MD")
                ikLastScaleCompensateMD = cmds.createNode("multiplyDivide", name=side+self.number_name+"_LastScale_Ik_MD")
                lastScaleBC = cmds.createNode("blendColors", name=side+self.number_name+"_LastScale_BC")
                cmds.connectAttr(self.worldRef+"."+attrNameLower+"Fk_ikFkBlend", lastScaleBC+".blender", force=True)
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

                # work with main fk controllers
                if cmds.getAttr(self.base+".mainControls"):
                    self.add_fk_main_ctrls(side, self.fkCtrlList)
                # create a masterModuleGrp to be checked if this rig exists:
                self.create_hook_setup(side, [self.fkZeroGrpList[0], self.ikCtrlGrp, self.origFromList[0], self.worldRef], [self.skinJointList[0], self.ikJointList[0], self.fkJointList[0], self.ikClusterGrp], [self.ikStaticDataGrp, ikMainLocGrp])
                # dynamic
                if self.get_guide_attr("dynamic"):
                    self.createDynamicChain(side+self.number_name)
                    cmds.xform(self.ctrl_hook_grp, pivots=cmds.xform(self.ikCtrlMain, worldSpace=True, rotatePivot=True, query=True))
                # delete duplicated group for side (mirror):
                cmds.delete(self.base, side+self.number_name+'_'+self.mirror_grp)
                self.ar.utils.addCustomAttr(self.origFromList, self.ar.utils.ignoreTransformIOAttr)
                self.ar.utils.addCustomAttr([self.ikClusterGrp, self.ikCtrlGrp, ikMainLocGrp, self.ikStaticDataGrp], self.ar.utils.ignoreTransformIOAttr)
                self.to_ids.extend([curveInfoNode, ikNormalizeMD, globalStretchBC, stretchableBC, stretchBC, ikStretchRevNode, vvBC, vvCond, vvMD, vvScaleCompensateMD, vvClp, fkLastScaleCompensateMD, ikLastScaleCompensateMD, lastScaleBC])
                self.ar.custom_attr.addAttr(0, [self.static_hook_grp], descendents=True) #dpID
            # finalize this rig:
            self.serialize_guide()
            self.composing_info()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and module_instance namespace:
        self.delete_guide()
        self.rename_unit_conversion()
        self.ar.custom_attr.addAttr(0, self.to_ids) #dpID
    

    def fixMirrorFlipping(self, item, s, value=-1, axis=None, *args):
        """ Just flip the controller to fix the mirror issue.
        """
        if s == 1:
            if self.flip:
                if not axis:
                    if self.mirror_axis == "X":
                        cmds.setAttr(item+".scaleZ", value)
                    elif self.mirror_axis == "Y":
                        cmds.setAttr(item+".scaleZ", -value)
                    elif self.mirror_axis == "Z":
                        cmds.setAttr(item+".scaleZ", value)
                else:
                    cmds.setAttr(item+".scale"+axis, value)


    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "worldRefList": self.worldRefList,
                            "worldRefShapeList": self.worldRefShapeList,
                        }
