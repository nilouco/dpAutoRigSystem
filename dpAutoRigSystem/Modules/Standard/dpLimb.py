# importing libraries:
from maya import cmds
from ..Base import dpBaseStandard
from ..Base import dpBaseLayout
from ..Library import dpSoftIk
from ..Library import dpIkFkSnap
from ...Tools import dpCorrectionManager
from functools import partial
from importlib import reload
from maya.api import OpenMaya as om
import math

# global variables to this module:
CLASS_NAME = "Limb"
TITLE = "m019_limb"
DESCRIPTION = "m020_limbDesc"
ICON = "/Icons/dp_limb.png"

# declaring member variables

DP_LIMB_VERSION = 3.4


class Limb(dpBaseStandard.BaseStandard, dpBaseLayout.BaseLayout):
    def __init__(self, *args, **kwargs):
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.armName = "Arm"
        self.legName = "Leg"
        dpBaseStandard.BaseStandard.__init__(self, *args, **kwargs)
        self.softIk = dpSoftIk.SoftIkClass(self.dpUIinst)
        self.correctionManager = dpCorrectionManager.CorrectionManager(self.dpUIinst, False)
        # declare variable
        self.integratedActionsDic = {}
        self.bendGrps = None
        # returned data from the dictionary
        self.ikExtremCtrlList = []
        self.ikExtremCtrlZeroList = []
        self.ikPoleVectorCtrlZeroList = []
        self.ikHandleToRFGrpList = []
        self.ikHandleConstList = []
        self.ikFkBlendGrpToRevFootList = []
        self.worldRefList = []
        self.worldRefShapeList = []
        self.extremJntList = []
        self.fixIkSpringSolverGrpList = []
        self.quadFrontLegList = []
        self.integrateOrigFromList = []
        self.ikStretchExtremLocList = []
        self.afkIsolateConst = []
        self.aScalableGrps = []
        self.origRotList = []
        self.bendJointList = []
        self.masterCtrlRefList = []
        self.rootCtrlRefList = []
        self.softIkCalibrateList = []
        self.correctiveCtrlGrpList = []
        self.ankleArticList = []
        self.ankleCorrectiveList = []
        self.jaxRotZMDList = []


    def createModuleLayout(self, *args):
        dpBaseStandard.BaseStandard.createModuleLayout(self)
        dpBaseLayout.BaseLayout.basicModuleLayout(self)


    def getHasBend(self):
        return cmds.getAttr(self.moduleGrp+".hasBend")


    def getBendJoints(self):
        return cmds.getAttr(self.moduleGrp+".numBendJoints")


    def getAlignWorld(self):
        return cmds.getAttr(self.moduleGrp+".alignWorld")


    def getHasAdditional(self):
        if cmds.objExists(self.moduleGrp+".additional"):
            return cmds.getAttr(self.moduleGrp+".additional")
        else:
            return 0


    def addFollowAttrName(self, ctrl, attr, *args):
        cmds.addAttr(ctrl, longName="followAttrName", dataType="string")
        cmds.setAttr(ctrl+".followAttrName", attr, type="string")


    # @dpUtils.profiler
    def createGuide(self, *args):
        dpBaseStandard.BaseStandard.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="type", attributeType='enum', enumName=self.dpUIinst.lang['m028_arm']+':'+self.dpUIinst.lang['m030_leg'])
        cmds.addAttr(self.moduleGrp, longName="hasBend", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".hasBend", 1)
        cmds.addAttr(self.moduleGrp, longName="numBendJoints", attributeType='long')
        cmds.setAttr(self.moduleGrp+".numBendJoints", 5)
        cmds.addAttr(self.moduleGrp, longName="style", attributeType='enum', enumName=self.dpUIinst.lang['m042_default']+':'+self.dpUIinst.lang['m026_biped']+':'+self.dpUIinst.lang['m037_quadruped']+':'+self.dpUIinst.lang['m043_quadSpring']+':'+self.dpUIinst.lang['m155_quadrupedExtra'])
        cmds.addAttr(self.moduleGrp, longName="alignWorld", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".alignWorld", 1)
        cmds.addAttr(self.moduleGrp, longName="articulation", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".articulation", 1)
        cmds.addAttr(self.moduleGrp, longName="additional", attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName="softIk", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".softIk", 1)
        cmds.addAttr(self.moduleGrp, longName="corrective", attributeType='bool')

        # create cvJointLoc and cvLocators:
        self.cvBeforeLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_Before", r=0.3, d=1, guide=True)
        self.cvMainLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_Main", r=0.5, d=1, guide=True)
        self.cvCornerLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_Corner", r=0.3, d=1, guide=True)
        self.cvCornerBLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_CornerB", r=0.5, d=1, guide=True)
        self.cvExtremLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_Extrem", r=0.5, d=1, guide=True)
        self.cvUpVectorLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_CornerUpVector", r=0.5, d=1, guide=True)
        
        # set quadruped locator config:
        cmds.parent(self.cvCornerBLoc, self.cvCornerLoc, relative=True)
        cmds.setAttr(self.cvCornerBLoc+".translateZ", 2)
        cmds.setAttr(self.cvCornerBLoc+".visibility", 0)

        # create jointGuides:
        cmds.select(clear=True)
        self.jGuideBefore = cmds.joint(name=self.guideName+"_JGuideBefore", radius=0.001)
        self.jGuideMain = cmds.joint(name=self.guideName+"_JGuideMain", radius=0.001)
        self.jGuideCorner = cmds.joint(name=self.guideName+"_JGuideCorner", radius=0.001)
        self.jGuideExtrem = cmds.joint(name=self.guideName+"_JGuideExtrem", radius=0.001)

        # create cornerGroups:
        self.cornerGrp = cmds.group(self.cvCornerLoc, name=self.cvCornerLoc+"_Grp")

        # set jointGuides as templates:
        cmds.setAttr(self.jGuideBefore+".template", 1)
        cmds.setAttr(self.jGuideMain+".template", 1)
        cmds.setAttr(self.jGuideCorner+".template", 1)
        cmds.setAttr(self.jGuideExtrem+".template", 1)
        cmds.parent(self.jGuideBefore, self.moduleGrp, relative=True)

        # create cvEnd:
        self.cvEndJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1, d=1, guide=True)
        cmds.parent(self.cvEndJoint, self.cvExtremLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.parent(self.jGuideEnd, self.jGuideExtrem)

        # make parents between cvLocs:
        cmds.parent(self.cvBeforeLoc, self.cvMainLoc, self.cornerGrp, self.cvExtremLoc, self.cvUpVectorLoc, self.moduleGrp)

        # connect cvLocs in jointGuides:
        self.ctrls.directConnect(self.cvBeforeLoc, self.jGuideBefore, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        cmds.parentConstraint(self.cvMainLoc, self.jGuideMain, maintainOffset=False, name=self.jGuideMain+"_PaC")
        cmds.parentConstraint(self.cvCornerLoc, self.jGuideCorner, maintainOffset=False, name=self.jGuideCorner+"_PaC")
        cmds.parentConstraint(self.cvExtremLoc, self.jGuideExtrem, maintainOffset=False, name=self.jGuideExtrem+"_PaC")

        # align cornerLocs:
        self.cornerAIC = cmds.aimConstraint(self.cvExtremLoc, self.cornerGrp, aimVector=(0.0, 0.0, 1.0), upVector=(0.0, -1.0, 0.0), worldUpType="object", worldUpObject=self.cvUpVectorLoc, name=self.cornerGrp+"_AiC")[0]

        # limit, lock and hide cvEnd:
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])

        # creating relationship of corner:
        self.cornerPointGrp = cmds.group(self.cornerGrp, name=self.cornerGrp+"_Zero_0_Grp")
        self.cornerPointConst = cmds.pointConstraint(self.cvMainLoc, self.cvExtremLoc, self.cornerPointGrp, maintainOffset=False, name=self.cornerPointGrp+"_PoC")[0]
        cmds.setAttr(self.cornerPointConst+'.'+self.cvMainLoc[self.cvMainLoc.rfind(":")+1:]+'W0', 0.52)
        cmds.setAttr(self.cornerPointConst+'.'+self.cvExtremLoc[self.cvExtremLoc.rfind(":")+1:]+'W1', 0.48)

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
        self.cornerUpVectorPointConst = cmds.pointConstraint(self.cvMainLoc, self.cvExtremLoc, self.cvUpVectorGrp, maintainOffset=True, name=self.cvUpVectorGrp+"_PoC")[0]
        cmds.setAttr(self.cornerUpVectorPointConst+'.'+self.cvMainLoc[self.cvMainLoc.rfind(":")+1:]+'W0', 0.52)
        cmds.setAttr(self.cornerUpVectorPointConst+'.'+self.cvExtremLoc[self.cvExtremLoc.rfind(":")+1:]+'W1', 0.48)
        cmds.setAttr(self.cvUpVectorLoc+".translateY", -10)

        # display cornerUpVector:
        cmds.addAttr(self.cvCornerLoc, longName="displayUpVector", attributeType="bool")
        cmds.setAttr(self.cvCornerLoc+".displayUpVector", keyable=False, channelBox=True)
        cmds.connectAttr(self.cvCornerLoc+".displayUpVector", self.cvUpVectorLoc+".visibility", force=True)

        # lock undesirable translate and rotate axis for corner guides:
        self.setLockCornerAttr(self.armName)

        # re orient guides:
        self.reOrientGuide()
        cmds.setAttr(self.cvExtremLoc+".translateX", lock=True)
        # include nodes into net
        self.addNodeToGuideNet([self.cvBeforeLoc, self.cvMainLoc, self.cvCornerLoc, self.cvCornerBLoc, self.cvExtremLoc, self.cvUpVectorLoc, self.cvEndJoint], ["Before", "Main", "Corner", "CornerB", "Extrem", "CornerUpVector", "JointEnd"])

        # create autoAim null groups:
        self.guideMainDrvNull = cmds.group(empty=True, name=self.cvMainLoc+"_Drv_Null")
        self.cornerDrvNull = cmds.group(empty=True, name=self.cvCornerLoc+"_Drv_Null")
        self.cornerDrvNullGrp = cmds.group(self.cornerDrvNull, name=self.cornerDrvNull+"_Grp")
        cmds.parent(self.guideMainDrvNull, self.cornerDrvNullGrp, self.moduleGrp)
        cmds.matchTransform(self.guideMainDrvNull, self.cvMainLoc)
        cmds.matchTransform(self.cornerDrvNullGrp, self.cvCornerLoc)
        cmds.setAttr(self.guideMainDrvNull+".visibility", 0)
        cmds.setAttr(self.cornerDrvNull+".visibility", 0)
        cmds.setAttr(self.cornerDrvNullGrp+".visibility", 0)
        
        # autoAim main function:
        self.createAutoAim()


    def createAutoAim(self, *args):
        """ AimConstraint setup in order to auto orient mainGuide with CornerGuide
        """ 
        # re-declaring guide names:
        self.cvMainLoc = self.guideName+"_Main"
        self.cvCornerLoc = self.guideName+"_Corner"
        self.cvExtremLoc = self.guideName+"_Extrem"
        self.cvUpVectorLoc = self.guideName+"_CornerUpVector"
        self.cornerPointGrp = self.guideName+"_Corner_Grp_Zero_0_Grp"
        self.guideMainDrvNull = self.guideName+"_Main_Drv_Null"
        self.cornerDrvNull = self.guideName+"_Corner_Drv_Null"
        self.cornerDrvNullGrp =  self.guideName+"_Corner_Drv_Null_Grp"

        # creating group to mainLoc:
        self.cvMainLocGrp = self.utils.zeroOut([self.cvMainLoc])[0]

        # checking limbType to create correctly up vector values:
        if  self.getLimbType()==self.armName:
            upVectorValues = (0.0, -1.0, 0.0)
        if  self.getLimbType()==self.legName:
            upVectorValues = (1.0, 0.0, 0.0)

        # deleting point constraint to change to the new null grp:
        cornerPointGrpConnections = cmds.listConnections(self.cornerPointGrp, type="constraint", source=True, destination=False)
        cvUpVectorGrpConnections = cmds.listConnections(self.cvUpVectorGrp, type="constraint", source=True, destination=False)
        if cornerPointGrpConnections and cvUpVectorGrpConnections:
            pocConnectionsList = cornerPointGrpConnections+cvUpVectorGrpConnections
            if pocConnectionsList:
                for connection in pocConnectionsList:
                    if cmds.objExists(connection):
                        cmds.delete(connection)
        
        # connecting guides transform to the null groups:
        for axis in self.axisList:
            cmds.connectAttr(self.cvMainLoc+".translate"+axis, self.guideMainDrvNull+".translate"+axis)
            cmds.connectAttr(self.cvMainLoc+".rotate"+axis, self.guideMainDrvNull+".rotate"+axis)
            cmds.connectAttr(self.cvCornerLoc+".translate"+axis, self.cornerDrvNull+".translate"+axis)
            cmds.connectAttr(self.cvCornerLoc+".rotate"+axis, self.cornerDrvNull+".rotate"+axis)
        
        # new point constraint from main null grp:
        self.cornerPoc = cmds.pointConstraint(self.guideMainDrvNull, self.cvExtremLoc, self.cornerPointGrp, maintainOffset=True, name=self.cornerPointGrp+"_PoC")[0]
        self.cornerUpVectorPoc = cmds.pointConstraint(self.guideMainDrvNull, self.cvExtremLoc, self.cvUpVectorGrp, maintainOffset=True, name=self.cvUpVectorGrp+"_PoC")[0]
        self.cornerNullPoc = cmds.pointConstraint(self.guideMainDrvNull, self.cvExtremLoc, self.cornerDrvNullGrp, maintainOffset=True, name=self.cornerDrvNullGrp+"_PoC")[0]
        self.cornerDrvNullAic = cmds.aimConstraint(self.cvExtremLoc, self.cornerDrvNullGrp, aimVector=(0.0, 0.0, 1.0), upVector=upVectorValues, worldUpType="object", worldUpObject=self.cvUpVectorLoc, name=self.cornerDrvNullGrp+"_AiC")

        # setting constraint values, using 0.5 to don't change the previous one which was used to correct placement:
        cmds.setAttr(self.cornerPoc+'.'+self.guideMainDrvNull[self.guideMainDrvNull.rfind(":")+1:]+'W0', 0.5)
        cmds.setAttr(self.cornerPoc+'.'+self.cvExtremLoc[self.cvExtremLoc.rfind(":")+1:]+'W1', 0.5)
        cmds.setAttr(self.cornerUpVectorPoc+'.'+self.guideMainDrvNull[self.guideMainDrvNull.rfind(":")+1:]+'W0', 0.5)
        cmds.setAttr(self.cornerUpVectorPoc+'.'+self.cvExtremLoc[self.cvExtremLoc.rfind(":")+1:]+'W1', 0.5)
        cmds.setAttr(self.cornerNullPoc+'.'+self.guideMainDrvNull[self.guideMainDrvNull.rfind(":")+1:]+'W0', 0.5)
        cmds.setAttr(self.cornerNullPoc+'.'+self.cvExtremLoc[self.cvExtremLoc.rfind(":")+1:]+'W1', 0.5)
        
        # main aimConstraint to the mainLocGrp:
        self.mainAic = cmds.aimConstraint(self.cornerDrvNull, self.cvMainLocGrp, maintainOffset=True, aimVector=(0.0, 0.0, 1.0), upVector=upVectorValues, worldUpType="object", worldUpObject=self.cvUpVectorLoc, name=self.cvMainLocGrp+"_AiC")[0]
        cmds.select(self.moduleGrp)


    def recreateAutoAim(self, *args):
        """ Need to delete the previous setup in order to autoAim works with different type of limb
        """
        # re-declaring guide names:
        self.cvMainLoc = self.guideName+"_Main"
        self.cvMainLocGrp = self.guideName+"_Main_Zero_0_Grp"
        self.guideMainDrvNull = self.guideName+"_Main_Drv_Null"
        self.cornerDrvNull = self.guideName+"_Corner_Drv_Null"
        self.cornerDrvNullAic = self.guideName+"_Corner_Drv_Null_Grp_AiC"
        self.cornerDrvNullGrp = self.guideName+"_Corner_Drv_Null_Grp"
        self.cvCornerLoc = self.guideName+"_Corner"
        self.cornerPoc = self.guideName+"_Corner_Grp_Zero_0_Grp_PoC"
        
        # deleting previous constraints:
        cmds.delete(self.cornerPoc, self.cornerDrvNullAic, self.cornerPoc, self.cornerUpVectorPoc, self.cornerNullPoc)

        # disconnecting direct connections:
        for axis in self.axisList:
            cmds.disconnectAttr(self.cvMainLoc+".translate"+axis, self.guideMainDrvNull+".translate"+axis)
            cmds.disconnectAttr(self.cvMainLoc+".rotate"+axis, self.guideMainDrvNull+".rotate"+axis)
            cmds.disconnectAttr(self.cvCornerLoc+".translate"+axis, self.cornerDrvNull+".translate"+axis)
            cmds.disconnectAttr(self.cvCornerLoc+".rotate"+axis, self.cornerDrvNull+".rotate"+axis)
        
       # deleting mainLoc group, this group previous received the main auto aimConstraint:
        cmds.parent(self.cvMainLoc, self.moduleGrp)
        cmds.delete(self.cvMainLocGrp)

        # setting new positions:
        cmds.matchTransform(self.guideMainDrvNull, self.cvMainLoc)
        cmds.matchTransform(self.cornerDrvNullGrp, self.cvCornerLoc)

        # re-orient guides:
        self.reOrientGuide()

        # autoAim main function:
        self.createAutoAim()


    def crossProduct(self, limbType, *args):
        """ Calculate cross product between guides Main, Corner and Extrem
            It will check which side the corner is to adjust the aim constraint offset
        """
        # re-declaring variables:
        self.cvMainLoc = self.guideName+"_Main"
        self.cvCornerLoc = self.guideName+"_Corner"
        self.cvExtremLoc = self.guideName+"_Extrem"

        # get guides position in worldSpace:
        posMain = om.MVector(cmds.xform(self.cvMainLoc, query=True, worldSpace=True, translation=True))
        posCorner = om.MVector(cmds.xform(self.cvCornerLoc, query=True, worldSpace=True, translation=True))
        posExtrem = om.MVector(cmds.xform(self.cvExtremLoc, query=True, worldSpace=True, translation=True))

        # create vector between guides position directions:
        vectorMainToCorner = posCorner - posMain
        vectorMainToExtrem = posExtrem - posMain

        # calculate crossProduct between vectors:
        crossProduct = vectorMainToCorner ^ vectorMainToExtrem

        # check position of crossProduct depending on the limbType:
        if limbType == self.armName:
            # if the limbType is arm the crossProduct will look for the axis y:
            if crossProduct.y <= 0:
                offsetValue = 1
            else:
                offsetValue = -1

        if limbType == self.legName:
            # if the limbtype is leg the crossProduct will look for the axis X
            if crossProduct.x <= 0:
                offsetValue = -1
            else:
                offsetValue = 1
        return offsetValue


    def setAimConstraintOffset(self, aimConstraint, *args):
        """ Adjust aimOffset depends on corner position
        """
        # re-declaring corner guide name:
        self.cvCornerLoc = self.guideName+"_Corner"
        
        # when the limbType is arm, it will call the crossProduct function to get the right offset for X
        if self.getLimbType()==self.armName:
            offsetAxis = ".offsetX"
            offsetValue = self.crossProduct(self.armName)
        
        # when the limbType is arm, it will call the crossProduct function to get the right offset for Y:
        if self.getLimbType()==self.legName:
            offsetAxis = ".offsetY"
            offsetValue = self.crossProduct(self.legName)

        # set the aimConstraint's offset according to limbType:
        cmds.setAttr(aimConstraint+offsetAxis, offsetValue)


    def reOrientGuide(self, *args):
        """ This function reOrient guides orientations, creating temporary aimConstraints for them.
        """
        # re-declaring guide names:
        self.cvBeforeLoc = self.guideName+"_Before"
        self.cvMainLoc = self.guideName+"_Main"
        self.cvCornerLoc = self.guideName+"_Corner"
        self.cvExtremLoc = self.guideName+"_Extrem"
        self.cvUpVectorLoc = self.guideName+"_CornerUpVector"

        # Adjust offset when it's arm or leg. Using diferent axis for arm or leg.
        if self.getLimbType()==self.armName:
            beforeTranslateAxis = ".translateY"
        if self.getLimbType()==self.legName:
            beforeTranslateAxis = ".translateX"

        # re-orient clavicle rotations:
        tempToDelBeforeUpVector = cmds.group(empty=True, name=self.cvBeforeLoc+"_UpVector_Tmp")
        cmds.matchTransform(tempToDelBeforeUpVector, self.cvBeforeLoc, position=True)
        beforeUpVectorTranslate = cmds.getAttr(tempToDelBeforeUpVector+beforeTranslateAxis)
        cmds.setAttr(tempToDelBeforeUpVector+beforeTranslateAxis, beforeUpVectorTranslate+10)
        tempToDelBeforeAic = cmds.aimConstraint(self.cvMainLoc, self.cvBeforeLoc, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0), worldUpType="object", worldUpObject=tempToDelBeforeUpVector, name=self.cvBeforeLoc+"_Tmp_AiC")[0]
        cmds.delete(tempToDelBeforeAic, tempToDelBeforeUpVector)
        
        # re-orient main shoulder guide
        tempToDelMainUpVector = cmds.group(empty=True, parent=self.moduleGrp, relative=True, name=self.cvMainLoc+"_UpVector_Tmp")
        cmds.setAttr(tempToDelMainUpVector+".translateX", 10)
        tempToDelMainAic = cmds.aimConstraint(self.cvCornerLoc, self.cvMainLoc, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0), worldUpType="object", worldUpObject=tempToDelMainUpVector, name=self.cvMainLoc+"_Tmp_AiC")[0]
        
        # aim offset for aimConstraint depending on limbType
        self.setAimConstraintOffset(tempToDelMainAic)
        cmds.delete(tempToDelMainAic, tempToDelMainUpVector)
        

    def reOrientGuideButton(self, *args):
        """ New functions when the button reOrient is pressed. For Arm, the extrem will point to the corner. For legs, the extrem will point to the ground.
        """
        # re-declaring guides names:
        self.cvExtremLoc = self.guideName+"_Extrem"
        self.cvCornerLoc = self.guideName+"_Corner"
        self.mainAic = self.guideName+"_Main_Zero_0_Grp_AiC"
        
        # reOrient guides first
        self.reOrientGuide()
        
        # re-orient extremLoc to align with cornerLoc. 
        if self.getLimbType()==self.armName:
            toUnparentList = []
            extremChildrenList = cmds.listRelatives(self.cvExtremLoc, children=True, type="transform")
            if extremChildrenList:
                extremChildrenGrpTemp = cmds.group(empty=True, name="extremChildren_Temp_Grp", parent=self.moduleGrp)
                for extremChildren in extremChildrenList:
                    if cmds.objExists(extremChildren+".pinGuide"):
                        toUnparentList.append(extremChildren)
                        cmds.parent(extremChildren, extremChildrenGrpTemp)
                tempUpVectorWrist = cmds.group(empty=True, name="tempUpVectorWrist_Null")
                cmds.parent(tempUpVectorWrist, self.moduleGrp)
                cmds.matchTransform(tempUpVectorWrist, self.cvExtremLoc)
                cmds.setAttr(tempUpVectorWrist+".translateX", 2)
                tempToDelWristAim = cmds.aimConstraint(self.cvCornerLoc, self.cvExtremLoc, aimVector=(0.0, 0.0, -1.0), upVector=(1.0, 0.0, 0.0), worldUpType="object", worldUpObject=tempUpVectorWrist, name=self.cvExtremLoc+"_Tmp_AiC")
                cmds.delete(tempToDelWristAim, tempUpVectorWrist)
            if toUnparentList:
                cmds.parent(toUnparentList, self.cvExtremLoc)
            cmds.delete(extremChildrenGrpTemp)

            # adjust offset depends on corner position
            cmds.setAttr(self.cvMainLoc+".rotateX", 0)
            self.setAimConstraintOffset(self.mainAic)
                
        # setup to reorient the ankle guide to point to the ground when rotate mainGuide
        if self.getLimbType()==self.legName:
            ankleToAimNull = cmds.group(empty=True, world=True, name="Temp_Ankle_ToAim_Null")
            cmds.matchTransform(ankleToAimNull, self.cvExtremLoc, position=True)
            cmds.setAttr(ankleToAimNull+".translateY", -10)
            tempToDelAnkleAim = cmds.aimConstraint(ankleToAimNull, self.cvExtremLoc, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0), name=self.cvExtremLoc+"_Tmp_AiC")
            cmds.delete(tempToDelAnkleAim, ankleToAimNull)

            # leg offset adjust
            cmds.setAttr(self.cvMainLoc+".rotateY", 0)
            self.setAimConstraintOffset(self.mainAic)
        cmds.select(self.moduleGrp)


    def reCreateEditSelectedModuleLayout(self, bSelect=False, *args):
        dpBaseLayout.BaseLayout.reCreateEditSelectedModuleLayout(self, bSelect)
        # if there is a type attribute:
        self.typeLayout = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 50, 77, 70), columnAlign=[(1, 'right'), (2, 'left'), (3, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (3, 'both', 10)], parent="selectedModuleColumn")
        cmds.text(self.dpUIinst.lang['m021_type'], parent=self.typeLayout)
        self.typeMenu = cmds.optionMenu("typeMenu", label='', changeCommand=self.changeType, parent=self.typeLayout)
        typeMenuItemList = [self.dpUIinst.lang['m028_arm'], self.dpUIinst.lang['m030_leg']]
        for item in typeMenuItemList:
            cmds.menuItem(label=item, parent=self.typeMenu)
        # read from guide attribute the current value to type:
        currentType = cmds.getAttr(self.moduleGrp+".type")
        cmds.optionMenu(self.typeMenu, edit=True, select=int(currentType+1))
        self.reOrientBT = cmds.button(label=self.dpUIinst.lang['m022_reOrient'], annotation=self.dpUIinst.lang['m023_reOrientDesc'], command=self.reOrientGuideButton, parent=self.typeLayout)

        # style layout:
        self.styleLayout = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 50, 50, 70), columnAlign=[(1, 'right'), (2, 'left'), (3, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (3, 'both', 10)], parent="selectedModuleColumn")
        cmds.text(label=self.dpUIinst.lang['m041_style'], visible=True, parent=self.styleLayout)
        self.styleMenu = cmds.optionMenu("styleMenu", label='', changeCommand=self.changeStyle, parent=self.styleLayout)
        styleMenuItemList = [self.dpUIinst.lang['m042_default'], self.dpUIinst.lang['m026_biped'], self.dpUIinst.lang['m037_quadruped'], self.dpUIinst.lang['m043_quadSpring'], self.dpUIinst.lang['m155_quadrupedExtra']]
        for item in styleMenuItemList:
            cmds.menuItem(label=item, parent=self.styleMenu)
        # read from guide attribute the current value to style:
        currentStyle = cmds.getAttr(self.moduleGrp+".style")
        cmds.optionMenu(self.styleMenu, edit=True, select=int(currentStyle+1))

        # bend layout:
        self.bendMainLayout = cmds.rowColumnLayout("bendMainLayout", numberOfColumns=2, columnWidth=[(1, 260), (2, 80)], columnSpacing=[(1, 2), (2, 10)], parent="selectedModuleColumn")
        self.bendLayout = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 20, 50, 20), columnAlign=[(1, 'right'), (2, 'left'), (3, 'left'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (4, 'both', 10)], parent=self.bendMainLayout)
        cmds.text(label=self.dpUIinst.lang['m044_addBend'], visible=True, parent=self.bendLayout)
        self.bendCB = cmds.checkBox(value=self.getHasBend(), label=' ', changeCommand=self.changeBend, parent=self.bendLayout)
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
        # additional ribbon joint:
        self.hasAdditional = self.getHasAdditional()
        self.additionalCB = cmds.checkBox("additionalCB", label=self.dpUIinst.lang['m180_additional'], value=self.hasAdditional, changeCommand=self.changeAdditional, parent=self.bendMainLayout)
        
        # align world layout:
        self.alignWorldLayout = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 20, 50, 20), columnAlign=[(1, 'right'), (2, 'left'), (3, 'left'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (4, 'both', 10)], parent="selectedModuleColumn")
        cmds.text(label=self.dpUIinst.lang['m080_alignWorld'], visible=True, parent=self.alignWorldLayout)
        self.alignWorldCB = cmds.checkBox(value=self.getAlignWorld(), label=' ', ofc=partial(self.setAlignWorld, 0), onc=partial(self.setAlignWorld, 1), parent=self.alignWorldLayout)

        
    def setAlignWorld(self, value, *args):
        cmds.setAttr(self.moduleGrp+".alignWorld", value)


    def changeBend(self, value, *args):
        """ Just set bend values and enable or disable UI elements.
        """
        self.hasBend = value
        cmds.optionMenu(self.bendNumJointsMenu, edit=True, enable=value)
        cmds.checkBox(self.additionalCB, edit=True, enable=value)
        cmds.setAttr(self.moduleGrp+".hasBend", value)


    def changeNumBend(self, numberBendJoints, *args):
        """ Change the number of joints used in the bend ribbon.
        """
        cmds.setAttr(self.moduleGrp+".numBendJoints", int(numberBendJoints))


    def changeAdditional(self, *args):
        self.hasAdditional = cmds.checkBox(self.additionalCB, query=True, value=True)
        cmds.setAttr(self.moduleGrp+".additional", self.hasAdditional)


    def changeStyle(self, style, *args):
        """ Change the style to be applyed custom actions to be more animator friendly.
            We will optimise: ik controls mirrored correctely, quadruped front legs using ikSpring solver, good parents and constraints
        """
        self.cvCornerBLoc = self.guideName+"_CornerB"
        # for Default style:
        if style == self.dpUIinst.lang['m042_default'] or style == 0:
            cmds.setAttr(self.cvCornerBLoc+".visibility", 0)
            cmds.setAttr(self.moduleGrp+".style", 0)
        # for Biped style:
        if style == self.dpUIinst.lang['m026_biped'] or style == 1:
            cmds.setAttr(self.cvCornerBLoc+".visibility", 0)
            cmds.setAttr(self.moduleGrp+".style", 1)
        # for Quadruped style:
        if style == self.dpUIinst.lang['m037_quadruped'] or style == 2:
            cmds.setAttr(self.cvCornerBLoc+".visibility", 1)
            cmds.setAttr(self.moduleGrp+".style", 2)
        # for Quadruped Spring style:
        if style == self.dpUIinst.lang['m043_quadSpring'] or style == 3:
            cmds.setAttr(self.cvCornerBLoc+".visibility", 1)
            cmds.setAttr(self.moduleGrp+".style", 3)
        # for Quadruped Extra style:
        if style == self.dpUIinst.lang['m155_quadrupedExtra'] or style == 4:
            cmds.setAttr(self.cvCornerBLoc+".visibility", 1)
            cmds.setAttr(self.moduleGrp+".style", 4)
        

    def changeType(self, type, *args):
        """ This function will modify the names of the rigged module to Arm or Leg options
            and rotate the moduleGrp in order to be more easy to user edit.
        """
        # re-declaring guide names:
        self.cvBeforeLoc = self.guideName+"_Before"
        self.cvMainLoc = self.guideName+"_Main"
        self.cornerGrp = self.guideName+"_Corner_Grp"
        self.cvCornerLoc = self.guideName+"_Corner"
        self.cvCornerBLoc = self.guideName+"_CornerB"
        self.cvExtremLoc = self.guideName+"_Extrem"
        self.cvEndJoint = self.guideName+"_JointEnd"
        self.cvUpVectorLoc = self.guideName+"_CornerUpVector"
        self.cornerAIC = self.cornerGrp+"_AiC"

        self.utils.unlockAttr([self.cvBeforeLoc, self.cvMainLoc, self.cornerGrp, self.cvCornerLoc, self.cvCornerBLoc, self.cvExtremLoc, self.cvEndJoint, self.cvUpVectorLoc, self.cornerAIC])

        # reset translations:
        translateAttrList = ['tx', 'ty', 'tz']
        guideList = [self.cvBeforeLoc, self.cvMainLoc, self.cornerGrp, self.cvExtremLoc, self.cvUpVectorLoc]
        for guideNode in guideList:
            for tAttr in translateAttrList:
                cmds.setAttr(guideNode+"."+tAttr, lock=False)
                cmds.setAttr(guideNode+"."+tAttr, 0)

        # for Arm type:
        if type == self.dpUIinst.lang['m028_arm'] or type == 0:
            cmds.setAttr(self.moduleGrp+".type", 0)
            cmds.setAttr(self.cvBeforeLoc+".translateX", -1)
            cmds.setAttr(self.cvBeforeLoc+".translateZ", -4)
            cmds.setAttr(self.cvExtremLoc+".translateZ", 10)
            cmds.setAttr(self.cvExtremLoc+".translateX", lock=True)
            cmds.setAttr(self.cornerGrp+".translateY", -0.75)
            cmds.setAttr(self.cvCornerLoc+".translateZ", 0)
            cmds.setAttr(self.cvEndJoint+".translateZ", 1.3)
            cmds.setAttr(self.moduleGrp+".rotateX", 90)
            cmds.setAttr(self.moduleGrp+".rotateY", 0)
            cmds.setAttr(self.moduleGrp+".rotateZ", 90)
            cmds.setAttr(self.cvUpVectorLoc+".translateY", -10)
            cmds.delete(self.cornerAIC)
            self.cornerAIC = cmds.aimConstraint(self.cvExtremLoc, self.cornerGrp, aimVector=(0.0, 0.0, 1.0), upVector=(0.0, -1.0, 0.0), worldUpType="object", worldUpObject=self.cvUpVectorLoc, name=self.cornerGrp+"_AiC")[0]
            self.setLockCornerAttr(self.armName)
            self.recreateAutoAim()
            
        # for Leg type:
        elif type == self.dpUIinst.lang['m030_leg'] or type == 1:
            cmds.setAttr(self.moduleGrp+".type", 1)
            cmds.setAttr(self.cvBeforeLoc+".translateY", 1)
            cmds.setAttr(self.cvBeforeLoc+".translateZ", -2)
            cmds.setAttr(self.cvExtremLoc+".translateZ", 10)
            cmds.setAttr(self.cvExtremLoc+".translateY", lock=True)
            cmds.setAttr(self.cornerGrp+".translateX", 0.75)
            cmds.setAttr(self.cvCornerLoc+".translateZ", 0)
            cmds.setAttr(self.cvEndJoint+".translateZ", 1.3)
            cmds.setAttr(self.moduleGrp+".rotateX", 0)
            cmds.setAttr(self.moduleGrp+".rotateY", -90)
            cmds.setAttr(self.moduleGrp+".rotateZ", 90)
            cmds.setAttr(self.cvUpVectorLoc+".translateX", 10)
            cmds.setAttr(self.cvUpVectorLoc+".translateY", 0.75)
            cmds.delete(self.cornerAIC)
            self.cornerAIC = cmds.aimConstraint(self.cvExtremLoc, self.cornerGrp, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0), worldUpType="object", worldUpObject=self.cvUpVectorLoc, name=self.cornerGrp+"_AiC")[0]
            self.setLockCornerAttr(self.legName)
            self.recreateAutoAim()
    
    
    def getLimbType(self, *args):
        """ This function will get the limbType
        """
        enumType = cmds.getAttr(self.moduleGrp+'.type')
        if enumType == 0:
            self.limbType = self.dpUIinst.lang['m028_arm']
            self.limbTypeName = self.armName
        elif enumType == 1:
            self.limbType = self.dpUIinst.lang['m030_leg']
            self.limbTypeName = self.legName
        return self.limbTypeName


    def getLimbStyle(self, *args):
        """ This function will get the limbStyle
        """
        enumStyle = cmds.getAttr(self.moduleGrp+'.style')
        if enumStyle == 0:
            self.limbStyle = self.dpUIinst.lang['m042_default']
        elif enumStyle == 1:
            self.limbStyle = self.dpUIinst.lang['m026_biped']
        elif enumStyle == 2:
            self.limbStyle = self.dpUIinst.lang['m037_quadruped']
        elif enumStyle == 3:
            self.limbStyle = self.dpUIinst.lang['m043_quadSpring']
        elif enumStyle == 4:
            self.limbStyle = self.dpUIinst.lang['m155_quadrupedExtra']
        return self.limbStyle
     

    def setLockCornerAttr(self, limbType, *args):
        """ Set corner guide lock attributes to specific limb type (arm or leg).
        """
        trAttrList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
        cornerAttrList = ['tx', 'ry', 'rz'] #arm
        if limbType == self.legName:
            cornerAttrList = ['ty', 'rx', 'rz'] #leg
        for attr in trAttrList:
            if attr in cornerAttrList:
                cmds.setAttr(self.cvCornerLoc+"."+attr, 0, lock=True)
                cmds.setAttr(self.cvCornerBLoc+"."+attr, 0, lock=True)
            else:
                cmds.setAttr(self.cvCornerLoc+"."+attr, lock=False)
                cmds.setAttr(self.cvCornerBLoc+"."+attr, lock=False)


    def getOriginalRotate(self, ctrl, *args):
        """ Use a temporary node to extract the world space rotation and returns it.
        """
        tempDup = cmds.duplicate(ctrl)[0]
        cmds.parent(tempDup, world=True)
        originalRotateList = cmds.xform(tempDup, query=True, rotation=True, worldSpace=True)
        cmds.delete(tempDup)
        return originalRotateList

    
    def getCalibratePresetList(self, s, isLeg, first, main, corner, kneeB, extrem, *args):
        """ Returns the calibration preset and invert lists for the asked limb joint.
        """
        presetList = None
        invertList = None
        if first: #clavicle/hips
            presetList = [{}, {"calibrateTX":1.0, "calibrateTZ":0.5, "calibrateRY":-30}]
            if s ==  1:
                invertList = [[], ["invertTX", "invertRY"]]
        elif main: #shoulder/leg
            if isLeg:
                presetList = [{}, {"calibrateTY":-0.5, "calibrateTZ":-0.4, "calibrateRX":30}, {"calibrateTX":1.0, "calibrateRY":30}]
            else:
                presetList = [{}, {"calibrateTY":0.5, "calibrateTZ":0.2}, {"calibrateTX":1.0, "calibrateRY":30}]
            if s == 1:
                invertList = [[], [], ["invertTX", "invertRY"]]
        elif corner: #elbow/knee
            presetList = [{}, {"calibrateTX":0.1, "calibrateTZ":-0.6, "calibrateRY":45}, {"calibrateTX":-0.4, "calibrateTZ":0.8, "calibrateRY":-65}, {"calibrateTX":0.3, "calibrateTZ":0.8, "calibrateRY":65}]
            if not isLeg:
                invertList = [[], ["invertRY"], [], []]
                if s == 1:
                    if self.getHasBend():
                        invertList = [[], ["invertTX", "invertTZ", "invertRY"], ["invertTX", "invertTZ"], ["invertTX", "invertTZ"]]
                    else:
                        invertList = [[], ["invertRY"], [], []]
        elif kneeB: #kneeB
            presetList = [{}, {"calibrateTX":0.1, "calibrateTZ":-0.6, "calibrateRY":-45}, {"calibrateTX":-0.4, "calibrateTZ":0.8, "calibrateRY":-65}, {"calibrateTX":0.3, "calibrateTZ":0.8, "calibrateRY":65}]
            if self.dpUIinst.lang['c057_back'] in self.userGuideName:
                invertList = [[], [], ["invertTX", "invertRY", "invertRZ"], ["invertTX", "invertRY", "invertRZ"]]
            if s == 1:
                invertList = [[], ["invertTX", "invertRY", "invertRZ"], ["invertTX", "invertRY", "invertRZ"], ["invertTX", "invertRY", "invertRZ"]]
                if self.dpUIinst.lang['c057_back'] in self.userGuideName:
                    invertList = [[], [], [], []]
        elif extrem: #wrist/ankle
            presetList = [{}, {"calibrateTX":0.7, "calibrateRY":-30}, {"calibrateTX":-0.7, "calibrateRY":30}, {"calibrateTY":0.7, "calibrateRX":30}, {"calibrateTY":-0.7, "calibrateRX":-30}]
            if s == 1:
                invertList = [[], ["invertTX", "invertRY", "invertRZ"], ["invertTX", "invertRY", "invertRZ"], ["invertTX", "invertRY", "invertRZ"], ["invertTX", "invertRY", "invertRZ"]]
        return presetList, invertList


    def rigModule(self, *args):
        dpBaseStandard.BaseStandard.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            # articulation joint:
            self.addArticJoint = self.getArticulation()
            # corrective network:
            self.addCorrective = self.getModuleAttr("corrective")
            # run for all sides
            for s, side in enumerate(self.sideList):
                attrNameLower = self.utils.getAttrNameLower(side, self.userGuideName)
                toCornerBendList = []
                
                # getting type of limb:
                self.getLimbType()

                # getting style of the limb:
                self.getLimbStyle()

                # re-declaring guide names:
                self.cvBeforeLoc = side+self.userGuideName+"_Guide_Before"
                self.cvMainLoc = side+self.userGuideName+"_Guide_Main"
                self.cvCornerLoc = side+self.userGuideName+"_Guide_Corner"
                self.cvCornerBLoc = side+self.userGuideName+"_Guide_CornerB"
                self.cvExtremLoc = side+self.userGuideName+"_Guide_Extrem"
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"

                # getting names from dic:
                if self.limbTypeName == self.armName:
                    beforeName = self.dpUIinst.lang['c000_arm_before']
                    mainName = self.dpUIinst.lang['c001_arm_main']
                    cornerName = self.dpUIinst.lang['c002_arm_corner']
                    cornerBName = self.dpUIinst.lang['c003_arm_cornerB']
                    extremName = self.dpUIinst.lang['c004_arm_extrem']
                else:
                    beforeName = self.dpUIinst.lang['c005_leg_before']
                    mainName = self.dpUIinst.lang['c006_leg_main']
                    cornerName = self.dpUIinst.lang['c007_leg_corner']
                    cornerBName = self.dpUIinst.lang['c008_leg_cornerB']
                    extremName = self.dpUIinst.lang['c009_leg_extrem']

                # mount cvLocList and jNameList:
                if self.limbStyle == self.dpUIinst.lang['m037_quadruped'] or self.limbStyle == self.dpUIinst.lang['m043_quadSpring'] or self.limbStyle == self.dpUIinst.lang['m155_quadrupedExtra']:
                    self.cvLocList = [self.cvBeforeLoc, self.cvMainLoc, self.cvCornerLoc, self.cvCornerBLoc, self.cvExtremLoc]
                    self.jNameList = [beforeName, mainName, cornerName, cornerBName, extremName]
                else:
                    self.cvLocList = [self.cvBeforeLoc, self.cvMainLoc, self.cvCornerLoc, self.cvExtremLoc]
                    self.jNameList = [beforeName, mainName, cornerName, extremName]

                # creating joint chains:
                self.chainDic = {}
                self.jSufixList = ['_Jnt', '_Ik_Jxt', '_Fk_Jxt', '_IkNotStretch_Jxt', '_IkAC_Jxt']
                self.jEndSufixList = ['_JEnd', '_Ik_JEnd', '_Fk_JEnd', '_IkNotStretch_JEnd', '_IkAC_JEnd']
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
                self.ikJointList = self.chainDic[self.jSufixList[1]]
                self.fkJointList = self.chainDic[self.jSufixList[2]]
                self.ikNSJointList = self.chainDic[self.jSufixList[3]]
                self.ikACJointList = self.chainDic[self.jSufixList[4]]
                
                # hide not skin joints in order to be more Rigger friendly when working the Skinning:
                cmds.setAttr(self.ikJointList[0]+".visibility", 0)
                cmds.setAttr(self.fkJointList[0]+".visibility", 0)
                cmds.setAttr(self.ikNSJointList[0]+".visibility", 0)
                cmds.setAttr(self.ikACJointList[1]+".visibility", 0)

                for o, skinJoint in enumerate(self.skinJointList):
                    if o < len(self.skinJointList) - 1:
                        cmds.addAttr(skinJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                        self.utils.setJointLabel(skinJoint, s+self.jointLabelAdd, 18, self.userGuideName+"_"+self.jNameList[o])

                # creating Fk controls and a hierarchy group to originedFrom data:
                self.fkCtrlList, self.origFromList = [], []
                for n, jName in enumerate(self.jNameList):
                    if n == 0:
                        fkCtrl = self.ctrls.cvControl("id_030_LimbClavicle", side+self.userGuideName+"_"+jName+"_Ctrl", r=(self.ctrlRadius * 2), d=self.curveDegree, rot=(45, 0 ,-90), guideSource=self.guideModuleName+"__"+self.cvLocList[n].replace("_Guide", ":Guide"))
                    else:
                        fkCtrl = self.ctrls.cvControl("id_031_LimbFk", side+self.userGuideName+"_"+jName+"_Fk_Ctrl", r=self.ctrlRadius, d=self.curveDegree, guideSource=self.guideModuleName+"__"+self.cvLocList[n].replace("_Guide", ":Guide"))
                    
                    # Setup axis order
                    if jName == beforeName:  # Clavicle and hip
                        cmds.setAttr(fkCtrl+".rotateOrder", 3)
                    elif jName == extremName and self.limbTypeName == self.legName:  # Ankle
                        cmds.setAttr(fkCtrl+".rotateOrder", 4)
                    elif jName == extremName and self.limbTypeName == self.armName:  # Hand
                        cmds.setAttr(fkCtrl+".rotateOrder", 4)
                    elif jName == mainName:  # Leg and Shoulder
                        cmds.setAttr(fkCtrl+".rotateOrder", 1)
                    elif self.limbTypeName == self.legName:  # Other legs ctrl
                        cmds.setAttr(fkCtrl+".rotateOrder", 2)
                    elif self.limbTypeName == self.armName:  # Other arm ctrl
                        cmds.setAttr(fkCtrl+".rotateOrder", 5)
                    else:
                        # Let the default axis order for other ctrl (Should not happen)
                        pass

                    # Other arm ctrl can keep the default xyz

                    self.fkCtrlList.append(fkCtrl)
                    cmds.setAttr(fkCtrl+'.visibility', keyable=False)
                    # creating the originedFrom attributes (in order to permit integrated parents in the future):
                    origGrp = cmds.group(empty=True, name=side+self.userGuideName+"_"+jName+"_OrigFrom_Grp")
                    self.origFromList.append(origGrp)
                    if n == 0: #Clavicle/Hips
                        self.utils.originedFrom(objName=origGrp, attrString=self.cvLocList[n][self.cvLocList[n].find("__")+1:].replace(":", "_"))
                    elif n == 1: #Shoulder/Leg
                        self.utils.originedFrom(objName=origGrp, attrString=self.cvLocList[n][self.cvLocList[n].find("__")+1:].replace(":", "_")+";"+self.cvMainLoc)
                    elif n == len(self.jNameList)-1: #Wrist/Ankle
                        self.utils.originedFrom(objName=origGrp, attrString=self.cvLocList[n][self.cvLocList[n].find("__")+1:].replace(":", "_")+";"+self.cvEndJoint+";"+self.radiusGuide)
                    else: #Corner
                        self.utils.originedFrom(objName=origGrp, attrString=self.cvLocList[n][self.cvLocList[n].find("__")+1:].replace(":", "_"))
                        if self.getHasBend():
                            toCornerBendList.append(self.cvLocList[n][self.cvLocList[n].find("__")+1:].replace(":", "_"))
                    cmds.parentConstraint(self.skinJointList[n], origGrp, maintainOffset=False, name=origGrp+"_PaC")
                    
                    if n > 1:
                        cmds.parent(fkCtrl, self.fkCtrlList[n - 1])
                        cmds.parent(origGrp, self.origFromList[n - 1])
                    # add wrist_toParent_Ctrl
                    if n == len(self.jNameList)-1:
                        self.toParentExtremCtrl = self.ctrls.cvControl("id_032_LimbToParent", ctrlName=side+self.userGuideName+"_"+extremName+"_ToParent_Ctrl", r=(self.ctrlRadius * 0.1), d=self.curveDegree, guideSource=self.guideName+"_Extrem")
                        cmds.parent(self.toParentExtremCtrl, origGrp)
                        if s == 0:
                            cmds.setAttr(self.toParentExtremCtrl+".translateX", self.ctrlRadius)
                        else:
                            cmds.setAttr(self.toParentExtremCtrl+".translateX", -self.ctrlRadius)
                        self.utils.zeroOut([self.toParentExtremCtrl], notTransformIO=False)
                        self.ctrls.setLockHide([self.toParentExtremCtrl], ['v'])
                # zeroOut controls:
                self.zeroFkCtrlList = self.utils.zeroOut(self.fkCtrlList)
                self.zeroFkCtrlGrp = cmds.group(self.zeroFkCtrlList[0], self.zeroFkCtrlList[1], name=side+self.userGuideName+"_Fk_Ctrl_Grp")
                
                # working with position, orientation of joints and make an orientConstrain for Fk controls:
                for n in range(len(self.jNameList)):
                    tempToDelA = cmds.parentConstraint(self.cvLocList[n], self.skinJointList[n], maintainOffset=False)
                    tempToDelB = cmds.parentConstraint(self.cvLocList[n], self.ikJointList[n], maintainOffset=False)
                    tempToDelB1 = cmds.parentConstraint(self.cvLocList[n], self.ikNSJointList[n], maintainOffset=False)
                    tempToDelB2 = cmds.parentConstraint(self.cvLocList[n], self.ikACJointList[n], maintainOffset=False)
                    tempToDelC = cmds.parentConstraint(self.cvLocList[n], self.fkJointList[n], maintainOffset=False)
                    tempToDelD = cmds.parentConstraint(self.cvLocList[n], self.zeroFkCtrlList[n], maintainOffset=False)
                    cmds.delete(tempToDelA, tempToDelB, tempToDelB1, tempToDelB2, tempToDelC, tempToDelD)
                    # freezeTransformations (rotates):
                    cmds.makeIdentity(self.skinJointList[n], self.ikJointList[n], self.ikNSJointList[n], self.ikACJointList[n], self.fkJointList[n], apply=True, rotate=True)
                    # fk control leads fk joint:
                    if n == 0:
                        cmds.parentConstraint(self.fkCtrlList[n], self.fkJointList[n], maintainOffset=True, name=side+self.userGuideName+"_"+self.jNameList[n]+"_PaC")
                    else:
                        cmds.parentConstraint(self.fkCtrlList[n], self.fkJointList[n], maintainOffset=True, name=side+self.userGuideName+"_"+self.jNameList[n]+"_Fk_PaC")
                    if n == 0:
                        clavicleJointList = [self.skinJointList[0], self.ikJointList[0], self.fkJointList[0], self.ikNSJointList[0]]
                        for clavicleJoint in clavicleJointList:
                            for axis in self.axisList:
                                cmds.connectAttr(self.fkCtrlList[0]+".scale"+axis, clavicleJoint+".scale"+axis, force=True)
                    elif n == 1 or n == 2: #shoulder/elbow
                        self.ctrls.setLockHide([self.fkCtrlList[n]], ['sx', 'sy'])
                    else:
                        self.ctrls.setLockHide([self.fkCtrlList[n]], ['sx', 'sy', 'sz'])
                
                # puting endJoints in the correct position:
                tempToDelE = cmds.parentConstraint(self.cvEndJoint, self.skinJointList[-1], maintainOffset=False)
                tempToDelF = cmds.parentConstraint(self.cvEndJoint, self.ikJointList[-1], maintainOffset=False)
                tempToDelF1 = cmds.parentConstraint(self.cvEndJoint, self.ikNSJointList[-1], maintainOffset=False)
                tempToDelF2 = cmds.parentConstraint(self.cvEndJoint, self.ikACJointList[-1], maintainOffset=False)
                tempToDelG = cmds.parentConstraint(self.cvEndJoint, self.fkJointList[-1], maintainOffset=False)
                cmds.delete(tempToDelE, tempToDelF, tempToDelF1, tempToDelF2, tempToDelG)

                # creating a group reference to recept the attributes:
                self.worldRef = self.ctrls.cvControl("id_036_LimbWorldRef", side+self.userGuideName+"_WorldRef_Ctrl", r=self.ctrlRadius, d=self.curveDegree, dir="+Z", guideSource=self.guideName+"_Base")
                cmds.addAttr(self.worldRef, longName="ikFkSnap", attributeType='short', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                cmds.addAttr(self.worldRef, longName=self.dpUIinst.lang['c113_length'], attributeType='float', defaultValue=1)
                self.worldRefList.append(self.worldRef)
                self.worldRefShape = cmds.listRelatives(self.worldRef, children=True, type='nurbsCurve')[0]
                self.worldRefShapeList.append(self.worldRefShape)
                # creating a group reference to follow masterCtrl and rootCtrl:
                self.masterCtrlRef = cmds.group(empty=True, name=side+self.userGuideName+"_MasterCtrlRef_Grp")
                self.masterCtrlRefList.append(self.masterCtrlRef)
                self.rootCtrlRef = cmds.group(empty=True, name=side+self.userGuideName+"_RootCtrlRef_Grp")
                self.rootCtrlRefList.append(self.rootCtrlRef)

                # parenting fkControls from 2 hierarchies (before and limb) using constraint, attention to fkIsolated shoulder:
                # creating a shoulder_ref group in order to use it as position relative, joint articulation origin and aim constraint target to self.quadExtraCtrl:
                self.shoulderRefGrp = cmds.group(empty=True, name=self.skinJointList[1]+"_Ref_Grp")
                # ask if the module is self.armName and turn default value to 1 if true.
                self.isolateDefaultValue = 0
                if self.limbTypeName == self.armName:
                    self.isolateDefaultValue = 1  
                cmds.parent(self.shoulderRefGrp, self.skinJointList[1], relative=True)
                cmds.parent(self.shoulderRefGrp, self.skinJointList[0], relative=False)
                cmds.pointConstraint(self.shoulderRefGrp, self.zeroFkCtrlList[1], maintainOffset=True, name=self.zeroFkCtrlList[1]+"_PoC")
                fkIsolateParentConst = cmds.parentConstraint(self.shoulderRefGrp, self.masterCtrlRef, self.zeroFkCtrlList[1], skipTranslate=["x", "y", "z"], maintainOffset=True, name=self.zeroFkCtrlList[1]+"_PaC")[0]               
                cmds.addAttr(self.fkCtrlList[1], longName=self.dpUIinst.lang['m095_isolate'].lower(), attributeType='float', minValue=0, maxValue=1, defaultValue=self.isolateDefaultValue, keyable=True)
                self.addFollowAttrName(self.fkCtrlList[1], self.dpUIinst.lang['m095_isolate'].lower())
                cmds.connectAttr(self.fkCtrlList[1]+'.'+self.dpUIinst.lang['m095_isolate'].lower(), fkIsolateParentConst+"."+self.masterCtrlRef+"W1", force=True)
                self.fkIsolateRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_FkIsolate_Rev")
                cmds.connectAttr(self.fkCtrlList[1]+'.'+self.dpUIinst.lang['m095_isolate'].lower(), self.fkIsolateRevNode+".inputX", force=True)
                cmds.connectAttr(self.fkIsolateRevNode+'.outputX', fkIsolateParentConst+"."+self.shoulderRefGrp+"W0", force=True) 
                self.afkIsolateConst.append(fkIsolateParentConst)

                # create orient constrain in order to blend ikFk:
                ikFkRevNode = self.utils.createJointBlend(self.ikJointList[1:], self.fkJointList[1:], self.skinJointList[1:], "Fk_ikFkBlend", attrNameLower, self.worldRef)

                # organize the ikFkBlend from before to limb:
                cmds.parentConstraint(self.fkCtrlList[0], self.ikJointList[0], maintainOffset=True, name=self.ikJointList[0]+"_PaC")
                cmds.parentConstraint(self.fkCtrlList[0], self.ikNSJointList[0], maintainOffset=True, name=self.ikNSJointList[0]+"_PaC")
                cmds.parentConstraint(self.fkCtrlList[0], self.fkJointList[0], maintainOffset=True, name=self.fkJointList[0]+"_PaC")
                cmds.parentConstraint(self.fkCtrlList[0], self.skinJointList[0], maintainOffset=True, name=self.skinJointList[0]+"_PaC")

                # creating ik controls:
                self.ikExtremCtrl = self.ctrls.cvControl("id_033_LimbWrist", ctrlName=side+self.userGuideName+"_"+extremName+"_Ik_Ctrl", r=(self.ctrlRadius * 0.5), d=self.curveDegree, guideSource=self.guideName+"_Extrem")
                self.ikExtremSubCtrl = self.ctrls.cvControl("id_094_LimbExtremSub", ctrlName=side+self.userGuideName+"_"+extremName+"_Ik_Sub_Ctrl", r=(self.ctrlRadius * 0.5), d=self.curveDegree, guideSource=self.guideName+"_Extrem")
                self.ikExtremOrientCtrl = self.ctrls.cvControl("id_101_LimbExtremOrient", ctrlName=side+self.userGuideName+"_"+extremName+"_Ik_Orient_Ctrl", r=(self.ctrlRadius * 0.7), d=self.curveDegree, guideSource=self.guideName+"_Extrem")
                self.ctrls.setLockHide([self.ikExtremSubCtrl], ["sx", "sy", "sz", "v"])
                self.ctrls.setSubControlDisplay(self.ikExtremCtrl, self.ikExtremSubCtrl, 0)
                cmds.parent(self.ikExtremSubCtrl, self.ikExtremCtrl)
                
                if self.limbTypeName == self.armName:
                    self.ikCornerCtrl = self.ctrls.cvControl("id_034_LimbElbow", ctrlName=side+self.userGuideName+"_"+cornerName+"_Ik_Ctrl", r=(self.ctrlRadius * 0.5), d=self.curveDegree, guideSource=self.guideName+"_Corner")
                    cmds.setAttr(self.ikExtremCtrl+".rotateOrder", 2) #zxy
                    cmds.setAttr(self.ikExtremSubCtrl+".rotateOrder", 2) #zxy
                    cmds.setAttr(self.ikExtremOrientCtrl+".rotateOrder", 2) #zxy
                else:
                    self.ikCornerCtrl = self.ctrls.cvControl("id_035_LimbKnee", ctrlName=side+self.userGuideName+"_"+cornerName+"_Ik_Ctrl", r=(self.ctrlRadius * 0.5), d=self.curveDegree, guideSource=self.guideName+"_Corner")
                    cmds.setAttr(self.ikExtremCtrl+".rotateOrder", 3) #xzy
                    cmds.setAttr(self.ikExtremSubCtrl+".rotateOrder", 3) #xzy
                    cmds.setAttr(self.ikExtremOrientCtrl+".rotateOrder", 3) #xzy
                self.ikExtremCtrlList.append(self.ikExtremCtrl)
                self.utils.originedFrom(objName=self.ikCornerCtrl, attrString=side+self.userGuideName+"_Guide_CornerUpVector")

                # getting them zeroOut groups:
                self.ikCornerCtrlZero = self.utils.zeroOut([self.ikCornerCtrl])[0]
                self.ikExtremCtrlZero = self.utils.zeroOut([self.ikExtremCtrl])[0]
                self.ikExtremCtrlZeroList.append(self.ikExtremCtrlZero)
                self.ikExtremOrientCtrlZero = self.utils.zeroOut([self.ikExtremOrientCtrl])[0]
                # putting ikCtrls in the correct position and orientation:
                cmds.delete(cmds.parentConstraint(self.cvExtremLoc, self.ikExtremCtrlZero, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvExtremLoc, self.ikExtremOrientCtrlZero, maintainOffset=False))
                self.ctrls.setLockHide([self.ikExtremOrientCtrl], ["tx", "ty", "tz", "sx", "sy", "sz", "v"])

                # fix stretch calcule to work with reverseFoot
                self.ikStretchExtremLoc = cmds.group(empty=True, name=side+self.userGuideName+"_"+extremName+"_Ik_Loc_Grp")
                if self.limbStyle == self.dpUIinst.lang['m037_quadruped'] or self.limbStyle == self.dpUIinst.lang['m043_quadSpring'] or self.limbStyle == self.dpUIinst.lang['m155_quadrupedExtra']:
                    cmds.delete(cmds.parentConstraint(self.skinJointList[3], self.ikStretchExtremLoc, maintainOffset=False)) #snap to kneeB
                else:    
                    cmds.delete(cmds.parentConstraint(self.cvExtremLoc, self.ikStretchExtremLoc, maintainOffset=False))
                
                # fixing ikControl group to get a good mirror orientation more animator friendly:
                self.ikExtremCtrlGrp = cmds.group(self.ikExtremCtrl, name=side+self.userGuideName+"_"+extremName+"_Ik_Ctrl_Grp")
                self.ikExtremCtrlOrientGrp = cmds.group(self.ikExtremCtrlGrp, name=side+self.userGuideName+"_"+extremName+"_Ik_Ctrl_Orient_Grp")
                # adjust rotate orders:
                cmds.setAttr(self.ikExtremCtrlGrp+".rotateOrder", cmds.getAttr(self.ikExtremCtrl+".rotateOrder"))
                cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateOrder", cmds.getAttr(self.ikExtremCtrl+".rotateOrder"))

                # orient ik controls properly:
                if s == 0 or self.limbTypeName == self.armName:
                    cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateX", -90)
                    cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateZ", -90)

                # verify if user wants to apply the good mirror orientation:
                if s == 1:
                    if self.limbStyle != self.dpUIinst.lang['m042_default']:
                        # these options is valides for Biped, Quadruped, Quadruped Spring and Quadruped Extra
                        if self.mirrorAxis != 'off':
                            for axis in self.mirrorAxis:
                                if axis == "X":
                                    if self.limbTypeName == self.armName:
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateX", -90)
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateY", 90)
                                        if self.getAlignWorld():
                                            cmds.setAttr(self.ikExtremCtrlOrientGrp+".scaleX", -1)
                                        else:
                                            cmds.setAttr(self.ikExtremCtrlOrientGrp+".scaleZ", -1)
                                    else: #leg
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateX", 90)
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotateZ", -90)
                                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".scaleX", -1)
                
                # to fix quadruped stretch locator after rotated ik extrem controller:
                ikStretchExtremLocZero = self.utils.zeroOut([self.ikStretchExtremLoc])[0]
                cmds.parent(ikStretchExtremLocZero, self.ikExtremSubCtrl, absolute=True)
                exposeCornerName = cornerName+"_Jnt"
                if self.getHasBend():
                    exposeCornerName = cornerName+"_Jxt"
                if self.limbStyle == self.dpUIinst.lang['m037_quadruped'] or self.limbStyle == self.dpUIinst.lang['m043_quadSpring'] or self.limbStyle == self.dpUIinst.lang['m155_quadrupedExtra']:
                    self.ikStretchExtremLocList.append(None)
                    exposeCornerName = cornerBName+"_Jnt"
                else:
                    self.ikStretchExtremLocList.append(ikStretchExtremLocZero)
                
                # connecting visibilities:
                cmds.connectAttr(self.worldRef+"."+attrNameLower+'Fk_ikFkBlend', self.zeroFkCtrlList[1]+".visibility", force=True)
                cmds.connectAttr(self.worldRef+"."+attrNameLower+"Fk_ikFkBlendRevOutputX", self.ikCornerCtrlZero+".visibility", force=True)
                cmds.connectAttr(self.worldRef+"."+attrNameLower+"Fk_ikFkBlendRevOutputX", self.ikExtremCtrlZero+".visibility", force=True)
                cmds.connectAttr(self.worldRef+"."+attrNameLower+"Fk_ikFkBlendRevOutputX", self.ikExtremOrientCtrlZero+".visibility", force=True)
                self.ctrls.setLockHide([self.ikCornerCtrl], ['v'], l=False)
                self.ctrls.setLockHide([self.ikExtremCtrl], ['sx', 'sy', 'sz', 'v'])

                # creating ikHandles:
                # verify the limb style:
                if self.limbStyle == self.dpUIinst.lang['m043_quadSpring']:
                    # verify if the ikSpringSolver plugin is loaded, if not, then load it
                    loadedIkSpring = self.utils.checkLoadedPlugin("ikSpringSolver", self.dpUIinst.lang['e013_cantLoadIkSpringSolver'])
                    if loadedIkSpring:
                        if not cmds.objExists('ikSpringSolver'):
                            cmds.createNode('ikSpringSolver', name='ikSpringSolver')
                        # using better quadruped front legs solution as ikSpringSolver:
                        ikHandleMainList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_IKH", startJoint=self.ikJointList[1], endEffector=self.ikJointList[len(self.ikJointList) - 2], solver='ikSpringSolver')
                        ikHandleNotStretchList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_NotStretch_IKH", startJoint=self.ikNSJointList[1], endEffector=self.ikNSJointList[len(self.ikNSJointList) - 2], solver='ikSpringSolver')
                        ikHandleACList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_AC_IKH", startJoint=self.ikACJointList[1], endEffector=self.ikACJointList[len(self.ikACJointList) - 2], solver='ikSpringSolver')
                    else:
                        # could not load the ikSpringSolver plutin, the we will use the regular solution as ikRPSolver:
                        ikHandleMainList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_IKH", startJoint=self.ikJointList[1], endEffector=self.ikJointList[len(self.ikJointList) - 2], solver='ikRPsolver')
                        ikHandleNotStretchList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_NotStretch_IKH", startJoint=self.ikNSJointList[1], endEffector=self.ikNSJointList[len(self.ikNSJointList) - 2], solver='ikRPsolver')
                        ikHandleACList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_AC_IKH", startJoint=self.ikACJointList[1], endEffector=self.ikACJointList[len(self.ikACJointList) - 2], solver='ikRPsolver')
                elif self.limbStyle == self.dpUIinst.lang['m155_quadrupedExtra']:
                    # creating double ikHandle in order to get an extra control for lower articulation in Quadruped Extra Control:
                    ikHandleMainList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_IKH", startJoint=self.ikJointList[1], endEffector=self.ikJointList[len(self.ikJointList) - 3], solver='ikRPsolver')
                    ikHandleNotStretchList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_NotStretch_IKH", startJoint=self.ikNSJointList[1], endEffector=self.ikNSJointList[len(self.ikNSJointList) - 2], solver='ikRPsolver')
                    ikHandleACList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_AC_IKH", startJoint=self.ikACJointList[1], endEffector=self.ikACJointList[len(self.ikACJointList) - 2], solver='ikRPsolver')
                    ikHandleExtraList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_Extra_IKH", startJoint=self.ikJointList[len(self.ikJointList) - 3], endEffector=self.ikJointList[len(self.ikJointList) - 2], solver='ikRPsolver')
                else:
                    # using regular solution as ikRPSolver:
                    ikHandleMainList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_IKH", startJoint=self.ikJointList[1], endEffector=self.ikJointList[len(self.ikJointList) - 2], solver='ikRPsolver')
                    ikHandleNotStretchList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_NotStretch_IKH", startJoint=self.ikNSJointList[1], endEffector=self.ikNSJointList[len(self.ikNSJointList) - 2], solver='ikRPsolver')
                    ikHandleACList = cmds.ikHandle(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_AC_IKH", startJoint=self.ikACJointList[1], endEffector=self.ikACJointList[len(self.ikACJointList) - 2], solver='ikRPsolver')

                # renaming effectors:
                cmds.rename(ikHandleMainList[1], side+self.userGuideName+"_"+self.limbType.capitalize()+"_Eff")
                cmds.rename(ikHandleNotStretchList[1], side+self.userGuideName+"_"+self.limbType.capitalize()+"_NotStretch_Eff")
                cmds.rename(ikHandleACList[1], side+self.userGuideName+"_"+self.limbType.capitalize()+"_AC_Eff")

                # creating ikHandle groups:
                cmds.setAttr(ikHandleMainList[0]+'.visibility', 0)
                ikHandleGrp = cmds.group(empty=True, name=side+self.userGuideName+"_IKH_Grp")
                self.ikHandleToRFGrp = cmds.group(empty=True, name=side+self.userGuideName+"_IKHToRF_Grp")
                self.ikHandleToRFGrpList.append(ikHandleGrp)
                cmds.setAttr(self.ikHandleToRFGrp+'.visibility', 0)
                cmds.parent(self.ikHandleToRFGrp, ikHandleGrp)
                # for ikHandle not stretch group:
                ikHandleNotStretchGrp = cmds.group(empty=True, name=side+self.userGuideName+"_NotStretch_IKH_Grp")
                cmds.setAttr(ikHandleNotStretchGrp+'.visibility', 0)
                cmds.parent(ikHandleNotStretchList[0], ikHandleNotStretchGrp)
                # for ikHandle auto clavicle group:
                ikHandleACGrp = cmds.group(empty=True, name=side+self.userGuideName+"_AC_IKH_Grp")
                cmds.setAttr(ikHandleACGrp+'.visibility', 0)
                cmds.parent(ikHandleACList[0], ikHandleACGrp)

                # setup quadruped extra control:
                if self.limbStyle == self.dpUIinst.lang['m155_quadrupedExtra']:
                    cmds.rename(ikHandleExtraList[1], side+self.userGuideName+"_"+self.limbType.capitalize()+"_Extra_Eff")
                    self.quadExtraCtrl = self.ctrls.cvControl("id_058_LimbQuadExtra", ctrlName=side+self.userGuideName+"_"+extremName+"_Ik_Extra_Ctrl", r=(self.ctrlRadius * 0.7), d=self.curveDegree, dir="-Z", guideSource=self.guideName+"_Extrem")
                    if s == 1:
                        cmds.setAttr(self.quadExtraCtrl+".rotateY", 180)
                        cmds.makeIdentity(self.quadExtraCtrl, rotate=True, apply=True)
                    quadExtraCtrlZero = self.utils.zeroOut([self.quadExtraCtrl])[0]
                    cmds.delete(cmds.parentConstraint(self.ikExtremCtrl, quadExtraCtrlZero, maintainOffset=False))
                    cmds.parent(quadExtraCtrlZero, ikHandleGrp)
                    cmds.parent(ikHandleExtraList[0], self.ikHandleToRFGrp)
                    cmds.setAttr(ikHandleExtraList[0]+".visibility", 0)
                    cmds.addAttr(self.quadExtraCtrl, longName='twist', attributeType='float', keyable=True)
                    cmds.connectAttr(self.quadExtraCtrl+'.twist', ikHandleExtraList[0]+".twist", force=True)
                    cmds.connectAttr(ikFkRevNode+".outputX", quadExtraCtrlZero+".visibility", force=True)
                    self.ctrls.setLockHide([self.quadExtraCtrl], ['sx', 'sy', 'sz', 'v'])
                
                # working with world axis orientation for limb extrem ik controls
                if self.getAlignWorld():
                    originalRotateMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_"+extremName+"_OriginalRotate_MD")
                    alignWorldRev = cmds.createNode("reverse", name=side+self.userGuideName+"_"+extremName+"_AlighWorld_Rev")
                    self.toIDList.extend([originalRotateMD, alignWorldRev])
                    cmds.addAttr(self.ikExtremCtrl, longName="alignWorld", attributeType="float", defaultValue=0, minValue=0, maxValue=1, keyable=True)
                    cmds.connectAttr(self.ikExtremCtrl+".alignWorld", alignWorldRev+".inputX", force=True)
                    if s == 0:
                        self.origRotList = self.getOriginalRotate(self.ikExtremCtrl)
                    elif self.limbStyle == self.dpUIinst.lang['m042_default']:
                        if self.limbTypeName == self.armName:
                            # get right side to alignWorld. It'll be a little glitch, but it seems be accordilly with the mirror using arm default setting. Recommended use biped limbStyle instead.
                            self.origRotList = self.getOriginalRotate(self.ikExtremCtrl)
                    for a, axis in enumerate(self.axisList):
                        cmds.setAttr(self.ikExtremCtrlOrientGrp+".rotate"+axis, 0)
                        cmds.setAttr(self.ikExtremCtrlZero+".rotate"+axis, 0)
                        # store original rotation values for initial default pose
                        cmds.addAttr(self.ikExtremCtrl, longName="originalRotate"+axis, attributeType="float", keyable=True)
                        cmds.setAttr(self.ikExtremCtrl+".originalRotate"+axis, self.origRotList[a], lock=True)
                        cmds.connectAttr(self.ikExtremCtrl+".originalRotate"+axis, originalRotateMD+".input1"+axis, force=True)
                        cmds.connectAttr(alignWorldRev+".outputX", originalRotateMD+".input2"+axis, force=True)
                        cmds.connectAttr(originalRotateMD+".output"+axis, self.ikExtremCtrlGrp+".rotate"+axis, force=True)

                # make ikControls lead ikHandles:
                ikHandleExtraGrp = cmds.group(empty=True, name=ikHandleMainList[0]+"_Grp")
                cmds.delete(cmds.parentConstraint(ikHandleMainList[0], ikHandleExtraGrp, maintainOffset=False))
                cmds.parent(ikHandleMainList[0], ikHandleExtraGrp)
                cmds.parent(ikHandleExtraGrp, self.ikHandleToRFGrp)
                if self.limbStyle == self.dpUIinst.lang['m155_quadrupedExtra']:
                    cmds.parent(ikHandleExtraGrp, ikStretchExtremLocZero, self.quadExtraCtrl)
                elif self.limbStyle == self.dpUIinst.lang['m037_quadruped'] or self.limbStyle == self.dpUIinst.lang['m043_quadSpring']:
                    cmds.parent(ikStretchExtremLocZero, self.ikHandleToRFGrp)
                    cmds.parentConstraint(ikHandleExtraGrp, ikStretchExtremLocZero, skipRotate=("x", "y", "z"), maintainOffset=True, name=ikStretchExtremLocZero+"_PaC")
                self.ikHandleConst = cmds.pointConstraint(self.ikExtremSubCtrl, ikHandleExtraGrp, maintainOffset=True, name=ikHandleGrp+"_PoC")[0]
                self.ikHandleConstList.append(self.ikHandleConst)
                
                cmds.orientConstraint(self.ikExtremSubCtrl, self.ikJointList[len(self.ikJointList) - 2], maintainOffset=True, name=self.ikJointList[len(self.ikJointList) - 2]+"_OrC")
                cmds.pointConstraint(self.ikExtremSubCtrl, ikHandleNotStretchList[0], maintainOffset=True, name=ikHandleNotStretchList[0]+"_PoC")[0]
                cmds.pointConstraint(self.ikExtremSubCtrl, ikHandleACList[0], maintainOffset=True, name=ikHandleACList[0]+"_PoC")[0]
                cmds.orientConstraint(self.ikExtremSubCtrl, self.ikNSJointList[len(self.ikNSJointList) - 2], maintainOffset=True, name=self.ikNSJointList[len(self.ikNSJointList) - 2]+"_OrC")

                # orient ik controller
                cmds.addAttr(self.ikExtremCtrl, longName="orient", attributeType="double", defaultValue=1, min=0, max=1, keyable=True)

                # twist:
                cmds.addAttr(self.ikExtremCtrl, longName='twist', attributeType='float', keyable=True)
                if s == 0:
                    cmds.connectAttr(self.ikExtremCtrl+'.twist', ikHandleMainList[0]+".twist", force=True)
                    cmds.connectAttr(self.ikExtremCtrl+'.twist', ikHandleNotStretchList[0]+".twist", force=True)
                    cmds.connectAttr(self.ikExtremCtrl+'.twist', ikHandleACList[0]+".twist", force=True)
                else:
                    twistMultDiv = cmds.createNode('multiplyDivide', name=self.ikExtremCtrl+"_MD")
                    self.toIDList.append(twistMultDiv)
                    cmds.setAttr(twistMultDiv+'.input2X', -1)
                    cmds.connectAttr(self.ikExtremCtrl+'.twist', twistMultDiv+'.input1X', force=True)
                    cmds.connectAttr(twistMultDiv+'.outputX', ikHandleMainList[0]+".twist", force=True)
                    cmds.connectAttr(twistMultDiv+'.outputX', ikHandleNotStretchList[0]+".twist", force=True)
                    cmds.connectAttr(twistMultDiv+'.outputX', ikHandleACList[0]+".twist", force=True)

                # working on corner poleVector:
                # based on Renauld Lessard swivel code: 
                # https://github.com/renaudll/omtk/blob/master/omtk/modules/rigIK.py
                
                # get joint chain positions
                startPos  = cmds.xform(self.ikJointList[1], query=True, worldSpace=True, rotatePivot=True) #shoulder, leg
                cornerPos = cmds.xform(self.ikJointList[2], query=True, worldSpace=True, rotatePivot=True) #elbow, knee
                endPos    = cmds.xform(self.ikJointList[3], query=True, worldSpace=True, rotatePivot=True) #wrist, ankle
                # calculate distances (joint lenghts)
                upperLimbLen = self.utils.distanceBet(self.ikJointList[1], self.ikJointList[2])[0]
                lowerLimbLen = self.utils.distanceBet(self.ikJointList[2], self.ikJointList[3])[0]
                chainLen = upperLimbLen+lowerLimbLen
                # ratio of placement of the middle joint
                pvRatio = upperLimbLen / chainLen
                # calculate the position of the base middle locator
                pvBasePosX = (endPos[0] - startPos[0]) * pvRatio+startPos[0]
                pvBasePosY = (endPos[1] - startPos[1]) * pvRatio+startPos[1]
                pvBasePosZ = (endPos[2] - startPos[2]) * pvRatio+startPos[2]
                # working with vectors
                cornerBasePosX = cornerPos[0] - pvBasePosX
                cornerBasePosY = cornerPos[1] - pvBasePosY
                cornerBasePosZ = cornerPos[2] - pvBasePosZ
                # magnitude of the vector
                magDir = math.sqrt(cornerBasePosX**2+cornerBasePosY**2+cornerBasePosZ**2)
                # normalize the vector
                normalDirX = cornerBasePosX / magDir
                normalDirY = cornerBasePosY / magDir
                normalDirZ = cornerBasePosZ / magDir
                # calculate the poleVector position by multiplying the unitary vector by the chain length
                pvDistX = normalDirX * chainLen
                pvDistY = normalDirY * chainLen
                pvDistZ = normalDirZ * chainLen
                # get the poleVector position
                pvPosX = pvBasePosX+pvDistX
                pvPosY = pvBasePosY+pvDistY
                pvPosZ = pvBasePosZ+pvDistZ
                # place poleVector zero out group in the correct position
                cmds.move(pvPosX, pvPosY, pvPosZ, self.ikCornerCtrlZero, objectSpace=False, worldSpaceDistance=True)

                # create poleVector constraint:
                cmds.poleVectorConstraint(self.ikCornerCtrl, ikHandleMainList[0], weight=1.0, name=ikHandleMainList[0]+"_PVC")
                cmds.poleVectorConstraint(self.ikCornerCtrl, ikHandleNotStretchList[0], weight=1.0, name=ikHandleNotStretchList[0]+"_PVC")
                cmds.poleVectorConstraint(self.ikCornerCtrl, ikHandleACList[0], weight=1.0, name=ikHandleACList[0]+"_PVC")

                # create annotation:
                annotLoc = cmds.spaceLocator(name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_Ant_Loc", position=(0, 0, 0))[0]
                annotation = cmds.annotate(annotLoc, tx="", point=(pvPosX, pvPosY, pvPosZ))
                annotation = cmds.listRelatives(annotation, parent=True)[0]
                annotation = cmds.rename(annotation, side+self.userGuideName+"_"+self.limbType.capitalize()+"_Ant")
                cmds.parent(annotation, self.ikCornerCtrl)
                cmds.parent(annotLoc, self.ikJointList[2], relative=True)
                cmds.setAttr(annotation+'.template', 1)
                cmds.setAttr(annotLoc+'.visibility', 0)
                # set annotation visibility as a display option attribute:
                cmds.addAttr(self.ikCornerCtrl, longName="displayAnnotation", attributeType='short', minValue=0, maxValue=1, keyable=False, defaultValue=1)
                cmds.setAttr(self.ikCornerCtrl+".displayAnnotation", channelBox=True)
                cmds.connectAttr(self.ikCornerCtrl+".displayAnnotation", annotation+".visibility", force=True)

                # prepare groups to rotate and translate automatically:
                self.ctrls.setLockHide([self.ikCornerCtrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
                self.cornerGrp = cmds.group(empty=True, name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_PoleVector_Grp", absolute=True)
                self.cornerOrientGrp = cmds.group(empty=True, name=side+self.userGuideName+"_"+self.limbType.capitalize()+"_PoleVectorOrient_Grp", absolute=True)
                cmds.delete(cmds.parentConstraint(self.ikExtremCtrl, self.cornerGrp, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.ikExtremCtrl, self.cornerOrientGrp, maintainOffset=False))
                cmds.parent(self.ikCornerCtrlZero, self.cornerGrp, absolute=True)
                # set a good orientation for the poleVector ctrl
                cmds.setAttr(self.ikCornerCtrlZero+".rotateX", 0)
                cmds.setAttr(self.ikCornerCtrlZero+".rotateY", 0)
                cmds.setAttr(self.ikCornerCtrlZero+".rotateZ", 0)
                if s == 1:
                    cmds.setAttr(self.ikCornerCtrlZero+".scaleX", -1)
                    cmds.setAttr(self.ikCornerCtrlZero+".scaleY", -1)
                    cmds.setAttr(self.ikCornerCtrlZero+".scaleZ", -1)
                self.zeroCornerGrp = self.utils.zeroOut([self.cornerGrp])[0]
                self.ikPoleVectorCtrlZeroList.append(self.zeroCornerGrp)

                # working with follow behavior of the poleVector:
                poleVectorAimLoc = cmds.spaceLocator(name=side+self.userGuideName+"_"+cornerName+"_Ik_Aim_Loc")[0]
                poleVectorUpLoc = cmds.spaceLocator(name=side+self.userGuideName+"_"+cornerName+"_Ik_Up_Loc")[0]
                poleVectorUpLocGrp = cmds.group(poleVectorUpLoc, name=poleVectorUpLoc+"_Grp")
                poleVectorLocatorsGrp = cmds.group(poleVectorAimLoc, poleVectorUpLocGrp, name=side+self.userGuideName+"_"+cornerName+"_Ik_Loc_Grp")
                cmds.setAttr(poleVectorLocatorsGrp+".visibility", 0)
                cmds.setAttr(poleVectorUpLoc+".translateZ", self.ctrlRadius)
                if pvPosZ < 0:
                    cmds.setAttr(poleVectorUpLoc+".translateZ", -self.ctrlRadius)
                cmds.delete(cmds.pointConstraint(self.cvMainLoc, poleVectorAimLoc, maintainOffset=False))
                cmds.pointConstraint(self.ikExtremSubCtrl, poleVectorUpLocGrp, maintainOffset=False, name=poleVectorUpLocGrp+"_PaC")
                for axis in self.axisList:
                    cmds.connectAttr(self.worldRef+".scaleX", poleVectorLocatorsGrp+".scale"+axis, force=True)
                
                # working with autoOrient of poleVector:
                cmds.addAttr(self.ikCornerCtrl, longName=self.dpUIinst.lang['c033_autoOrient'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.75, keyable=True)
                if self.limbTypeName == self.armName:
                    cmds.setAttr(self.ikCornerCtrl+'.'+self.dpUIinst.lang['c033_autoOrient'], 0)
                    cmds.addAttr(self.ikCornerCtrl+'.'+self.dpUIinst.lang['c033_autoOrient'], edit=True, defaultValue=0)
                upLocOrientConst = cmds.parentConstraint(self.ikExtremCtrl, self.rootCtrlRef, poleVectorUpLocGrp, skipTranslate=["x", "y", "z"], maintainOffset=True, name=poleVectorUpLocGrp+"_OrC")[0]
                cmds.setAttr(upLocOrientConst+".interpType", 2) #shortest
                upLocOrientRev = cmds.createNode('reverse', name=side+self.userGuideName+"_UpLocOrient_Rev")
                cmds.connectAttr(self.ikCornerCtrl+'.'+self.dpUIinst.lang['c033_autoOrient'], upLocOrientRev+".inputX", force=True)
                cmds.connectAttr(self.ikCornerCtrl+'.'+self.dpUIinst.lang['c033_autoOrient'], upLocOrientConst+"."+self.ikExtremCtrl+"W0", force=True)
                cmds.connectAttr(upLocOrientRev+'.outputX', upLocOrientConst+"."+self.rootCtrlRef+"W1", force=True)
                cmds.aimConstraint(self.ikExtremSubCtrl, poleVectorAimLoc, worldUpType="object", worldUpObject=poleVectorUpLoc, aimVector=(0, 0, 1), upVector=(1, 0, 0), maintainOffset=False, name=poleVectorUpLoc+"_AiC")
                cmds.parentConstraint(poleVectorAimLoc, self.cornerGrp, maintainOffset=True, name=self.cornerGrp+"_PaC")

                # make poleVectorCtrl's follow really pin from masterCtrl:
                cmds.addAttr(self.ikCornerCtrl, longName="pin", attributeType='short', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                poleVectorPinPC = cmds.parentConstraint(self.masterCtrlRef, self.ikCornerCtrlZero, maintainOffset=True, name=self.ikCornerCtrlZero+"_PaC")[0]
                cmds.connectAttr(self.ikCornerCtrl+'.pin', poleVectorPinPC+"."+self.masterCtrlRef+"W0", force=True)
                
                # quadExtraCtrl autoOrient setup:
                if self.limbStyle == self.dpUIinst.lang['m155_quadrupedExtra']:
                    cmds.addAttr(self.quadExtraCtrl, longName='autoOrient', attributeType='float', minValue=0, max=1, defaultValue=1, keyable=True)
                    cmds.setAttr(self.quadExtraCtrl+".autoOrient", 0)
                    quadExtraRotNull = cmds.group(name=self.quadExtraCtrl+"_AutoOrient_Null", empty=True)
                    self.utils.addCustomAttr([quadExtraRotNull], self.utils.ignoreTransformIOAttr)
                    cmds.delete(cmds.parentConstraint(self.quadExtraCtrl, quadExtraRotNull, maintainOffset=False))
                    cmds.parent(quadExtraRotNull, self.ikHandleToRFGrp)
                    autoOrientRev = cmds.createNode("reverse", name=self.quadExtraCtrl+"_AutoOrient_Rev")
                    self.toIDList.append(autoOrientRev)
                    autoOrientConst = cmds.parentConstraint(self.ikHandleToRFGrp, quadExtraRotNull, quadExtraCtrlZero, skipTranslate=["x", "y", "z"], maintainOffset=True, name=quadExtraCtrlZero+"_PaC")[0]
                    cmds.setAttr(autoOrientConst+".interpType", 0) #noflip
                    cmds.connectAttr(self.quadExtraCtrl+".autoOrient", autoOrientRev+".inputX", force=True)
                    cmds.connectAttr(autoOrientRev+".outputX", autoOrientConst+"."+self.ikHandleToRFGrp+"W0", force=True)
                    cmds.connectAttr(self.quadExtraCtrl+".autoOrient", autoOrientConst+"."+quadExtraRotNull+"W1", force=True)
                    # avoid cycle error from Maya warning:
                    cmds.cycleCheck(evaluation=False)
                    cmds.aimConstraint(self.shoulderRefGrp, quadExtraRotNull, aimVector=(0, 1, 0), upVector=(0, 0, 1), worldUpType="object", worldUpObject=self.ikCornerCtrl, name=quadExtraCtrlZero+"_AiC")[0]
                    cmds.cycleCheck(evaluation=True)
                    # hack to parent constraint offset recalculation (Update button on Attribute Editor):
                    cmds.parentConstraint(self.ikHandleToRFGrp, quadExtraRotNull, quadExtraCtrlZero, edit=True, maintainOffset=True)
                    cmds.setAttr(self.quadExtraCtrl+".autoOrient", 1)

                # stretch system:
                kNameList = [beforeName, self.limbType.capitalize()]
                distBetGrp = cmds.group(empty=True, name=side+self.userGuideName+"_DistBet_Grp")
                jointChainLengthValue = self.utils.jointChainLength(self.ikJointList[1:4])

                # creating attributes:
                cmds.addAttr(self.ikExtremCtrl, longName="startChainLength", attributeType='float', defaultValue=jointChainLengthValue, keyable=False)
                cmds.addAttr(self.ikExtremCtrl, longName="stretchable", attributeType='float', minValue=0, defaultValue=1, maxValue=1, keyable=True)
                cmds.addAttr(self.ikExtremCtrl, longName=self.dpUIinst.lang['c113_length'], attributeType='float', minValue=0.001, defaultValue=1, keyable=True)
                self.ctrls.setLockHide([self.ikExtremCtrl], ['startChainLength'])

                # creating distance betweens, multiplyDivides and reverse nodes:
                self.distBetweenList = self.utils.distanceBet(self.ikJointList[1], self.ikStretchExtremLoc, name=side+self.userGuideName+"_"+kNameList[1]+"_DistBet", keep=True)
                cmds.setAttr(self.distBetweenList[5]+"."+self.distBetweenList[4]+"W1", 0)
                cmds.parent(self.distBetweenList[2], self.distBetweenList[3], self.distBetweenList[4], distBetGrp)
                cmds.connectAttr(self.ikExtremCtrl+"."+self.dpUIinst.lang['c113_length'], self.worldRef+"."+self.dpUIinst.lang['c113_length'], force=True)
                cmds.parentConstraint(self.skinJointList[0], self.distBetweenList[4], maintainOffset=True, name=self.distBetweenList[4]+"_PaC")

                # (James) if we use the ribbon controls we won't implement the forearm control
                # create the forearm control if limb type is arm and there is not bend (ribbon) implementation:
                if self.limbTypeName == self.armName and self.getHasBend() == False:
                    # create forearm joint:
                    forearmJnt = cmds.duplicate(self.skinJointList[2], name=side+self.userGuideName+ "_" +self.dpUIinst.lang[ 'c030_forearm']+self.jSufixList[0])[0]
                    self.utils.setJointLabel(forearmJnt, s+self.jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang[ 'c030_forearm'])
                    # delete its children:
                    childList = cmds.listRelatives(forearmJnt, children=True, fullPath=True)
                    cmds.delete(childList)
                    cmds.parent(forearmJnt, self.skinJointList[2])
                    # move forearmJnt to correct position:
                    tempDist = self.utils.distanceBet(self.skinJointList[2], self.skinJointList[3])[0]
                    txElbow = cmds.xform(self.skinJointList[2], worldSpace=True, translation=True, query=True)[0]
                    txWrist = cmds.xform(self.skinJointList[3], worldSpace=True, translation=True, query=True)[0]
                    if (txWrist - txElbow) > 0:
                        forearmDistZ = tempDist / 3
                    else:
                        forearmDistZ = -(tempDist / 3)
                    cmds.move(0, 0, forearmDistZ, forearmJnt, localSpace=True, worldSpaceDistance=True)
                    # create forearmCtrl:
                    forearmCtrl = self.ctrls.cvControl("id_037_LimbForearm", side+self.userGuideName+"_"+self.dpUIinst.lang['c030_forearm']+"_Ctrl", r=(self.ctrlRadius * 0.75), d=self.curveDegree, guideSource=self.guideName+"_Corner")
                    forearmGrp = cmds.group(forearmCtrl, name=side+self.userGuideName+"_"+self.dpUIinst.lang['c030_forearm']+"_Grp")
                    forearmZero = cmds.group(forearmGrp, name=side+self.userGuideName+"_"+self.dpUIinst.lang['c030_forearm']+"_Zero_0_Grp")
                    tempToDelete = cmds.parentConstraint(forearmJnt, forearmZero, maintainOffset=False)
                    cmds.delete(tempToDelete)
                    cmds.parentConstraint(self.skinJointList[2], forearmZero, maintainOffset=True, name=forearmZero+"_PaC")
                    cmds.orientConstraint(forearmCtrl, forearmJnt, skip=["x", "y"], maintainOffset=True, name=forearmJnt+"_OrC")
                    # create attribute to forearm autoRotate:
                    cmds.addAttr(forearmCtrl, longName=self.dpUIinst.lang['c033_autoOrient'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.75, keyable=True)
                    self.ctrls.setLockHide([forearmCtrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'sx', 'sy', 'sz', 'v', 'ro'])
                    # make rotate connections:
                    forearmMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_"+self.dpUIinst.lang[ 'c030_forearm']+"_MD")
                    self.toIDList.append(forearmMD)
                    cmds.connectAttr(forearmCtrl+'.'+self.dpUIinst.lang['c033_autoOrient'], forearmMD+'.input1X')
                    cmds.connectAttr(self.skinJointList[3]+'.rotateZ', forearmMD+'.input2X')
                    cmds.connectAttr(forearmMD+'.outputX', forearmGrp+'.rotateZ')
                    ikExtremOrientPaC = cmds.parentConstraint(forearmCtrl, self.ikExtremSubCtrl, self.ikExtremOrientCtrlZero, maintainOffset=True, name=self.ikExtremOrientCtrlZero+"_PaC")[0]
                    ikExtremOrientPacW0 = forearmCtrl+"W0"
                elif self.limbTypeName == self.legName and self.getHasBend() == False:
                    ikExtremOrientPaC = cmds.parentConstraint(self.skinJointList[-3], self.ikExtremSubCtrl, self.ikExtremOrientCtrlZero, maintainOffset=True, name=self.ikExtremOrientCtrlZero+"_PaC")[0]
                    ikExtremOrientPacW0 = self.skinJointList[-3]+"W0"

                # creating a group to receive the reverseFootCtrlGrp (if module integration is on):
                self.ikFkBlendGrpToRevFoot = cmds.group(empty=True, name=side+self.userGuideName+"_IkFkBlendGrpToRevFoot_Grp")
                self.ikFkBlendGrpToRevFootList.append(self.ikFkBlendGrpToRevFoot)
                cmds.delete(cmds.parentConstraint(self.ikExtremCtrl, self.ikFkBlendGrpToRevFoot, maintainOffset=False))

                # offset parent constraint
                parentConstToRFOffset = cmds.parentConstraint(self.ikExtremSubCtrl, self.fkCtrlList[len(self.fkCtrlList) - 1], self.ikNSJointList[-2], self.ikFkBlendGrpToRevFoot, maintainOffset=True, name=self.ikFkBlendGrpToRevFoot+"_PaC")[0]
                cmds.connectAttr(self.worldRef+"."+attrNameLower+'Fk_ikFkBlend', parentConstToRFOffset+"."+self.fkCtrlList[len(self.fkCtrlList) - 1]+"W1", force=True)

                # work with scalable extrem hand or foot:
                cmds.addAttr(self.fkCtrlList[-1], longName=self.dpUIinst.lang['c040_uniformScale'], attributeType="double", minValue=0.001, defaultValue=1)
                cmds.addAttr(self.ikExtremCtrl, longName=self.dpUIinst.lang['c040_uniformScale'], attributeType="double", minValue=0.001, defaultValue=1)
                cmds.setAttr(self.fkCtrlList[-1]+"."+self.dpUIinst.lang['c040_uniformScale'], edit=True, keyable=True)
                cmds.setAttr(self.ikExtremCtrl+"."+self.dpUIinst.lang['c040_uniformScale'], edit=True, keyable=True)
                # add scale multiplier attribute
                cmds.addAttr(self.fkCtrlList[-1], longName=self.dpUIinst.lang['c040_uniformScale']+self.dpUIinst.lang['c105_multiplier'].capitalize(), attributeType='double', minValue=0.001, defaultValue=1)
                cmds.addAttr(self.ikExtremCtrl, longName=self.dpUIinst.lang['c040_uniformScale']+self.dpUIinst.lang['c105_multiplier'].capitalize(), attributeType='double', minValue=0.001, defaultValue=1)
                ikScaleMD = cmds.rename(cmds.createNode('multiplyDivide'), side+self.userGuideName+"_"+self.dpUIinst.lang['c105_multiplier'].capitalize()+'_Ik_MD')
                fkScaleMD = cmds.rename(cmds.createNode('multiplyDivide'), side+self.userGuideName+"_"+self.dpUIinst.lang['c105_multiplier'].capitalize()+'_Fk_MD')
                cmds.connectAttr(self.ikExtremCtrl+"."+self.dpUIinst.lang['c040_uniformScale'], ikScaleMD+".input1X", force=True)
                cmds.connectAttr(self.ikExtremCtrl+"." +self.dpUIinst.lang['c040_uniformScale']+self.dpUIinst.lang['c105_multiplier'].capitalize(), ikScaleMD+".input2X", force=True)
                cmds.connectAttr(self.fkCtrlList[-1]+"."+self.dpUIinst.lang['c040_uniformScale'], fkScaleMD+".input1X", force=True)
                cmds.connectAttr(self.fkCtrlList[-1]+"."+self.dpUIinst.lang['c040_uniformScale']+self.dpUIinst.lang['c105_multiplier'].capitalize(), fkScaleMD+".input2X", force=True)
                # integrate uniformScale and scaleMultiplier attributes
                uniBlend = cmds.createNode("blendColors", name=side+self.userGuideName+"_"+self.dpUIinst.lang['c040_uniformScale'][0].capitalize()+self.dpUIinst.lang['c040_uniformScale'][1:]+"_BC")
                cmds.connectAttr(uniBlend+".outputR", origGrp+".scaleX", force=True)
                cmds.connectAttr(uniBlend+".outputR", origGrp+".scaleY", force=True)
                cmds.connectAttr(uniBlend+".outputR", origGrp+".scaleZ", force=True)
                cmds.connectAttr(uniBlend+".outputR", self.skinJointList[-2]+".scaleX", force=True)
                cmds.connectAttr(uniBlend+".outputR", self.skinJointList[-2]+".scaleY", force=True)
                cmds.connectAttr(uniBlend+".outputR", self.skinJointList[-2]+".scaleZ", force=True)
                cmds.connectAttr(uniBlend+".outputR", self.ikFkBlendGrpToRevFoot+".scaleX", force=True)
                cmds.connectAttr(uniBlend+".outputR", self.ikFkBlendGrpToRevFoot+".scaleY", force=True)
                cmds.connectAttr(uniBlend+".outputR", self.ikFkBlendGrpToRevFoot+".scaleZ", force=True)
                cmds.connectAttr(self.worldRef+"."+attrNameLower+'Fk_ikFkBlend', uniBlend+".blender", force=True)
                cmds.connectAttr(fkScaleMD+'.outputX', uniBlend+'.color1R', force=True)
                cmds.connectAttr(ikScaleMD+'.outputX', uniBlend+'.color2R', force=True)
                
                if self.limbStyle != self.dpUIinst.lang['m042_default']:
                    if self.limbStyle == self.dpUIinst.lang['m043_quadSpring']:
                        # fix the group for the ikSpringSolver to avoid Maya bug about rotation from masterCtrl :P
                        cmds.parent(self.ikJointList[1], world=True)
                        self.fixIkSpringSolverGrp = cmds.group(self.ikJointList[1], name=side+self.userGuideName+"_IkFixSpringSolver_Grp")
                        self.fixIkSpringSolverGrpList.append(self.fixIkSpringSolverGrp)
                        cmds.setAttr(self.fixIkSpringSolverGrp+".visibility", 0)
                        cmds.parentConstraint(self.ikJointList[0], self.ikJointList[1], maintainOffset=True, name=self.ikJointList[1]+"_PaC")
                    if self.limbStyle == self.dpUIinst.lang['m037_quadruped'] or self.limbStyle == self.dpUIinst.lang['m043_quadSpring']:
                        # tell main script to create parent constraint from chestA to ikCtrl for front legs
                        self.quadFrontLegList.append(self.ikExtremCtrlOrientGrp)

                # work with not stretch ik setup:
                ikStretchableMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_IkStretchable_MD")
                cmds.connectAttr(self.ikExtremCtrl+".stretchable", ikStretchableMD+".input1X", force=True)
                cmds.connectAttr(self.worldRef+"."+attrNameLower+"Fk_ikFkBlendRevOutputX", ikStretchableMD+".input2X", force=True)

                ikStretchCtrlCnd = cmds.createNode('condition', name=side+self.userGuideName+"_IkStretchCtrl_Cnd")
                cmds.setAttr(ikStretchCtrlCnd+".secondTerm", 1)
                cmds.setAttr(ikStretchCtrlCnd+".operation", 3)
                cmds.connectAttr(ikStretchableMD+".outputX", ikStretchCtrlCnd+".colorIfFalseR", force=True)
                cmds.connectAttr(self.worldRef+"."+attrNameLower+"Fk_ikFkBlendRevOutputX", ikStretchCtrlCnd+".colorIfTrueR", force=True)
                cmds.connectAttr(self.ikExtremCtrl+".stretchable", ikStretchCtrlCnd+".firstTerm", force=True)
                cmds.connectAttr(ikStretchCtrlCnd+".outColorR", parentConstToRFOffset+"."+self.ikExtremSubCtrl+"W0", force=True)

                ikStretchDifPMA = cmds.createNode('plusMinusAverage', name=side+self.userGuideName+"_Stretch_Dif_PMA")
                cmds.setAttr(ikStretchDifPMA+".operation", 2)
                cmds.connectAttr(self.worldRef+"."+attrNameLower+"Fk_ikFkBlendRevOutputX", ikStretchDifPMA+".input1D[0]", force=True)
                cmds.connectAttr(self.ikExtremCtrl+".stretchable", ikStretchDifPMA+".input1D[1]", force=True)

                ikStretchCnd = cmds.createNode('condition', name=side+self.userGuideName+"_IkStretch_Cnd")
                cmds.setAttr(ikStretchCnd+".operation", 3)
                cmds.setAttr(ikStretchCnd+".secondTerm", 1)
                cmds.connectAttr(ikStretchDifPMA+".output1D", ikStretchCnd+".colorIfFalseR", force=True)
                cmds.connectAttr(self.ikExtremCtrl+".stretchable", ikStretchCnd+".firstTerm", force=True)

                ikStretchClp = cmds.createNode('clamp', name=side+self.userGuideName+"_IkStretch_Clp")
                cmds.setAttr(ikStretchClp+".maxR", 1)
                cmds.connectAttr(ikStretchCnd+".outColorR", ikStretchClp+".inputR", force=True)
                cmds.connectAttr(ikStretchClp+".outputR", parentConstToRFOffset+"."+self.ikNSJointList[-2]+"W2", force=True)

                # prepare to disable stretch in fk mode
                cmds.addAttr(self.ikExtremCtrl, longName="disableIkFkRevOutputX", attributeType="double", keyable=False)
                cmds.connectAttr(self.worldRef+"."+attrNameLower+"Fk_ikFkBlendRevOutputX", self.ikExtremCtrl+".disableIkFkRevOutputX", force=True)

                # create a masterModuleGrp to be checked if this rig exists:
                ctrlHookList = [self.zeroFkCtrlGrp, self.zeroCornerGrp, self.ikExtremCtrlZero, self.ikExtremOrientCtrlZero, self.cornerOrientGrp, distBetGrp, self.origFromList[0], self.origFromList[1], self.ikFkBlendGrpToRevFoot, self.worldRef, self.masterCtrlRef, self.rootCtrlRef]
                if self.limbTypeName == self.armName:
                    # (James) not implementing the forearm control if we use ribbons (yet)
                    if not self.getHasBend():
                        # use forearm control
                        ctrlHookList.append(forearmZero)
                self.hookSetup(side, ctrlHookList, [self.skinJointList[0], self.ikJointList[0], self.fkJointList[0], self.ikNSJointList[0], self.ikACJointList[1]], [ikHandleGrp, ikHandleNotStretchGrp, ikHandleACGrp, poleVectorLocatorsGrp])
                
                # Ribbon feature by James do Carmo, thanks!
                loadedRibbon = False
                # (James) add bend to limb
                if self.getHasBend():
                    try:
                        from ..Library import jcRibbon
                        if self.dpUIinst.dev:
                            reload(jcRibbon)
                        RibbonClass = jcRibbon.RibbonClass(self.dpUIinst, self)
                        loadedRibbon = True
                    except Exception as e:
                        print(e)
                        print(self.dpUIinst.lang['e012_cantLoadRibbon'])
                    
                    if loadedRibbon:
                        num = self.getBendJoints()
                        iniJoint = side+self.userGuideName+"_"+mainName+'_Jnt'
                        corner = side+self.userGuideName+"_"+cornerName+'_Jnt'
                        cornerJxt = side+self.userGuideName+"_"+cornerName+'_Jxt'
                        splited = self.userGuideName.split('_')
                        prefix = ''.join(side)
                        name = ''
                        if len(splited) > 1:
                            prefix += splited[0]
                            name += splited[1]
                        else:
                            name += self.userGuideName
                        loc = cmds.spaceLocator(n=side+self.userGuideName+'_auxOriLoc', p=(0, 0, 0))[0]

                        cmds.delete(cmds.parentConstraint(iniJoint, loc, mo=False, w=1))

                        if name == self.dpUIinst.lang['c006_leg_main']:  # leg
                            if s == 0:  # left side (or first side = original)
                                cmds.delete(cmds.aimConstraint(corner, loc, mo=False, weight=2, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(1, 0, 0)))
                            else:
                                cmds.delete(cmds.aimConstraint(corner, loc, mo=False, weight=2, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(-1, 0, 0)))
                        else:
                            cmds.delete(cmds.aimConstraint(corner, loc, mo=False, weight=2, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(0, 1, 0)))

                        if self.limbTypeName == self.armName:
                            self.bendGrps = RibbonClass.addRibbonToLimb(prefix, name, loc, iniJoint, 'x', num, cornerJxt, side=s, arm=True, worldRef=self.worldRef, jointLabelAdd=self.jointLabelAdd, addArtic=self.addArticJoint, additional=self.hasAdditional, addCorrect=self.addCorrective, jcrNumber=3, jcrPosList=[(0, 0, -0.25*self.ctrlRadius), (0.2*self.ctrlRadius, 0, 0.4*self.ctrlRadius), (-0.2*self.ctrlRadius, 0, 0.4*self.ctrlRadius)])
                        else:
                            self.bendGrps = RibbonClass.addRibbonToLimb(prefix, name, loc, iniJoint, 'x', num, side=s, arm=False, worldRef=self.worldRef, jointLabelAdd=self.jointLabelAdd, addArtic=self.addArticJoint, additional=self.hasAdditional, addCorrect=self.addCorrective, jcrNumber=3, jcrPosList=[(0, 0, -0.25*self.ctrlRadius), (0.2*self.ctrlRadius, 0, 0.4*self.ctrlRadius), (-0.2*self.ctrlRadius, 0, 0.4*self.ctrlRadius)])
                        cmds.delete(loc)
                        
                        ikExtremOrientPaC = cmds.parentConstraint(self.bendGrps["extraCtrlList"][-1], self.ikExtremSubCtrl, self.ikExtremOrientCtrlZero, maintainOffset=True, name=self.ikExtremOrientCtrlZero+"_PaC")[0]
                        ikExtremOrientPacW0 = self.bendGrps["extraCtrlList"][-1]+"W0"

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
                        for jntIndex in range(1, len(self.skinJointList) - 2):
                            if not "B_" in self.skinJointList[jntIndex]: #avoid quadruped kneeB renaming
                                self.skinJointList[jntIndex] = self.skinJointList[jntIndex].replace("_Jnt", "_Jxt")
                        
                        # implementing auto rotate twist bones:
                        # check if we have loaded the quatNode.mll Maya plugin in order to create quatToEuler node, also decomposeMatrix from matrixNodes:
                        loadedQuatNode = self.utils.checkLoadedPlugin("quatNodes", self.dpUIinst.lang['e014_cantLoadQuatNode'])
                        loadedMatrixPlugin = self.utils.checkLoadedPlugin("matrixNodes", self.dpUIinst.lang['e002_matrixPluginNotFound'])
                        if loadedQuatNode and loadedMatrixPlugin:
                            twistBoneMD = self.bendGrps['twistBoneMD']
                            shoulderChildLoc = cmds.spaceLocator(name=twistBoneMD+"_Child_Loc")[0]
                            shoulderParentLoc = cmds.spaceLocator(name=twistBoneMD+"_Parent_Loc")[0]
                            cmds.setAttr(shoulderChildLoc+".visibility", 0)
                            cmds.setAttr(shoulderParentLoc+".visibility", 0)
                            cmds.delete(cmds.parentConstraint(self.skinJointList[1], shoulderParentLoc, mo=False))
                            cmds.parent(shoulderParentLoc, self.skinJointList[0])
                            cmds.parent(shoulderChildLoc, self.skinJointList[1], relative=True)
                            self.utils.twistBoneMatrix(shoulderParentLoc, shoulderChildLoc, self.skinJointList[1], twistBoneMD)
                        
                        # fix autoRotate flipping issue:
                        upCtrl = self.bendGrps['ctrlList'][0]
                        downCtrl = self.bendGrps['ctrlList'][1]
                        if s == 0: #left
                            cmds.setAttr(upCtrl+".invert", 1)
                            cmds.setAttr(downCtrl+".invert", 1)

                cmds.setAttr(ikExtremOrientPaC+".interpType", 2) #shortest
                orientRevNode = cmds.createNode("reverse", name=side+self.userGuideName+"_"+extremName+"_Ik_Orient_Rev")
                self.toIDList.append(orientRevNode)
                cmds.connectAttr(self.ikExtremCtrl+".orient", orientRevNode+".inputX")
                cmds.connectAttr(self.ikExtremCtrl+".orient", ikExtremOrientPaC+"."+self.ikExtremSubCtrl+"W1")
                cmds.connectAttr(orientRevNode+".outputX", ikExtremOrientPaC+"."+ikExtremOrientPacW0)

                # auto clavicle:
                # loading Maya matrix node
                loadedQuatNode = self.utils.checkLoadedPlugin("quatNodes", self.dpUIinst.lang['e014_cantLoadQuatNode'])
                loadedMatrixPlugin = self.utils.checkLoadedPlugin("matrixNodes", self.dpUIinst.lang['e002_matrixPluginNotFound'])
                if loadedQuatNode and loadedMatrixPlugin:
                    # create auto clavicle group:
                    self.clavicleCtrlGrp = cmds.group(name=self.fkCtrlList[0]+"_Grp", empty=True)
                    cmds.delete(cmds.parentConstraint(self.zeroFkCtrlList[0], self.clavicleCtrlGrp, maintainOffset=False))
                    cmds.parent(self.clavicleCtrlGrp, self.zeroFkCtrlList[0])
                    # invert scale for right side before:
                    if s == 1:
                        cmds.setAttr(self.clavicleCtrlGrp+".scaleX", -1)
                        cmds.setAttr(self.clavicleCtrlGrp+".scaleY", -1)
                        cmds.setAttr(self.clavicleCtrlGrp+".scaleZ", -1)
                    cmds.parent(self.fkCtrlList[0], self.clavicleCtrlGrp, relative=True)
                    
                    # create auto clavicle attribute:
                    cmds.addAttr(self.fkCtrlList[0], longName=self.dpUIinst.lang['c032_follow'], attributeType="float", minValue=0, maxValue=1, defaultValue=0, keyable=True)
                    self.addFollowAttrName(self.fkCtrlList[0], self.dpUIinst.lang['c032_follow'])
                    
                    # ik auto clavicle locators:
                    acIkUpLoc = cmds.spaceLocator(name=side+self.userGuideName+"_AC_Up_Loc")[0]
                    acIkAimLoc = cmds.spaceLocator(name=side+self.userGuideName+"_AC_Aim_Loc")[0]
                    acOrigLoc = cmds.spaceLocator(name=side+self.userGuideName+"_AC_Orig_Loc")[0]
                    acFkLoc = cmds.spaceLocator(name=side+self.userGuideName+"_AC_Fk_Loc")[0]
                    acIkMainLoc = cmds.spaceLocator(name=side+self.userGuideName+"_AC_Ik_"+mainName+"_Loc")[0]
                    acIkCornerLoc = cmds.spaceLocator(name=side+self.userGuideName+"_AC_Ik_"+cornerName+"_Loc")[0]
                    acRefMainLoc = cmds.spaceLocator(name=side+self.userGuideName+"_AC_Ref_"+mainName+"_Loc")[0]
                    cmds.parent(acIkCornerLoc, acIkMainLoc)
                    acLocGrp = cmds.group(acIkUpLoc, acIkAimLoc, acOrigLoc, acFkLoc, acIkMainLoc, name=side+self.userGuideName+"_AC_Loc_Grp")
                    cmds.setAttr(acLocGrp+".inheritsTransform", 0) #important to calculate world space matrix to extract rotations correctlly
                    cmds.setAttr(acLocGrp+".visibility", 0)
                    cmds.setAttr(acRefMainLoc+".visibility", 0)
                    if self.limbTypeName == self.armName:
                        cmds.setAttr(acIkUpLoc+".translateY", 1)
                    else:
                        cmds.setAttr(acIkUpLoc+".translateZ", 1)
                    cmds.delete(cmds.pointConstraint(self.fkCtrlList[1], acLocGrp, maintainOffset=False))
                    cmds.parent([acRefMainLoc, acLocGrp], self.toScalableHookGrp)
                    cmds.delete(cmds.pointConstraint(self.ikACJointList[1], acRefMainLoc, maintainOffset=False))
                    cmds.parentConstraint(self.ikACJointList[1], acRefMainLoc, skipTranslate=["x", "y", "z"], maintainOffset=False, name=acRefMainLoc+"_PaC")
                    self.ctrls.directConnect(acRefMainLoc, acIkMainLoc, ['rx', 'ry', 'rz']) #shoulder rotate
                    cmds.delete(cmds.parentConstraint(self.fkCtrlList[2], acIkCornerLoc, maintainOffset=False))
                    cmds.parentConstraint(acIkMainLoc, acIkUpLoc, maintainOffset=True, name=acIkUpLoc+"_PaC")
                    
                    # aim constraint: (edited in order to point to limb corner (elbow/knee) outside of clavicle hierarchy to avoid cycle error).
                    if self.limbTypeName == self.armName:
                        if s == 0: #left
                            cmds.aimConstraint(acIkCornerLoc, acIkAimLoc, maintainOffset=True, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="object", worldUpObject=acIkUpLoc, name=acIkAimLoc+"_AiC")
                        else: #right
                            cmds.aimConstraint(acIkCornerLoc, acIkAimLoc, maintainOffset=True, weight=1, aimVector=(-1, 0, 0), upVector=(0, 1, 0), worldUpType="object", worldUpObject=acIkUpLoc, name=acIkAimLoc+"_AiC")
                    else: #leg
                        cmds.aimConstraint(acIkCornerLoc, acIkAimLoc, maintainOffset=True, weight=1, aimVector=(0, -1, 0), upVector=(0, 0, 1), worldUpType="object", worldUpObject=acIkUpLoc, name=acIkAimLoc+"_AiC")
                    
                    # fk auto clavicle setup:
                    self.ctrls.directConnect(self.fkCtrlList[1], acFkLoc, ['rx', 'ry', 'rz'])
                    # auto clavicle matrix rotate extraction:
                    acIkMM = cmds.createNode("multMatrix", name=side+self.userGuideName+"_AC_Ik_MM")
                    acIkDM = cmds.createNode("decomposeMatrix", name=side+self.userGuideName+"_AC_Ik_DM")
                    acIkQtE = cmds.createNode("quatToEuler", name=side+self.userGuideName+"_AC_Ik_QtE")
                    acFkMM = cmds.createNode("multMatrix", name=side+self.userGuideName+"_AC_Fk_MM")
                    acFkDM = cmds.createNode("decomposeMatrix", name=side+self.userGuideName+"_AC_Fk_DM")
                    acFkQtE = cmds.createNode("quatToEuler", name=side+self.userGuideName+"_AC_Fk_QtE")
                    acBC = cmds.createNode("blendColors", name=side+self.userGuideName+"_AC_BC")
                    acInvBC = cmds.createNode("blendColors", name=side+self.userGuideName+"_AC_Inv_BC")
                    acInvMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_AC_Inv_MD")
                    acMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_AC_MD")
                    self.toIDList.extend([acIkMM, acIkDM, acIkQtE, acFkMM, acFkDM, acFkQtE, acBC, acInvBC, acInvMD, acMD])
                    cmds.setAttr(acFkQtE+".inputRotateOrder", 1) #yzx
                    # add attributes to control inverse value setup to blend ikFk:
                    ikFkRotAttrList = ["ikRotateX", "ikRotateY", "ikRotateZ", "fkRotateX", "fkRotateY", "fkRotateZ"]
                    for ikFkRotAttr in ikFkRotAttrList:
                        cmds.addAttr(self.fkCtrlList[0], longName=ikFkRotAttr, attributeType="float", minValue=-1, defaultValue=1, maxValue=1)
                    # set values of ik and fk rotates:
                    if s == 0: #left side
                        if self.limbTypeName == self.legName:
                            cmds.setAttr(self.fkCtrlList[0]+".ikRotateY", -1)
                            cmds.setAttr(self.fkCtrlList[0]+".fkRotateX", -1)
                    else: #right side
                        if self.limbTypeName == self.armName:
                            cmds.setAttr(self.fkCtrlList[0]+".ikRotateY", -1)
                        else: #leg
                            cmds.setAttr(self.fkCtrlList[0]+".fkRotateX", -1)
                        cmds.setAttr(self.fkCtrlList[0]+".ikRotateZ", -1)

                    # connections inverse values from fkCtrlList[0] (Clavile or Hips) to inverseBlendColor:
                    cmds.connectAttr(self.fkCtrlList[0]+".ikRotateX", acInvBC+".color2R", force=True)
                    cmds.connectAttr(self.fkCtrlList[0]+".ikRotateY", acInvBC+".color2G", force=True)
                    cmds.connectAttr(self.fkCtrlList[0]+".ikRotateZ", acInvBC+".color2B", force=True)
                    cmds.connectAttr(self.fkCtrlList[0]+".fkRotateX", acInvBC+".color1R", force=True)
                    cmds.connectAttr(self.fkCtrlList[0]+".fkRotateY", acInvBC+".color1G", force=True)
                    cmds.connectAttr(self.fkCtrlList[0]+".fkRotateZ", acInvBC+".color1B", force=True)

                    # connections auto clavicle Ik:
                    cmds.connectAttr(acOrigLoc+".worldInverseMatrix[0]", acIkMM+".matrixIn[0]", force=True)
                    cmds.connectAttr(acIkAimLoc+".worldMatrix[0]", acIkMM+".matrixIn[1]", force=True)
                    cmds.connectAttr(acIkMM+".matrixSum", acIkDM+".inputMatrix", force=True)
                    cmds.connectAttr(acIkDM+".outputQuatX", acIkQtE+".inputQuatX", force=True)
                    cmds.connectAttr(acIkDM+".outputQuatY", acIkQtE+".inputQuatY", force=True)
                    cmds.connectAttr(acIkDM+".outputQuatZ", acIkQtE+".inputQuatZ", force=True)
                    cmds.connectAttr(acIkDM+".outputQuatW", acIkQtE+".inputQuatW", force=True)
                    # connections auto clavicle Fk:
                    cmds.connectAttr(acOrigLoc+".worldInverseMatrix[0]", acFkMM+".matrixIn[0]", force=True)
                    cmds.connectAttr(acFkLoc+".worldMatrix[0]", acFkMM+".matrixIn[1]", force=True)
                    cmds.connectAttr(acFkMM+".matrixSum", acFkDM+".inputMatrix", force=True)
                    cmds.connectAttr(acFkDM+".outputQuatX", acFkQtE+".inputQuatX", force=True)
                    cmds.connectAttr(acFkDM+".outputQuatY", acFkQtE+".inputQuatY", force=True)
                    cmds.connectAttr(acFkDM+".outputQuatZ", acFkQtE+".inputQuatZ", force=True)
                    cmds.connectAttr(acFkDM+".outputQuatW", acFkQtE+".inputQuatW", force=True)
                    # fk to auto clavicle blend colors:
                    if self.limbTypeName == self.armName:
                        cmds.connectAttr(acFkQtE+".outputRotate.outputRotateX", acBC+".color1G", force=True)
                        cmds.connectAttr(acFkQtE+".outputRotate.outputRotateY", acBC+".color1B", force=True)
                        cmds.connectAttr(acFkQtE+".outputRotate.outputRotateZ", acBC+".color1R", force=True)
                    else: #leg
                        cmds.connectAttr(acFkQtE+".outputRotate.outputRotateX", acBC+".color1B", force=True)
                        cmds.connectAttr(acFkQtE+".outputRotate.outputRotateY", acBC+".color1R", force=True)
                        cmds.connectAttr(acFkQtE+".outputRotate.outputRotateZ", acBC+".color1G", force=True)
                    # ik to auto clavicle blend colors:
                    cmds.connectAttr(acIkQtE+".outputRotate.outputRotateX", acBC+".color2R", force=True)
                    cmds.connectAttr(acIkQtE+".outputRotate.outputRotateY", acBC+".color2G", force=True)
                    cmds.connectAttr(acIkQtE+".outputRotate.outputRotateZ", acBC+".color2B", force=True)
                    cmds.connectAttr(self.worldRef+"."+attrNameLower+"Fk_ikFkBlend", acBC+".blender", force=True)
                    cmds.connectAttr(self.worldRef+"."+attrNameLower+"Fk_ikFkBlend", acInvBC+".blender", force=True)
                    cmds.connectAttr(acBC+".output.outputR", acInvMD+".input1X", force=True)
                    cmds.connectAttr(acBC+".output.outputG", acInvMD+".input1Y", force=True)
                    cmds.connectAttr(acBC+".output.outputB", acInvMD+".input1Z", force=True)
                    cmds.connectAttr(acInvBC+".output.outputR", acInvMD+".input2X", force=True)
                    cmds.connectAttr(acInvBC+".output.outputG", acInvMD+".input2Y", force=True)
                    cmds.connectAttr(acInvBC+".output.outputB", acInvMD+".input2Z", force=True)
                    cmds.connectAttr(acInvMD+".outputX", acMD+".input1X", force=True)
                    cmds.connectAttr(acInvMD+".outputY", acMD+".input1Y", force=True)
                    cmds.connectAttr(acInvMD+".outputZ", acMD+".input1Z", force=True)
                    cmds.connectAttr(self.fkCtrlList[0]+"."+self.dpUIinst.lang['c032_follow'], acMD+".input2X", force=True)
                    cmds.connectAttr(self.fkCtrlList[0]+"."+self.dpUIinst.lang['c032_follow'], acMD+".input2Y", force=True)
                    cmds.connectAttr(self.fkCtrlList[0]+"."+self.dpUIinst.lang['c032_follow'], acMD+".input2Z", force=True)
                    if self.limbTypeName == self.armName:
                        cmds.connectAttr(acMD+".outputX", self.clavicleCtrlGrp+".rotateZ", force=True)
                        cmds.connectAttr(acMD+".outputY", self.clavicleCtrlGrp+".rotateX", force=True)
                        cmds.connectAttr(acMD+".outputZ", self.clavicleCtrlGrp+".rotateY", force=True)
                    else: #leg
                        cmds.connectAttr(acMD+".outputX", self.clavicleCtrlGrp+".rotateX", force=True)
                        cmds.connectAttr(acMD+".outputY", self.clavicleCtrlGrp+".rotateZ", force=True)
                        cmds.connectAttr(acMD+".outputZ", self.clavicleCtrlGrp+".rotateY", force=True)
                
                # arrange correct before and extrem skinning joints naming in order to be easy to skinning paint weight UI:
                # default value for 5 bend joints:
                beforeNumber = "00" #clavicle/hips
                firstNumber =  "01" #shoulder/leg
                cornerNumber = "07" #elbow/knee
                extremNumber = "13" #wrist/ankle
                if self.getHasBend():                    
                    if not self.addArticJoint:
                        extremNumber = "10"
                    numBendJnt = self.getBendJoints()
                    if numBendJnt == 3:
                        cornerNumber = "05"
                        extremNumber = "09"
                        if not self.addArticJoint:
                            extremNumber = "06"
                    elif numBendJnt == 7:
                        cornerNumber = "09"
                        extremNumber = "17"
                        if not self.addArticJoint:
                            extremNumber = "14"
                    self.skinJointList[0] = cmds.rename(self.skinJointList[0], side+self.userGuideName+"_"+beforeNumber+"_"+beforeName+self.jSufixList[0])
                    self.skinJointList[-2] = cmds.rename(self.skinJointList[-2], side+self.userGuideName+"_"+extremNumber+"_"+extremName+self.jSufixList[0])
                    if self.addArticJoint:
                        self.cornerJntList = []
                        if self.bendGrps:
                            self.bendJointList = cmds.listRelatives(self.bendGrps['jntGrp'])
                            self.utils.setJointLabel(cmds.listRelatives(self.bendJointList[numBendJnt])[0], s+self.jointLabelAdd, 18, self.userGuideName+"_"+cornerNumber+"_"+cornerName)
                            jar = cmds.rename(cmds.listRelatives(self.bendJointList[numBendJnt])[0], side+self.userGuideName+"_"+cornerNumber+"_"+cornerName+"_Jar")
                            self.cornerJntList.append(jar)
                            if self.limbStyle == self.dpUIinst.lang['m037_quadruped'] or self.limbStyle == self.dpUIinst.lang['m043_quadSpring'] or self.limbStyle == self.dpUIinst.lang['m155_quadrupedExtra']:
                                if self.dpUIinst.lang['c056_front'] in self.userGuideName:
                                    if s == 0:
                                        cmds.setAttr(self.cornerJntList[0]+".rotateX", 0)
                                    else:
                                        cmds.setAttr(self.cornerJntList[0]+".rotateX", 180)
                            if self.addCorrective:
                                jcrList = cmds.listRelatives(self.cornerJntList[0], children=True, allDescendents=True)
                                if jcrList:
                                    for j, jcr in enumerate(jcrList):
                                        self.utils.setJointLabel(jcr, s+self.jointLabelAdd, 18, self.userGuideName+"_"+cornerNumber+"_"+cornerName+"_"+str(j))
                                        renamedJcr = cmds.rename(jcr, side+self.userGuideName+"_"+cornerNumber+"_"+cornerName+"_"+str(j)+"_Jcr")
                                        self.cornerJntList.append(renamedJcr)
                            if toCornerBendList:
                                self.utils.originedFrom(objName=self.bendGrps['ctrlList'][2], attrString=";".join(toCornerBendList))
                                cmds.delete(side+self.userGuideName+"_"+cornerName+"_OrigFrom_Grp_PaC")
                                cmds.parentConstraint(self.ikExtremOrientCtrl, side+self.userGuideName+"_"+cornerName+"_OrigFrom_Grp", maintainOffset=True, name=side+self.userGuideName+"_"+cornerName+"_OrigFrom_Grp_PaC")
                else:
                    if self.addCorrective:
                        self.cornerJntList = self.utils.articulationJoint(self.skinJointList[1], self.skinJointList[2], 3, [(0, 0, -0.25*self.ctrlRadius), (0.2*self.ctrlRadius, 0, 0.4*self.ctrlRadius), (-0.2*self.ctrlRadius, 0, 0.4*self.ctrlRadius)])
                    else:
                        self.cornerJntList = self.utils.articulationJoint(self.skinJointList[1], self.skinJointList[2])
                    # fixing jar rotations
                    if s == 0:
                        if self.limbType == self.armName:
                            cmds.setAttr(self.cornerJntList[0]+".rotateY", -90)
                            cmds.setAttr(self.cornerJntList[0]+".rotateZ", -90)
                        else:
                            cmds.setAttr(self.cornerJntList[0]+".rotateY", 90)
                            if self.limbStyle == self.dpUIinst.lang['m037_quadruped'] or self.limbStyle == self.dpUIinst.lang['m043_quadSpring'] or self.limbStyle == self.dpUIinst.lang['m155_quadrupedExtra']:
                                if self.dpUIinst.lang['c056_front'] in self.userGuideName:
                                    cmds.setAttr(self.cornerJntList[0]+".rotateX", 180)
                                else:
                                    cmds.setAttr(self.cornerJntList[0]+".rotateX", 0)
                                cmds.setAttr(self.cornerJntList[0]+".rotateZ", 180)
                            else:
                                cmds.setAttr(self.cornerJntList[0]+".rotateX", -90)
                                cmds.setAttr(self.cornerJntList[0]+".rotateZ", 90)
                    else:
                        if self.limbType == self.armName:
                            cmds.setAttr(self.cornerJntList[0]+".rotateX", 180)
                            cmds.setAttr(self.cornerJntList[0]+".rotateY", 90)
                            cmds.setAttr(self.cornerJntList[0]+".rotateZ", 90)
                        else:
                            cmds.setAttr(self.cornerJntList[0]+".rotateY", -90)
                            if self.limbStyle == self.dpUIinst.lang['m037_quadruped'] or self.limbStyle == self.dpUIinst.lang['m043_quadSpring'] or self.limbStyle == self.dpUIinst.lang['m155_quadrupedExtra']:
                                cmds.setAttr(self.cornerJntList[0]+".rotateZ", 180)
                                if self.dpUIinst.lang['c056_front'] in self.userGuideName:
                                    cmds.setAttr(self.cornerJntList[0]+".rotateX", 180)
                            else:
                                cmds.setAttr(self.cornerJntList[0]+".rotateX", 90)
                                cmds.setAttr(self.cornerJntList[0]+".rotateZ", 90)

                # corrective variables:
                isLeg = False
                mainJarYValue = 0.3
                mainAxisOrder = 0
                if self.limbType == self.legName:
                    isLeg = True
                    mainJarYValue = -0.3
                    mainAxisOrder = 3
                # Roll, Yaw, Pitch
                # Hour/AntiHour, Left/Right, Up/Down

                # corner corrective network:
                self.correctiveCtrl = self.toParentExtremCtrl
                if self.getHasBend():
                    self.correctiveCtrl = self.bendGrps['ctrlList'][2]
                self.cornerCorrectiveNet = self.setupCorrectiveNet(self.correctiveCtrl, self.skinJointList[1], self.skinJointList[2], side+self.userGuideName+"_"+self.jNameList[2]+"_YawRight", 0, 0, -110, isLeg, [side+self.userGuideName+"_"+self.jNameList[2]+"_YawLeft", 1, 1, -110])
                correctionNetInputValue = cmds.getAttr(self.cornerCorrectiveNet+".inputValue")
                if correctionNetInputValue > 0:
                    cmds.setAttr(self.cornerCorrectiveNet+".inputEnd", correctionNetInputValue+110)

                # add hook attributes to be read when rigging integrated modules:
                cmds.parentConstraint(self.toCtrlHookGrp, self.toScalableHookGrp, maintainOffset=True, name=self.toScalableHookGrp+"_PaC")
                cmds.parentConstraint(self.toCtrlHookGrp, poleVectorAimLoc, skipRotate=["x", "y", "z"], maintainOffset=True, name=poleVectorAimLoc+"_PaC")
                self.aScalableGrps.append(self.toScalableHookGrp)

                # add main articulationJoint:
                if self.addArticJoint:
                    if self.addCorrective:
                        # corrective controls group
                        self.correctiveCtrlsGrp = cmds.group(name=side+self.userGuideName+"_Corrective_Grp", empty=True)
                        self.correctiveCtrlGrpList.append(self.correctiveCtrlsGrp)
                        cmds.parent(self.correctiveCtrlsGrp, self.toCtrlHookGrp)
                        
                        # clavicle / hips
                        beforeCorrectiveNetList = [None]
                        beforeCorrectiveNetList.append(self.setupCorrectiveNet(self.fkCtrlList[0], self.toScalableHookGrp, self.skinJointList[0], side+self.userGuideName+"_"+self.jNameList[0]+"_PitchUp", 1, 1, 60, isLeg, [side+self.userGuideName+"_"+self.jNameList[0]+"_PitchUp", 1, 1, 60]))
                        beforeCalibratePresetList, invertList = self.getCalibratePresetList(s, isLeg, True, False, False, False, False)
                        beforeJxt = cmds.duplicate(self.skinJointList[0], name=side+self.userGuideName+"_"+self.jNameList[0]+"_Jxt")[0]
                        cmds.delete(cmds.listRelatives(beforeJxt, children=True, allDescendents=True, fullPath=True))
                        beforeJntList = self.utils.articulationJoint(beforeJxt, self.skinJointList[0], 1, [(0.3*self.ctrlRadius, 0, 0.3*self.ctrlRadius)])
                        self.setupJcrControls(beforeJntList, s, self.jointLabelAdd, self.userGuideName+"_"+beforeNumber+"_"+beforeName, beforeCorrectiveNetList, beforeCalibratePresetList, invertList)

                        # shoulder / leg
                        mainCorrectiveNetList = [None]
                        mainCorrectiveNetList.append(self.setupCorrectiveNet(self.fkCtrlList[0], self.shoulderRefGrp, self.skinJointList[1], side+self.userGuideName+"_"+self.jNameList[1]+"_PitchUp", 0, mainAxisOrder, -91, isLeg, [side+self.userGuideName+"_"+self.jNameList[1]+"_PitchDown", 0, mainAxisOrder, 91]))
                        mainCorrectiveNetList.append(self.setupCorrectiveNet(self.fkCtrlList[0], self.shoulderRefGrp, self.skinJointList[1], side+self.userGuideName+"_"+self.jNameList[1]+"_YawRight", 1, 1, 46, isLeg, [side+self.userGuideName+"_"+self.jNameList[1]+"_YawLeft", 1, 4, 91]))
                        mainCalibratePresetList, invertList = self.getCalibratePresetList(s, isLeg, False, True, False, False, False)
                        mainJntList = self.utils.articulationJoint(self.shoulderRefGrp, self.skinJointList[1], 2, [(0, mainJarYValue*self.ctrlRadius, 0), (0.3*self.ctrlRadius, 0, 0)])
                        self.setupJcrControls(mainJntList, s, self.jointLabelAdd, self.userGuideName+"_"+firstNumber+"_"+mainName, mainCorrectiveNetList, mainCalibratePresetList, invertList)
                        
                        # elbow / knee
                        cornerCalibratePresetList, invertList = self.getCalibratePresetList(s, isLeg, False, False, True, False, False)
                        cornerCorrectiveNetList = [None, self.cornerCorrectiveNet, self.cornerCorrectiveNet, self.cornerCorrectiveNet]
                        self.setupJcrControls(self.cornerJntList, s, self.jointLabelAdd, self.userGuideName+"_"+cornerNumber+"_"+cornerName, cornerCorrectiveNetList, cornerCalibratePresetList, invertList)

                        # quadruped kneeB
                        if self.limbStyle == self.dpUIinst.lang['m037_quadruped'] or self.limbStyle == self.dpUIinst.lang['m043_quadSpring'] or self.limbStyle == self.dpUIinst.lang['m155_quadrupedExtra']:
                            kneeBCorrectiveNetList = [None]
                            if self.dpUIinst.lang['c056_front'] in self.userGuideName:
                                kneeBCorrectiveNetList.append(self.setupCorrectiveNet(self.toParentExtremCtrl, self.skinJointList[-4], self.skinJointList[-3], side+self.userGuideName+"_"+self.jNameList[-3]+"B_PitchUp", 1, 1, -80, isLeg, [side+self.userGuideName+"_"+self.jNameList[-3]+"B_PitchUp", 1, 1, -80]))
                            else:
                                kneeBCorrectiveNetList.append(self.setupCorrectiveNet(self.toParentExtremCtrl, self.skinJointList[-4], self.skinJointList[-3], side+self.userGuideName+"_"+self.jNameList[-3]+"B_PitchDown", 1, 1, 80, isLeg, [side+self.userGuideName+"_"+self.jNameList[-3]+"B_PitchDown", 1, 1, 80]))
                            kneeBCorrectiveNetList.append(kneeBCorrectiveNetList[1])
                            kneeBCorrectiveNetList.append(kneeBCorrectiveNetList[1])
                            kneeBCalibratePresetList, invertList = self.getCalibratePresetList(s, isLeg, False, False, False, True, False)
                            kneeBJntList = self.utils.articulationJoint(self.skinJointList[-4], self.skinJointList[-3], 3, [(0, 0, -0.25*self.ctrlRadius), (0.2*self.ctrlRadius, 0, 0.4*self.ctrlRadius), (-0.2*self.ctrlRadius, 0, 0.4*self.ctrlRadius)])
                            self.setupJcrControls(kneeBJntList, s, self.jointLabelAdd, self.userGuideName+"_"+cornerNumber+"_"+cornerBName, kneeBCorrectiveNetList, kneeBCalibratePresetList, invertList)
                            # fix quadruped front and back jar rotation
                            cmds.setAttr(kneeBJntList[0]+".rotateY", -90)
                            if self.dpUIinst.lang['c056_front'] in self.userGuideName:
                                if s == 1:
                                    cmds.setAttr(kneeBJntList[0]+".rotateX", 180)
                                    cmds.setAttr(kneeBJntList[0]+".scaleX", -1)
                            elif self.dpUIinst.lang['c057_back'] in self.userGuideName:
                                if s == 0:
                                    cmds.setAttr(kneeBJntList[0]+".rotateX", 180)
                                    cmds.setAttr(kneeBJntList[0]+".scaleX", -1)
                        
                        # wrist / ankle
                        extremCorrectiveNetList = [None]
                        extremCorrectiveNetList.append(self.setupCorrectiveNet(self.toParentExtremCtrl, self.skinJointList[-3], self.ikExtremOrientCtrl, side+self.userGuideName+"_"+self.jNameList[-1]+"_PitchUp", 1, 4, 80, isLeg, [side+self.userGuideName+"_"+self.jNameList[-1]+"_PitchUp", 1, 1, 80]))
                        extremCorrectiveNetList.append(self.setupCorrectiveNet(self.toParentExtremCtrl, self.skinJointList[-3], self.ikExtremOrientCtrl, side+self.userGuideName+"_"+self.jNameList[-1]+"_PitchDown", 1, 4, -80, isLeg, [side+self.userGuideName+"_"+self.jNameList[-1]+"_PitchDown", 1, 1, -80]))
                        extremCorrectiveNetList.append(self.setupCorrectiveNet(self.toParentExtremCtrl, self.skinJointList[-3], self.ikExtremOrientCtrl, side+self.userGuideName+"_"+self.jNameList[-1]+"_YawRight", 0, 2, -80, isLeg, [side+self.userGuideName+"_"+self.jNameList[-1]+"_YawRight", 0, 0, -80]))
                        extremCorrectiveNetList.append(self.setupCorrectiveNet(self.toParentExtremCtrl, self.skinJointList[-3], self.ikExtremOrientCtrl, side+self.userGuideName+"_"+self.jNameList[-1]+"_YawLeft", 0, 2, 80, isLeg, [side+self.userGuideName+"_"+self.jNameList[-1]+"_YawLeft", 0, 0, 80]))
                        extremCalibratePresetList, invertList = self.getCalibratePresetList(s, isLeg, False, False, False, False, True)
                        extremJntList = self.utils.articulationJoint(self.skinJointList[-3], self.skinJointList[-2], 4, [(0.2*self.ctrlRadius, 0, 0), (-0.2*self.ctrlRadius, 0, 0), (0, 0.2*self.ctrlRadius, 0), (0, -0.2*self.ctrlRadius, 0)], orientCtrl=self.ikExtremOrientCtrl)
                        self.setupJcrControls(extremJntList, s, self.jointLabelAdd, self.userGuideName+"_"+extremNumber+"_"+extremName, extremCorrectiveNetList, extremCalibratePresetList, invertList)
                        # fix rotate with 100% of value for the wrist axis - Thanks Andre Ruegger for the help!
                        extremJax = cmds.listRelatives(extremJntList[0], parent=True, type="joint")[0]
                        orientConnection = cmds.listConnections(extremJax+".rotateZ", destination=False, source=True, plugs=True)[0]
                        cmds.disconnectAttr(orientConnection, extremJax+".rotateZ")
                        jaxRotZMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_"+extremName+"_RotZ_Fix_MD")
                        self.toIDList.append(jaxRotZMD)
                        cmds.setAttr(jaxRotZMD+".input2Z", 2)
                        cmds.connectAttr(orientConnection, jaxRotZMD+".input1Z", force=True)
                        cmds.connectAttr(jaxRotZMD+".outputZ", extremJax+".rotateZ", force=True)
                        # expose ankle data to be replaced by foot connections when integrating modules
                        self.ankleArticList.append([extremJax, extremJntList[0]+"_OrC", side+self.userGuideName+"_"+exposeCornerName])
                        self.ankleCorrectiveList.append(extremCorrectiveNetList)
                        self.jaxRotZMDList.append(jaxRotZMD)

                    else:
                        beforeJntList = self.utils.articulationJoint(self.toScalableHookGrp, self.skinJointList[0])
                        mainJntList = self.utils.articulationJoint(self.shoulderRefGrp, self.skinJointList[1])
                        if not self.cornerJntList:
                            self.cornerJntList = self.utils.articulationJoint(self.skinJointList[1], self.skinJointList[2], doScale=False)
                        extremJntList = self.utils.articulationJoint(self.skinJointList[-3], self.skinJointList[-2], orientCtrl=self.ikExtremOrientCtrl)
                        self.utils.setJointLabel(self.cornerJntList[0], s+self.jointLabelAdd, 18, self.userGuideName+"_01_"+cornerName)
                        cmds.rename(self.cornerJntList[0], side+self.userGuideName+"_01_"+cornerName+"_Jar")
                        if self.limbStyle == self.dpUIinst.lang['m037_quadruped'] or self.limbStyle == self.dpUIinst.lang['m043_quadSpring'] or self.limbStyle == self.dpUIinst.lang['m155_quadrupedExtra']:
                            cornerBJntList = self.utils.articulationJoint(self.skinJointList[2], self.skinJointList[3], doScale=False)
                            self.utils.setJointLabel(cornerBJntList[0], s+self.jointLabelAdd, 18, self.userGuideName+"_01_"+cornerBName)
                            cmds.rename(cornerBJntList[0], side+self.userGuideName+"_01_"+cornerBName+"_Jar")
                        self.ankleArticList.append([cmds.listRelatives(extremJntList[0], parent=True, type="joint")[0], extremJntList[0]+"_OrC", side+self.userGuideName+"_"+exposeCornerName])
                        self.ankleCorrectiveList.append(None)
                        cmds.setAttr(beforeJntList[0]+"_OrC.interpType", 1) #average
                        self.jaxRotZMDList.append(None)
                    if s == 1:
                        for jar in [beforeJntList[0], mainJntList[0], extremJntList[0]]:
                            cmds.setAttr(jar+".rotateX", 180)
                            cmds.setAttr(jar+".scaleX", -1)
                    self.utils.setJointLabel(beforeJntList[0], s+self.jointLabelAdd, 18, self.userGuideName+"_00_"+beforeName)
                    self.utils.setJointLabel(mainJntList[0], s+self.jointLabelAdd, 18, self.userGuideName+"_"+firstNumber+"_"+mainName)
                    self.utils.setJointLabel(extremJntList[0], s+self.jointLabelAdd, 18, self.userGuideName+"_"+extremNumber+"_"+extremName)
                    mainJntList[0] = cmds.rename(mainJntList[0], side+self.userGuideName+"_"+firstNumber+"_"+mainName+"_Jar")
                    extremJntList[0] = cmds.rename(extremJntList[0], side+self.userGuideName+"_"+extremNumber+"_"+extremName+"_Jar")
                else:
                    self.ankleArticList.append(None)
                    self.ankleCorrectiveList.append(None)

                # add main sub controller
                if self.addArticJoint:
                    if self.getHasBend():
                        if self.bendGrps:
                            mainJar = mainJntList[0]
                            mainJax = cmds.listRelatives(mainJntList[0], parent=True, type="joint")[0]
                            mainSubCtrl = self.ctrls.cvControl("id_095_LimbMainSub", ctrlName=side+self.userGuideName+"_"+mainName+"_Sub_Ctrl", r=(self.ctrlRadius * 0.9), d=self.curveDegree, guideSource=self.guideName+"_Main")
                            self.ctrls.setLockHide([mainSubCtrl], ["sx", "sy", "sz", "v"])
                            self.ctrls.setSubControlDisplay(self.fkCtrlList[0], mainSubCtrl, 0)
                            mainSubCtrlZero = self.utils.zeroOut([mainSubCtrl])[0]
                            cmds.delete(self.bendGrps['bottomPosPaC'][1])
                            pac1 = cmds.parentConstraint(mainJax, mainSubCtrlZero, maintainOffset=False, name=mainSubCtrlZero+"_PaC")[0]
                            pac2 = cmds.parentConstraint(mainSubCtrl, mainJar, maintainOffset=True, name=mainJar+"_PaC")[0]
                            pac3 = cmds.parentConstraint(mainJar, self.bendGrps['bottomPosPaC'][0], maintainOffset=True, name=self.bendGrps['bottomPosPaC'][0]+"_PaC")[0]
                            cmds.setAttr(pac1+".interpType", 0) #noFlip
                            cmds.setAttr(pac2+".interpType", 0) #noFlip
                            cmds.setAttr(pac3+".interpType", 0) #noFlip
                            cmds.parent(mainSubCtrlZero, self.toCtrlHookGrp)

                # softIk:
                self.softIkCalibrateList.append(self.softIk.createSoftIk(side+self.userGuideName, self.ikExtremCtrl, ikHandleMainList[0], self.ikJointList[1:4], self.skinJointList[1:4], self.distBetweenList[1], self.worldRef))
                # orient ikHandle group setup:
                softIkOrientLoc = cmds.spaceLocator(name=side+self.userGuideName+"_SoftIk_Aim_Loc")[0]
                cmds.delete(cmds.parentConstraint(self.ikJointList[1], softIkOrientLoc, maintainOffset=False))
                cmds.parent(softIkOrientLoc, self.ikJointList[0])
                cmds.aimConstraint(self.ikExtremCtrl, softIkOrientLoc, aimVector=(0.0, 0.0, 1.0), upVector=(0.0, 1.0, 0.0), worldUpType="object", worldUpObject=self.ikCornerCtrl, name=softIkOrientLoc+"_AiC")
                cmds.orientConstraint(softIkOrientLoc, ikHandleExtraGrp, maintainOffset=False, name=ikHandleGrp+"_OrC")
                # leg with softIk on and stretchable equals to zero reverser foot issue fix:
                if self.limbType == self.legName:
                    rfDistBetList = self.utils.distanceBet(self.ikNSJointList[3], self.ikExtremCtrl, name=side+self.userGuideName+"_"+kNameList[1]+"_RF_DistBet", keep=True)
                    cmds.delete(rfDistBetList[4])
                    cmds.parent(rfDistBetList[2:4], distBetGrp)
                    rfSoftIkCnd = cmds.createNode("condition", name=side+self.userGuideName+"_RF_SoftIk_Cnd")
                    rfStretchableCnd = cmds.createNode("condition", name=side+self.userGuideName+"_RF_Stretchable_Cnd")
                    rfDistInvMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_RF_DistInv_MD")
                    self.toIDList.extend([rfSoftIkCnd, rfStretchableCnd, rfDistInvMD])
                    cmds.setAttr(rfDistInvMD+".input2X", -1)
                    cmds.setAttr(rfStretchableCnd+".colorIfFalseR", 0)
                    cmds.connectAttr(rfDistBetList[1]+".distance", rfSoftIkCnd+".colorIfFalseR", force=True)
                    cmds.connectAttr(self.ikExtremCtrl+".softIk", rfSoftIkCnd+".firstTerm", force=True)
                    cmds.connectAttr(rfSoftIkCnd+".outColorR", rfDistInvMD+".input1X", force=True)
                    cmds.connectAttr(rfDistInvMD+".outputX", rfStretchableCnd+".colorIfTrueR", force=True)
                    cmds.connectAttr(self.ikExtremCtrl+".stretchable", rfStretchableCnd+".firstTerm", force=True)
                    cmds.connectAttr(rfStretchableCnd+".outColorR", self.ikStretchExtremLoc+".translateZ", force=True)
                    cmds.orientConstraint(softIkOrientLoc, ikStretchExtremLocZero, maintainOffset=False, name=ikStretchExtremLocZero+"_OrC")
                
                # ikFkSnap
                dpIkFkSnap.IkFkSnapClass(self.dpUIinst, side+self.userGuideName, self.worldRef, self.fkCtrlList, [self.ikCornerCtrl, self.ikExtremCtrl, self.ikExtremSubCtrl], self.ikJointList, [self.dpUIinst.lang['c018_revFoot_roll'], self.dpUIinst.lang['c019_revFoot_spin'], self.dpUIinst.lang['c020_revFoot_turn']], self.dpUIinst.lang['c040_uniformScale'])
                
                # calibration attribute:
                if self.limbTypeName == self.armName:
                    ikExtremCalibrationList = [
                                            self.dpUIinst.lang['c040_uniformScale']+self.dpUIinst.lang['c105_multiplier'].capitalize(),
                                            "softIk_"+self.dpUIinst.lang['c111_calibrate']
                    ]
                else: #leg
                    ikExtremCalibrationList = [
                                            self.dpUIinst.lang['c015_revFoot_F']+self.dpUIinst.lang['c018_revFoot_roll'].capitalize()+self.dpUIinst.lang['c102_angle'].capitalize(),
                                            self.dpUIinst.lang['c015_revFoot_F']+self.dpUIinst.lang['c018_revFoot_roll'].capitalize()+self.dpUIinst.lang['c103_plant'].capitalize(),
                                            self.dpUIinst.lang['c040_uniformScale']+self.dpUIinst.lang['c105_multiplier'].capitalize(),
                                            "softIk_"+self.dpUIinst.lang['c111_calibrate']
                    ]
                fkExtremCalibrationList = [self.dpUIinst.lang['c040_uniformScale']+self.dpUIinst.lang['c105_multiplier'].capitalize()]
                fkBeforeCalibrationList = [self.dpUIinst.lang['c032_follow']]
                if self.limbStyle == self.dpUIinst.lang['m155_quadrupedExtra']:
                    self.ctrls.setStringAttrFromList(self.quadExtraCtrl, ['autoOrient'])
                self.ctrls.setStringAttrFromList(self.ikExtremCtrl, ikExtremCalibrationList)
                self.ctrls.setStringAttrFromList(self.fkCtrlList[-1], fkExtremCalibrationList)
                self.ctrls.setStringAttrFromList(self.fkCtrlList[0], fkBeforeCalibrationList)

                # integrating dics:
                self.extremJntList.append(self.skinJointList[-2])
                self.integrateOrigFromList.append(self.origFromList)
                
                # clean-up before joint, it isn't used to autoClavicle:
                cmds.delete(self.ikACJointList[0])
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)
                self.utils.addCustomAttr([self.zeroFkCtrlGrp, self.masterCtrlRef, self.rootCtrlRef, self.shoulderRefGrp, self.ikStretchExtremLoc, self.ikExtremCtrlGrp, self.ikExtremCtrlOrientGrp, self.ikHandleToRFGrp, self.cornerGrp, self.cornerOrientGrp, ikHandleACGrp, self.clavicleCtrlGrp, acLocGrp], self.utils.ignoreTransformIOAttr)
                self.utils.addCustomAttr(self.ikHandleToRFGrpList, self.utils.ignoreTransformIOAttr)
                self.toIDList.extend([self.fkIsolateRevNode, upLocOrientConst, upLocOrientRev, ikScaleMD, fkScaleMD, uniBlend, ikStretchableMD, ikStretchCtrlCnd, ikStretchDifPMA, ikStretchCnd, ikStretchClp])
                self.dpUIinst.customAttr.addAttr(0, [self.toStaticHookGrp], descendents=True) #dpID
            # finalize this rig:
            self.serializeGuide()
            self.integratingInfo()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and moduleInstance namespace:
        self.deleteModule()
        self.renameUnitConversion()
        self.dpUIinst.customAttr.addAttr(0, self.toIDList) #dpID


    def integratingInfo(self, *args):
        dpBaseStandard.BaseStandard.integratingInfo(self)
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.integratedActionsDic = {
            "module": {
                "ikCtrlList": self.ikExtremCtrlList,
                "ikCtrlZeroList": self.ikExtremCtrlZeroList,
                "ikPoleVectorZeroList": self.ikPoleVectorCtrlZeroList,
                "ikHandleGrpList": self.ikHandleToRFGrpList,
                "ikHandleConstList": self.ikHandleConstList,
                "ikFkBlendGrpToRevFootList": self.ikFkBlendGrpToRevFootList,
                "worldRefList": self.worldRefList,
                "worldRefShapeList": self.worldRefShapeList,
                "limbTypeName": self.limbTypeName,
                "extremJntList": self.extremJntList,
                "fixIkSpringSolverGrpList": self.fixIkSpringSolverGrpList,
                "limbStyle": self.limbStyle,
                "quadFrontLegList": self.quadFrontLegList,
                "integrateOrigFromList": self.integrateOrigFromList,
                "ikStretchExtremLoc": self.ikStretchExtremLocList,
                "limbManualVolume": self.dpUIinst.lang['m019_limb'].lower()+"Manual_"+self.dpUIinst.lang['c031_volumeVariation'],
                "scalableGrp": self.aScalableGrps,
                "masterCtrlRefList": self.masterCtrlRefList,
                "rootCtrlRefList": self.rootCtrlRefList,
                "softIkCalibrateList": self.softIkCalibrateList,
                "correctiveCtrlGrpList": self.correctiveCtrlGrpList,
                "addArticJoint": self.addArticJoint,
                "addCorrective": self.addCorrective, 
                "ankleArticList": self.ankleArticList,
                "ankleCorrectiveList": self.ankleCorrectiveList,
                "jaxRotZMDList": self.jaxRotZMDList
            }
        }
