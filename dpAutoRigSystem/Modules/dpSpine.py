# importing libraries:
import maya.cmds as cmds
from Library import dpControls as ctrls
from Library import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout

# global variables to this module:
CLASS_NAME = "Spine"
TITLE = "m011_spine"
DESCRIPTION = "m012_spineDesc"
ICON = "/Icons/dp_spine.png"


class Spine(Base.StartClass, Layout.LayoutClass):
    def __init__(self, *args, **kwargs):
        # Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        Base.StartClass.__init__(self, *args, **kwargs)

        # Declare variable
        self.integratedActionsDic = {}
        self.cvJointLoc = None
        self.shapeSizeCH = None

        # List of returned data:
        self.aHipsAList = []
        self.aChestAList = []
        self.aVolVariationAttrList = []
        self.aActVolVariationAttrList = []
        self.aMScaleVolVariationAttrList = []
        self.aFkCtrl = []
        self.aIkCtrl = []
        self.aRbnJointList = []
        self.aClusterGrp = []

    def createModuleLayout(self, *args):
        Base.StartClass.createModuleLayout(self)
        Layout.LayoutClass.basicModuleLayout(self)
        # Custom MODULE LAYOUT:
        # verify if we are creating or re-loading this module instance:
        firstTime = cmds.getAttr(self.moduleGrp + '.nJoints')
        if firstTime == 1:
            try:
                cmds.intField(self.nJointsIF, edit=True, value=3, minValue=3)
            except:
                pass
            self.changeJointNumber(3)
    
    
    def reCreateEditSelectedModuleLayout(self, bSelect=False, *args):
        Layout.LayoutClass.reCreateEditSelectedModuleLayout(self, bSelect)
        # style layout:
        self.styleLayout = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 50, 50, 70),
                                          columnAlign=[(1, 'right'), (2, 'left'), (3, 'right')], adjustableColumn=4,
                                          columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2),
                                                        (3, 'both', 10)], parent="selectedColumn")
        cmds.text(label=self.langDic[self.langName]['m041_style'], visible=True, parent=self.styleLayout)
        self.styleMenu = cmds.optionMenu("styleMenu", label='', changeCommand=self.changeStyle, parent=self.styleLayout)
        styleMenuItemList = [self.langDic[self.langName]['m042_default'], self.langDic[self.langName]['m026_biped']]
        for item in styleMenuItemList:
            cmds.menuItem(label=item, parent=self.styleMenu)
        # read from guide attribute the current value to style:
        currentStyle = cmds.getAttr(self.moduleGrp + ".style")
        cmds.optionMenu(self.styleMenu, edit=True, select=int(currentStyle + 1))
        
        
    def changeStyle(self, style, *args):
        """ Change the style to be applyed custom actions to be more animator friendly.
            We will optimise: control world orientation
        """
        # for Default style:
        if style == self.langDic[self.langName]['m042_default']:
            cmds.setAttr(self.moduleGrp + ".style", 0)
        # for Biped style:
        if style == self.langDic[self.langName]['m026_biped']:
            cmds.setAttr(self.moduleGrp + ".style", 1)


    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.setAttr(self.moduleGrp + ".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        cmds.addAttr(self.moduleGrp, longName="nJoints", attributeType='long')
        cmds.addAttr(self.moduleGrp, longName="style", attributeType='enum', enumName=self.langDic[self.langName]['m042_default'] + ':' + self.langDic[self.langName]['m026_biped'])
        cmds.setAttr(self.moduleGrp + ".nJoints", 1)
        self.cvJointLoc, shapeSizeCH = ctrls.cvJointLoc(ctrlName=self.guideName + "_JointLoc1", r=0.5)
        self.connectShapeSize(shapeSizeCH)
        self.cvEndJoint, shapeSizeCH = ctrls.cvLocator(ctrlName=self.guideName + "_JointEnd", r=0.1)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvEndJoint, self.cvJointLoc)
        cmds.setAttr(self.cvEndJoint + ".tz", 1.3)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        cmds.parent(self.cvJointLoc, self.moduleGrp)
        # Edit GUIDE:
        cmds.setAttr(self.moduleGrp + ".rx", -90)
        cmds.setAttr(self.moduleGrp + ".ry", -90)
        cmds.setAttr(self.moduleGrp + "_RadiusCtrl.tx", 4)

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
        # get the number of joints existing:
        self.currentNJoints = cmds.getAttr(self.moduleGrp + ".nJoints")
        # start analisys the difference between values:
        if self.enteredNJoints != self.currentNJoints:
            self.cvEndJoint = self.guideName + "_JointEnd"
            if self.currentNJoints > 1:
                # delete current point constraints:
                for n in range(2, self.currentNJoints):
                    cmds.delete(self.guideName + "_ParentConstraint" + str(n))
            # verify if the nJoints is greather or less than the current
            if self.enteredNJoints > self.currentNJoints:
                # add the new cvLocators:
                for n in range(self.currentNJoints + 1, self.enteredNJoints + 1):
                    # create another N cvLocator:
                    self.cvLocator, shapeSizeCH = ctrls.cvLocator(ctrlName=self.guideName + "_JointLoc" + str(n), r=0.3)
                    self.connectShapeSize(shapeSizeCH)
                    # set its nJoint value as n:
                    cmds.setAttr(self.cvLocator + ".nJoint", n)
                    # parent its group to the first cvJointLocator:
                    self.cvLocGrp = cmds.group(self.cvLocator, name=self.cvLocator + "_Grp")
                    cmds.parent(self.cvLocGrp, self.guideName + "_JointLoc" + str(n - 1), relative=True)
                    cmds.setAttr(self.cvLocGrp + ".translateZ", 2)
                    if n > 2:
                        cmds.parent(self.cvLocGrp, self.guideName + "_JointLoc1", absolute=True)
            elif self.enteredNJoints < self.currentNJoints:
                # re-parent cvEndJoint:
                self.cvLocator = self.guideName + "_JointLoc" + str(self.enteredNJoints)
                cmds.parent(self.cvEndJoint, world=True)
                # delete difference of nJoints:
                for n in range(self.enteredNJoints, self.currentNJoints):
                    # re-parent the children guides:
                    childrenGuideBellowList = utils.getGuideChildrenList(
                        self.guideName + "_JointLoc" + str(n + 1) + "_Grp")
                    if childrenGuideBellowList:
                        for childGuide in childrenGuideBellowList:
                            cmds.parent(childGuide, self.cvLocator)
                    cmds.delete(self.guideName + "_JointLoc" + str(n + 1) + "_Grp")
            # re-parent cvEndJoint:
            cmds.parent(self.cvEndJoint, self.cvLocator)
            cmds.setAttr(self.cvEndJoint + ".tz", 1.3)
            cmds.setAttr(self.cvEndJoint + ".visibility", 0)
            # re-create parentConstraints:
            if self.enteredNJoints > 1:
                for n in range(2, self.enteredNJoints):
                    self.parentConst = cmds.parentConstraint(self.guideName + "_JointLoc1",
                                                             self.cvEndJoint,
                                                             self.guideName + "_JointLoc" + str(n) + "_Grp",
                                                             name=self.guideName + "_ParentConstraint" + str(n),
                                                             maintainOffset=True)[0]
                    nParentValue = (n - 1) / float(self.enteredNJoints - 1)
                    cmds.setAttr(self.parentConst + ".Guide_JointLoc1W0", 1 - nParentValue)
                    cmds.setAttr(self.parentConst + ".Guide_JointEndW1", nParentValue)
                    ctrls.setLockHide([self.guideName + "_JointLoc" + str(n)], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
            # actualise the nJoints in the moduleGrp:
            cmds.setAttr(self.moduleGrp + ".nJoints", self.enteredNJoints)
            self.currentNJoints = self.enteredNJoints
            # re-build the preview mirror:
            Layout.LayoutClass.createPreviewMirror(self)
        cmds.select(self.moduleGrp)

    def rigModule(self, *args):
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            self.currentStyle = cmds.getAttr(self.moduleGrp + ".style")
            # start as no having mirror:
            sideList = [""]
            # analisys the mirror module:
            self.mirrorAxis = cmds.getAttr(self.moduleGrp + ".mirrorAxis")
            if self.mirrorAxis != 'off':
                # get rigs names:
                self.mirrorNames = cmds.getAttr(self.moduleGrp + ".mirrorName")
                # get first and last letters to use as side initials (prefix):
                sideList = [self.mirrorNames[0] + '_', self.mirrorNames[len(self.mirrorNames) - 1] + '_']
                for s, side in enumerate(sideList):
                    duplicated = cmds.duplicate(self.moduleGrp, name=side + self.userGuideName + '_Guide_Base')[0]
                    allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                    for item in allGuideList:
                        cmds.rename(item, side + self.userGuideName + "_" + item)
                    self.mirrorGrp = cmds.group(name="Guide_Base_Grp", empty=True)
                    cmds.parent(side + self.userGuideName + '_Guide_Base', self.mirrorGrp, absolute=True)
                    # re-rename grp:
                    cmds.rename(self.mirrorGrp, side + self.userGuideName + '_' + self.mirrorGrp)
                    # do a group mirror with negative scaling:
                    if s == 1:
                        for axis in self.mirrorAxis:
                            cmds.setAttr(side + self.userGuideName + '_' + self.mirrorGrp + '.scale' + axis, -1)
            else:  # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName + '_Guide_Base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName + "_" + item)
                self.mirrorGrp = cmds.group(self.userGuideName + '_Guide_Base', name="Guide_Base_Grp", relative=True)
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName + '_' + self.mirrorGrp)
            # store the number of this guide by module type
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # run for all sides
            for s, side in enumerate(sideList):
                self.base = side + self.userGuideName + '_Guide_Base'
                # get the number of joints to be created:
                self.nJoints = cmds.getAttr(self.base + ".nJoints")
                # create controls:
                self.hipsA = ctrls.cvBox(
                    ctrlName=side + self.userGuideName + "_" + self.langDic[self.langName]['c_hips'] + "A_Ctrl",
                    r=self.ctrlRadius, h=(self.ctrlRadius * 0.25))
                self.hipsB = \
                cmds.circle(name=side + self.userGuideName + "_" + self.langDic[self.langName]['c_hips'] + "B_Ctrl",
                            ch=False, o=True, nr=(0, 1, 0), d=1, s=8, radius=self.ctrlRadius)[0]
                self.chestA = ctrls.cvBox(
                    ctrlName=side + self.userGuideName + "_" + self.langDic[self.langName]['c_chest'] + "A_Ctrl",
                    r=self.ctrlRadius, h=(self.ctrlRadius * 0.25))
                self.chestB = \
                cmds.circle(name=side + self.userGuideName + "_" + self.langDic[self.langName]['c_chest'] + "B_Ctrl",
                            ch=False, o=True, nr=(0, 1, 0), d=1, s=8, radius=self.ctrlRadius)[0]
                cmds.addAttr(self.hipsA, longName=side + self.userGuideName + '_' + self.langDic[self.langName]['c_volumeVariation'], attributeType="float", defaultValue=1, keyable=True)
                cmds.addAttr(self.hipsA, longName=side + self.userGuideName + '_active_' + self.langDic[self.langName]['c_volumeVariation'], attributeType="float", defaultValue=1, keyable=True)
                cmds.addAttr(self.hipsA, longName=side + self.userGuideName + '_masterScale_' + self.langDic[self.langName]['c_volumeVariation'], attributeType="float", defaultValue=1, keyable=True)
                ctrls.setLockHide([self.hipsA, self.hipsB, self.chestA, self.chestB], ['v'], l=False)
                self.aHipsAList.append(self.hipsA)
                self.aChestAList.append(self.chestA)
                self.aVolVariationAttrList.append(side + self.userGuideName + '_' + self.langDic[self.langName]['c_volumeVariation'])
                self.aActVolVariationAttrList.append(side + self.userGuideName + '_active_' + self.langDic[self.langName]['c_volumeVariation'])
                self.aMScaleVolVariationAttrList.append(side + self.userGuideName + '_masterScale_' + self.langDic[self.langName]['c_volumeVariation'])

                # Setup axis order
                if self.rigType == Base.RigType.quadruped:
                    cmds.setAttr(self.hipsA + ".rotateOrder", 1)
                    cmds.setAttr(self.hipsB + ".rotateOrder", 1)
                    cmds.setAttr(self.chestA + ".rotateOrder", 1)
                    cmds.setAttr(self.chestB + ".rotateOrder", 1)
                else:
                    cmds.setAttr(self.hipsA + ".rotateOrder", 3)
                    cmds.setAttr(self.hipsB + ".rotateOrder", 3)
                    cmds.setAttr(self.chestA + ".rotateOrder", 3)
                    cmds.setAttr(self.chestB + ".rotateOrder", 3)

                # Keep a list of ctrls we want to colorize a certain way
                self.aFkCtrl.append([self.hipsB, self.chestB])
                self.aIkCtrl.append([self.hipsA, self.chestA])

                # organize hierarchy:
                cmds.parent(self.hipsB, self.hipsA)
                cmds.parent(self.chestB, self.chestA)
                if self.currentStyle == 0: #default
                    cmds.rotate(-90, 0, 0, self.hipsA, self.chestA)
                    cmds.makeIdentity(self.hipsA, self.chestA, apply=True, rotate=True)
                # position of controls:
                bottomLocGuide = side + self.userGuideName + "_Guide_JointLoc1"
                topLocGuide = side + self.userGuideName + "_Guide_JointLoc" + str(self.nJoints)
                # snap controls to guideLocators:
                cmds.delete(cmds.parentConstraint(bottomLocGuide, self.hipsA, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(topLocGuide, self.chestA, maintainOffset=False))
                
                # change axis orientation for biped stype
                if self.currentStyle == 1: #biped
                    cmds.rotate(0, 0, 0, self.hipsA, self.chestA)
                    cmds.makeIdentity(self.hipsA, self.chestA, apply=True, rotate=True)
                cmds.parent(self.chestA, self.hipsA)
                
                # zeroOut transformations:
                utils.zeroOut([self.hipsA, self.chestA])
                # modify the pivots of chest controls:
                upPivotPos = cmds.xform(side + self.userGuideName + "_Guide_JointLoc" + str(self.nJoints - 1),
                                        query=True, worldSpace=True, translation=True)
                cmds.move(upPivotPos[0], upPivotPos[1], upPivotPos[2], self.chestA + ".scalePivot",
                          self.chestA + ".rotatePivot")  # , self.chestB+".scalePivot", self.chestB+".rotatePivot")
                # add originedFrom attributes to hipsA, hipsB and chestB:
                utils.originedFrom(objName=self.hipsA, attrString=self.base)
                utils.originedFrom(objName=self.hipsB, attrString=bottomLocGuide)
                utils.originedFrom(objName=self.chestB, attrString=topLocGuide)
                # create a simple spine ribbon:
                returnedRibbonList = ctrls.createSimpleRibbon(name=side + self.userGuideName + '_Rbn',
                                                              totalJoints=(self.nJoints - 1))
                rbnNurbsPlane = returnedRibbonList[0]
                rbnNurbsPlaneShape = returnedRibbonList[1]
                rbnJointGrpList = returnedRibbonList[2]
                self.aRbnJointList = returnedRibbonList[3]
                # position of ribbon nurbs plane:
                cmds.setAttr(rbnNurbsPlane + ".tz", -4)
                cmds.move(0, 0, 0, rbnNurbsPlane + ".scalePivot", rbnNurbsPlane + ".rotatePivot")
                cmds.rotate(90, 90, 0, rbnNurbsPlane)
                cmds.makeIdentity(rbnNurbsPlane, apply=True, translate=True, rotate=True)
                downLocPos = cmds.xform(side + self.userGuideName + "_Guide_JointLoc1",
                                        query=True, worldSpace=True, translation=True)
                upLocPos = cmds.xform(side + self.userGuideName + "_Guide_JointLoc" + str(self.nJoints),
                                      query=True, worldSpace=True, translation=True)
                cmds.move(downLocPos[0], downLocPos[1], downLocPos[2], rbnNurbsPlane)
                # create up and down clusters:
                downCluster = \
                cmds.cluster(rbnNurbsPlane + ".cv[0:3][0:1]", name=side + self.userGuideName + '_Down_Cls')[1]
                upCluster = \
                cmds.cluster(rbnNurbsPlane + ".cv[0:3][" + str(self.nJoints) + ":" + str(self.nJoints + 1) + "]",
                             name=side + self.userGuideName + '_Up_Cls')[1]
                # get positions of joints from ribbon nurbs plane:
                startRbnJointPos = cmds.xform(side + self.userGuideName + "_Rbn0_Jnt",
                                              query=True, worldSpace=True, translation=True)
                endRbnJointPos = cmds.xform(side + self.userGuideName + "_Rbn" + str(self.nJoints - 1) + "_Jnt",
                                            query=True, worldSpace=True, translation=True)
                # move pivots of clusters to start and end positions:
                cmds.move(startRbnJointPos[0], startRbnJointPos[1], startRbnJointPos[2],
                          downCluster + ".scalePivot", downCluster + ".rotatePivot")
                cmds.move(endRbnJointPos[0], endRbnJointPos[1], endRbnJointPos[2],
                          upCluster + ".scalePivot", upCluster + ".rotatePivot")
                # snap clusters to guideLocators:
                tempDel = cmds.parentConstraint(bottomLocGuide, downCluster, maintainOffset=False)
                cmds.delete(tempDel)
                tempDel = cmds.parentConstraint(topLocGuide, upCluster, maintainOffset=False)
                cmds.delete(tempDel)
                # rotate clusters to compensate guide:
                upClusterRot = cmds.xform(upCluster, query=True, worldSpace=True, rotation=True)
                downClusterRot = cmds.xform(downCluster, query=True, worldSpace=True, rotation=True)
                cmds.xform(upCluster, worldSpace=True,
                           rotation=(upClusterRot[0] + 90, upClusterRot[1], upClusterRot[2]))
                cmds.xform(downCluster, worldSpace=True,
                           rotation=(downClusterRot[0] + 90, downClusterRot[1], downClusterRot[2]))
                # scaleY of the clusters in order to avoid great extremity deforms:
                rbnHeight = ctrls.distanceBet(side + self.userGuideName + "_Guide_JointLoc" + str(self.nJoints),
                                              side + self.userGuideName + "_Guide_JointLoc1", keep=False)[0]
                cmds.setAttr(upCluster + ".sy", rbnHeight / 10)
                cmds.setAttr(downCluster + ".sy", rbnHeight / 10)
                # parent clusters in controls (up and down):
                cmds.parentConstraint(self.hipsB, downCluster, maintainOffset=True,
                                      name=downCluster + "_ParentConstraint")
                cmds.parentConstraint(self.chestB, upCluster, maintainOffset=True, name=upCluster + "_ParentConstraint")
                # organize a group of clusters:
                clustersGrp = cmds.group(name=side + self.userGuideName + "_Rbn_Clusters_Grp", empty=True)
                self.aClusterGrp.append(clustersGrp)
                if hideJoints:
                    cmds.setAttr(clustersGrp + ".visibility", 0)
                cmds.parent(downCluster, upCluster, clustersGrp, relative=True)
                # make ribbon joints groups scalable:
                for r, rbnJntGrp in enumerate(rbnJointGrpList):
                    if ((r > 0) and (r < (len(rbnJointGrpList) - 1))):
                        scaleGrp = cmds.group(rbnJntGrp, name=rbnJntGrp.replace("_Grp", "_Scale_Grp"))
                        ctrls.directConnect(scaleGrp, rbnJntGrp, ['sx', 'sz'])
                        cmds.scaleConstraint(clustersGrp, scaleGrp, maintainOffset=True, name=rbnJntGrp + "_Scale")
                    else:
                        cmds.scaleConstraint(clustersGrp, rbnJntGrp, maintainOffset=True,
                                             name=rbnJntGrp + "_Scale")
                # calculate the distance to volumeVariation:
                arcLenShape = cmds.createNode('arcLengthDimension', name=side + self.userGuideName + "_Rbn_ArcLenShape")
                arcLenFather = cmds.listRelatives(arcLenShape, parent=True)[0]
                arcLen = cmds.rename(arcLenFather, side + self.userGuideName + "_Rbn_ArcLen")
                arcLenShape = cmds.listRelatives(arcLen, children=True, shapes=True)[0]
                cmds.setAttr(arcLen + '.visibility', 0)
                # connect nurbsPlaneShape to arcLength node:
                cmds.connectAttr(rbnNurbsPlaneShape + '.worldSpace[0]', arcLenShape + '.nurbsGeometry')
                cmds.setAttr(arcLenShape + '.vParamValue', 1)
                # avoid undesired squash if rotateZ the nurbsPlane:
                cmds.setAttr(arcLenShape + '.uParamValue', 0.5)
                arcLenValue = cmds.getAttr(arcLenShape + '.arcLengthInV')
                # create a multiplyDivide to output the squashStretch values:
                rbnMD = cmds.createNode('multiplyDivide', name=side + self.userGuideName + "_Rbn_MD")
                cmds.connectAttr(arcLenShape + '.arcLengthInV', rbnMD + '.input2X')
                cmds.setAttr(rbnMD + '.input1X', arcLenValue)
                cmds.setAttr(rbnMD + '.operation', 2)
                # create a blendColor, a condition and a multiplyDivide in order to get the correct result value of volumeVariation:
                rbnBlendColors = cmds.createNode('blendColors', name=side + self.userGuideName + "_Rbn_BlendColor")
                cmds.connectAttr(self.hipsA + '.' + side + self.userGuideName + '_' + self.langDic[self.langName]['c_volumeVariation'], rbnBlendColors + '.blender')
                rbnCond = cmds.createNode('condition', name=side+self.userGuideName+'_Rbn_Cond')
                cmds.connectAttr(self.hipsA + '.' + side + self.userGuideName + '_active_' + self.langDic[self.langName]['c_volumeVariation'], rbnCond + '.firstTerm')
                cmds.connectAttr(rbnBlendColors+'.outputR', rbnCond + '.colorIfTrueR')
                cmds.connectAttr(rbnMD + '.outputX', rbnBlendColors + '.color1R')
                rbnVVMD = cmds.createNode('multiplyDivide', name=side + self.userGuideName + "_Rbn_VV_MD")
                cmds.connectAttr(self.hipsA + '.' + side + self.userGuideName + '_masterScale_' + self.langDic[self.langName]['c_volumeVariation'], rbnVVMD + '.input2X')
                cmds.connectAttr(rbnVVMD + '.outputX', rbnCond + '.colorIfFalseR')
                cmds.setAttr(rbnVVMD + '.operation', 2)
                cmds.setAttr(rbnBlendColors + '.color2R', 1)
                cmds.setAttr(rbnCond+".secondTerm", 1)
                # middle ribbon setup:
                for n in range(1, self.nJoints - 1):
                    if self.currentStyle == 0: #default
                        self.middle = cmds.circle(name=side + self.userGuideName + "_" + self.langDic[self.langName]['c_middle'] + str(n) + "_Ctrl", ch=False, o=True, nr=(0, 0, 1), d=3, s=8, radius=self.ctrlRadius)[0]
                        cmds.setAttr(self.middle + ".rotateOrder", 4)
                    else: #biped
                        self.middle = cmds.circle(name=side + self.userGuideName + "_" + self.langDic[self.langName]['c_middle'] + str(n) + "_Ctrl", ch=False, o=True, nr=(0, 1, 0), d=3, s=8, radius=self.ctrlRadius)[0]
                        cmds.setAttr(self.middle + ".rotateOrder", 3)
                    self.aFkCtrl[s].append(self.middle)
                    ctrls.setLockHide([self.middle], ['sx', 'sy', 'sz'])
                    cmds.setAttr(self.middle + '.visibility', keyable=False)
                    cmds.parent(self.middle, self.hipsA)
                    middleLocGuide = side + self.userGuideName + "_Guide_JointLoc" + str(n + 1)
                    cmds.delete(cmds.parentConstraint(middleLocGuide, self.middle, maintainOffset=False))
                    if self.currentStyle == 1: #biped
                        cmds.rotate(0, 0, 0, self.middle)
                    utils.zeroOut([self.middle])
                    middleCluster = cmds.cluster(rbnNurbsPlane + ".cv[0:3][" + str(n + 1) + "]",
                                                 name=side + self.userGuideName + '_Middle_Cls')[1]
                    middleLocPos = cmds.xform(side + self.userGuideName + "_Guide_JointLoc" + str(n), query=True,
                                              worldSpace=True, translation=True)
                    tempDel = cmds.parentConstraint(middleLocGuide, middleCluster, maintainOffset=False)
                    cmds.delete(tempDel)
                    middleClusterRot = cmds.xform(middleCluster, query=True, worldSpace=True, rotation=True)
                    cmds.xform(middleCluster, worldSpace=True,
                               rotation=(middleClusterRot[0] + 90, middleClusterRot[1], middleClusterRot[2]))
                    cmds.parentConstraint(self.middle, middleCluster, maintainOffset=True,
                                          name=middleCluster + "_ParentConstraint")
                    # parenting constraints like guide locators:
                    self.parentConst = cmds.parentConstraint(self.hipsB, self.chestB, self.middle + "_Zero",
                                                             name=self.middle + "_ParentConstraint",
                                                             maintainOffset=True)[0]
                    nParentValue = (n) / float(self.nJoints - 1)
                    cmds.setAttr(self.parentConst + "." + self.hipsB + "W0", 1 - nParentValue)
                    cmds.setAttr(self.parentConst + "." + self.chestB + "W1", nParentValue)
                    cmds.parent(middleCluster, clustersGrp, relative=True)
                    # add originedFrom attribute to this middle ctrl:
                    utils.originedFrom(objName=self.middle, attrString=middleLocGuide)
                    # apply volumeVariation to joints in the middle ribbon setup:
                    cmds.connectAttr(rbnCond + '.outColorR', self.aRbnJointList[n] + '.scaleX')
                    cmds.connectAttr(rbnCond + '.outColorR', self.aRbnJointList[n] + '.scaleZ')
                # update spine volume variation setup
                currentVV = cmds.getAttr(rbnMD + '.outputX')
                cmds.setAttr(rbnVVMD + '.input1X', currentVV)
                # organize groups:
                self.rbnRigGrp = cmds.group(name=side + self.userGuideName + "_Grp", empty=True)
                self.rbnControlGrp = cmds.group(name=side + self.userGuideName + "_Control_Grp", empty=True)
                cmds.parent(self.hipsA + "_Zero", self.rbnControlGrp, relative=True)
                cmds.parent(clustersGrp, side + self.userGuideName + "_Rbn_RibbonJoint_Grp", self.rbnControlGrp,
                            arcLen, self.rbnRigGrp, relative=True)
                if hideJoints:
                    cmds.setAttr(side + self.userGuideName + "_Rbn_RibbonJoint_Grp.visibility", 0)
                # add hook attributes to be read when rigging integrated modules:
                utils.addHook(objName=self.rbnControlGrp, hookType='ctrlHook')
                utils.addHook(objName=clustersGrp, hookType='scalableHook')
                utils.addHook(objName=self.rbnRigGrp, hookType='staticHook')
                cmds.addAttr(self.rbnRigGrp, longName="dpAR_name", dataType="string")
                cmds.addAttr(self.rbnRigGrp, longName="dpAR_type", dataType="string")
                cmds.setAttr(self.rbnRigGrp + ".dpAR_name", self.userGuideName, type="string")
                cmds.setAttr(self.rbnRigGrp + ".dpAR_type", CLASS_NAME, type="string")
                # add module type counter value
                cmds.addAttr(self.rbnRigGrp, longName='dpAR_count', attributeType='long', keyable=False)
                cmds.setAttr(self.rbnRigGrp + '.dpAR_count', dpAR_count)
                # lockHide scale of up and down controls:
                ctrls.setLockHide([self.hipsA, self.hipsB, self.chestA, self.chestB], ['sx', 'sy', 'sz'])
                # delete duplicated group for side (mirror):
                cmds.delete(side + self.userGuideName + '_' + self.mirrorGrp)
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
                "hipsAList": self.aHipsAList,
                "chestAList": self.aChestAList,
                "volumeVariationAttrList": self.aVolVariationAttrList,
                "ActiveVolumeVariationAttrList": self.aActVolVariationAttrList,
                "MasterScaleVolumeVariationAttrList": self.aMScaleVolVariationAttrList,
                "FkCtrls": self.aFkCtrl,
                "IkCtrls": self.aIkCtrl,
                "jointList": self.aRbnJointList,
                "scalableGrp": self.aClusterGrp,
            }
        }
