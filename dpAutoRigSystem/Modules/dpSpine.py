# importing libraries:
from maya import cmds
from . import dpBaseClass
from . import dpLayoutClass

# global variables to this module:
CLASS_NAME = "Spine"
TITLE = "m011_spine"
DESCRIPTION = "m012_spineDesc"
ICON = "/Icons/dp_spine.png"

DP_SPINE_VERSION = 2.2


class Spine(dpBaseClass.StartClass, dpLayoutClass.LayoutClass):
    def __init__(self, *args, **kwargs):
        # Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseClass.StartClass.__init__(self, *args, **kwargs)

        # Declare variable
        self.integratedActionsDic = {}
        self.cvJointLoc = None
        self.shapeSizeCH = None
        self.currentNJoints = 3

        # List of returned data:
        self.aHipsAList = []
        self.tipList = []
        self.aVolVariationAttrList = []
        self.aActVolVariationAttrList = []
        self.aMScaleVolVariationAttrList = []
        self.aIkFkBlendAttrList = []
        self.aInnerCtrls = []
        self.aOuterCtrls = []
        self.aRbnJointList = []
        self.aClusterGrp = []


    def createModuleLayout(self, *args):
        dpBaseClass.StartClass.createModuleLayout(self)
        dpLayoutClass.LayoutClass.basicModuleLayout(self)
    
    
    def reCreateEditSelectedModuleLayout(self, bSelect=False, *args):
        dpLayoutClass.LayoutClass.reCreateEditSelectedModuleLayout(self, bSelect)
        # style layout:
        self.styleLayout = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 50, 50, 70), columnAlign=[(1, 'right'), (2, 'left'), (3, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (3, 'both', 10)], parent="selectedModuleColumn")
        cmds.text(label=self.dpUIinst.lang['m041_style'], visible=True, parent=self.styleLayout)
        self.styleMenu = cmds.optionMenu("styleMenu", label='', changeCommand=self.changeStyle, parent=self.styleLayout)
        styleMenuItemList = [self.dpUIinst.lang['m042_default'], self.dpUIinst.lang['m026_biped']]
        for item in styleMenuItemList:
            cmds.menuItem(label=item, parent=self.styleMenu)
        # read from guide attribute the current value to style:
        currentStyle = cmds.getAttr(self.moduleGrp+".style")
        cmds.optionMenu(self.styleMenu, edit=True, select=int(currentStyle+1))
        
        
    def changeStyle(self, style, *args):
        """ Change the style to be applyed custom actions to be more animator friendly.
            We will optimise: control world orientation
        """
        # for Default style:
        if style == self.dpUIinst.lang['m042_default']:
            cmds.setAttr(self.moduleGrp+".style", 0)
        # for Biped style:
        if style == self.dpUIinst.lang['m026_biped']:
            cmds.setAttr(self.moduleGrp+".style", 1)


    def createGuide(self, *args):
        dpBaseClass.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="nJoints", attributeType='long', defaultValue=1)
        cmds.addAttr(self.moduleGrp, longName="style", attributeType='enum', enumName=self.dpUIinst.lang['m042_default']+':'+self.dpUIinst.lang['m026_biped'])
        self.cvJointLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLoc1", r=0.5, d=1, guide=True)
        self.cvEndJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1, d=1, guide=True)
        cmds.parent(self.cvEndJoint, self.cvJointLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        cmds.parent(self.cvJointLoc, self.moduleGrp)
        # Edit GUIDE:
        cmds.setAttr(self.moduleGrp+".rx", -90)
        cmds.setAttr(self.moduleGrp+".ry", -90)
        cmds.setAttr(self.moduleGrp+"_RadiusCtrl.tx", 4)
        self.changeJointNumber(3)


    def changeJointNumber(self, enteredNJoints, *args):
        """ Edit the number of joints in the guide.
        """
        self.utils.useDefaultRenderLayer()
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
                self.cvEndJoint = self.guideName+"_JointEnd"
                if self.currentNJoints > 1:
                    # delete current point constraints:
                    for n in range(2, self.currentNJoints):
                        cmds.delete(self.guideName+"_PaC"+str(n))
                # verify if the nJoints is greather or less than the current
                if self.enteredNJoints > self.currentNJoints:
                    # add the new cvLocators:
                    for n in range(self.currentNJoints+1, self.enteredNJoints+1):
                        # create another N cvLocator:
                        self.cvLocator = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointLoc"+str(n), r=0.3, d=1, guide=True)
                        # set its nJoint value as n:
                        cmds.setAttr(self.cvLocator+".nJoint", n)
                        # parent its group to the first cvJointLocator:
                        self.cvLocGrp = cmds.group(self.cvLocator, name=self.cvLocator+"_Grp")
                        cmds.parent(self.cvLocGrp, self.guideName+"_JointLoc"+str(n-1), relative=True)
                        cmds.setAttr(self.cvLocGrp+".translateZ", 2)
                        if n > 2:
                            cmds.parent(self.cvLocGrp, self.guideName+"_JointLoc1", absolute=True)
                elif self.enteredNJoints < self.currentNJoints:
                    # re-parent cvEndJoint:
                    self.cvLocator = self.guideName+"_JointLoc" + str(self.enteredNJoints)
                    cmds.parent(self.cvEndJoint, world=True)
                    # delete difference of nJoints:
                    for n in range(self.enteredNJoints, self.currentNJoints):
                        # re-parent the children guides:
                        childrenGuideBellowList = self.utils.getGuideChildrenList(self.guideName+"_JointLoc"+str(n+1)+"_Grp")
                        if childrenGuideBellowList:
                            for childGuide in childrenGuideBellowList:
                                cmds.parent(childGuide, self.cvLocator)
                        cmds.delete(self.guideName+"_JointLoc"+str(n+1)+"_Grp")
                # re-parent cvEndJoint:
                cmds.parent(self.cvEndJoint, self.cvLocator)
                cmds.setAttr(self.cvEndJoint+".tz", 1.3)
                cmds.setAttr(self.cvEndJoint+".visibility", 0)
                # re-create parentConstraints:
                if self.enteredNJoints > 1:
                    for n in range(2, self.enteredNJoints):
                        self.parentConst = cmds.parentConstraint(self.guideName+"_JointLoc1", self.cvEndJoint, self.guideName+"_JointLoc"+str(n)+"_Grp", name=self.guideName+"_PaC"+str(n), maintainOffset=True)[0]
                        nParentValue = (n-1) / float(self.enteredNJoints-1)
                        cmds.setAttr(self.parentConst+".Guide_JointLoc1W0", 1-nParentValue)
                        cmds.setAttr(self.parentConst+".Guide_JointEndW1", nParentValue)
                        self.ctrls.setLockHide([self.guideName+"_JointLoc"+ str(n)], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
                # actualise the nJoints in the moduleGrp:
                cmds.setAttr(self.moduleGrp+".nJoints", self.enteredNJoints)
                self.currentNJoints = self.enteredNJoints
                # re-build the preview mirror:
                dpLayoutClass.LayoutClass.createPreviewMirror(self)
            cmds.select(self.moduleGrp)
        else:
            self.changeJointNumber(3)


    def rigModule(self, *args):
        dpBaseClass.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            self.currentStyle = cmds.getAttr(self.moduleGrp+".style")
            # start as no having mirror:
            sideList = [""]
            # analisys the mirror module:
            self.mirrorAxis = cmds.getAttr(self.moduleGrp+".mirrorAxis")
            if self.mirrorAxis != 'off':
                # get rigs names:
                self.mirrorNames = cmds.getAttr(self.moduleGrp+".mirrorName")
                # get first and last letters to use as side initials (prefix):
                sideList = [self.mirrorNames[0]+'_', self.mirrorNames[len(self.mirrorNames)-1]+'_']
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
                        for axis in self.mirrorAxis:
                            cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.scale' + axis, -1)
                # joint labelling:
                jointLabelAdd = 1
            else:  # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_Guide_Base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(self.userGuideName+'_Guide_Base', name="Guide_Base_Grp", relative=True)
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
                # joint labelling:
                jointLabelAdd = 0
            # store the number of this guide by module type
            dpAR_count = self.utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # naming main controls:
            hipsName  = self.dpUIinst.lang['c100_bottom']
            chestName = self.dpUIinst.lang['c099_top']
            baseName = self.dpUIinst.lang['c106_base']
            endName = self.dpUIinst.lang['c120_tip']
            if self.currentStyle == 1: #Biped
                hipsName  = self.dpUIinst.lang['c027_hips']
                chestName = self.dpUIinst.lang['c028_chest']
            # run for all sides
            for s, side in enumerate(sideList):
                attrNameLower = self.utils.getAttrNameLower(side, self.userGuideName)
                self.base = side+self.userGuideName+'_Guide_Base'
                self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"
                # get the number of joints to be created:
                self.nJoints = cmds.getAttr(self.base+".nJoints")
                # create controls:
                self.hipsACtrl = self.ctrls.cvControl("id_041_SpineHipsA", ctrlName=side+self.userGuideName+"_"+hipsName+"A_Ctrl", r=self.ctrlRadius, d=self.curveDegree)
                self.chestACtrl = self.ctrls.cvControl("id_044_SpineChestA", ctrlName=side+self.userGuideName+"_"+chestName+"A_Ctrl", r=self.ctrlRadius, d=self.curveDegree)
                # create start and end Fk controls:
                self.hipsFkCtrl = self.ctrls.cvControl("id_067_SpineFk", ctrlName=side+self.userGuideName+"_"+hipsName+"A_Fk_Ctrl", r=self.ctrlRadius, d=self.curveDegree, dir="+Z")
                self.chestFkCtrl = self.ctrls.cvControl("id_067_SpineFk", ctrlName=side+self.userGuideName+"_"+chestName+"A_Fk_Ctrl", r=self.ctrlRadius, d=self.curveDegree, dir="+Z")
                # optimize controls CV shapes:
                tempHipsACluster = cmds.cluster(self.hipsACtrl)[1]
                cmds.setAttr(tempHipsACluster+".scaleY", 0.25)
                cmds.delete(self.hipsACtrl, constructionHistory=True)
                tempChestACluster = cmds.cluster(self.chestACtrl)[1]
                cmds.setAttr(tempChestACluster+".scaleY", 0.4)
                cmds.delete(self.chestACtrl, constructionHistory=True)
                hipsFkCtrlCVPos = -0.4*self.ctrlRadius
                if self.currentStyle == 1:
                    hipsFkCtrlCVPos = 0.4*self.ctrlRadius
                cmds.move(0, hipsFkCtrlCVPos, 0, self.hipsFkCtrl+"0Shape.cv[0:5]", relative=True, worldSpace=True, worldSpaceDistance=True)
                
                self.hipsBCtrl = self.ctrls.cvControl("id_042_SpineHipsB", side+self.userGuideName+"_"+hipsName+"B_Ctrl", r=self.ctrlRadius, d=self.curveDegree, dir="+X")
                self.chestBCtrl = self.ctrls.cvControl("id_045_SpineChestB", side+self.userGuideName+"_"+chestName+"B_Ctrl", r=self.ctrlRadius, d=self.curveDegree, dir="+X")
                cmds.addAttr(self.hipsACtrl, longName=attrNameLower+'_'+self.dpUIinst.lang['c031_volumeVariation'], attributeType="float", defaultValue=1, keyable=True)
                cmds.addAttr(self.hipsACtrl, longName=attrNameLower+'Active_'+self.dpUIinst.lang['c031_volumeVariation'], attributeType="float", defaultValue=1, keyable=True)
                cmds.addAttr(self.hipsACtrl, longName=attrNameLower+'_masterScale_'+self.dpUIinst.lang['c031_volumeVariation'], attributeType="float", defaultValue=1, keyable=True)
                cmds.addAttr(self.hipsACtrl, longName=attrNameLower+'Fk_ikFkBlend', attributeType="float", min=0, max=1, defaultValue=1, keyable=True)
                self.aHipsAList.append(self.hipsACtrl)
                self.aVolVariationAttrList.append(attrNameLower+'_'+self.dpUIinst.lang['c031_volumeVariation'])
                self.aActVolVariationAttrList.append(attrNameLower+'Active_'+self.dpUIinst.lang['c031_volumeVariation'])
                self.aMScaleVolVariationAttrList.append(attrNameLower+'_masterScale_'+self.dpUIinst.lang['c031_volumeVariation'])
                self.aIkFkBlendAttrList.append(attrNameLower+'Fk_ikFkBlend')
                
                # base and end controls:
                self.baseCtrl = self.ctrls.cvControl("id_089_SpineBase", side+self.userGuideName+"_"+baseName+"_Ctrl", r=0.75*self.ctrlRadius, d=self.curveDegree, dir="+X")
                self.tipCtrl = self.ctrls.cvControl("id_090_SpineTip", side+self.userGuideName+"_"+endName+"_Ctrl", r=0.75*self.ctrlRadius, d=self.curveDegree, dir="+X")
                self.tipList.append(self.tipCtrl)
                
                # Setup axis order
                if self.rigType == dpBaseClass.RigType.quadruped:
                    cmds.setAttr(self.hipsACtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.hipsBCtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.chestACtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.chestBCtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.hipsFkCtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.chestFkCtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.baseCtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.tipCtrl + ".rotateOrder", 1)
                    cmds.rotate(90, 0, 0, self.hipsACtrl, self.hipsBCtrl, self.chestACtrl, self.chestBCtrl, self.hipsFkCtrl, self.chestFkCtrl, self.baseCtrl, self.tipCtrl)
                    cmds.makeIdentity(self.hipsACtrl, self.hipsBCtrl, self.chestACtrl, self.chestBCtrl, self.hipsFkCtrl, self.chestFkCtrl, self.baseCtrl, self.tipCtrl, apply=True, rotate=True)
                else:
                    cmds.setAttr(self.hipsACtrl + ".rotateOrder", 3)
                    cmds.setAttr(self.hipsBCtrl + ".rotateOrder", 3)
                    cmds.setAttr(self.chestACtrl + ".rotateOrder", 3)
                    cmds.setAttr(self.chestBCtrl + ".rotateOrder", 3)
                    cmds.setAttr(self.hipsFkCtrl + ".rotateOrder", 3)
                    cmds.setAttr(self.chestFkCtrl + ".rotateOrder", 3)
                    cmds.setAttr(self.baseCtrl + ".rotateOrder", 3)
                    cmds.setAttr(self.tipCtrl + ".rotateOrder", 3)
                
                # Keep a list of ctrls we want to colorize a certain way
                self.aInnerCtrls.append([self.hipsBCtrl, self.chestBCtrl])
                self.aOuterCtrls.append([self.hipsACtrl, self.chestACtrl, self.hipsFkCtrl, self.chestFkCtrl])
                
                # organize hierarchy:
                cmds.parent(self.hipsBCtrl, self.hipsACtrl)
                cmds.parent(self.chestBCtrl, self.chestACtrl)
                cmds.parent(self.hipsFkCtrl, self.hipsACtrl)
                cmds.parent(self.chestFkCtrl, self.chestACtrl)
                cmds.parent(self.baseCtrl, self.hipsBCtrl, relative=True)
                cmds.parent(self.tipCtrl, self.chestBCtrl, relative=True)
                if self.currentStyle == 0: #default
                    cmds.rotate(-90, 0, 0, self.hipsACtrl, self.chestACtrl)
                    cmds.makeIdentity(self.hipsACtrl, self.chestACtrl, apply=True, rotate=True)
                # position of controls:
                bottomLocGuide = side+self.userGuideName+"_Guide_JointLoc1"
                topLocGuide = side+self.userGuideName+"_Guide_JointLoc"+str(self.nJoints)
                # snap controls to guideLocators:
                cmds.delete(cmds.parentConstraint(bottomLocGuide, self.hipsACtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(topLocGuide, self.chestACtrl, maintainOffset=False))
                
                # change axis orientation for biped style
                if self.currentStyle == 1: #biped
                    cmds.rotate(0, 0, 0, self.hipsACtrl, self.chestACtrl)
                    cmds.makeIdentity(self.hipsACtrl, self.chestACtrl, apply=True, rotate=True)
                cmds.parent(self.chestACtrl, self.hipsACtrl)
                
                # zeroOut transformations:
                self.hipsACtrlZero, self.chestAZero, self.chestBGrp, self.hipsFkCtrlZero, self.chestFkCtrlZero = self.utils.zeroOut([self.hipsACtrl, self.chestACtrl, self.chestBCtrl, self.hipsFkCtrl, self.chestFkCtrl])
                self.chestBGrp = cmds.rename(self.chestBGrp, self.chestBGrp.replace("Zero", "Grp"))
                self.chestBZero = self.utils.zeroOut([self.chestBGrp])[0]
                self.baseCtrlZero = self.utils.zeroOut([self.baseCtrl])[0]
                self.tipCtrlZero = self.utils.zeroOut([self.tipCtrl])[0]
                self.ctrls.setLockHide([self.hipsACtrl, self.hipsBCtrl, self.chestACtrl, self.chestBCtrl, self.hipsFkCtrl, self.chestFkCtrl], ['v'], l=False)
                # modify the pivots of chest controls:
                upPivotPos = cmds.xform(side+self.userGuideName+"_Guide_JointLoc"+str(self.nJoints-1), query=True, worldSpace=True, translation=True)
                cmds.move(upPivotPos[0], upPivotPos[1], upPivotPos[2], self.chestACtrl+".scalePivot", self.chestACtrl+".rotatePivot")
                
                # add originedFrom attributes to hipsA, hipsB and chestB:
                self.utils.originedFrom(objName=self.hipsACtrl, attrString=self.base+";"+self.radiusGuide)
                self.utils.originedFrom(objName=self.baseCtrl, attrString=bottomLocGuide)
                self.utils.originedFrom(objName=self.tipCtrl, attrString=topLocGuide)

                # create base and end joints:
                cmds.select(clear=True)
                baseJnt = cmds.joint(name=side+self.userGuideName+"_00_"+self.dpUIinst.lang['c106_base']+"_Jnt", scaleCompensate=False)
                cmds.addAttr(baseJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.select(clear=True)
                tipJnt = cmds.joint(name=side+self.userGuideName+"_"+str(self.nJoints+1).zfill(2)+"_"+self.dpUIinst.lang['c120_tip']+"_Jnt", scaleCompensate=False)
                cmds.addAttr(tipJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                self.utils.setJointLabel(baseJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c106_base'])
                self.utils.setJointLabel(tipJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c120_tip'])
                # Base and end controllers:
                cmds.parentConstraint(self.baseCtrl, baseJnt, maintainOffset=False, name=baseJnt+"_PaC")
                cmds.scaleConstraint(self.baseCtrl, baseJnt, maintainOffset=True, name=baseJnt+"_ScC")
                cmds.parentConstraint(self.tipCtrl, tipJnt, maintainOffset=False, name=tipJnt+"_PaC")
                cmds.scaleConstraint(self.tipCtrl, tipJnt, maintainOffset=True, name=tipJnt+"_ScC")

                # create a simple spine ribbon:
                returnedRibbonList = self.ctrls.createSimpleRibbon(name=side+self.userGuideName, totalJoints=(self.nJoints-1), jointLabelNumber=(s+jointLabelAdd), jointLabelName=self.userGuideName)
                rbnNurbsPlane = returnedRibbonList[0]
                rbnNurbsPlaneShape = returnedRibbonList[1]
                rbnJointGrpList = returnedRibbonList[2]
                self.aRbnJointList = returnedRibbonList[3]
                # position of ribbon nurbs plane:
                cmds.setAttr(rbnNurbsPlane+".tz", -4)
                cmds.move(0, 0, 0, rbnNurbsPlane+".scalePivot", rbnNurbsPlane+".rotatePivot")
                cmds.rotate(90, 90, 0, rbnNurbsPlane)
                cmds.makeIdentity(rbnNurbsPlane, apply=True, translate=True, rotate=True)
                downLocPos = cmds.xform(side+self.userGuideName+"_Guide_JointLoc1", query=True, worldSpace=True, translation=True)
                upLocPos = cmds.xform(side+self.userGuideName+"_Guide_JointLoc"+str(self.nJoints), query=True, worldSpace=True, translation=True)
                cmds.move(downLocPos[0], downLocPos[1], downLocPos[2], rbnNurbsPlane)
                # create up and down clusters:
                downCluster = cmds.cluster(rbnNurbsPlane+".cv[0:3][0:1]", name=side+self.userGuideName+'_Down_Cls')[1]
                upCluster = cmds.cluster(rbnNurbsPlane+".cv[0:3]["+str(self.nJoints)+":"+str(self.nJoints+1)+"]", name=side+self.userGuideName+'_Up_Cls')[1]
                # get positions of joints from ribbon nurbs plane:
                startRbnJointPos = cmds.xform(side+self.userGuideName+"_01_Jnt", query=True, worldSpace=True, translation=True)
                endRbnJointPos = cmds.xform(side+self.userGuideName+"_%02d_Jnt"%(self.nJoints), query=True, worldSpace=True, translation=True)
                # move pivots of clusters to start and end positions:
                cmds.move(startRbnJointPos[0], startRbnJointPos[1], startRbnJointPos[2], downCluster+".scalePivot", downCluster+".rotatePivot")
                cmds.move(endRbnJointPos[0], endRbnJointPos[1], endRbnJointPos[2], upCluster+".scalePivot", upCluster+".rotatePivot")
                # snap clusters to guideLocators:
                tempDel = cmds.parentConstraint(bottomLocGuide, downCluster, maintainOffset=False)
                cmds.delete(tempDel)
                tempDel = cmds.parentConstraint(topLocGuide, upCluster, maintainOffset=False)
                cmds.delete(tempDel)
                # rotate clusters to compensate guide:
                upClusterRot = cmds.xform(upCluster, query=True, worldSpace=True, rotation=True)
                downClusterRot = cmds.xform(downCluster, query=True, worldSpace=True, rotation=True)
                cmds.xform(upCluster, worldSpace=True, rotation=(upClusterRot[0]+90, upClusterRot[1], upClusterRot[2]))
                cmds.xform(downCluster, worldSpace=True, rotation=(downClusterRot[0]+90, downClusterRot[1], downClusterRot[2]))
                # scaleY of the clusters in order to avoid great extremity deforms:
                rbnHeight = self.utils.distanceBet(side+self.userGuideName+"_Guide_JointLoc"+str(self.nJoints), side+self.userGuideName+"_Guide_JointLoc1", keep=False)[0]
                cmds.setAttr(upCluster+".sy", rbnHeight / 10)
                cmds.setAttr(downCluster+".sy", rbnHeight / 10)
                # parent clusters in controls (up and down):
                cmds.parentConstraint(self.hipsBCtrl, downCluster, maintainOffset=True, name=downCluster+"_PaC")
                cmds.parentConstraint(self.chestBCtrl, upCluster, maintainOffset=True, name=upCluster+"_PaC")
                # organize a group of clusters:
                self.toScalableHookGrp = cmds.group(name=side+self.userGuideName+"_Scalable_Grp", empty=True)
                self.aClusterGrp.append(self.toScalableHookGrp)
                if hideJoints:
                    cmds.setAttr(self.toScalableHookGrp+".visibility", 0)
                cmds.parent(downCluster, upCluster, self.toScalableHookGrp, relative=True)
                # make ribbon joints groups scalable:
                middleScaleYMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_MiddleScaleY_MD")
                cmds.setAttr(middleScaleYMD+".operation", 2)
                cmds.setAttr(middleScaleYMD+".input1X", 1)
                for r, rbnJntGrp in enumerate(rbnJointGrpList):
                    if ((r > 0) and (r < (len(rbnJointGrpList) - 1))):
                        scaleGrp = cmds.group(rbnJntGrp, name=rbnJntGrp.replace("_Grp", "_Scale_Grp"))
                        self.ctrls.directConnect(scaleGrp, rbnJntGrp, ['sx', 'sy', 'sz'])
                        cmds.scaleConstraint(self.toScalableHookGrp, scaleGrp, maintainOffset=True, name=rbnJntGrp+"_ScC")
                        cmds.connectAttr(middleScaleYMD+".outputX", self.aRbnJointList[r]+".scaleY", force=True)
                    else:
                        cmds.scaleConstraint(self.toScalableHookGrp, rbnJntGrp, maintainOffset=True, name=rbnJntGrp+"_ScC")
                if scaleGrp:
                    cmds.connectAttr(scaleGrp+".scaleY", middleScaleYMD+".input2X", force=True)
                # calculate the distance to volumeVariation:
                arcLenShape = cmds.createNode('arcLengthDimension', name=side+self.userGuideName+"_Rbn_ArcLenShape")
                arcLenFather = cmds.listRelatives(arcLenShape, parent=True)[0]
                arcLen = cmds.rename(arcLenFather, side+self.userGuideName+"_Rbn_ArcLen")
                arcLenShape = cmds.listRelatives(arcLen, children=True, shapes=True)[0]
                cmds.setAttr(arcLen+'.visibility', 0)
                # connect nurbsPlaneShape to arcLength node:
                cmds.connectAttr(rbnNurbsPlaneShape+'.worldSpace[0]', arcLenShape+'.nurbsGeometry')
                cmds.setAttr(arcLenShape+'.vParamValue', 1)
                # avoid undesired squash if rotateZ the nurbsPlane:
                cmds.setAttr(arcLenShape+'.uParamValue', 0.5)
                arcLenValue = cmds.getAttr(arcLenShape+'.arcLengthInV')
                # create a multiplyDivide to output the squashStretch values:
                rbnMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_Rbn_MD")
                cmds.connectAttr(arcLenShape+'.arcLengthInV', rbnMD+'.input2X')
                cmds.setAttr(rbnMD+'.input1X', arcLenValue)
                cmds.setAttr(rbnMD+'.operation', 2)
                # create a blendColor, a condition and a multiplyDivide in order to get the correct result value of volumeVariation:
                rbnBlendColors = cmds.createNode('blendColors', name=side+self.userGuideName+"_Rbn_BC")
                cmds.connectAttr(self.hipsACtrl+'.'+attrNameLower+'_'+self.dpUIinst.lang['c031_volumeVariation'], rbnBlendColors+'.blender')
                rbnCond = cmds.createNode('condition', name=side+self.userGuideName+'_Rbn_Cond')
                cmds.connectAttr(self.hipsACtrl+'.'+attrNameLower+'Active_'+self.dpUIinst.lang['c031_volumeVariation'], rbnCond+'.firstTerm')
                cmds.connectAttr(rbnBlendColors+'.outputR', rbnCond+'.colorIfTrueR')
                cmds.connectAttr(rbnMD+'.outputX', rbnBlendColors+'.color1R')
                rbnVVMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_Rbn_VV_MD")
                cmds.connectAttr(self.hipsACtrl+'.'+attrNameLower+'_masterScale_'+self.dpUIinst.lang['c031_volumeVariation'], rbnVVMD+'.input2X')
                cmds.connectAttr(rbnVVMD+'.outputX', rbnCond+'.colorIfFalseR')
                cmds.setAttr(rbnVVMD+'.operation', 2)
                cmds.setAttr(rbnBlendColors+'.color2R', 1)
                cmds.setAttr(rbnCond+".secondTerm", 1)
                # middle ribbon setup:
                for n in range(1, self.nJoints - 1):
                    if self.currentStyle == 0: #default
                        self.middleCtrl = self.ctrls.cvControl("id_043_SpineMiddle", side+self.userGuideName+"_"+self.dpUIinst.lang['c029_middle']+str(n)+"_Ctrl", r=self.ctrlRadius, d=self.curveDegree)
                        self.middleFkCtrl = self.ctrls.cvControl("id_067_SpineFk", side+self.userGuideName+"_"+self.dpUIinst.lang['c029_middle']+str(n)+"_Fk_Ctrl", r=self.ctrlRadius, d=self.curveDegree)
                        cmds.setAttr(self.middleCtrl+".rotateOrder", 4)
                        cmds.setAttr(self.middleFkCtrl+".rotateOrder", 4)
                        cmds.rotate(0, 0, 90, self.middleCtrl, self.middleFkCtrl)
                        cmds.makeIdentity(self.middleCtrl, self.middleFkCtrl, apply=True, rotate=True)
                    else: #biped
                        self.middleCtrl = self.ctrls.cvControl("id_043_SpineMiddle", side+self.userGuideName+"_"+self.dpUIinst.lang['c029_middle']+str(n)+"_Ctrl", r=self.ctrlRadius, d=self.curveDegree, dir="+X")
                        self.middleFkCtrl = self.ctrls.cvControl("id_067_SpineFk", side+self.userGuideName+"_"+self.dpUIinst.lang['c029_middle']+str(n)+"_Fk_Ctrl", r=self.ctrlRadius, d=self.curveDegree, dir="+X")
                        cmds.setAttr(self.middleCtrl+".rotateOrder", 3)
                        cmds.setAttr(self.middleFkCtrl+".rotateOrder", 3)
                    self.aInnerCtrls[s].append(self.middleCtrl)
                    self.aOuterCtrls[s].append(self.middleFkCtrl)
                    self.ctrls.setLockHide([self.middleCtrl, self.middleFkCtrl], ['sx', 'sy', 'sz'])
                    cmds.setAttr(self.middleCtrl+'.visibility', keyable=False)
                    cmds.setAttr(self.middleFkCtrl+'.visibility', keyable=False)
                    cmds.parent(self.middleCtrl, self.hipsACtrl)
                    middleLocGuide = side+self.userGuideName+"_Guide_JointLoc"+str(n + 1)
                    cmds.delete(cmds.parentConstraint(middleLocGuide, self.middleCtrl, maintainOffset=False))
                    cmds.delete(cmds.parentConstraint(middleLocGuide, self.middleFkCtrl, maintainOffset=False))
                    if self.currentStyle == 1: #biped
                        cmds.rotate(0, 0, 0, self.middleCtrl, self.middleFkCtrl)
                    if self.rigType == dpBaseClass.RigType.quadruped:
                        cmds.rotate(90, 0, 0, self.middleCtrl, self.middleFkCtrl)
                        cmds.makeIdentity(self.middleCtrl, self.middleFkCtrl, apply=True, rotate=True)
                    self.middleCtrlGrp = self.utils.zeroOut([self.middleCtrl])[0]
                    self.middleCtrlGrp = cmds.rename(self.middleCtrlGrp, self.middleCtrlGrp.replace("Zero", "Grp"))
                    self.middleCtrlZero = self.utils.zeroOut([self.middleCtrlGrp])[0]
                    self.middleFkCtrlZero = self.utils.zeroOut([self.middleFkCtrl])[0]
                    middleCluster = cmds.cluster(rbnNurbsPlane+".cv[0:3]["+str(n+1)+"]", name=side+self.userGuideName+'_Middle_Cls')[1]
                    middleLocPos = cmds.xform(side+self.userGuideName+"_Guide_JointLoc"+str(n), query=True, worldSpace=True, translation=True)
                    tempDel = cmds.parentConstraint(middleLocGuide, middleCluster, maintainOffset=False)
                    cmds.delete(tempDel)
                    middleClusterRot = cmds.xform(middleCluster, query=True, worldSpace=True, rotation=True)
                    cmds.xform(middleCluster, worldSpace=True, rotation=(middleClusterRot[0]+90, middleClusterRot[1], middleClusterRot[2]))
                    cmds.parentConstraint(self.middleCtrl, middleCluster, maintainOffset=True, name=middleCluster+"_PaC")
                    # parenting constraints like guide locators:
                    self.parentConst = cmds.parentConstraint(self.hipsBCtrl, self.chestBCtrl, self.middleCtrlZero, name=self.middleCtrl+"_PaC", maintainOffset=True)[0]
                    nParentValue = (n) / float(self.nJoints-1)
                    cmds.setAttr(self.parentConst+"."+self.hipsBCtrl+"W0", 1-nParentValue)
                    cmds.setAttr(self.parentConst+"."+self.chestBCtrl+"W1", nParentValue)
                    cmds.parent(middleCluster, self.toScalableHookGrp, relative=True)
                    # add originedFrom attribute to this middle ctrl:
                    middleOrigGrp = cmds.group(empty=True, name=side+self.userGuideName+"_"+self.dpUIinst.lang['c029_middle']+str(n)+"_OrigFrom_Grp")
                    self.utils.originedFrom(objName=middleOrigGrp, attrString=middleLocGuide)
                    cmds.parentConstraint(self.aRbnJointList[n], middleOrigGrp, maintainOffset=False, name=middleOrigGrp+"_PaC")
                    cmds.parent(middleOrigGrp, self.hipsACtrl)
                    # apply volumeVariation to joints in the middle ribbon setup:
                    cmds.connectAttr(rbnCond+'.outColorR', self.aRbnJointList[n]+'.scaleX')
                    cmds.connectAttr(rbnCond+'.outColorR', self.aRbnJointList[n]+'.scaleZ')
                    # create intensity attribute to drive joint with more force in horizontal:
                    cmds.addAttr(self.middleCtrl, longName=self.dpUIinst.lang['c049_intensity'], attributeType="float", min=0, max=1, defaultValue=0, keyable=True)
                    cmds.addAttr(self.middleFkCtrl, longName=self.dpUIinst.lang['c049_intensity'], attributeType="float", min=0, max=1, defaultValue=0, keyable=True)
                    jointFather = cmds.listRelatives(self.aRbnJointList[n], allParents=True)[0]
                    intRevNode = cmds.createNode("reverse", name=side+self.userGuideName+"_"+self.dpUIinst.lang['c029_middle']+str(n)+"_"+self.dpUIinst.lang['c049_intensity'].capitalize()+"_Rev")
                    middleIntBC = cmds.createNode("blendColors", name=side+self.userGuideName+"_"+self.dpUIinst.lang['c029_middle']+str(n)+"_"+self.dpUIinst.lang['c049_intensity'].capitalize()+"_BC")
                    middleIntPC = cmds.parentConstraint(self.middleCtrl, jointFather, self.aRbnJointList[n], maintainOffset=True, name=self.aRbnJointList[n]+"_"+self.dpUIinst.lang['c049_intensity'].capitalize()+"_PaC")[0]
                    cmds.connectAttr(self.middleFkCtrl+"."+self.dpUIinst.lang['c049_intensity'], middleIntBC+".color1R", force=True)
                    cmds.connectAttr(self.middleCtrl+"."+self.dpUIinst.lang['c049_intensity'], middleIntBC+".color2R", force=True)
                    cmds.connectAttr(self.hipsACtrl+'.'+attrNameLower+'Fk_ikFkBlend', middleIntBC+".blender", force=True)
                    cmds.connectAttr(middleIntBC+".outputR", middleIntPC+"."+self.middleCtrl+"W0", force=True)
                    cmds.connectAttr(self.middleCtrl+"."+self.dpUIinst.lang['c049_intensity'], intRevNode+".inputX", force=True)
                    cmds.connectAttr(intRevNode+".outputX", middleIntPC+"."+jointFather+"W1", force=True)
                    # fk middle control hierarchy:
                    if n == 1: #first middle
                        cmds.parent(self.middleFkCtrlZero, self.hipsFkCtrl)
                    else:
                        cmds.parent(self.middleFkCtrlZero, side+self.userGuideName+"_"+self.dpUIinst.lang['c029_middle']+str(n-1)+"_Fk_Ctrl")
                    # build fk setup:
                    self.middleCtrlGrpPC = cmds.parentConstraint(self.middleCtrlZero, self.middleFkCtrl, self.middleCtrlGrp, maintainOffset=True, name=self.middleCtrlGrp+"_IkFkBlend_PaC")[0]
                    if n == 1:
                        self.revNode = cmds.createNode('reverse', name=side+self.userGuideName+"_IkFkBlend_Rev")
                        cmds.connectAttr(self.hipsACtrl+'.'+attrNameLower+'Fk_ikFkBlend', self.revNode+".inputX", force=True)
                    # connecting ikFkBlend using the reverse node:
                    cmds.connectAttr(self.hipsACtrl+'.'+attrNameLower+'Fk_ikFkBlend', self.middleCtrlGrpPC+"."+self.middleFkCtrl+"W1", force=True)
                    cmds.connectAttr(self.revNode+'.outputX', self.middleCtrlGrpPC+"."+self.middleCtrlZero+"W0", force=True)
                    # ikFkBlend visibility:
                    cmds.connectAttr(self.revNode+'.outputX', self.middleCtrlZero+".visibility", force=True)
                
                # finishing ikFkBlend:
                chestACtrlShape = cmds.listRelatives(self.chestACtrl, children=True, type="shape")[0]
                chestBCtrlShape = cmds.listRelatives(self.chestBCtrl, children=True, type="shape")[0]
                cmds.parent(self.chestFkCtrlZero, self.middleFkCtrl)
                self.chestCtrlGrpPC = cmds.parentConstraint(self.chestBZero, self.chestFkCtrl, self.chestBGrp, maintainOffset=True, name=self.chestBGrp+"_IkFkBlend_PaC")[0]
                cmds.connectAttr(self.hipsACtrl+'.'+attrNameLower+'Fk_ikFkBlend', self.chestCtrlGrpPC+"."+self.chestFkCtrl+"W1", force=True)
                cmds.connectAttr(self.revNode+'.outputX', self.chestCtrlGrpPC+"."+self.chestBZero+"W0", force=True)
                cmds.connectAttr(self.revNode+'.outputX', chestACtrlShape+".visibility", force=True)
                cmds.connectAttr(self.revNode+'.outputX', chestBCtrlShape+".visibility", force=True)
                cmds.connectAttr(self.hipsACtrl+'.'+attrNameLower+'Fk_ikFkBlend', self.hipsFkCtrlZero+".visibility", force=True)
                cmds.connectAttr(self.hipsACtrl+'.'+attrNameLower+'Fk_ikFkBlend', self.chestFkCtrlZero+".visibility", force=True)
                
                # update spine volume variation setup
                currentVV = cmds.getAttr(rbnMD+'.outputX')
                cmds.setAttr(rbnVVMD+'.input1X', currentVV)
                # organize groups:
                self.toStaticHookGrp = cmds.group(name=side+self.userGuideName+"_Static_Grp", empty=True)
                self.toCtrlHookGrp = cmds.group(name=side+self.userGuideName+"_Control_Grp", empty=True)
                cmds.parent(self.hipsACtrlZero, self.toCtrlHookGrp, relative=True)
                cmds.parent(self.toScalableHookGrp, side+self.userGuideName+"_Rbn_RibbonJoint_Grp", self.toCtrlHookGrp, arcLen, self.toStaticHookGrp, relative=True)
                cmds.parent(baseJnt, tipJnt, self.toStaticHookGrp)
                if hideJoints:
                    cmds.setAttr(side+self.userGuideName+"_Rbn_RibbonJoint_Grp.visibility", 0)
                # add hook attributes to be read when rigging integrated modules:
                self.utils.addHook(objName=self.toCtrlHookGrp, hookType='ctrlHook')
                self.utils.addHook(objName=self.toScalableHookGrp, hookType='scalableHook')
                self.utils.addHook(objName=self.toStaticHookGrp, hookType='staticHook')
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_name", dataType="string")
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_type", dataType="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_name", self.userGuideName, type="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_type", CLASS_NAME, type="string")
                # add module type counter value
                cmds.addAttr(self.toStaticHookGrp, longName='dpAR_count', attributeType='long', keyable=False)
                cmds.setAttr(self.toStaticHookGrp+'.dpAR_count', dpAR_count)
                self.hookSetup()
                # lockHide scale of up and down controls:
                self.ctrls.setLockHide([self.hipsACtrl, self.hipsBCtrl, self.chestACtrl, self.chestBCtrl, self.hipsFkCtrl, self.chestFkCtrl], ['sx', 'sy', 'sz'])
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)
            # finalize this rig:
            self.integratingInfo()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and moduleInstance namespace:
        self.deleteModule()

    def integratingInfo(self, *args):
        dpBaseClass.StartClass.integratingInfo(self)
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.integratedActionsDic = {
            "module": {
                "hipsAList": self.aHipsAList,
                "tipList": self.tipList,
                "volumeVariationAttrList": self.aVolVariationAttrList,
                "ActiveVolumeVariationAttrList": self.aActVolVariationAttrList,
                "MasterScaleVolumeVariationAttrList": self.aMScaleVolVariationAttrList,
                "IkFkBlendAttrList": self.aIkFkBlendAttrList,
                "InnerCtrls": self.aInnerCtrls,
                "OuterCtrls": self.aOuterCtrls,
                "jointList": self.aRbnJointList,
                "scalableGrp": self.aClusterGrp,
            }
        }
