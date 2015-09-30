# importing libraries:
import maya.cmds as cmds
import dpControls as ctrls
import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout

# importing Renaud Lessard module:
loadedIkFkSnap = False

try:
    from sstk.maya.animation import sqIkFkTools
    from sstk.libs import libSerialization
    loadedIkFkSnap = True
except:
    try:
        from Library import sqIkFkTools
        from Library import libSerialization
        loadedIkFkSnap = True
    except:
        print "Not loaded sqIkFkTools"
        pass

# global variables to this module:
CLASS_NAME = "Limb"
TITLE = "m019_limb"
DESCRIPTION = "m020_limbDesc"
ICON = "/Icons/dp_limb.png"

class Limb(Base.StartClass, Layout.LayoutClass):
    def __init__(self, dpUIinst, langDic, langName, userGuideName):
        Base.StartClass.__init__(self, dpUIinst, langDic, langName, userGuideName, CLASS_NAME, TITLE, DESCRIPTION, ICON)
        pass
    
    
    def createModuleLayout(self, *args):
        Base.StartClass.createModuleLayout(self)
        Layout.LayoutClass.basicModuleLayout(self)
    
    def getHasBend(self):
        return cmds.getAttr(self.moduleGrp+".hasBend")
        
    def getBendJoints(self):
        return cmds.getAttr(self.moduleGrp+".numBendJoints")
    
    
    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="nJoints", attributeType='long')
        cmds.setAttr(self.moduleGrp+".nJoints", 0)
        cmds.addAttr(self.moduleGrp, longName="type", attributeType='enum', enumName=self.langDic[self.langName]['m028_arm']+':'+self.langDic[self.langName]['m030_leg'])
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        cmds.addAttr(self.moduleGrp, longName="hasBend", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".hasBend", 1)
        cmds.addAttr(self.moduleGrp, longName="numBendJoints", attributeType='long')
        cmds.setAttr(self.moduleGrp+".numBendJoints", 5)
        cmds.addAttr(self.moduleGrp, longName="style", attributeType='enum', enumName=self.langDic[self.langName]['m042_default']+':'+self.langDic[self.langName]['m026_biped']+':'+self.langDic[self.langName]['m037_quadruped']+':'+self.langDic[self.langName]['m043_quadSpring'])
        
        # create cvJointLoc and cvLocators:
        self.cvBeforeLoc, shapeSizeCH   = ctrls.cvJointLoc(ctrlName=self.guideName+"_Before", r=0.3)
        self.connectShapeSize(shapeSizeCH)
        self.cvMainLoc, shapeSizeCH     = ctrls.cvJointLoc(ctrlName=self.guideName+"_Main", r=0.5)
        self.connectShapeSize(shapeSizeCH)
        self.cvCornerLoc, shapeSizeCH   = ctrls.cvLocator(ctrlName=self.guideName+"_Corner", r=0.3)
        self.connectShapeSize(shapeSizeCH)
        self.cvCornerBLoc, shapeSizeCH  = ctrls.cvLocator(ctrlName=self.guideName+"_CornerB", r=0.5)
        self.connectShapeSize(shapeSizeCH)
        self.cvExtremLoc, shapeSizeCH   = ctrls.cvJointLoc(ctrlName=self.guideName+"_Extrem", r=0.5)
        self.connectShapeSize(shapeSizeCH)
        self.cvUpVectorLoc, shapeSizeCH = ctrls.cvLocator(ctrlName=self.guideName+"_CornerUpVector", r=0.5)
        self.connectShapeSize(shapeSizeCH)

        # set quadruped locator config:
        cmds.parent(self.cvCornerBLoc, self.cvCornerLoc, relative=True)
        cmds.setAttr(self.cvCornerBLoc+".translateZ", 2)
        cmds.setAttr(self.cvCornerBLoc+".visibility", 0)
        
        # create jointGuides:
        cmds.select(clear=True)
        self.jGuideBefore  = cmds.joint(name=self.guideName+"_JGuideBefore", radius=0.001)
        self.jGuideMain    = cmds.joint(name=self.guideName+"_JGuideMain", radius=0.001)
        self.jGuideCorner = cmds.joint(name=self.guideName+"_JGuideCorner", radius=0.001)
        self.jGuideExtrem  = cmds.joint(name=self.guideName+"_JGuideExtrem", radius=0.001)
        
        # create cornerGroups:
        self.cornerGrp = cmds.group(self.cvCornerLoc, name=self.cvCornerLoc+"_Grp")
        
        # set jointGuides as templates:
        cmds.setAttr(self.jGuideBefore+".template", 1)
        cmds.setAttr(self.jGuideMain+".template", 1)
        cmds.setAttr(self.jGuideCorner+".template", 1)
        cmds.setAttr(self.jGuideExtrem+".template", 1)
        cmds.parent(self.jGuideBefore, self.moduleGrp, relative=True)
        
        # create cvEnd:
        self.cvEndJoint, shapeSizeCH = ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvEndJoint, self.cvExtremLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.parent(self.jGuideEnd, self.jGuideExtrem)
        
        # make parents between cvLocs:
        cmds.parent(self.cvBeforeLoc, self.cvMainLoc, self.cornerGrp, self.cvExtremLoc, self.cvUpVectorLoc, self.moduleGrp)
        
        # connect cvLocs in jointGuides:
        ctrls.directConnect(self.cvBeforeLoc, self.jGuideBefore, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        cmds.parentConstraint(self.cvMainLoc, self.jGuideMain, maintainOffset=False, name=self.jGuideMain+"_ParentConstraint")
        cmds.parentConstraint(self.cvCornerLoc, self.jGuideCorner, maintainOffset=False, name=self.jGuideCorner+"_ParentConstraint")
        cmds.parentConstraint(self.cvExtremLoc, self.jGuideExtrem, maintainOffset=False, name=self.jGuideExtrem+"_ParentConstraint")
        
        # align cornerLocs:
        cmds.aimConstraint(self.cvExtremLoc, self.cornerGrp, aimVector=(0.0, 0.0, 1.0), upVector=(0.0, -1.0, 0.0), worldUpType="object", worldUpObject=self.cvUpVectorLoc, name=self.cornerGrp+"_AimConstraint")
        
        # limit, lock and hide cvEnd:
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        
        # creating relationship of corner:
        self.cornerPointGrp = cmds.group(self.cornerGrp, name=self.cornerGrp+"_Zero")
        cornerPointConst = cmds.pointConstraint(self.cvMainLoc, self.cvExtremLoc, self.cornerPointGrp, maintainOffset=False, name=self.cornerPointGrp+"_PointConstraint")[0]
        cmds.setAttr(cornerPointConst+'.'+self.cvMainLoc[self.cvMainLoc.rfind(":")+1:]+'W0', 0.52)
        cmds.setAttr(cornerPointConst+'.'+self.cvExtremLoc[self.cvExtremLoc.rfind(":")+1:]+'W1', 0.48)
        
        # transform cvLocs in order to put as a good limb guide:
        cmds.setAttr(self.cvBeforeLoc+".translateX", -0.5)
        cmds.setAttr(self.cvBeforeLoc+".translateZ", -2)
        cmds.setAttr(self.cvExtremLoc+".translateZ", 10)
        cmds.setAttr(self.cornerGrp+".translateY", -0.75)
        cmds.setAttr(self.moduleGrp+".translateX", 4)
        cmds.setAttr(self.moduleGrp+".rotateX", 90)
        cmds.setAttr(self.moduleGrp+".rotateZ", 90)
        # editing cornerUpVector:
        self.cvUpVectorGrp = cmds.group(self.cvUpVectorLoc, name=self.cvUpVectorLoc+"_Grp")
        cornerPositionList = cmds.xform(self.cvCornerLoc, query=True, worldSpace=True, rotatePivot=True)
        cmds.move(cornerPositionList[0], cornerPositionList[1], cornerPositionList[2], self.cvUpVectorGrp)
        cmds.pointConstraint(self.cvExtremLoc, self.cvUpVectorGrp, maintainOffset=True, name=self.cvUpVectorGrp+"_PointConstraint")
        cmds.setAttr(self.cvUpVectorLoc+".translateY", -10)
        
        # re orient guides:
        self.reOrientGuide()
    
    def reCreateEditSelectedModuleLayout(self, *args):
        Layout.LayoutClass.reCreateEditSelectedModuleLayout(self)
        # if there is a type attribute:
        cmds.text(self.nSegmentsText, edit=True, visible=False, parent=self.segDelColumn)
        cmds.intField(self.nJointsIF, edit=True, editable=False, visible=False, parent=self.segDelColumn)
        
        self.typeLayout = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 50, 77, 70), columnAlign=[(1, 'right'), (2, 'left'), (3, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (3, 'both', 10)], parent="selectedColumn" )
        cmds.text(self.langDic[self.langName]['m021_type'], parent=self.typeLayout)
        self.typeMenu = cmds.optionMenu("typeMenu", label='', changeCommand=self.changeType, parent=self.typeLayout)
        typeMenuItemList = [self.langDic[self.langName]['m028_arm'], self.langDic[self.langName]['m030_leg']]
        for item in typeMenuItemList:
            cmds.menuItem(label=item, parent=self.typeMenu)
        # read from guide attribute the current value to type:
        currentType = cmds.getAttr(self.moduleGrp+".type")
        cmds.optionMenu(self.typeMenu, edit=True, select=int(currentType+1))
        self.reOrientBT = cmds.button(label=self.langDic[self.langName]['m022_reOrient'], annotation=self.langDic[self.langName]['m023_reOrientDesc'], command=self.reOrientGuide, parent=self.typeLayout)
        
        # style layout:
        self.styleLayout = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 50, 77, 70), columnAlign=[(1, 'right'), (2, 'left'), (3, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (3, 'both', 10)], parent="selectedColumn")
        cmds.text(label=self.langDic[self.langName]['m041_style'], visible=True, parent=self.styleLayout)
        self.styleMenu = cmds.optionMenu("styleMenu", label='', changeCommand=self.changeStyle, parent=self.styleLayout)
        styleMenuItemList = [self.langDic[self.langName]['m042_default'], self.langDic[self.langName]['m026_biped'], self.langDic[self.langName]['m037_quadruped'], self.langDic[self.langName]['m043_quadSpring']]
        for item in styleMenuItemList:
            cmds.menuItem(label=item, parent=self.styleMenu)
        # read from guide attribute the current value to style:
        currentStyle = cmds.getAttr(self.moduleGrp+".style")
        cmds.optionMenu(self.styleMenu, edit=True, select=int(currentStyle+1))
        
        # bend layout:
        self.bendLayout = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 50, 77, 70), columnAlign=[(1, 'right'), (2, 'left'), (3, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (3, 'both', 10)], parent="selectedColumn")
        cmds.text(label=self.langDic[self.langName]['m044_addBend'], visible=True, parent=self.bendLayout)
        self.bendChkbox = cmds.checkBox(value=self.getHasBend(), label=' ', ofc=self.setBendFalse, onc=self.setBendTrue, parent=self.bendLayout)
        self.bendNumJointsMenu = cmds.optionMenu("bendNumJointsMenu", label='Ribbon Joints', changeCommand=self.changeNumBend, enable=self.getHasBend(), parent=self.bendLayout)
        bendNumMenuItemList = [3, 5, 7]
        for item in bendNumMenuItemList:
            cmds.menuItem(label=item, parent=self.bendNumJointsMenu)
        # read from guide attribute the current value to number of joints for bend:
        currentNumberBendJoints = cmds.getAttr(self.moduleGrp+".numBendJoints")
        for i, item in enumerate(bendNumMenuItemList):
            if currentNumberBendJoints == item:
                cmds.optionMenu(self.bendNumJointsMenu, edit=True, select=i+1)
                break
    
    
    def setBendTrue(self, *args):
        self.hasBend=True
        cmds.optionMenu(self.bendNumJointsMenu, edit=True, enable=True)
        cmds.setAttr(self.moduleGrp+".hasBend", 1)
    
    def setBendFalse(self, *args):
        self.hasBend=False
        cmds.optionMenu(self.bendNumJointsMenu, edit=True, enable=False)
        cmds.setAttr(self.moduleGrp+".hasBend", 0)
    
    def changeNumBend(self, numberBendJoints, *args):
        """ Change the number of joints used in the bend ribbon.
        """
        cmds.setAttr(self.moduleGrp+".numBendJoints", int(numberBendJoints))
    
    def changeStyle(self, style, *args):
        """ Change the style to be applyed custom actions to be more animator friendly.
            We will optimise: ik controls mirrored correctely, quadruped front legs using ikSpring solver, good parents and constraints
        """
        self.cvCornerBLoc = self.guideName+"_CornerB"
        # for Default style:
        if style == self.langDic[self.langName]['m042_default']:
            cmds.setAttr(self.cvCornerBLoc+".visibility", 0)
            cmds.setAttr(self.moduleGrp+".style", 0)
        # for Biped style:
        if style == self.langDic[self.langName]['m026_biped']:
            cmds.setAttr(self.cvCornerBLoc+".visibility", 0)
            cmds.setAttr(self.moduleGrp+".style", 1)
        # for Quadruped style:
        if style == self.langDic[self.langName]['m037_quadruped']:
            cmds.setAttr(self.cvCornerBLoc+".visibility", 1)
            cmds.setAttr(self.moduleGrp+".style", 2)
        # for Quadruped Spring style:
        if style == self.langDic[self.langName]['m043_quadSpring']:
            cmds.setAttr(self.cvCornerBLoc+".visibility", 1)
            cmds.setAttr(self.moduleGrp+".style", 3)
    
    def changeType(self, type, *args):
        """ This function will modify the names of the rigged module to Arm of Leg options
            and rotate the moduleGrp in order to be more easy to user edit.
        """
        # re-declaring guide names:
        self.cvBeforeLoc = self.guideName+"_Before"
        self.cvMainLoc = self.guideName+"_Main"
        self.cornerGrp = self.guideName+"_Corner_Grp"
        self.cvExtremLoc = self.guideName+"_Extrem"
        self.cvEndJoint = self.guideName+"_JointEnd"
        self.cvUpVectorLoc = self.guideName+"_CornerUpVector"
        
        # reset translations:
        translateAttrList = ['tx', 'ty', 'tz']
        for tAttr in translateAttrList:
            cmds.setAttr(self.cvBeforeLoc+"."+tAttr, 0)
            cmds.setAttr(self.cvMainLoc+"."+tAttr, 0)
            cmds.setAttr(self.cornerGrp+"."+tAttr, 0)
            cmds.setAttr(self.cvExtremLoc+"."+tAttr, 0)
            cmds.setAttr(self.cvUpVectorLoc+"."+tAttr, 0)
        
        # for Arm type:
        if type == self.langDic[self.langName]['m028_arm']:
            cmds.setAttr(self.moduleGrp+".type", 0)
            cmds.setAttr(self.cvBeforeLoc+".translateX", -1)
            cmds.setAttr(self.cvBeforeLoc+".translateZ", -4)
            cmds.setAttr(self.cvExtremLoc+".translateZ", 10)
            cmds.setAttr(self.cornerGrp+".translateY", -0.75)
            cmds.setAttr(self.cvEndJoint+".translateZ", 1.3)
            cmds.setAttr(self.moduleGrp+".rotateX", 90)
            cmds.setAttr(self.moduleGrp+".rotateY", 0)
            cmds.setAttr(self.moduleGrp+".rotateZ", 90)
            cmds.setAttr(self.cvUpVectorLoc+".translateY", -10)
            cmds.delete(self.cornerGrp+"_AimConstraint")
            cmds.aimConstraint(self.cvExtremLoc, self.cornerGrp, aimVector=(0.0, 0.0, 1.0), upVector=(0.0, -1.0, 0.0), worldUpType="object", worldUpObject=self.cvUpVectorLoc, name=self.cornerGrp+"_AimConstraint")
        
        # for Leg type:
        elif type == self.langDic[self.langName]['m030_leg']:
            cmds.setAttr(self.moduleGrp+".type", 1)
            cmds.setAttr(self.cvBeforeLoc+".translateY", 1)
            cmds.setAttr(self.cvBeforeLoc+".translateZ", -2)
            cmds.setAttr(self.cvExtremLoc+".translateZ", 10)
            cmds.setAttr(self.cornerGrp+".translateX", 0.75)
            cmds.setAttr(self.cvEndJoint+".translateZ", 1.3)
            cmds.setAttr(self.moduleGrp+".rotateX", 0)
            cmds.setAttr(self.moduleGrp+".rotateY", -90)
            cmds.setAttr(self.moduleGrp+".rotateZ", 90)
            cmds.setAttr(self.cvUpVectorLoc+".translateX", 10)
            cmds.delete(self.cornerGrp+"_AimConstraint")
            cmds.aimConstraint(self.cvExtremLoc, self.cornerGrp, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0), worldUpType="object", worldUpObject=self.cvUpVectorLoc, name=self.cornerGrp+"_AimConstraint")
            
        # reset rotations:
        self.reOrientGuide()
    
    
    def reOrientGuide(self, *args):
        """ This function reOrient guides orientations, creating temporary aimConstraints for them.
        """
        # re-declaring guide names:
        self.cvBeforeLoc  = self.guideName+"_Before"
        self.cvMainLoc    = self.guideName+"_Main"
        self.cvCornerLoc = self.guideName+"_Corner"
        self.cvExtremLoc  = self.guideName+"_Extrem"
        
        # re-orient rotations:
        tempToDelBefore = cmds.aimConstraint(self.cvMainLoc, self.cvBeforeLoc, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0))
        tempToDelMain   = cmds.aimConstraint(self.cvCornerLoc, self.cvMainLoc, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0))
        cmds.delete(tempToDelBefore, tempToDelMain)
        cmds.setAttr(self.cvExtremLoc+'.rotateX', 0)
        cmds.setAttr(self.cvExtremLoc+'.rotateY', 0)
        cmds.setAttr(self.cvExtremLoc+'.rotateZ', 0)
        
    
    def rigModule(self, *args):
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            # declaring lists to send information for integration:
            self.ikExtremCtrlList, self.ikExtremCtrlZeroList, self.ikPoleVectorCtrlZeroList, self.ikHandleToRFGrpList, self.ikHandlePointConstList, self.ikFkBlendGrpToRevFootList, self.worldRefList, self.worldRefShapeList, self.extremJntList, self.parentConstToRFOffsetList, self.fixIkSpringSolverGrpList, self.quadFrontLegList, self.integrateOrigFromList, self.ikStretchExtremLocList, self.ikFkNetworkList = [], [], [], [], [], [], [], [], [], [], [], [], [], [], []
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
                        for axis in self.mirrorAxis:
                            cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.scale'+axis, -1)
            else: # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_Guide_Base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(self.userGuideName+'_Guide_Base', name="Guide_Base_Grp", relative=True)
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
            # store the number of this guide by module type
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # run for all sides
            for s, side in enumerate(sideList):
                # getting type of limb:
                enumType = cmds.getAttr(self.moduleGrp+'.type')
                if enumType == 0:
                    self.limbType = self.langDic[self.langName]['m028_arm']
                    limbTypeName = "arm"
                elif enumType == 1:
                    self.limbType = self.langDic[self.langName]['m030_leg']
                    limbTypeName = "leg"
                # getting style of the limb:
                enumStyle = cmds.getAttr(self.moduleGrp+'.style')
                if enumStyle == 0:
                    self.limbStyle = self.langDic[self.langName]['m042_default']
                elif enumStyle == 1:
                    self.limbStyle = self.langDic[self.langName]['m026_biped']
                elif enumStyle == 2:
                    self.limbStyle = self.langDic[self.langName]['m037_quadruped']
                elif enumStyle == 3:
                    self.limbStyle = self.langDic[self.langName]['m043_quadSpring']
                
                # re-declaring guide names:
                self.cvBeforeLoc  = side+self.userGuideName+"_Guide_Before"
                self.cvMainLoc    = side+self.userGuideName+"_Guide_Main"
                self.cvCornerLoc  = side+self.userGuideName+"_Guide_Corner"
                self.cvCornerBLoc = side+self.userGuideName+"_Guide_CornerB"
                self.cvExtremLoc  = side+self.userGuideName+"_Guide_Extrem"
                self.cvEndJoint   = side+self.userGuideName+"_Guide_JointEnd"
                
                # getting names from dic:
                beforeName  = self.langDic[self.langName]['c_'+limbTypeName+'_before']
                mainName    = self.langDic[self.langName]['c_'+limbTypeName+'_main']
                cornerName  = self.langDic[self.langName]['c_'+limbTypeName+'_corner']
                cornerBName = self.langDic[self.langName]['c_'+limbTypeName+'_cornerB']
                extremName  = self.langDic[self.langName]['c_'+limbTypeName+'_extrem']

                # mount cvLocList and jNameList:
                if self.limbStyle == self.langDic[self.langName]['m037_quadruped'] or self.limbStyle == self.langDic[self.langName]['m043_quadSpring']:
                    self.cvLocList = [self.cvBeforeLoc, self.cvMainLoc, self.cvCornerLoc, self.cvCornerBLoc, self.cvExtremLoc]
                    self.jNameList = [beforeName, mainName, cornerName, cornerBName, extremName]
                else:
                    self.cvLocList = [self.cvBeforeLoc, self.cvMainLoc, self.cvCornerLoc, self.cvExtremLoc]
                    self.jNameList = [beforeName, mainName, cornerName, extremName]
                
                # creating joint to skin, ik, Fk and ikNotStretch chains:
                self.chainDic      = {}
                self.jSufixList    = ['_Jnt', '_Ik_Jxt', '_Fk_Jxt', '_IkNotStretch_Jxt']
                self.jEndSufixList = ['_JEnd', '_Ik_JEnd', '_Fk_JEnd', '_IkNotStretch_JEnd']
                for t, sufix in enumerate(self.jSufixList):
                    self.wipList = []
                    cmds.select(clear=True)
                    for n, jName in enumerate(self.jNameList):
                        newJoint = cmds.joint(name=side+self.userGuideName+"_"+jName+sufix)
                        self.wipList.append(newJoint)
                    jEndJnt = cmds.joint(name=side+self.userGuideName+self.jEndSufixList[t])
                    self.wipList.append(jEndJnt)
                    self.chainDic[sufix] = self.wipList
                # getting jointLists:
                self.skinJointList = self.chainDic[self.jSufixList[0]]
                self.ikJointList   = self.chainDic[self.jSufixList[1]]
                self.fkJointList   = self.chainDic[self.jSufixList[2]]
                self.ikNSJointList = self.chainDic[self.jSufixList[3]]
                
                for o, skinJoint in enumerate(self.skinJointList):
                    if o < len(self.skinJointList)-1:
                        cmds.addAttr(skinJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                self.extremJntList.append(self.skinJointList[-2])
                
                # creating Fk controls and a hierarchy group to originedFrom data:
                self.fkCtrlList, self.origFromList = [], []
                for n, jName in enumerate(self.jNameList):
                    if n == 0:
                        fkCtrl = cmds.circle(name=side+self.userGuideName+"_"+jName+"_Ctrl", ch=False, o=True, nr=(0, 0, 1), d=1, s=8, radius=self.ctrlRadius)[0]
                    else:
                        fkCtrl = cmds.circle(name=side+self.userGuideName+"_"+jName+"_Fk_Ctrl", ch=False, o=True, nr=(0, 0, 1), d=1, s=8, radius=self.ctrlRadius)[0]
                    self.fkCtrlList.append(fkCtrl)
                    cmds.setAttr(fkCtrl+'.visibility', keyable=False)
                    # creating the originedFrom attributes (in order to permit integrated parents in the future):
                    origGrp = cmds.group(empty=True, name=side+self.userGuideName+"_"+jName+"_OrigFrom_Grp")
                    self.origFromList.append(origGrp)
                    utils.originedFrom(objName=origGrp, attrString=self.cvLocList[n][self.cvLocList[n].find("__")+1:].replace(":", "_"))
                    cmds.parentConstraint(self.skinJointList[n], origGrp, maintainOffset=False, name=origGrp+"_ParentConstraint")
                    if n > 1:
                        cmds.parent(fkCtrl, self.fkCtrlList[n-1])
                        cmds.parent(origGrp, self.origFromList[n-1])
                    # add wrist_toParent_Ctrl
                    if n == len(self.jNameList)-1:
                        self.toParentExtremCtrl = ctrls.cvBall(ctrlName=side+self.userGuideName+"_"+extremName+"_ToParent_Ctrl", r=self.ctrlRadius*0.1)
                        cmds.parent(self.toParentExtremCtrl, origGrp)
                        if s == 0:
                            cmds.setAttr(self.toParentExtremCtrl+".translateX", self.ctrlRadius)
                        else:
                            cmds.setAttr(self.toParentExtremCtrl+".translateX", -self.ctrlRadius)
                        utils.zeroOut([self.toParentExtremCtrl])
                        ctrls.setLockHide([self.toParentExtremCtrl], ['v'])
                # zeroOut controls:
                self.zeroFkCtrlList = utils.zeroOut(self.fkCtrlList)
                self.zeroFkCtrlGrp  = cmds.group(self.zeroFkCtrlList[0], self.zeroFkCtrlList[1], name=side+self.userGuideName+"_FkCtrl_Grp")
                
                # invert scale for right side before:
                if s == 1:
                    cmds.setAttr(self.fkCtrlList[0]+".scaleX", -1)
                    cmds.setAttr(self.fkCtrlList[0]+".scaleY", -1)
                    cmds.setAttr(self.fkCtrlList[0]+".scaleZ", -1)
                
                # working with position, orientation of joints and make an orientConstrain for Fk controls:
                for n in range(len(self.jNameList)):
                    tempToDelA = cmds.parentConstraint(self.cvLocList[n], self.skinJointList[n], maintainOffset=False)
                    tempToDelB = cmds.parentConstraint(self.cvLocList[n], self.ikJointList[n], maintainOffset=False)
                    tempToDelB1 = cmds.parentConstraint(self.cvLocList[n], self.ikNSJointList[n], maintainOffset=False)
                    tempToDelC = cmds.parentConstraint(self.cvLocList[n], self.fkJointList[n], maintainOffset=False)
                    tempToDelD = cmds.parentConstraint(self.cvLocList[n], self.zeroFkCtrlList[n], maintainOffset=False)
                    cmds.delete(tempToDelA, tempToDelB, tempToDelB1, tempToDelC, tempToDelD)
                    # freezeTransformations (rotates):
                    cmds.makeIdentity(self.skinJointList[n], self.ikJointList[n], self.ikNSJointList[n], self.fkJointList[n], apply=True, rotate=True)
                    # fk control leads fk joint:
                    if n == 0:
                        cmds.parentConstraint(self.fkCtrlList[n], self.fkJointList[n], maintainOffset=True, name=side+self.userGuideName+"_"+self.jNameList[n]+"_ParentConstraint")
                    else:
                        cmds.parentConstraint(self.fkCtrlList[n], self.fkJointList[n], maintainOffset=True, name=side+self.userGuideName+"_"+self.jNameList[n]+"_Fk_ParentConstraint")
                    ctrls.setLockHide([self.fkCtrlList[n]], ['sx', 'sy', 'sz'])

                # puting endJoints in the correct position:
                tempToDelE = cmds.parentConstraint(self.cvEndJoint, self.skinJointList[-1], maintainOffset=False)
                tempToDelF = cmds.parentConstraint(self.cvEndJoint, self.ikJointList[-1], maintainOffset=False)
                tempToDelF1 = cmds.parentConstraint(self.cvEndJoint, self.ikNSJointList[-1], maintainOffset=False)
                tempToDelG = cmds.parentConstraint(self.cvEndJoint, self.fkJointList[-1], maintainOffset=False)
                cmds.delete(tempToDelE, tempToDelF, tempToDelF1, tempToDelG)
                
                # creating a group reference to recept the attributes:
                self.worldRef = cmds.circle(name=side+self.userGuideName+"_WorldRef", ch=False, o=True, nr=(0, 1, 0), d=3, s=8, radius=self.ctrlRadius)[0]
                cmds.addAttr(self.worldRef, longName=side+self.limbType+str(dpAR_count)+'_IkFkBlend', attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                if not cmds.objExists(self.worldRef+'.globalStretch'):
                    cmds.addAttr(self.worldRef, longName='globalStretch', attributeType='float', minValue=0, maxValue=1, defaultValue=1, keyable=True)
                self.worldRefList.append(self.worldRef)
                self.worldRefShape = cmds.listRelatives(self.worldRef, children=True, type='nurbsCurve')[0]
                self.worldRefShapeList.append(self.worldRefShape)
                
                # parenting fkControls from 2 hierarchies (before and limb) using constraint, attention to fkIsolated shoulder:
                # creating a shoulder_null group in order to use it as position relative:
                self.shoulderNullGrp = cmds.group(empty=True, name=self.skinJointList[1]+"_null")
                cmds.parent(self.shoulderNullGrp, self.skinJointList[1], relative=True)
                cmds.parent(self.shoulderNullGrp, self.skinJointList[0], relative=False)
                cmds.pointConstraint(self.shoulderNullGrp, self.zeroFkCtrlList[1], maintainOffset=True, name=self.zeroFkCtrlList[1]+"_PointConstraint")
                fkIsolateParentConst = cmds.parentConstraint(self.shoulderNullGrp, self.worldRef, self.zeroFkCtrlList[1], skipTranslate=["x", "y", "z"], maintainOffset=True, name=self.zeroFkCtrlList[1]+"_ParentConstraint")[0]
                cmds.addAttr(self.fkCtrlList[1], longName=self.langDic[self.langName]['c_Follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=1, keyable=True)
                cmds.connectAttr(self.fkCtrlList[1]+'.'+self.langDic[self.langName]['c_Follow'], fkIsolateParentConst+"."+self.shoulderNullGrp+"W0", force=True)
                self.fkIsolateRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_FkIsolate_Rev")
                cmds.connectAttr(self.fkCtrlList[1]+'.'+self.langDic[self.langName]['c_Follow'], self.fkIsolateRevNode+".inputX", force=True)
                cmds.connectAttr(self.fkIsolateRevNode+'.outputX', fkIsolateParentConst+"."+self.worldRef+"W1", force=True)

                # create orient constrain in order to blend ikFk:
                self.ikFkRevList = []
                for n in range(len(self.jNameList)):
                    if n > 0:
                        parentConst = cmds.parentConstraint(self.ikJointList[n], self.fkJointList[n], self.skinJointList[n], maintainOffset=True, name=side+self.userGuideName+"_"+self.jNameList[n]+"_IkFkBlend_ParentConstraint")[0]
                        if n == 1:
                            revNode = cmds.createNode('reverse', name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_Rev")
                            cmds.connectAttr(self.worldRef+"."+side+self.limbType+str(dpAR_count)+'_IkFkBlend', revNode+".inputX", force=True)
                        else:
                            revNode = side+self.userGuideName+"_"+self.limbType.capitalize()+"_Rev"
                        self.ikFkRevList.append(revNode)
                        # connecting ikFkBlend using the reverse node:
                        cmds.connectAttr(self.worldRef+"."+side+self.limbType+str(dpAR_count)+'_IkFkBlend', parentConst+"."+self.fkJointList[n]+"W1", force=True)
                        cmds.connectAttr(revNode+'.outputX', parentConst+"."+self.ikJointList[n]+"W0", force=True)
                # organize the ikFkBlend from before to limb:
                cmds.parentConstraint(self.fkCtrlList[0], self.ikJointList[0], maintainOffset=True, name=self.ikJointList[0]+"_ParentConstraint")
                cmds.parentConstraint(self.fkCtrlList[0], self.ikNSJointList[0], maintainOffset=True, name=self.ikJointList[0]+"_ParentConstraint")
                cmds.parentConstraint(self.fkCtrlList[0], self.fkJointList[0], maintainOffset=True, name=self.fkJointList[0]+"_ParentConstraint")
                cmds.parentConstraint(self.fkCtrlList[0], self.skinJointList[0], maintainOffset=True, name=self.skinJointList[0]+"_ParentConstraint")
                
                # creating ik controls:
                if self.limbType == self.langDic[self.langName]['m028_arm']:
                    self.ikCornerCtrl = ctrls.cvElbow(ctrlName=side+self.userGuideName+"_"+cornerName+"_Ik_Ctrl", r=self.ctrlRadius*0.5)
                else:
                    self.ikCornerCtrl = ctrls.cvKnee(ctrlName=side+self.userGuideName+"_"+cornerName+"_Ik_Ctrl", r=self.ctrlRadius*0.5)
                cmds.addAttr(self.ikCornerCtrl, longName='active', attributeType='float', minValue=0, maxValue=1, defaultValue=1, keyable=True);
                cmds.setAttr(self.ikCornerCtrl+'.active', 1);
                self.ikExtremCtrl  = ctrls.cvBox(ctrlName=side+self.userGuideName+"_"+extremName+"_Ik_Ctrl", r=self.ctrlRadius*0.5)
                self.ikExtremCtrlList.append(self.ikExtremCtrl)
                # getting them zeroOut groups:
                self.ikCornerCtrlZero = utils.zeroOut([self.ikCornerCtrl])[0]
                self.ikExtremCtrlZero = utils.zeroOut([self.ikExtremCtrl])[0]
                self.ikExtremCtrlZeroList.append(self.ikExtremCtrlZero)
                # putting ikCtrls in the correct position and orientation:
                tempToDelH = cmds.parentConstraint(self.cvExtremLoc, self.ikExtremCtrlZero, maintainOffset=False)
                cmds.delete(tempToDelH)
                # fix stretch calcule to work with reverseFoot
                self.ikStretchExtremLoc = cmds.group(empty=True, name=side+self.userGuideName+"_"+extremName+"_Ik_Loc_Grp")
                self.ikStretchExtremLocList.append(self.ikStretchExtremLoc)
                cmds.delete(cmds.parentConstraint(self.cvExtremLoc, self.ikStretchExtremLoc, maintainOffset=False))
                cmds.parent(self.ikStretchExtremLoc, self.ikExtremCtrl, absolute=True)
                
                # mirror poleVector control zeroOut group:
                if s == 1:
                    cmds.setAttr(self.ikCornerCtrlZero+".scaleX", -1)
                
                # fixing ikControl group to get a good mirror orientation more animator friendly:
                self.ikExtremCtrlGrp = cmds.group(self.ikExtremCtrl, name=side+self.userGuideName+"_"+extremName+"_Ik_Ctrl_Grp")
                self.ikExtremCtrlOrientGrp = cmds.group(self.ikExtremCtrlGrp, name=side+self.userGuideName+"_"+extremName+"_Ik_Ctrl_Orient_Grp")
                
                # verify if user wants to apply the good mirror orientation:
                if self.limbStyle != self.langDic[self.langName]['m042_default']:
                    # these options is valides for Biped, Quadruped and Quadruped Spring
                    if self.mirrorAxis != 'off':
                        for axis in self.mirrorAxis:
                            if axis == "X":
                                if self.limbType == self.langDic[self.langName]['m028_arm']:
                                    # original guide
                                    if s == 0:
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateY", -90)
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateZ", -90)
                                    # mirrored guide
                                    else:
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateY", -90)
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateZ", 90)
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".scaleX", -1)
                                # leg type
                                else:
                                    # original guide
                                    if s == 0:
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateX", -90)
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateZ", -90)
                                    # mirrored guide
                                    else:
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateX", 90)
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateZ", -90)
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".scaleX", -1)
                
                # connecting visibilities:
                cmds.connectAttr(self.worldRef+"."+side+self.limbType+str(dpAR_count)+'_IkFkBlend', self.zeroFkCtrlList[1]+".visibility", force=True)
                cmds.connectAttr(side+self.userGuideName+"_"+self.limbType.capitalize()+"_Rev"+".outputX", self.ikCornerCtrlZero+".visibility", force=True)
                cmds.connectAttr(side+self.userGuideName+"_"+self.limbType.capitalize()+"_Rev"+".outputX", self.ikExtremCtrlZero+".visibility", force=True)
                ctrls.setLockHide([self.ikCornerCtrl, self.ikExtremCtrl], ['v'], l=False)
                
                # creating ikHandles:
                # verify the limb style:
                if self.limbStyle == self.langDic[self.langName]['m043_quadSpring']:
                    loaded = True
                    # verify if the ikSpringSolver plugin is loaded, if not, then load it
                    if not cmds.pluginInfo('ikSpringSolver.mll', query=True, loaded=True):
                        loaded = False
                        try:
                            cmds.loadPlugin('ikSpringSolver.mll')
                            loaded = True
                        except:
                            print "Error: Can not load the ikSpringSolver plugin!"
                            print "Applied default ikRPSolver instead."
                            pass
                    if loaded:
                        if not cmds.objExists('ikSpringSolver'):
                            cmds.createNode('ikSpringSolver', name='ikSpringSolver')
                        # using better quadruped front legs solution as ikSpringSolver:
                        ikHandleMainList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_IkHandle", startJoint=self.ikJointList[1], endEffector=self.ikJointList[len(self.ikJointList)-2], solver='ikSpringSolver')
                        ikHandleNotStretchList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_NotStretch_IkHandle", startJoint=self.ikNSJointList[1], endEffector=self.ikNSJointList[len(self.ikNSJointList)-2], solver='ikSpringSolver')
                    else:
                        # could not load the ikSpringSolver plutin, the we will use the regular solution as ikRPSolver:
                        ikHandleMainList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_IkHandle", startJoint=self.ikJointList[1], endEffector=self.ikJointList[len(self.ikJointList)-2], solver='ikRPsolver')
                        ikHandleNotStretchList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_NotStretch_IkHandle", startJoint=self.ikNSJointList[1], endEffector=self.ikNSJointList[len(self.ikNSJointList)-2], solver='ikRPsolver')
                else:
                    # using regular solution as ikRPSolver:
                    ikHandleMainList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_IkHandle", startJoint=self.ikJointList[1], endEffector=self.ikJointList[len(self.ikJointList)-2], solver='ikRPsolver')
                    ikHandleNotStretchList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_NotStretch_IkHandle", startJoint=self.ikNSJointList[1], endEffector=self.ikNSJointList[len(self.ikNSJointList)-2], solver='ikRPsolver')
                
                # renaming effectors:
                cmds.rename(ikHandleMainList[1], ikHandleMainList[0].capitalize()+"_Effector")
                cmds.rename(ikHandleNotStretchList[1], ikHandleNotStretchList[0].capitalize()+"_Effector")
                
                # creating ikHandle groups:
                ikHandleGrp = cmds.group(empty=True, name=side+self.userGuideName+"_IkHandle_Grp")
                cmds.setAttr(ikHandleGrp+'.visibility', 0)
                self.ikHandleToRFGrp = cmds.group(empty=True, name=side+self.userGuideName+"_IkHandleToRF_Grp")
                self.ikHandleToRFGrpList.append(self.ikHandleToRFGrp)
                cmds.setAttr(self.ikHandleToRFGrp+'.visibility', 0)
                cmds.parent(ikHandleMainList[0], self.ikHandleToRFGrp)
                cmds.parent(self.ikHandleToRFGrp, ikHandleGrp)
                # for ikHandle not stretch group:
                ikHandleNotStretchGrp = cmds.group(empty=True, name=side+self.userGuideName+"_NotStretch_IkHandle_Grp")
                cmds.setAttr(ikHandleNotStretchGrp+'.visibility', 0)
                cmds.parent(ikHandleNotStretchList[0], ikHandleNotStretchGrp)
                
                # make ikControls lead ikHandles:
                self.ikHandlePointConst = cmds.pointConstraint(self.ikExtremCtrl, ikHandleMainList[0], maintainOffset=True, name=ikHandleMainList[0]+"_ParentConstraint")[0]
                self.ikHandlePointConstList.append(self.ikHandlePointConst)
                cmds.orientConstraint(self.ikExtremCtrl, self.ikJointList[len(self.ikJointList)-2], maintainOffset=True, name=self.ikJointList[len(self.ikJointList)-2]+"_OrientConstraint")
                ctrls.setLockHide([self.ikExtremCtrl], ['sx', 'sy', 'sz'])
                cmds.pointConstraint(self.ikExtremCtrl, ikHandleNotStretchList[0], maintainOffset=True, name=ikHandleNotStretchList[0]+"_PointConstraint")[0]
                cmds.orientConstraint(self.ikExtremCtrl, self.ikNSJointList[len(self.ikNSJointList)-2], maintainOffset=True, name=self.ikNSJointList[len(self.ikNSJointList)-2]+"_OrientConstraint")
                
                # twist:
                cmds.addAttr(self.ikExtremCtrl, longName='twist', attributeType='float', keyable=True)
                if s == 0:
                    cmds.connectAttr(self.ikExtremCtrl+'.twist', ikHandleMainList[0]+".twist", force=True)
                    cmds.connectAttr(self.ikExtremCtrl+'.twist', ikHandleNotStretchList[0]+".twist", force=True)
                else:
                    twistMultDiv = cmds.createNode('multiplyDivide', name=self.ikExtremCtrl+"_MD")
                    cmds.setAttr(twistMultDiv+'.input2X', -1)
                    cmds.connectAttr(self.ikExtremCtrl+'.twist', twistMultDiv+'.input1X', force=True)
                    cmds.connectAttr(twistMultDiv+'.outputX', ikHandleMainList[0]+".twist", force=True)
                    cmds.connectAttr(twistMultDiv+'.outputX', ikHandleNotStretchList[0]+".twist", force=True)

                # corner poleVector:
                baseMiddlePointList = ctrls.middlePoint(self.ikJointList[1], self.ikJointList[3], createLocator=True)
                poleVectorLoc = cmds.spaceLocator(name=side+self.userGuideName+"_PoleVectorLoc")
                cmds.delete(cmds.parentConstraint(self.ikJointList[2], poleVectorLoc, maintainOffset=False))
                cmds.delete(cmds.aimConstraint(self.ikJointList[1], poleVectorLoc, aimVector=(1.0, 0.0, 0.0), upVector=(0.0, 1.0, 0.0), worldUpType="object", worldUpObject=self.ikJointList[1], maintainOffset=False))

                # corner look at base:
                cmds.delete(cmds.aimConstraint(baseMiddlePointList[1], poleVectorLoc, aimVector=(0.0, 0.0, -1.0), upVector=(0.0, 1.0, 0.0), maintainOffset=False))
                
                # move to along Z axis in order to go away from base middle locator:
                distToMove = ctrls.distanceBet(self.ikJointList[1], self.ikJointList[3])[0] * 1.1
                cmds.move(0, 0, distToMove, poleVectorLoc, relative=True, objectSpace=True, worldSpaceDistance=True)
                
                # put poleVector control in the correct position:
                cornerPos = cmds.xform(poleVectorLoc, query=True, worldSpace=True, rotatePivot=True)
                cmds.delete(cmds.parentConstraint(poleVectorLoc, self.ikCornerCtrlZero, maintainOffset=False))
                cmds.delete(baseMiddlePointList[1], poleVectorLoc)
                
                # create poleVector constraint:
                poleVectorConstA = cmds.poleVectorConstraint(self.ikCornerCtrl, ikHandleMainList[0], weight=1.0, name=ikHandleMainList[0]+"_PoleVectorConstraint")
                poleVectorConstB = cmds.poleVectorConstraint(self.ikCornerCtrl, ikHandleNotStretchList[0], weight=1.0, name=ikHandleNotStretchList[0]+"_PoleVectorConstraint")
                cmds.connectAttr(self.ikCornerCtrl+'.active', poleVectorConstA[0]+"."+self.ikCornerCtrl+"W0", force=True)
                cmds.connectAttr(self.ikCornerCtrl+'.active', poleVectorConstB[0]+"."+self.ikCornerCtrl+"W0", force=True)
                
                # create annotation:
                annotLoc = cmds.spaceLocator(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_Ant_Loc", position=(0,0,0))[0]
                annotation = cmds.annotate(annotLoc, tx="", point=cornerPos)
                annotation = cmds.listRelatives(annotation, parent=True)[0]
                annotation = cmds.rename(annotation, side+self.userGuideName+"_"+self.limbType.capitalize()+"_Ant")
                cmds.parent(annotation, self.ikCornerCtrl)
                cmds.parent(annotLoc, self.ikJointList[2], relative=True)
                cmds.setAttr(annotation+'.template', 1)
                cmds.setAttr(annotLoc+'.visibility', 0)
                # set annotation visibility as a display option attribute:
                cmds.addAttr(self.ikCornerCtrl, longName="displayAnnotation", attributeType='bool', keyable=True)
                cmds.setAttr(self.ikCornerCtrl+".displayAnnotation", 1)
                cmds.connectAttr(self.ikCornerCtrl+".displayAnnotation", annotation+".visibility", force=True)
                
                # prepare groups to rotate and translate automatically:
                cmds.aimConstraint(annotLoc, self.ikCornerCtrl, aimVector=(0.0, 0.0, -1.0), upVector=(0.0, 1.0, 0.0), name=self.ikCornerCtrl+"_AimConstraint")
                ctrls.setLockHide([self.ikCornerCtrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                self.cornerGrp       = cmds.group(empty=True, name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_PoleVector_Grp", absolute=True)
                self.cornerOrientGrp = cmds.group(empty=True, name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_PoleVectorOrient_Grp", absolute=True)
                tempToDelA = cmds.parentConstraint(self.ikExtremCtrl, self.cornerGrp, maintainOffset=False)
                tempToDelB = cmds.parentConstraint(self.ikExtremCtrl, self.cornerOrientGrp, maintainOffset=False)
                cmds.delete(tempToDelA, tempToDelB)
                cmds.parent(self.ikCornerCtrlZero, self.cornerGrp, absolute=True)
                self.zeroCornerGrp = utils.zeroOut([self.cornerGrp])[0]
                self.ikPoleVectorCtrlZeroList.append(self.zeroCornerGrp)
                
                # working with autoOrient of poleVector:
                cmds.addAttr(self.ikCornerCtrl, longName=self.langDic[self.langName]['c_autoOrient'], attributeType='float', minValue=0, maxValue=1, defaultValue=1, keyable=True)
                if self.limbType == self.langDic[self.langName]['m028_arm']:
                    cmds.setAttr(self.ikCornerCtrl+'.'+self.langDic[self.langName]['c_autoOrient'], 0)
                if self.limbStyle == self.langDic[self.langName]['m042_default']:
                    self.cornerOrient = cmds.orientConstraint(self.cornerOrientGrp, self.ikExtremCtrl, self.cornerGrp, skip=("y", "z"), maintainOffset=True, name=self.cornerGrp+"_OrientConstraint")[0]
                else: # biped, quadruped, quadSpring
                    if self.limbType == self.langDic[self.langName]['m028_arm']:
                        self.cornerOrient = cmds.orientConstraint(self.cornerOrientGrp, self.ikExtremCtrl, self.cornerGrp, skip=("y", "z"), maintainOffset=True, name=self.cornerGrp+"_OrientConstraint")[0]
                    else: # leg
                        self.cornerOrient = cmds.orientConstraint(self.cornerOrientGrp, self.ikExtremCtrl, self.cornerGrp, skip=("x", "z"), maintainOffset=True, name=self.cornerGrp+"_OrientConstraint")[0]
                self.cornerOrientRev = cmds.createNode('reverse', name=side+self.userGuideName+"_CornerOrient_Rev")
                cmds.connectAttr(self.ikCornerCtrl+'.'+self.langDic[self.langName]['c_autoOrient'], self.cornerOrientRev+".inputX", force=True)
                cmds.connectAttr(self.cornerOrientRev+'.outputX', self.cornerOrient+"."+self.cornerOrientGrp+"W0", force=True)
                cmds.connectAttr(self.ikCornerCtrl+'.'+self.langDic[self.langName]['c_autoOrient'], self.cornerOrient+"."+self.ikExtremCtrl+"W1", force=True)
                
                # working with follow of poleVector:
                self.cornerPoint = cmds.pointConstraint(self.cornerOrientGrp, self.ikExtremCtrl, self.cornerGrp, maintainOffset=True, name=self.cornerGrp+"_ParentConstraint")[0]
                cmds.addAttr(self.ikCornerCtrl, longName=self.langDic[self.langName]['c_Follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=1, keyable=True)
                self.cornerPointRev = cmds.createNode('reverse', name=side+self.userGuideName+"_CornerPoint_Rev")
                cmds.connectAttr(self.ikCornerCtrl+'.'+self.langDic[self.langName]['c_Follow'], self.cornerPointRev+".inputX", force=True)
                cmds.connectAttr(self.cornerPointRev+'.outputX', self.cornerPoint+"."+self.cornerOrientGrp+"W0", force=True)
                cmds.connectAttr(self.ikCornerCtrl+'.'+self.langDic[self.langName]['c_Follow'], self.cornerPoint+"."+self.ikExtremCtrl+"W1", force=True)
                
                
                # stretch system:
                kNameList  = [beforeName, self.limbType.capitalize()]
                distBetGrp = cmds.group(empty=True, name=side+self.userGuideName+"_DistBet_Grp")
                
                # creating attributes:
                cmds.addAttr(self.ikExtremCtrl, longName="stretchable", attributeType='float', minValue=0, defaultValue=1, keyable=True)
                cmds.addAttr(self.ikExtremCtrl, longName="stretchType", attributeType='enum', enumName="negative:positive:both", defaultValue=1, keyable=False)
                
                # creating distance betweens, multiplyDivides and reverse nodes:
                self.distBetweenList = ctrls.distanceBet(self.ikJointList[1], self.ikStretchExtremLoc, name=side+self.userGuideName+"_"+kNameList[1]+"_DistBet", keep=True)
                cmds.parent(self.distBetweenList[2], self.distBetweenList[3], self.distBetweenList[4], distBetGrp)
                
                # stretch permited only in ik mode:
                self.stretchIkFkMultDiv  = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_"+kNameList[1]+"_StretchIkFk_MD")
                cmds.connectAttr(self.ikFkRevList[1]+'.outputX', self.stretchIkFkMultDiv+".input1X", force=True)
                cmds.connectAttr(self.worldRef+'.globalStretch', self.stretchIkFkMultDiv+".input2X", force=True)
                
                # turn On or Off the stretch using Stretchable attribute in the ikCtrl:
                self.stretchOnOffMultDiv = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_"+kNameList[1]+"_StretchOnOff_MD")
                cmds.connectAttr(self.stretchIkFkMultDiv+'.outputX', self.stretchOnOffMultDiv+".input1X", force=True)
                cmds.connectAttr(self.ikExtremCtrl+'.stretchable', self.stretchOnOffMultDiv+".input2X", force=True)
                
                # connect values in the W0 or reverse in W1 to ikCtrl lead or not the nullC of the distanceBetween not (controling the pointConstraint):
                self.stretchRev = cmds.createNode('reverse', name=side+self.userGuideName+"_"+kNameList[1]+"_Stretch_Rev")
                cmds.connectAttr(self.stretchOnOffMultDiv+'.outputX', self.stretchRev+".inputX", force=True)
                cmds.connectAttr(self.stretchOnOffMultDiv+'.outputX', self.distBetweenList[5]+"."+self.ikStretchExtremLoc+"W0", force=True)
                cmds.connectAttr(self.stretchRev+'.outputX', self.distBetweenList[5]+"."+self.distBetweenList[4]+"W1", force=True)
                
                # here we calculate the stretch comparing with the current distance result:
                self.stretchMultDiv = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_"+kNameList[1]+"_Stretch_MD")
                cmds.connectAttr(self.distBetweenList[1]+'.distance', self.stretchMultDiv+".input1X", force=True)
                
                startStretchValue = ctrls.distanceBet(self.ikJointList[1], self.ikJointList[2], keep=False)[0] + ctrls.distanceBet(self.ikJointList[2], self.ikStretchExtremLoc, keep=False)[0]
                startStretchValue = startStretchValue * 0.9999
                cmds.setAttr(self.stretchMultDiv+'.input2X', startStretchValue)
                
                cmds.setAttr(self.stretchMultDiv+'.operation', 2)
                
                # use a condition node to check what value will be send to joints scale:
                self.stretchCond = cmds.createNode('condition', name=side+self.userGuideName+"_"+kNameList[1]+"_Stretch_Cnd")
                cmds.connectAttr(self.stretchMultDiv+'.outputX', self.stretchCond+".firstTerm", force=True)
                cmds.connectAttr(self.stretchMultDiv+'.outputX', self.stretchCond+".colorIfTrueR", force=True)
                cmds.setAttr(self.stretchCond+'.secondTerm', 1.0)
                
                # choosing what type of operation will be used (calculate as a Case):
                # negative (0) = 4
                # positive (1) = 2
                # both     (2) = 1
                # else     (x) = 2
                self.stretchCondOp0 = cmds.createNode('condition', name=side+self.userGuideName+"_"+kNameList[1]+"_StretchOp0_Cnd")
                self.stretchCondOp1 = cmds.createNode('condition', name=side+self.userGuideName+"_"+kNameList[1]+"_StretchOp1_Cnd")
                self.stretchCondOp2 = cmds.createNode('condition', name=side+self.userGuideName+"_"+kNameList[1]+"_StretchOp2_Cnd")
                cmds.setAttr(self.stretchCondOp0+'.colorIfTrueR', 4)
                cmds.setAttr(self.stretchCondOp1+'.colorIfTrueR', 2)
                cmds.setAttr(self.stretchCondOp2+'.colorIfTrueR', 1)
                cmds.setAttr(self.stretchCondOp2+'.colorIfFalseR', 2)
                cmds.setAttr(self.stretchCondOp1+'.secondTerm', 1)
                cmds.setAttr(self.stretchCondOp2+'.secondTerm', 2)
                cmds.connectAttr(self.ikExtremCtrl+'.stretchType', self.stretchCondOp0+'.firstTerm', force=True)
                cmds.connectAttr(self.ikExtremCtrl+'.stretchType', self.stretchCondOp1+'.firstTerm', force=True)
                cmds.connectAttr(self.ikExtremCtrl+'.stretchType', self.stretchCondOp2+'.firstTerm', force=True)
                cmds.connectAttr(self.stretchCondOp1+'.outColorR', self.stretchCondOp0+'.colorIfFalseR', force=True)
                cmds.connectAttr(self.stretchCondOp2+'.outColorR', self.stretchCondOp1+'.colorIfFalseR', force=True)
                cmds.connectAttr(self.stretchCondOp0+".outColorR", self.stretchCond+'.operation', force=True)
                
                for j in range(1, 4):
                    cmds.connectAttr(self.stretchCond+'.outColorR', self.skinJointList[j]+'.scaleZ', force=True)
                    cmds.connectAttr(self.stretchCond+'.outColorR', self.ikJointList[j]+'.scaleZ', force=True)
                
                # do ikHandle off when before is fk in order to turn off the stretch:
                cmds.parentConstraint(self.skinJointList[0], self.distBetweenList[4], maintainOffset=True, name=self.distBetweenList[4]+"_ParentConstraint")
                
                #(James) if we use the ribbon controls we won't implement the forearm control
                
                # create the forearm control if limb type is arm and there is not bend (ribbon) implementation:
                if self.limbType == self.langDic[self.langName]['m028_arm'] and self.getHasBend() == False:
                    # create forearm joint:
                    forearmJnt = cmds.duplicate(self.skinJointList[2], name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_forearm']+self.jSufixList[0])[0]
                    # delete its children:
                    childList = cmds.listRelatives(forearmJnt, children=True, fullPath=True)
                    cmds.delete(childList)
                    cmds.parent(forearmJnt, self.skinJointList[2])
                    # move forearmJnt to correct position:
                    tempDist = ctrls.distanceBet(self.skinJointList[2], self.skinJointList[3])[0]
                    txElbow = cmds.xform(self.skinJointList[2], worldSpace=True, translation=True, query=True)[0]
                    txWrist = cmds.xform(self.skinJointList[3], worldSpace=True, translation=True, query=True)[0]
                    if (txWrist - txElbow) > 0:
                        forearmDistZ = tempDist/3
                    else:
                        forearmDistZ = -(tempDist/3)
                    cmds.move(0,0, forearmDistZ, forearmJnt, localSpace=True, worldSpaceDistance=True)
                    # create forearmCtrl:
                    forearmCtrl = cmds.circle(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_forearm']+"_Ctrl", ch=False, o=True, nr=(0, 0, 1), d=1, s=8, radius=(self.ctrlRadius * 0.75))[0]
                    forearmGrp  = cmds.group(forearmCtrl, name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_forearm']+"_Grp")
                    forearmZero = cmds.group(forearmGrp,  name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_forearm']+"_Zero")
                    tempToDelete = cmds.parentConstraint(forearmJnt, forearmZero, maintainOffset=False)
                    cmds.delete(tempToDelete)
                    cmds.parentConstraint(self.skinJointList[2], forearmZero, maintainOffset=True, name=forearmZero+"_ParentConstraint")
                    cmds.orientConstraint(forearmCtrl, forearmJnt, skip=["x","y"], maintainOffset=True, name=forearmJnt+"_OrientConstraint")
                    # create attribute to forearm autoRotate:
                    cmds.addAttr(forearmCtrl, longName=self.langDic[self.langName]['c_autoOrient'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.75, keyable=True)
                    ctrls.setLockHide([forearmCtrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'sx', 'sy', 'sz', 'v'])
                    # make rotate connections:
                    forearmMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_forearm']+"_MD")
                    cmds.connectAttr(forearmCtrl+'.'+self.langDic[self.langName]['c_autoOrient'], forearmMD+'.input1X')
                    cmds.connectAttr(self.skinJointList[3]+'.rotateZ', forearmMD+'.input2X')
                    cmds.connectAttr(forearmMD+'.outputX', forearmGrp+'.rotateZ')
                
                # creating a group to receive the reverseFootCtrlGrp (if module integration is on):
                self.ikFkBlendGrpToRevFoot = cmds.group(empty=True, name=side+self.userGuideName+"_IkFkBlendGrpToRevFoot_Grp")
                self.ikFkBlendGrpToRevFootList.append(self.ikFkBlendGrpToRevFoot)
                tempToDelToRFpc = cmds.parentConstraint(self.ikExtremCtrl, self.ikFkBlendGrpToRevFoot, maintainOffset=False)
                cmds.delete(tempToDelToRFpc)
                
                # this next parentConstraint does not calculate correctly when we use negative scale
                # then we will use a workarround in order to set a good offset
                parentConstToRFOffset = cmds.parentConstraint(self.ikExtremCtrl, self.fkCtrlList[len(self.fkCtrlList)-1], self.ikNSJointList[-2], self.ikFkBlendGrpToRevFoot, maintainOffset=True, name=self.ikFkBlendGrpToRevFoot+"_ParentConstraint")[0]
                self.parentConstToRFOffsetList.append(parentConstToRFOffset)
                cmds.connectAttr(self.worldRef+"."+side+self.limbType+str(dpAR_count)+'_IkFkBlend', parentConstToRFOffset+"."+self.fkCtrlList[len(self.fkCtrlList)-1]+"W1", force=True)

                # organize to be corriged the offset when we will apply the parentConstraint
                # there is a bug in the Maya calculation if we use negative scale (mirrored :P)
                cmds.addAttr(parentConstToRFOffset, longName="mustCorrectOffset", attributeType='bool', keyable=False)
                cmds.addAttr(parentConstToRFOffset, longName="fixOffsetX", attributeType='long', keyable=False)
                cmds.addAttr(parentConstToRFOffset, longName="fixOffsetY", attributeType='long', keyable=False)
                cmds.addAttr(parentConstToRFOffset, longName="fixOffsetZ", attributeType='long', keyable=False)
                
                if self.limbStyle != self.langDic[self.langName]['m042_default']:
                    # these options are valides for Biped, Quadruped and Quadruped Spring legs
                    if self.mirrorAxis != 'off':
                        if s == 1: # mirrored guide
                            if self.limbType == self.langDic[self.langName]['m030_leg']:
                                for axis in self.mirrorAxis:
                                    if axis == "X":
                                        # must fix offset of the parentConstrain in the future when this will be integrated
                                        cmds.setAttr(parentConstToRFOffset+".mustCorrectOffset", 1)
                                        cmds.setAttr(parentConstToRFOffset+".fixOffsetX", 90)
                                        cmds.setAttr(parentConstToRFOffset+".fixOffsetY", 180)
                                        cmds.setAttr(parentConstToRFOffset+".fixOffsetZ", -90)
                    
                    if self.limbStyle == self.langDic[self.langName]['m043_quadSpring']:
                        # fix the group for the ikSpringSolver to avoid Maya bug about rotation from masterCtrl :P
                        cmds.parent(self.ikJointList[1], world=True)
                        self.fixIkSpringSolverGrp = cmds.group(self.ikJointList[1], name=side+self.userGuideName+"_IkFixSpringSolver_Grp")
                        self.fixIkSpringSolverGrpList.append(self.fixIkSpringSolverGrp)
                        cmds.setAttr(self.fixIkSpringSolverGrp+".visibility", 0)
                        cmds.parentConstraint(self.ikJointList[0], self.ikJointList[1], maintainOffset=True, name=self.ikJointList[1]+"_ParentConstraint")
                        
                    if self.limbStyle == self.langDic[self.langName]['m037_quadruped'] or self.limbStyle == self.langDic[self.langName]['m043_quadSpring']:
                        # tell main script to create parent constraint from chestA to ikCtrl for front legs
                        self.quadFrontLegList.append(self.ikExtremCtrlOrientGrp)
                
                # work with not stretch ik setup:
                stretchDifMD = cmds.shadingNode('multiplyDivide', asUtility=True, name=side+self.userGuideName+"_Stretchable_Dif_MD")
                cmds.connectAttr(self.ikExtremCtrl+".stretchable", stretchDifMD+".input1X", force=True)
                cmds.connectAttr(revNode+".outputX", stretchDifMD+".input2X", force=True)
                
                ikStretchCtrlCnd = cmds.shadingNode('condition', asUtility=True, name=side+self.userGuideName+"_ikStretchCtrl_Cnd")
                cmds.setAttr(ikStretchCtrlCnd+".secondTerm", 1)
                cmds.setAttr(ikStretchCtrlCnd+".operation", 3)
                cmds.connectAttr(stretchDifMD+".outputX", ikStretchCtrlCnd+".colorIfFalseR", force=True)
                cmds.connectAttr(revNode+".outputX", ikStretchCtrlCnd+".colorIfTrueR", force=True)
                cmds.connectAttr(self.ikExtremCtrl+".stretchable", ikStretchCtrlCnd+".firstTerm", force=True)
                cmds.connectAttr(ikStretchCtrlCnd+".outColorR", parentConstToRFOffset+"."+self.ikExtremCtrl+"W0", force=True)
                
                ikStretchDifPMA = cmds.shadingNode('plusMinusAverage', asUtility=True, name=self.userGuideName+"_Stretch_Dif_PMA")
                cmds.setAttr(ikStretchDifPMA+".operation", 2)
                cmds.connectAttr(revNode+".outputX", ikStretchDifPMA+".input1D[0]", force=True)
                cmds.connectAttr(self.ikExtremCtrl+".stretchable", ikStretchDifPMA+".input1D[1]", force=True)
                
                ikStretchCnd = cmds.shadingNode('condition', asUtility=True, name=side+self.userGuideName+"_ikStretch_Cnd")
                cmds.setAttr(ikStretchCnd+".operation", 3)
                cmds.setAttr(ikStretchCnd+".secondTerm", 1)
                cmds.connectAttr(ikStretchDifPMA+".output1D", ikStretchCnd+".colorIfFalseR", force=True)
                cmds.connectAttr(self.ikExtremCtrl+".stretchable", ikStretchCnd+".firstTerm", force=True)
                
                ikStretchClp = cmds.shadingNode('clamp', asUtility=True, name=side+self.userGuideName+"_IkStretch_Clp")
                cmds.setAttr(ikStretchClp+".maxR", 1)
                cmds.connectAttr(ikStretchCnd+".outColorR", ikStretchClp+".inputR", force=True)
                cmds.connectAttr(ikStretchClp+".outputR", parentConstToRFOffset+"."+self.ikNSJointList[-2]+"W2", force=True)
                
                
                # create a masterModuleGrp to be checked if this rig exists:
                if self.limbType == self.langDic[self.langName]['m028_arm']:
                    # (James) not implementing the forearm control if we use ribbons (yet)
                    if self.getHasBend() == True:
                        # do not use forearm control
                        self.toCtrlHookGrp = cmds.group(self.zeroFkCtrlGrp, self.zeroCornerGrp, self.ikExtremCtrlZero, self.cornerOrientGrp, distBetGrp, self.origFromList[0], self.origFromList[1], self.ikFkBlendGrpToRevFoot, self.worldRef, name=side+self.userGuideName+"_Control_Grp")
                    else:
                        # use forearm control
                        self.toCtrlHookGrp = cmds.group(self.zeroFkCtrlGrp, self.zeroCornerGrp, self.ikExtremCtrlZero, self.cornerOrientGrp, forearmZero, distBetGrp, self.origFromList[0], self.origFromList[1], self.ikFkBlendGrpToRevFoot, self.worldRef, name=side+self.userGuideName+"_Control_Grp")
                else:
                    self.toCtrlHookGrp = cmds.group(self.zeroFkCtrlGrp, self.zeroCornerGrp, self.ikExtremCtrlZero, self.cornerOrientGrp, distBetGrp, self.origFromList[0], self.origFromList[1], self.ikFkBlendGrpToRevFoot, self.worldRef, name=side+self.userGuideName+"_Control_Grp")
                self.toScalableHookGrp = cmds.group(self.skinJointList[0], self.ikJointList[0], self.fkJointList[0], self.ikNSJointList[0], name=side+self.userGuideName+"_Joint_Grp")
                cmds.parentConstraint(self.toCtrlHookGrp, self.toScalableHookGrp, maintainOffset=True, name=self.toScalableHookGrp+"_ParentConstraint")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, ikHandleGrp, ikHandleNotStretchGrp, name=side+self.userGuideName+"_Grp")
                
                
                # new ribbon feature by James do Carmo, thanks!
                # not using bend or ikFkSnap systems to quadruped
                if self.limbStyle != self.langDic[self.langName]['m037_quadruped'] and self.limbStyle != self.langDic[self.langName]['m043_quadSpring']:
                    #(James) add bend to limb
                    if self.getHasBend():
                        import jcRibbon as rb
                        reload(rb)
                        num = self.getBendJoints()
                        iniJoint = side+self.userGuideName+"_"+mainName+'_Jnt'
                        corner = side+self.userGuideName+"_"+cornerName+'_Jnt'
                        splited = self.userGuideName.split('_')
                        prefix =''.join(side)
                        name = ''
                        if len(splited) > 1:
                            prefix+=splited[0]
                            name+=splited[1]
                        else:
                            name+=self.userGuideName
                        loc = cmds.spaceLocator(n=side+self.userGuideName+'_auxOriLoc',p=(0,0,0))[0]
                        
                        cmds.delete(cmds.parentConstraint(iniJoint,loc,mo=False,w=1))
                        
                        if name == self.langDic[self.langName]['c_leg_main']: # leg
                            if s == 0: # left side (or first side = original)
                                cmds.delete(cmds.aimConstraint(corner,loc,mo=False,weight=2,aimVector=(1,0,0),upVector=(0,1,0),worldUpType="vector",worldUpVector=(1,0,0)))
                            else:
                                cmds.delete(cmds.aimConstraint(corner,loc,mo=False,weight=2,aimVector=(1,0,0),upVector=(0,1,0),worldUpType="vector",worldUpVector=(-1,0,0)))
                        else:
                            cmds.delete(cmds.aimConstraint(corner,loc,mo=False,weight=2,aimVector=(1,0,0),upVector=(0,1,0),worldUpType="vector",worldUpVector=(0,1,0)))
                        
                        if self.limbType == self.langDic[self.langName]['m028_arm']:
                            if s == 0:
                                self.bendGrps = rb.addRibbonToLimb(prefix,name,loc,iniJoint,'x',num,mirror=False,ctrlRadius=(self.ctrlRadius * 0.5), arm=True, worldRef=self.worldRef)
                            else:
                                self.bendGrps = rb.addRibbonToLimb(prefix,name,loc,iniJoint,'x',num,mirror=False,ctrlRadius=(self.ctrlRadius * 0.5), side=1, arm=True, worldRef=self.worldRef)
                        else:
                            if s == 0:
                                self.bendGrps = rb.addRibbonToLimb(prefix,name,loc,iniJoint,'x',num,mirror=False,ctrlRadius=(self.ctrlRadius * 0.5), arm=False, worldRef=self.worldRef)
                            else:
                                self.bendGrps = rb.addRibbonToLimb(prefix,name,loc,iniJoint,'x',num,mirror=False,ctrlRadius=(self.ctrlRadius * 0.5), side=1, arm=False, worldRef=self.worldRef)
                        cmds.delete(loc)

                        cmds.parent(self.bendGrps['ctrlsGrp'], self.toCtrlHookGrp)
                        cmds.parent(self.bendGrps['scaleGrp'], self.toScalableHookGrp)
                        cmds.parent(self.bendGrps['staticGrp'], self.toStaticHookGrp)
                        
                        self.bendGrpList = self.bendGrps['bendGrpList']
                        self.extraBendList = self.bendGrps['extraBendGrp']
                        
                        if self.bendGrpList:
                            if not cmds.objExists(self.worldRef+".bends"):
                                cmds.addAttr(self.worldRef, longName='bends', attributeType='long', minValue=0, maxValue=1, defaultValue=1, keyable=True)
                                cmds.addAttr(self.worldRef, longName='extraBends', attributeType='long', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                            for bendGrpNode in self.bendGrpList:
                                cmds.connectAttr(self.worldRef+".bends", bendGrpNode+".visibility", force=True)
                            for extraBendGrp in self.extraBendList:
                                cmds.connectAttr(self.worldRef+".extraBends", extraBendGrp+".visibility", force=True)
                        
                        # correct joint skin naming:
                        for jntIndex in range(1, len(self.skinJointList)-2):
                            self.skinJointList[jntIndex] = self.skinJointList[jntIndex].replace("_Jnt", "_Jxt")
                
                if loadedIkFkSnap:
                    # do otherCtrlList get extraCtrlList from bendy
                    otherCtrlList = []
                    if self.getHasBend():
                        otherCtrlList = self.bendGrps['extraCtrlList']
                    otherCtrlList.append(self.toParentExtremCtrl)
                    # create a ghost value in order to avoid ikFkNetwork crashes without footRoll attributes:
                    cmds.addAttr(self.worldRef, longName='footRollPlaceHolder', attributeType='long', defaultValue=0, keyable=False)
                    # create ikFkNetwork:
                    data = sqIkFkTools.IkFkNetwork()
                    # initialise ikFkNetwork:
                    if self.limbStyle == self.langDic[self.langName]['m037_quadruped'] or self.limbStyle == self.langDic[self.langName]['m043_quadSpring']:
                        data.init(
                                self.ikExtremCtrl,
                                self.ikCornerCtrl,
                                [self.ikJointList[1], self.ikJointList[2], self.ikJointList[3], self.ikJointList[4]],
                                [self.fkCtrlList[1], self.fkCtrlList[2], self.fkCtrlList[3], self.ikJointList[4]],
                                self.worldRef+'.'+side+self.limbType+str(dpAR_count)+'_IkFkBlend',
                                footRollAtts=[self.worldRef+'.footRollPlaceHolder'],
                                otherCtrls=otherCtrlList
                            )
                    else:
                        data.init(
                                self.ikExtremCtrl,
                                self.ikCornerCtrl,
                                [self.ikJointList[1], self.ikJointList[2], self.ikJointList[3]],
                                [self.fkCtrlList[1], self.fkCtrlList[2], self.fkCtrlList[3]],
                                self.worldRef+'.'+side+self.limbType+str(dpAR_count)+'_IkFkBlend',
                                footRollAtts=[self.worldRef+'.footRollPlaceHolder'],
                                otherCtrls=otherCtrlList
                            )
                    # serialise ikFkNetwork:
                    ikFkNet = libSerialization.export_network(data)
                    ikFkNet = cmds.rename(ikFkNet.__melobject__(), side+self.userGuideName+"_"+str(dpAR_count)+"_IkFkNetwork")
                    self.ikFkNetworkList.append(ikFkNet)
                    if self.limbStyle != self.langDic[self.langName]['m037_quadruped'] and self.limbStyle != self.langDic[self.langName]['m043_quadSpring']:
                        lastIndex = len(otherCtrlList)
                        if self.getHasBend():
                            cmds.connectAttr(self.bendGrps['ctrlList'][0]+".message", ikFkNet+".otherCtrls["+str(lastIndex+1)+"]", force=True)
                            cmds.connectAttr(self.bendGrps['ctrlList'][1]+".message", ikFkNet+".otherCtrls["+str(lastIndex+2)+"]", force=True)
                            cmds.connectAttr(self.bendGrps['ctrlList'][2]+".message", ikFkNet+".otherCtrls["+str(lastIndex+3)+"]", force=True)
                        elif self.limbType == self.langDic[self.langName]['m028_arm']:
                            cmds.connectAttr(forearmCtrl+".message", ikFkNet+".otherCtrls["+str(lastIndex+1)+"]", force=True)

                self.integrateOrigFromList.append(self.origFromList)
                
                # add hook attributes to be read when rigging integrated modules:
                utils.addHook(objName=self.toCtrlHookGrp, hookType='ctrlHook')
                utils.addHook(objName=self.skinJointList[len(self.skinJointList)-1], hookType='revFootExtremJointHook')
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
                                                "ikCtrlList"                : self.ikExtremCtrlList,
                                                "ikCtrlZeroList"            : self.ikExtremCtrlZeroList,
                                                "ikPoleVectorZeroList"      : self.ikPoleVectorCtrlZeroList,
                                                "ikHandleGrpList"           : self.ikHandleToRFGrpList,
                                                "ikHandlePointConstList"    : self.ikHandlePointConstList,
                                                "ikFkBlendGrpToRevFootList" : self.ikFkBlendGrpToRevFootList,
                                                "worldRefList"              : self.worldRefList,
                                                "worldRefShapeList"         : self.worldRefShapeList,
                                                "limbType"                  : self.limbType,
                                                "extremJntList"             : self.extremJntList,
                                                "parentConstToRFOffsetList" : self.parentConstToRFOffsetList,
                                                "fixIkSpringSolverGrpList"  : self.fixIkSpringSolverGrpList,
                                                "limbStyle"                 : self.limbStyle,
                                                "quadFrontLegList"          : self.quadFrontLegList,
                                                "integrateOrigFromList"     : self.integrateOrigFromList,
                                                "ikStretchExtremLoc"        : self.ikStretchExtremLocList,
                                                "ikFkNetworkList"           : self.ikFkNetworkList,
                                                "limbManualVolume"          : "limbManualVolume",
                                                }
                                    }