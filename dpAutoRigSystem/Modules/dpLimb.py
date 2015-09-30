# importing libraries:
import maya.cmds as cmds
import dpControls as ctrls
import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout

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
        self.cvBeforeLoc   = ctrls.cvJointLoc(ctrlName=self.guideName+"_before", r=0.3)
        self.cvMainLoc     = ctrls.cvJointLoc(ctrlName=self.guideName+"_main", r=0.5)
        self.cvCornerALoc  = ctrls.cvLocator(ctrlName=self.guideName+"_cornerA", r=0.3)
        self.cvCornerBLoc  = ctrls.cvLocator(ctrlName=self.guideName+"_cornerB", r=0.3)
        self.cvExtremLoc   = ctrls.cvJointLoc(ctrlName=self.guideName+"_extrem", r=0.5)
        self.cvUpVectorLoc = ctrls.cvLocator(ctrlName=self.guideName+"_cornerUpVector", r=0.5)
        
        # create jointGuides:
        cmds.select(clear=True)
        self.jGuideBefore  = cmds.joint(name=self.guideName+"_jGuideBefore", radius=0.001)
        self.jGuideMain    = cmds.joint(name=self.guideName+"_jGuideMain", radius=0.001)
        self.jGuideCornerA = cmds.joint(name=self.guideName+"_jGuideCornerA", radius=0.001)
        self.jGuideCornerB = cmds.joint(name=self.guideName+"_jGuideCornerB", radius=0.001)
        self.jGuideExtrem  = cmds.joint(name=self.guideName+"_jGuideExtrem", radius=0.001)
        
        # create cornerGroups:
        self.cornerAGrp = cmds.group(self.cvCornerALoc, name=self.cvCornerALoc+"_grp")
        self.cornerBGrp = cmds.group(self.cvCornerBLoc, name=self.cvCornerBLoc+"_grp")
        
        # set jointGuides as templates:
        cmds.setAttr(self.jGuideBefore+".template", 1)
        cmds.setAttr(self.jGuideMain+".template", 1)
        cmds.setAttr(self.jGuideCornerA+".template", 1)
        cmds.setAttr(self.jGuideCornerB+".template", 1)
        cmds.setAttr(self.jGuideExtrem+".template", 1)
        cmds.parent(self.jGuideBefore, self.moduleGrp, relative=True)
        
        # create cvEnd:
        self.cvEndJoint = ctrls.cvLocator(ctrlName=self.guideName+"_jointEnd", r=0.1)
        cmds.parent(self.cvEndJoint, self.cvExtremLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_jGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.parent(self.jGuideEnd, self.jGuideExtrem)
        
        # make parents between cvLocs:
        cmds.parent(self.cvBeforeLoc, self.cvMainLoc, self.cornerAGrp, self.cornerBGrp, self.cvExtremLoc, self.cvUpVectorLoc, self.moduleGrp)
        
        # connect cvLocs in jointGuides:
        ctrls.directConnect(self.cvBeforeLoc, self.jGuideBefore, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        cmds.parentConstraint(self.cvMainLoc, self.jGuideMain, maintainOffset=False, name=self.jGuideMain+"_parentConstraint")
        cmds.parentConstraint(self.cvCornerALoc, self.jGuideCornerA, maintainOffset=False, name=self.jGuideCornerA+"_parentConstraint")
        cmds.parentConstraint(self.cvCornerBLoc, self.jGuideCornerB, maintainOffset=False, name=self.jGuideCornerB+"_parentConstraint")
        cmds.parentConstraint(self.cvExtremLoc, self.jGuideExtrem, maintainOffset=False, name=self.jGuideExtrem+"_parentConstraint")
        
        # align cornerLocs:
        cmds.aimConstraint(self.cvMainLoc, self.cornerAGrp, aimVector=(0.0, 0.0, -1.0), upVector=(1.0, 0.0, 0.0), worldUpType="object", worldUpObject=self.cvUpVectorLoc, name=self.cornerAGrp+"_aimConstraint")
        self.aim = cmds.aimConstraint(self.cvExtremLoc, self.cornerBGrp, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0), worldUpType="object", worldUpObject=self.cvUpVectorLoc, name=self.cornerBGrp+"_aimConstraint")
        
        # limit, lock and hide cvEnd:
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        
        # creating relationship of corners A and B:
        self.cornerAPointGrp = cmds.group(self.cornerAGrp, name=self.cornerAGrp+"_zero")
        self.cornerBPointGrp = cmds.group(self.cornerBGrp, name=self.cornerBGrp+"_zero")
        pointConstA = cmds.pointConstraint(self.cvMainLoc, self.cvExtremLoc, self.cornerAPointGrp, maintainOffset=False, name=self.cornerAPointGrp+"_pointConstraint")[0]
        pointConstB = cmds.pointConstraint(self.cvMainLoc, self.cvExtremLoc, self.cornerBPointGrp, maintainOffset=False, name=self.cornerBPointGrp+"_pointConstraint")[0]
        cmds.setAttr(pointConstA+'.'+self.cvMainLoc[self.cvMainLoc.rfind(":")+1:]+'W0', 0.52)
        cmds.setAttr(pointConstA+'.'+self.cvExtremLoc[self.cvExtremLoc.rfind(":")+1:]+'W1', 0.48)
        cmds.setAttr(pointConstB+'.'+self.cvMainLoc[self.cvMainLoc.rfind(":")+1:]+'W0', 0.48)
        cmds.setAttr(pointConstB+'.'+self.cvExtremLoc[self.cvExtremLoc.rfind(":")+1:]+'W1', 0.52)
        
        # transform cvLocs in order to put as a good limb guide:
        cmds.setAttr(self.cvBeforeLoc+".translateX", -0.5)
        cmds.setAttr(self.cvBeforeLoc+".translateZ", -2)
        cmds.setAttr(self.cvExtremLoc+".translateZ", 10)
        cmds.setAttr(self.cornerAGrp+".translateY", -0.75)
        cmds.setAttr(self.cornerBGrp+".translateY", -0.75)
        cmds.setAttr(self.moduleGrp+".translateX", 4)
        cmds.setAttr(self.moduleGrp+".rotateX", 90)
        cmds.setAttr(self.moduleGrp+".rotateZ", 90)
        # editing cornerUpVector:
        self.cvUpVectorGrp = cmds.group(self.cvUpVectorLoc, name=self.cvUpVectorLoc+"_grp")
        cmds.pointConstraint(self.cvExtremLoc, self.cvUpVectorGrp, maintainOffset=False, name=self.cvUpVectorGrp+"_pointConstraint")
        #cornerAGrpPos = cmds.xform(self.cvCornerALoc, rotatePivot=True, worldSpace=True, query=True)
        #cmds.move(cornerAGrpPos[0], cornerAGrpPos[1], cornerAGrpPos[2], self.cvUpVectorGrp, absolute=True)
        #cmds.makeIdentity(self.cvUpVectorLoc, apply=True)
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
        # for Default style:
        if style == self.langDic[self.langName]['m042_default']:
            cmds.setAttr(self.moduleGrp+".style", 0)
        # for Biped style:
        if style == self.langDic[self.langName]['m026_biped']:
            cmds.setAttr(self.moduleGrp+".style", 1)
        # for Quadruped style:
        if style == self.langDic[self.langName]['m037_quadruped']:
            cmds.setAttr(self.moduleGrp+".style", 2)
        # for Quadruped Spring style:
        if style == self.langDic[self.langName]['m043_quadSpring']:
            cmds.setAttr(self.moduleGrp+".style", 3)
    
    def changeType(self, type, *args):
        """ This function will modify the names of the rigged module to Arm of Leg options
            and rotate the moduleGrp in order to be more easy to user edit.
        """
        # re-declaring guide names:
        self.cvBeforeLoc = self.guideName+"_before"
        self.cvMainLoc   = self.guideName+"_main"
        self.cornerAGrp  = self.guideName+"_cornerA_grp"
        self.cornerBGrp  = self.guideName+"_cornerB_grp"
        self.cvExtremLoc = self.guideName+"_extrem"
        self.cvEndJoint  = self.guideName+"_jointEnd"
#        self.aim         = self.cornerBGrp+"_aimConstraint"
        self.cvUpVectorLoc = self.guideName+"_cornerUpVector"
        
        # reset translations:
        translateAttrList = ['tx', 'ty', 'tz']
        for tAttr in translateAttrList:
            cmds.setAttr(self.cvBeforeLoc+"."+tAttr, 0)
            cmds.setAttr(self.cvMainLoc+"."+tAttr, 0)
            cmds.setAttr(self.cornerAGrp+"."+tAttr, 0)
            cmds.setAttr(self.cornerBGrp+"."+tAttr, 0)
            cmds.setAttr(self.cvExtremLoc+"."+tAttr, 0)
            cmds.setAttr(self.cvUpVectorLoc+"."+tAttr, 0)
        
        # for Arm type:
        if type == self.langDic[self.langName]['m028_arm']:
            cmds.setAttr(self.moduleGrp+".type", 0)
            cmds.setAttr(self.cvBeforeLoc+".translateX", -1)
            cmds.setAttr(self.cvBeforeLoc+".translateZ", -4)
            cmds.setAttr(self.cvExtremLoc+".translateZ", 10)
            cmds.setAttr(self.cornerAGrp+".translateY", -0.75)
            cmds.setAttr(self.cornerBGrp+".translateY", -0.75)
            cmds.setAttr(self.cvEndJoint+".translateZ", 1.3)
            cmds.setAttr(self.moduleGrp+".rotateX", 90)
            cmds.setAttr(self.moduleGrp+".rotateY", 0)
            cmds.setAttr(self.moduleGrp+".rotateZ", 90)
#            cmds.setAttr(self.aim+'.upVectorX',1)
            cmds.setAttr(self.cvUpVectorLoc+".translateY", -10)
        
        # for Leg type:
        elif type == self.langDic[self.langName]['m030_leg']:
            cmds.setAttr(self.moduleGrp+".type", 1)
            cmds.setAttr(self.cvBeforeLoc+".translateY", 1)
            cmds.setAttr(self.cvBeforeLoc+".translateZ", -2)
            cmds.setAttr(self.cvExtremLoc+".translateZ", 10)
            cmds.setAttr(self.cornerAGrp+".translateX", 0.75)
            cmds.setAttr(self.cornerBGrp+".translateX", 0.75)
            cmds.setAttr(self.cvEndJoint+".translateZ", 1.3)
            cmds.setAttr(self.moduleGrp+".rotateX", 0)
            cmds.setAttr(self.moduleGrp+".rotateY", -90)
            cmds.setAttr(self.moduleGrp+".rotateZ", 90)
#            cmds.setAttr(self.aim+'.upVectorX',-1)
            cmds.setAttr(self.cvUpVectorLoc+".translateX", 10)
            
        # reset rotations:
        self.reOrientGuide()
    
    
    def reOrientGuide(self, *args):
        """ This function reOrient guides orientations, creating temporary aimConstraints for them.
        """
        # re-declaring guide names:
        self.cvBeforeLoc  = self.guideName+"_before"
        self.cvMainLoc    = self.guideName+"_main"
        self.cvCornerALoc = self.guideName+"_cornerA"
        self.cvCornerBLoc = self.guideName+"_cornerB"
        self.cvExtremLoc  = self.guideName+"_extrem"
        
        # re-orient rotations:
        tempToDelBefore = cmds.aimConstraint(self.cvMainLoc, self.cvBeforeLoc, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0))
        tempToDelMain   = cmds.aimConstraint(self.cvCornerALoc, self.cvMainLoc, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0))
        cmds.delete(tempToDelBefore, tempToDelMain)
        cmds.setAttr(self.cvExtremLoc+'.rotateX', 0)
        cmds.setAttr(self.cvExtremLoc+'.rotateY', 0)
        cmds.setAttr(self.cvExtremLoc+'.rotateZ', 0)
        
        # for Arm type:
        type = cmds.getAttr(self.moduleGrp+".type")
        if type == 0:
            tempToDelExtrem = cmds.aimConstraint(self.cvCornerBLoc, self.cvExtremLoc, aimVector=(0.0, 0.0, -1.0), upVector=(1.0, 0.0, 0.0))
            cmds.delete(tempToDelExtrem)
    
    
    def rigModule(self, *args):
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            # declaring lists to send information for integration:
            self.ikExtremCtrlList, self.ikExtremCtrlZeroList, self.ikPoleVectorCtrlZeroList, self.ikHandleToRFGrpList, self.ikHandlePointConstList, self.ikFkBlendGrpToRevFootList, self.worldRefList, self.worldRefShapeList, self.extremJntList, self.parentConstToRFOffsetList, self.fixIkSpringSolverGrpList, self.quadFrontLegList = [], [], [], [], [], [], [], [], [], [], [], []
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
                    duplicated = cmds.duplicate(self.moduleGrp, name=side+self.userGuideName+'_guide_base')[0]
                    allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                    for item in allGuideList:
                        cmds.rename(item, side+self.userGuideName+"_"+item)
                    self.mirrorGrp = cmds.group(name="guide_base_grp", empty=True)
                    cmds.parent(side+self.userGuideName+'_guide_base', self.mirrorGrp, absolute=True)
                    # re-rename grp:
                    cmds.rename(self.mirrorGrp, side+self.userGuideName+'_'+self.mirrorGrp)
                    # do a group mirror with negative scaling:
                    if s == 1:
                        for axis in self.mirrorAxis:
                            cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.scale'+axis, -1)
            else: # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_guide_base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(self.userGuideName+'_guide_base', name="guide_base_grp", relative=True)
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
            # store the number of this guide by module type
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # run for all sides
            for s, side in enumerate(sideList):
                # getting type of limb:
                enumType = cmds.getAttr(self.moduleGrp+'.type')
                if enumType == 0:
                    self.limbType = "arm"
                elif enumType == 1:
                    self.limbType = "leg"
                # getting style of the limb:
                enumStyle = cmds.getAttr(self.moduleGrp+'.style')
                if enumStyle == 0:
                    self.limbStyle = "default"
                elif enumStyle == 1:
                    self.limbStyle = "biped"
                elif enumStyle == 2:
                    self.limbStyle = "quadruped"
                elif enumStyle == 3:
                    self.limbStyle = "quadSpring"
                
                # re-declaring guide names:
                self.cvBeforeLoc  = side+self.userGuideName+"_guide_before"
                self.cvMainLoc    = side+self.userGuideName+"_guide_main"
                self.cvCornerALoc = side+self.userGuideName+"_guide_cornerA"
                self.cvCornerBLoc = side+self.userGuideName+"_guide_cornerB"
                self.cvExtremLoc  = side+self.userGuideName+"_guide_extrem"
                self.cvEndJoint   = side+self.userGuideName+"_guide_jointEnd"
                self.cvLocList = [self.cvBeforeLoc, self.cvMainLoc, self.cvCornerALoc, self.cvCornerBLoc, self.cvExtremLoc]
                
                # getting names from dic:
                beforeName  = self.langDic[self.langName]['c_'+self.limbType+'_before']
                mainName    = self.langDic[self.langName]['c_'+self.limbType+'_main']
                cornerName  = self.langDic[self.langName]['c_'+self.limbType+'_corner']
                cornerAName = cornerName+"A"
                cornerBName = cornerName+"B"
                extremName  = self.langDic[self.langName]['c_'+self.limbType+'_extrem']
                self.jNameList = [beforeName, mainName, cornerAName, cornerBName, extremName]
                
                
                # creating joint to skin, ik and Fk chains:
                self.chainDic      = {}
                self.jSufixList    = ['_jnt', '_ik_jxt', '_fk_jxt']
                self.jEndSufixList = ['_jEnd', '_ik_jEnd', '_fk_jEnd']
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
                
                for o, skinJoint in enumerate(self.skinJointList):
                    if o < len(self.skinJointList)-1:
                        cmds.addAttr(skinJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                self.extremJntList.append(self.skinJointList[-2])
                
                # creating Fk controls and a hierarchy group to originedFrom data:
                self.fkCtrlList, self.origFromList = [], []
                for n, jName in enumerate(self.jNameList):
                    fkCtrl = cmds.circle(name=side+self.userGuideName+"_"+jName+"_fk_ctrl", ch=False, o=True, nr=(0, 0, 1), d=1, s=8, radius=self.ctrlRadius)[0]
                    self.fkCtrlList.append(fkCtrl)
                    cmds.setAttr(fkCtrl+'.visibility', keyable=False)
                    # creating the originedFrom attributes (in order to permit integrated parents in the future):
                    origGrp = cmds.group(empty=True, name=side+self.userGuideName+"_"+jName+"_origFrom_grp")
                    self.origFromList.append(origGrp)
                    utils.originedFrom(objName=origGrp, attrString=self.cvLocList[n][self.cvLocList[n].find("__")+1:].replace(":", "_"))
                    cmds.parentConstraint(self.skinJointList[n], origGrp, maintainOffset=False, name=origGrp+"_parentConstraint")
                    if n > 1:
                        cmds.parent(fkCtrl, self.fkCtrlList[n-1])
                        cmds.parent(origGrp, self.origFromList[n-1])
                # zeroOut controls:
                self.zeroFkCtrlList = utils.zeroOut(self.fkCtrlList)
                self.zeroFkCtrlGrp  = cmds.group(self.zeroFkCtrlList[0], self.zeroFkCtrlList[1], name=side+self.userGuideName+"_fkCtrl_grp")
                
                # working with position, orientation of joints and make an orientConstrain for Fk controls:
                for n in range(len(self.jNameList)):
                    tempToDelA = cmds.parentConstraint(self.cvLocList[n], self.skinJointList[n], maintainOffset=False)
                    tempToDelB = cmds.parentConstraint(self.cvLocList[n], self.ikJointList[n], maintainOffset=False)
                    tempToDelC = cmds.parentConstraint(self.cvLocList[n], self.fkJointList[n], maintainOffset=False)
                    tempToDelD = cmds.parentConstraint(self.cvLocList[n], self.zeroFkCtrlList[n], maintainOffset=False)
                    cmds.delete(tempToDelA, tempToDelB, tempToDelC, tempToDelD)
                    # freezeTransformations (rotates):
                    cmds.makeIdentity(self.skinJointList[n], self.ikJointList[n], self.fkJointList[n], apply=True, rotate=True)
                    # fk control leads fk joint:
                    cmds.orientConstraint(self.fkCtrlList[n], self.fkJointList[n], maintainOffset=True, name=side+self.userGuideName+"_"+self.jNameList[n]+"_fk_orientConstraint")
                    ctrls.setLockHide([self.fkCtrlList[n]], ['tx', 'ty', 'tz', 'sx', 'sy', 'sz'])
                # puting endJoints in the correct position:
                tempToDelE = cmds.parentConstraint(self.cvEndJoint, self.skinJointList[-1], maintainOffset=False)
                tempToDelF = cmds.parentConstraint(self.cvEndJoint, self.ikJointList[-1], maintainOffset=False)
                tempToDelG = cmds.parentConstraint(self.cvEndJoint, self.fkJointList[-1], maintainOffset=False)
                cmds.delete(tempToDelE, tempToDelF, tempToDelG)
                
                # creating an unique control to corner:
                self.cornerCtrl = cmds.circle(name=side+self.userGuideName+"_"+cornerName+"_fk_ctrl", ch=False, o=True, nr=(0, 0, 1), d=1, s=8, radius=self.ctrlRadius)[0]
                tempToDelC = cmds.parentConstraint(self.cvCornerALoc, self.cornerCtrl, maintainOffset=False)
                cmds.delete(tempToDelC)
                cmds.parent(self.cornerCtrl, self.fkCtrlList[1])
                utils.zeroOut([self.cornerCtrl])
                self.axisFree = 'Y'
                ctrls.setLockHide([self.cornerCtrl], ['tx', 'ty', 'tz', 'rx', 'rz', 'sx', 'sy', 'sz', 'v'])
                self.cornerMultDiv = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_"+cornerName+"_md")
                cmds.connectAttr(self.cornerCtrl+".rotate"+self.axisFree, self.cornerMultDiv+".input1"+self.axisFree, force=True)
                cmds.setAttr(self.cornerMultDiv+".input2"+self.axisFree, 0.5)
                self.jCornerName = [cornerAName, cornerBName]
                for c, corner in enumerate(self.jCornerName):
                    cmds.connectAttr(self.cornerMultDiv+".output"+self.axisFree, side+self.userGuideName+"_"+corner+"_fk_ctrl.rotate"+self.axisFree, force=True)
                    self.cornerShapeList = cmds.listRelatives(side+self.userGuideName+"_"+corner+"_fk_ctrl", children=True, shapes=True)
                    if self.cornerShapeList:
                        cmds.setAttr(self.cornerShapeList[0]+".visibility", 0)
                    cmds.rename(side+self.userGuideName+"_"+corner+"_fk_ctrl", side+self.userGuideName+"_"+corner+"_fk_ctrl_old")
                
                # parenting fkControls from 2 hierarchies (before and limb) using constraint:
                cmds.parentConstraint(self.skinJointList[0], self.zeroFkCtrlList[1], maintainOffset=True, name=self.zeroFkCtrlList[1]+"_parentConstraint")
                
                # creating a group reference to recept the attributes:
                self.worldRef = cmds.circle(name=side+self.userGuideName+"_worldRef", ch=False, o=True, nr=(0, 1, 0), d=3, s=8, radius=self.ctrlRadius)[0]
                cmds.addAttr(self.worldRef, longName=side+beforeName+str(dpAR_count)+'_IkFkBlend', attributeType='float', minValue=0, maxValue=1, defaultValue=1, keyable=True)
                cmds.addAttr(self.worldRef, longName=side+self.limbType+str(dpAR_count)+'_IkFkBlend', attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                if not cmds.objExists(self.worldRef+'.globalStretch'):
                    cmds.addAttr(self.worldRef, longName='globalStretch', attributeType='float', minValue=0, maxValue=1, defaultValue=1, keyable=True)
                self.worldRefList.append(self.worldRef)
                self.worldRefShape = cmds.listRelatives(self.worldRef, children=True, type='nurbsCurve')[0]
                self.worldRefShapeList.append(self.worldRefShape)
                
                # create orient constrain in order to blend ikFk:
                self.ikFkRevList = []
                for n in range(len(self.jNameList)):
                    orientConst = cmds.orientConstraint(self.ikJointList[n], self.fkJointList[n], self.skinJointList[n], maintainOffset=True, name=side+self.userGuideName+"_"+self.jNameList[n]+"_ikFkBlend_oc")[0]
                    if n == 0:
                        partLimbName = beforeName
                    else:
                        partLimbName = self.limbType
                    if n == 0 or n == 1:
                        revNode = cmds.createNode('reverse', name=side+self.userGuideName+"_"+partLimbName+"_rev")
                        cmds.connectAttr(self.worldRef+"."+side+partLimbName+str(dpAR_count)+'_IkFkBlend', revNode+".inputX", force=True)
                    else:
                        revNode = side+self.userGuideName+"_"+self.limbType+"_rev"
                    self.ikFkRevList.append(revNode)
                    # connecting ikFkBlend using the reverse node:
                    cmds.connectAttr(self.worldRef+"."+side+partLimbName+str(dpAR_count)+'_IkFkBlend', orientConst+"."+self.fkJointList[n]+"W1", force=True)
                    cmds.connectAttr(revNode+'.outputX', orientConst+"."+self.ikJointList[n]+"W0", force=True)
                # organize the ikFkBlend from before to limb:
                cmds.orientConstraint(self.fkCtrlList[0], self.ikJointList[0], maintainOffset=True, name=self.ikJointList[0]+"_orientConstraint")
                
                # creating ik controls:
                self.ikBeforeCtrl  = ctrls.cvClavicle(ctrlName=side+self.userGuideName+"_"+beforeName+"_ik_ctrl", r=self.ctrlRadius)
                cmds.setAttr(self.ikBeforeCtrl+'.rotateY', 90)
                cmds.setAttr(self.ikBeforeCtrl+'.rotateZ', -90)
                cmds.makeIdentity(self.ikBeforeCtrl, apply=True, rotate=True)
                if enumType == 0: # arm
                    self.ikCornerCtrl = ctrls.cvElbow(ctrlName=side+self.userGuideName+"_"+cornerAName[:-1]+"_ik_ctrl", r=self.ctrlRadius*0.5)
                else:
                    self.ikCornerCtrl = ctrls.cvKnee(ctrlName=side+self.userGuideName+"_"+cornerAName[:-1]+"_ik_ctrl", r=self.ctrlRadius*0.5)
                cmds.addAttr(self.ikCornerCtrl, longName='active', attributeType='float', minValue=0, maxValue=1, defaultValue=1, keyable=True);
                cmds.setAttr(self.ikCornerCtrl+'.active', 1);
                self.ikExtremCtrl  = ctrls.cvBox(ctrlName=side+self.userGuideName+"_"+extremName+"_ik_ctrl", r=self.ctrlRadius*0.5)
                self.ikExtremCtrlList.append(self.ikExtremCtrl)
                # getting them zeroOut groups:
                self.ikBeforeCtrlZero = utils.zeroOut([self.ikBeforeCtrl])[0]
                self.ikCornerCtrlZero = utils.zeroOut([self.ikCornerCtrl])[0]
                self.ikExtremCtrlZero = utils.zeroOut([self.ikExtremCtrl])[0]
                self.ikExtremCtrlZeroList.append(self.ikExtremCtrlZero)
                # putting ikCtrls in the correct position and orientation:
                tempToDelH = cmds.parentConstraint(self.cvMainLoc, self.ikBeforeCtrlZero, maintainOffset=False)
                tempToDelI = cmds.parentConstraint(self.cvExtremLoc, self.ikExtremCtrlZero, maintainOffset=False)
                cmds.delete(tempToDelH, tempToDelI)
                
                # mirror poleVector control zeroOut group:
                if s == 1:
                    cmds.setAttr(self.ikCornerCtrlZero+".scaleX", -1)
                
                # fixing ikControl group to get a good mirror orientation more animator friendly:
                self.ikExtremCtrlGrp = cmds.group(self.ikExtremCtrl, name=side+self.userGuideName+"_"+extremName+"_ik_ctrl_grp")
                self.ikExtremCtrlOrientGrp = cmds.group(self.ikExtremCtrlGrp, name=side+self.userGuideName+"_"+extremName+"_ik_ctrl_orient_grp")
                
                # verify if user wants to apply the good mirror orientation:
                if enumStyle != 0: # Default
                    # these options is valides for Biped, Quadruped and Quadruped Spring
                    if self.mirrorAxis != 'off':
                        for axis in self.mirrorAxis:
                            if axis == "X":
                                # arm type
                                if enumType == 0:
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
                cmds.connectAttr(self.worldRef+"."+side+beforeName+str(dpAR_count)+'_IkFkBlend', self.zeroFkCtrlList[0]+".visibility", force=True)
                cmds.connectAttr(self.worldRef+"."+side+self.limbType+str(dpAR_count)+'_IkFkBlend', self.zeroFkCtrlList[1]+".visibility", force=True)
                cmds.connectAttr(side+self.userGuideName+"_"+beforeName+"_rev"+".outputX", self.ikBeforeCtrlZero+".visibility", force=True)
                cmds.connectAttr(side+self.userGuideName+"_"+self.limbType+"_rev"+".outputX", self.ikCornerCtrlZero+".visibility", force=True)
                cmds.connectAttr(side+self.userGuideName+"_"+self.limbType+"_rev"+".outputX", self.ikExtremCtrlZero+".visibility", force=True)
                ctrls.setLockHide([self.ikBeforeCtrl, self.ikCornerCtrl, self.ikExtremCtrl], ['v'], l=False)
                
                # creating ikHandles:
                ikHandleBeforeList = cmds.ikHandle(name=side+self.userGuideName+"_"+beforeName+"_ikHandle", startJoint=self.ikJointList[0], endEffector=self.ikJointList[1], solver='ikRPsolver')
                
                # verify the limb style:
                if enumStyle == 3: # quadruped spring
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
                        ikHandleMainList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType+"_ikHandle", startJoint=self.ikJointList[1], endEffector=self.ikJointList[len(self.ikJointList)-2], solver='ikSpringSolver')
                    else:
                        # could not load the ikSpringSolver plutin, the we will use the regular solution as ikRPSolver:
                        ikHandleMainList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType+"_ikHandle", startJoint=self.ikJointList[1], endEffector=self.ikJointList[len(self.ikJointList)-2], solver='ikRPsolver')
                else:
                    # using regular solution as ikRPSolver:
                    ikHandleMainList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType+"_ikHandle", startJoint=self.ikJointList[1], endEffector=self.ikJointList[len(self.ikJointList)-2], solver='ikRPsolver')
                
                # renaming effectors:
                self.ikHandleBeforeEffector = cmds.rename(ikHandleBeforeList[1], ikHandleBeforeList[0]+"_effector")
                cmds.rename(ikHandleMainList[1], ikHandleMainList[0]+"_effector")
                
                # creating ikHandle groups:
                ikHandleGrp = cmds.group(empty=True, name=side+self.userGuideName+"_ikHandle_grp")
                cmds.setAttr(ikHandleGrp+'.visibility', 0)
                cmds.parent(ikHandleBeforeList[0], ikHandleGrp)
                self.ikHandleToRFGrp = cmds.group(empty=True, name=side+self.userGuideName+"_ikHandleToRF_grp")
                self.ikHandleToRFGrpList.append(self.ikHandleToRFGrp)
                cmds.setAttr(self.ikHandleToRFGrp+'.visibility', 0)
                cmds.parent(ikHandleMainList[0], self.ikHandleToRFGrp)
                cmds.parent(self.ikHandleToRFGrp, ikHandleGrp)
                
                # make ikControls lead ikHandles:
                cmds.pointConstraint(self.ikBeforeCtrl, ikHandleBeforeList[0], maintainOffset=True, name=ikHandleBeforeList[0]+"_pointConstraint")
                ctrls.setLockHide([self.ikBeforeCtrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
                self.ikHandlePointConst = cmds.pointConstraint(self.ikExtremCtrl, ikHandleMainList[0], maintainOffset=True, name=ikHandleMainList[0]+"_pointConstraint")[0]
                self.ikHandlePointConstList.append(self.ikHandlePointConst)
                cmds.orientConstraint(self.ikExtremCtrl, self.ikJointList[len(self.ikJointList)-2], maintainOffset=True, name=self.ikJointList[len(self.ikJointList)-2]+"_orientConstraint")
                ctrls.setLockHide([self.ikExtremCtrl], ['sx', 'sy', 'sz'])
                
                # twist:
                twistCtrlList = [self.ikBeforeCtrl, self.ikExtremCtrl]
                twistIkHandleList = [ikHandleBeforeList[0], ikHandleMainList[0]]
                for i, ikCtrl in enumerate(twistCtrlList):
                    cmds.addAttr(twistCtrlList[i], longName='twist', attributeType='float', keyable=True)
                    if s == 0:
                        cmds.connectAttr(twistCtrlList[i]+'.twist', twistIkHandleList[i]+".twist", force=True)
                    else:
                        twistMultDiv = cmds.createNode('multiplyDivide', name=twistCtrlList[i]+"_md")
                        cmds.setAttr(twistMultDiv+'.input2X', -1)
                        cmds.connectAttr(twistCtrlList[i]+'.twist', twistMultDiv+'.input1X', force=True)
                        cmds.connectAttr(twistMultDiv+'.outputX', twistIkHandleList[i]+".twist", force=True)
                    
                    # corner poleVector:
                    if i == 1:
                        baseMiddlePointList   = ctrls.middlePoint(self.ikJointList[1], self.ikJointList[len(self.ikJointList)-2], createLocator=True)
                        cornerMiddlePointList = ctrls.middlePoint(self.ikJointList[2], self.ikJointList[3], createLocator=True)
                        
                        # corner look at base:
                        tempToDel = cmds.aimConstraint(baseMiddlePointList[1], cornerMiddlePointList[1], aimVector=(0.0, 0.0, -1.0), upVector=(0.0, 1.0, 0.0))
                        cmds.delete(tempToDel)
                        
                        # move to along Z axis in order to go away from base middle locator:
                        distToMove = ctrls.distanceBet(self.ikJointList[1], self.ikJointList[len(self.ikJointList)-2])[0] * 1.1
                        cmds.move(0, 0, distToMove, cornerMiddlePointList[1], relative=True, objectSpace=True, worldSpaceDistance=True)
                        
                        # put poleVector control in the correct position:
                        cornerPos = cmds.xform(cornerMiddlePointList[1], query=True, worldSpace=True, rotatePivot=True)
                        cmds.setAttr(self.ikCornerCtrlZero+'.translateX', cornerPos[0])
                        cmds.setAttr(self.ikCornerCtrlZero+'.translateY', cornerPos[1])
                        cmds.setAttr(self.ikCornerCtrlZero+'.translateZ', cornerPos[2])
                        tempToDel = cmds.aimConstraint(baseMiddlePointList[1], self.ikCornerCtrlZero, aimVector=(0.0, 0.0, -1.0), upVector=(0.0, 1.0, 0.0))
                        cmds.delete(tempToDel, baseMiddlePointList[1], cornerMiddlePointList[1])
                        
                        # create poleVector constraint:
                        poleVectorConst = cmds.poleVectorConstraint(self.ikCornerCtrl, ikHandleMainList[0], weight=1.0, name=ikHandleMainList[0]+"_poleVectorConstraint")
                        cmds.connectAttr(self.ikCornerCtrl+'.active', poleVectorConst[0]+"."+self.ikCornerCtrl+"W0", force=True)
                        
                        # create annotation:
                        annotLoc = cmds.spaceLocator(name=side+self.userGuideName+"_"+self.limbType+"_ant_loc", position=(0,0,0))[0]
                        annotation = cmds.annotate(annotLoc, tx="", point=cornerPos)
                        annotation = cmds.listRelatives(annotation, parent=True)[0]
                        annotation = cmds.rename(annotation, side+self.userGuideName+"_"+self.limbType+"_ant")
                        cmds.parent(annotation, self.ikCornerCtrl)
                        cmds.parent(annotLoc, self.ikJointList[2], relative=True)
                        cmds.setAttr(annotation+'.template', 1)
                        cmds.setAttr(annotLoc+'.visibility', 0)
                        
                        # prepare groups to rotate and translate automatically:
                        cmds.aimConstraint(annotLoc, self.ikCornerCtrl, aimVector=(0.0, 0.0, -1.0), upVector=(0.0, 1.0, 0.0), name=self.ikCornerCtrl+"_aimConstraint")
                        ctrls.setLockHide([self.ikCornerCtrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                        self.cornerGrp       = cmds.group(empty=True, name=side+self.userGuideName+"_"+self.limbType+"_poleVector_grp", absolute=True)
                        self.cornerOrientGrp = cmds.group(empty=True, name=side+self.userGuideName+"_"+self.limbType+"_poleVectorOrient_grp", absolute=True)
                        tempToDelA = cmds.parentConstraint(self.ikExtremCtrl, self.cornerGrp, maintainOffset=False)
                        tempToDelB = cmds.parentConstraint(self.ikExtremCtrl, self.cornerOrientGrp, maintainOffset=False)
                        cmds.delete(tempToDelA, tempToDelB)
                        cmds.parent(self.ikCornerCtrlZero, self.cornerGrp, absolute=True)
                        self.zeroCornerGrp = utils.zeroOut([self.cornerGrp])[0]
                        self.ikPoleVectorCtrlZeroList.append(self.zeroCornerGrp)
                        
                        # working with autoOrient of poleVector:
                        cmds.addAttr(self.ikCornerCtrl, longName=self.langDic[self.langName]['c_autoOrient'], attributeType='float', minValue=0, maxValue=1, defaultValue=1, keyable=True)
                        if enumType == 0: # arm
                            cmds.setAttr(self.ikCornerCtrl+'.'+self.langDic[self.langName]['c_autoOrient'], 0)
                        if self.limbStyle == "default":
                            self.cornerOrient = cmds.orientConstraint(self.cornerOrientGrp, self.ikExtremCtrl, self.cornerGrp, skip=("y", "z"), maintainOffset=True, name=self.cornerGrp+"_orientConstraint")[0]
                        else: # biped, quadruped, etc
                            if enumType == 0: # arm
                                self.cornerOrient = cmds.orientConstraint(self.cornerOrientGrp, self.ikExtremCtrl, self.cornerGrp, skip=("y", "z"), maintainOffset=True, name=self.cornerGrp+"_orientConstraint")[0]
                            else: # leg
                                self.cornerOrient = cmds.orientConstraint(self.cornerOrientGrp, self.ikExtremCtrl, self.cornerGrp, skip=("x", "z"), maintainOffset=True, name=self.cornerGrp+"_orientConstraint")[0]
                        self.cornerOrientRev = cmds.createNode('reverse', name=side+self.userGuideName+"_cornerOrient_rev")
                        cmds.connectAttr(self.ikCornerCtrl+'.'+self.langDic[self.langName]['c_autoOrient'], self.cornerOrientRev+".inputX", force=True)
                        cmds.connectAttr(self.cornerOrientRev+'.outputX', self.cornerOrient+"."+self.cornerOrientGrp+"W0", force=True)
                        cmds.connectAttr(self.ikCornerCtrl+'.'+self.langDic[self.langName]['c_autoOrient'], self.cornerOrient+"."+self.ikExtremCtrl+"W1", force=True)
                        
                        # working with follow of poleVector:
                        self.cornerPoint = cmds.pointConstraint(self.cornerOrientGrp, self.ikExtremCtrl, self.cornerGrp, maintainOffset=True, name=self.cornerGrp+"_pointConstraint")[0]
                        cmds.addAttr(self.ikCornerCtrl, longName=self.langDic[self.langName]['c_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=1, keyable=True)
                        self.cornerPointRev = cmds.createNode('reverse', name=side+self.userGuideName+"_cornerPoint_rev")
                        cmds.connectAttr(self.ikCornerCtrl+'.'+self.langDic[self.langName]['c_follow'], self.cornerPointRev+".inputX", force=True)
                        cmds.connectAttr(self.cornerPointRev+'.outputX', self.cornerPoint+"."+self.cornerOrientGrp+"W0", force=True)
                        cmds.connectAttr(self.ikCornerCtrl+'.'+self.langDic[self.langName]['c_follow'], self.cornerPoint+"."+self.ikExtremCtrl+"W1", force=True)
                
                
                # stretch system:
                stretchCtrlList = [self.ikBeforeCtrl, self.ikExtremCtrl]
                kNameList       = [beforeName, self.limbType]
                distBetGrp = cmds.group(empty=True, name=side+self.userGuideName+"_distBet_grp")
                
                for k, stretchCtrl in enumerate(stretchCtrlList):
                    # creating attributes:
                    cmds.addAttr(stretchCtrl, longName="stretchable", attributeType='float', minValue=0, defaultValue=0.6, keyable=True)
                    cmds.addAttr(stretchCtrl, longName="stretchType", attributeType='enum', enumName="negative:positive:both", defaultValue=1, keyable=True)
                    
                    # creating distance betweens, multiplyDivides and reverse nodes:
                    self.distBetweenList = ctrls.distanceBet(self.ikJointList[k], stretchCtrl, name=side+self.userGuideName+"_"+kNameList[k]+"_db", keep=True)
                    cmds.parent(self.distBetweenList[2], self.distBetweenList[3], self.distBetweenList[4], distBetGrp)
                    
                    # stretch permited only in ik mode:
                    self.stretchIkFkMultDiv  = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_"+kNameList[k]+"_stretchIkFk_md")
                    cmds.connectAttr(self.ikFkRevList[k]+'.outputX', self.stretchIkFkMultDiv+".input1X", force=True)
                    cmds.connectAttr(self.worldRef+'.globalStretch', self.stretchIkFkMultDiv+".input2X", force=True)
                    
                    # turn On or Off the stretch using Stretchable attribute in the ikCtrl:
                    self.stretchOnOffMultDiv = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_"+kNameList[k]+"_stretchOnOff_md")
                    cmds.connectAttr(self.stretchIkFkMultDiv+'.outputX', self.stretchOnOffMultDiv+".input1X", force=True)
                    cmds.connectAttr(stretchCtrl+'.stretchable', self.stretchOnOffMultDiv+".input2X", force=True)
                    
                    # connect values in the W0 or reverse in W1 to ikCtrl lead or not the nullC of the distanceBetween not (controling the pointConstraint):
                    self.stretchRev = cmds.createNode('reverse', name=side+self.userGuideName+"_"+kNameList[k]+"_stretch_rev")
                    cmds.connectAttr(self.stretchOnOffMultDiv+'.outputX', self.stretchRev+".inputX", force=True)
                    cmds.connectAttr(self.stretchOnOffMultDiv+'.outputX', self.distBetweenList[5]+"."+stretchCtrl+"W0", force=True)
                    cmds.connectAttr(self.stretchRev+'.outputX', self.distBetweenList[5]+"."+self.distBetweenList[4]+"W1", force=True)
                    
                    # here we calculate the stretch comparing with the current distance result:
                    self.stretchMultDiv = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_"+kNameList[k]+"_stretch_md")
                    cmds.connectAttr(self.distBetweenList[1]+'.distance', self.stretchMultDiv+".input1X", force=True)
                    cmds.setAttr(self.stretchMultDiv+'.input2X', cmds.getAttr(self.stretchMultDiv+".input1X"))
                    cmds.setAttr(self.stretchMultDiv+'.operation', 2)
                    
                    # use a condition node to check what value will be send to joints scale:
                    self.stretchCond = cmds.createNode('condition', name=side+self.userGuideName+"_"+kNameList[k]+"_stretch_cnd")
                    cmds.connectAttr(self.stretchMultDiv+'.outputX', self.stretchCond+".firstTerm", force=True)
                    cmds.connectAttr(self.stretchMultDiv+'.outputX', self.stretchCond+".colorIfTrueR", force=True)
                    cmds.setAttr(self.stretchCond+'.secondTerm', 1.0)
                    
                    # choosing what type of operation will be used (calculate as a Case):
                    # negative (0) = 4
                    # positive (1) = 2
                    # both     (2) = 1
                    # else     (x) = 2
                    self.stretchCondOp0 = cmds.createNode('condition', name=side+self.userGuideName+"_"+kNameList[k]+"_stretchOp0_cnd")
                    self.stretchCondOp1 = cmds.createNode('condition', name=side+self.userGuideName+"_"+kNameList[k]+"_stretchOp1_cnd")
                    self.stretchCondOp2 = cmds.createNode('condition', name=side+self.userGuideName+"_"+kNameList[k]+"_stretchOp2_cnd")
                    cmds.setAttr(self.stretchCondOp0+'.colorIfTrueR', 4)
                    cmds.setAttr(self.stretchCondOp1+'.colorIfTrueR', 2)
                    cmds.setAttr(self.stretchCondOp2+'.colorIfTrueR', 1)
                    cmds.setAttr(self.stretchCondOp2+'.colorIfFalseR', 2)
                    cmds.setAttr(self.stretchCondOp1+'.secondTerm', 1)
                    cmds.setAttr(self.stretchCondOp2+'.secondTerm', 2)
                    cmds.connectAttr(stretchCtrl+'.stretchType', self.stretchCondOp0+'.firstTerm', force=True)
                    cmds.connectAttr(stretchCtrl+'.stretchType', self.stretchCondOp1+'.firstTerm', force=True)
                    cmds.connectAttr(stretchCtrl+'.stretchType', self.stretchCondOp2+'.firstTerm', force=True)
                    cmds.connectAttr(self.stretchCondOp1+'.outColorR', self.stretchCondOp0+'.colorIfFalseR', force=True)
                    cmds.connectAttr(self.stretchCondOp2+'.outColorR', self.stretchCondOp1+'.colorIfFalseR', force=True)
                    cmds.connectAttr(self.stretchCondOp0+".outColorR", self.stretchCond+'.operation', force=True)
                    
                    # connect the result value in the joints scale:
                    if k == 0:
                        cmds.connectAttr(self.stretchCond+'.outColorR', self.skinJointList[0]+'.scaleZ', force=True)
                        cmds.connectAttr(self.stretchCond+'.outColorR', self.ikJointList[0]+'.scaleZ', force=True)
                    else:
                        for j in range(1, 4):
                            cmds.connectAttr(self.stretchCond+'.outColorR', self.skinJointList[j]+'.scaleZ', force=True)
                            cmds.connectAttr(self.stretchCond+'.outColorR', self.ikJointList[j]+'.scaleZ', force=True)
                
                # do ikHandle off when before is fk in order to turn off the stretch:
                cmds.connectAttr(self.ikFkRevList[0]+".outputX", ikHandleBeforeList[0]+".ikBlend", force=True)
                cmds.parentConstraint(self.fkCtrlList[0], self.ikBeforeCtrlZero, maintainOffset=True, name=self.ikBeforeCtrlZero+"_parentConstraint")
                cmds.parentConstraint(self.skinJointList[0], self.distBetweenList[4], maintainOffset=True, name=self.distBetweenList[4]+"_parentConstraint")
                
                #(James) if we use the ribbon controls we won't implement the forearm control
                
                # create the forearm control if limb type is arm and there is not bend (ribbon) implementation:
                if enumType == 0 and self.getHasBend() == False:
                    # create forearm joint:
                    forearmJnt = cmds.duplicate(self.skinJointList[3], name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_forearm']+self.jSufixList[0])[0]
                    # delete its children:
                    childList = cmds.listRelatives(forearmJnt, children=True, fullPath=True)
                    cmds.delete(childList)
                    # parent to elbowB joint:
                    cmds.parent(forearmJnt, self.skinJointList[3])
                    # move forearmJnt to correct position:
                    tempDist = ctrls.distanceBet(self.skinJointList[3], self.skinJointList[4])[0]
                    txElbowA = cmds.xform(self.skinJointList[2], worldSpace=True, translation=True, query=True)[0]
                    txElbowB = cmds.xform(self.skinJointList[3], worldSpace=True, translation=True, query=True)[0]
                    if (txElbowB - txElbowA) > 0:
                        forearmDistZ = tempDist/3
                    else:
                        forearmDistZ = -(tempDist/3)
                    cmds.move(0,0, forearmDistZ, forearmJnt, localSpace=True, worldSpaceDistance=True)
                    # create forearmCtrl:
                    forearmCtrl = cmds.circle(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_forearm']+"_ctrl", ch=False, o=True, nr=(0, 0, 1), d=1, s=8, radius=(self.ctrlRadius * 0.75))[0]
                    forearmGrp  = cmds.group(forearmCtrl, name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_forearm']+"_grp")
                    forearmZero = cmds.group(forearmGrp,  name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_forearm']+"_zero")
                    tempToDelete = cmds.parentConstraint(forearmJnt, forearmZero, maintainOffset=False)
                    cmds.delete(tempToDelete)
                    cmds.parentConstraint(self.skinJointList[3], forearmZero, maintainOffset=True, name=forearmZero+"_parentConstraint")
                    cmds.orientConstraint(forearmCtrl, forearmJnt, skip=["x","y"], maintainOffset=True, name=forearmJnt+"_orientConstraint")
                    # create attribute to forearm autoRotate:
                    cmds.addAttr(forearmCtrl, longName=self.langDic[self.langName]['c_autoOrient'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.75, keyable=True)
                    ctrls.setLockHide([forearmCtrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'sx', 'sy', 'sz', 'v'])
                    # make rotate connections:
                    forearmMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_forearm']+"_md")
                    cmds.connectAttr(forearmCtrl+'.'+self.langDic[self.langName]['c_autoOrient'], forearmMD+'.input1X')
                    cmds.connectAttr(self.skinJointList[4]+'.rotateZ', forearmMD+'.input2X')
                    cmds.connectAttr(forearmMD+'.outputX', forearmGrp+'.rotateZ')
                
                # creating a group to receive the reverseFootCtrlGrp (if module integration is on):
                self.ikFkBlendGrpToRevFoot = cmds.group(empty=True, name=side+self.userGuideName+"_ikFkBlendGrpToRevFoot_grp")
                self.ikFkBlendGrpToRevFootList.append(self.ikFkBlendGrpToRevFoot)
                tempToDelToRFpc = cmds.parentConstraint(self.ikExtremCtrl, self.ikFkBlendGrpToRevFoot, maintainOffset=False)
                cmds.delete(tempToDelToRFpc)
                
                # this next parentConstraint does not calculate correctly when we use negative scale
                # then we will use a workarround in order to set a good offset
                parentConstToRFOffset = cmds.parentConstraint(self.ikExtremCtrl, self.fkCtrlList[len(self.fkCtrlList)-1], self.ikFkBlendGrpToRevFoot, maintainOffset=True, name=self.ikFkBlendGrpToRevFoot+"_parentConstraint")[0]
                self.parentConstToRFOffsetList.append(parentConstToRFOffset)
                cmds.connectAttr(self.ikFkRevList[len(self.ikFkRevList)-1]+'.outputX', parentConstToRFOffset+"."+self.ikExtremCtrl+"W0", force=True)
                cmds.connectAttr(self.worldRef+"."+side+self.limbType+str(dpAR_count)+'_IkFkBlend', parentConstToRFOffset+"."+self.fkCtrlList[len(self.fkCtrlList)-1]+"W1", force=True)
                
                # organize to be corriged the offset when we will apply the parentConstraint
                # there is a bug in the Maya calculation if we use negative scale (mirrored :P)
                cmds.addAttr(parentConstToRFOffset, longName="mustCorrectOffset", attributeType='bool', keyable=False)
                cmds.addAttr(parentConstToRFOffset, longName="fixOffsetX", attributeType='long', keyable=False)
                cmds.addAttr(parentConstToRFOffset, longName="fixOffsetY", attributeType='long', keyable=False)
                cmds.addAttr(parentConstToRFOffset, longName="fixOffsetZ", attributeType='long', keyable=False)
                
                if enumStyle != 0: # Default
                    # these options are valides for Biped, Quadruped and Quadruped Spring legs
                    if self.mirrorAxis != 'off':
                        if s == 1: # mirrored guide
                            if enumType == 1: # leg
                                for axis in self.mirrorAxis:
                                    if axis == "X":
                                        # must fix offset of the parentConstrain in the future when this will be integrated
                                        cmds.setAttr(parentConstToRFOffset+".mustCorrectOffset", 1)
                                        cmds.setAttr(parentConstToRFOffset+".fixOffsetX", 90)
                                        cmds.setAttr(parentConstToRFOffset+".fixOffsetY", 180)
                                        cmds.setAttr(parentConstToRFOffset+".fixOffsetZ", -90)
                    
                    if enumStyle == 3: # Quadruped Spring
                        # fix the group for the ikSpringSolver to avoid Maya bug about rotation from masterCtrl :P
                        cmds.parent(self.ikJointList[1], world=True)
                        cmds.parent(self.ikHandleBeforeEffector, world=True)
                        self.fixIkSpringSolverGrp = cmds.group(self.ikJointList[1], self.ikHandleBeforeEffector, name=side+self.userGuideName+"_ikFixSpringSolver_grp")
                        self.fixIkSpringSolverGrpList.append(self.fixIkSpringSolverGrp)
                        cmds.setAttr(self.fixIkSpringSolverGrp+".visibility", 0)
                        cmds.parentConstraint(self.ikJointList[0], self.ikJointList[1], maintainOffset=True, name=self.ikJointList[1]+"_parentConstraint")
                        
                    if enumStyle == 2 or enumStyle == 3: # Quadruped, Quadruped Spring
                        # tell main script to create parent constraint from chestA to ikCtrl for front legs
                        self.quadFrontLegList.append(self.ikExtremCtrlOrientGrp)
                
                # create a masterModuleGrp to be checked if this rig exists:
                if enumType == 0:
                    # (James) not implementing the forearm control if we use ribbons (yet)
                    if self.getHasBend() == True:
                        # do not use forearm control
                        self.toCtrlHookGrp = cmds.group(self.zeroFkCtrlGrp, self.zeroCornerGrp, self.ikBeforeCtrlZero, self.ikExtremCtrlZero, self.cornerOrientGrp, distBetGrp, self.origFromList[0], self.origFromList[1], self.ikFkBlendGrpToRevFoot, self.worldRef, name=side+self.userGuideName+"_control_grp")
                    else:
                        # use forearm control
                        self.toCtrlHookGrp = cmds.group(self.zeroFkCtrlGrp, self.zeroCornerGrp, self.ikBeforeCtrlZero, self.ikExtremCtrlZero, self.cornerOrientGrp, forearmZero, distBetGrp, self.origFromList[0], self.origFromList[1], self.ikFkBlendGrpToRevFoot, self.worldRef, name=side+self.userGuideName+"_control_grp")
                else:
                    self.toCtrlHookGrp = cmds.group(self.zeroFkCtrlGrp, self.zeroCornerGrp, self.ikBeforeCtrlZero, self.ikExtremCtrlZero, self.cornerOrientGrp, distBetGrp, self.origFromList[0], self.origFromList[1], self.ikFkBlendGrpToRevFoot, self.worldRef, name=side+self.userGuideName+"_control_grp")
                self.toScalableHookGrp = cmds.group(self.skinJointList[0], self.ikJointList[0], self.fkJointList[0], name=side+self.userGuideName+"_joint_grp")
                cmds.parentConstraint(self.toCtrlHookGrp, self.toScalableHookGrp, maintainOffset=True)
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, ikHandleGrp, name=side+self.userGuideName+"_grp")
                
                
                # new ribbon feature by James do Carmo, thanks!
                #(James) add bend to limb
                if self.getHasBend():
                    import jcRibbon as rb
                    reload(rb)
                    num = self.getBendJoints()
                    iniJoint = side+self.userGuideName+"_"+mainName+'_jnt'
                    cornerA = side+self.userGuideName+"_"+cornerAName+'_jnt'
                    splited = self.userGuideName.split('_')
                    prefix =''.join(side)
                    name = ''
                    if len(splited) > 1:
                        prefix+=splited[0]
                        name+=splited[1]
                    else:
                        name+=self.userGuideName
                    loc = cmds.spaceLocator(n=side+self.userGuideName+'_auxOriLoc',p=(0,0,0))[0]
                    #locGrp = cmds.group(loc,n=side+self.userGuideName+'auxOriLoc_grp')
                    
                    cmds.delete(cmds.parentConstraint(iniJoint,loc,mo=False,w=1))
                    
                    if name == self.langDic[self.langName]['c_leg_main']: # leg
                        if s == 0: # left side (or first side = original)
                            cmds.delete(cmds.aimConstraint(cornerA,loc,mo=False,weight=2,aimVector=(1,0,0),upVector=(0,1,0),worldUpType="vector",worldUpVector=(1,0,0)))
                        else:
                            cmds.delete(cmds.aimConstraint(cornerA,loc,mo=False,weight=2,aimVector=(1,0,0),upVector=(0,1,0),worldUpType="vector",worldUpVector=(-1,0,0)))
                    else:
                        cmds.delete(cmds.aimConstraint(cornerA,loc,mo=False,weight=2,aimVector=(1,0,0),upVector=(0,1,0),worldUpType="vector",worldUpVector=(0,1,0)))
                    
                    #addRibbonToLimb(prefix='',nome=None,oriLoc=None,iniJnt=None,num=5,mirror=True,ctrlRadius=1):
                    self.bendGrps = rb.addRibbonToLimb(prefix,name,loc,iniJoint,'x',num,mirror=False,ctrlRadius=(self.ctrlRadius * 0.5))
                    cmds.delete(loc)
                    
                    cmds.parent(self.bendGrps['ctrlsGrp'], self.toCtrlHookGrp)
                    cmds.parent(self.bendGrps['scaleGrp'], self.toScalableHookGrp)
                    cmds.parent(self.bendGrps['staticGrp'], self.toStaticHookGrp)
                    
                    
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
                                                }
                                    }
