# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "HeadDeformer"
TITLE = "m051_headDef"
DESCRIPTION = "m052_headDefDesc"
ICON = "/Icons/dp_headDeformer.png"


class HeadDeformer():
    def __init__(self, dpUIinst, langDic, langName):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.headName = self.langDic[self.langName]['c_head']
        # call main function
        self.dpMain(self)
    
    
    def dpMain(self, *args):
        """ Just main to call dpHeadDeformers function.
        """
        self.dpHeadDeformer()
    
    
    def dpHeadDeformer(self, *args):
        """ Create the arrow curve and deformers (squash and bends).
        """
        # get a list of selected items
        selList = cmds.ls(selection=True)
        
        if selList:
            # twist deformer
            twistDefList = cmds.nonLinear(selList, name="TwistHead", type="twist")
            defSize = cmds.getAttr(twistDefList[0]+".highBound")
            defScale = cmds.getAttr(twistDefList[1]+".scaleY")
            defTy = -(defSize * defScale)
            defTy = self.dpCheckLinearUnit(defTy)
            cmds.setAttr(twistDefList[0]+".lowBound", 0)
            cmds.setAttr(twistDefList[0]+".highBound", (defSize * 2))
            cmds.setAttr(twistDefList[1]+".ty", defTy)
            
            # squash deformer
            squashDefList = cmds.nonLinear(selList, name="SquashHead", type="squash")
            cmds.setAttr(squashDefList[0]+".highBound", (defSize * 4))
            cmds.setAttr(squashDefList[1]+".ty", defTy)
            cmds.setAttr(squashDefList[0]+".startSmoothness", 1)
            
            # side bend deformer
            sideBendDefList = cmds.nonLinear(selList, name="BendSideHead", type="bend")
            cmds.setAttr(sideBendDefList[0]+".lowBound", 0)
            cmds.setAttr(sideBendDefList[0]+".highBound", (defSize * 4))
            cmds.setAttr(sideBendDefList[1]+".ty", defTy)
            
            # front bend deformer
            frontBendDefList = cmds.nonLinear(selList, name="BendFrontHead", type="bend")
            cmds.setAttr(frontBendDefList[0]+".lowBound", 0)
            cmds.setAttr(frontBendDefList[0]+".highBound", (defSize * 4))
            cmds.setAttr(frontBendDefList[1]+".ry", -90)
            cmds.setAttr(frontBendDefList[1]+".ty", defTy)
            
            # arrow control curve
            arrowCtrl = self.dpCvArrow(self.headName+"Deformer_Ctrl")
            # add control intensite attributes
            cmds.addAttr(arrowCtrl, longName="intensityX", attributeType='float', keyable=True)
            cmds.addAttr(arrowCtrl, longName="intensityY", attributeType='float', keyable=True)
            cmds.addAttr(arrowCtrl, longName="intensityZ", attributeType='float', keyable=True)
            cmds.setAttr(arrowCtrl+".intensityX", 0.1)
            cmds.setAttr(arrowCtrl+".intensityY", 0.1)
            cmds.setAttr(arrowCtrl+".intensityZ", 0.1)
            
            # multiply divide in order to intensify influences
            mdNode = cmds.createNode("multiplyDivide", name=self.headName+"Deformer_MD")
            mdTwistNode = cmds.createNode("multiplyDivide", name=self.headName+"Deformer_Twist_MD")
            cmds.setAttr(mdTwistNode+".input2Y", -1)
            
            # connections
            cmds.connectAttr(arrowCtrl+".tx", mdNode+".input1X", force=True)
            cmds.connectAttr(arrowCtrl+".ty", mdNode+".input1Y", force=True)
            cmds.connectAttr(arrowCtrl+".tz", mdNode+".input1Z", force=True)
            cmds.connectAttr(arrowCtrl+".ry", mdTwistNode+".input1Y", force=True)
            cmds.connectAttr(arrowCtrl+".intensityX", mdNode+".input2X", force=True)
            cmds.connectAttr(arrowCtrl+".intensityY", mdNode+".input2Y", force=True)
            cmds.connectAttr(arrowCtrl+".intensityZ", mdNode+".input2Z", force=True)
            cmds.connectAttr(mdNode+".outputX", sideBendDefList[0]+".curvature", force=True)
            cmds.connectAttr(mdNode+".outputY", squashDefList[0]+".factor", force=True)
            cmds.connectAttr(mdNode+".outputZ", frontBendDefList[0]+".curvature", force=True)
            cmds.connectAttr(mdTwistNode+".outputY", twistDefList[0]+".endAngle", force=True)
            # change squash to be more cartoon
            cmds.setDrivenKeyframe(squashDefList[0]+".lowBound", currentDriver=mdNode+".outputY", driverValue=-1, value=-4, inTangentType="auto", outTangentType="auto")
            cmds.setDrivenKeyframe(squashDefList[0]+".lowBound", currentDriver=mdNode+".outputY", driverValue=0, value=-2, inTangentType="auto", outTangentType="auto")
            cmds.setDrivenKeyframe(squashDefList[0]+".lowBound", currentDriver=mdNode+".outputY", driverValue=2, value=-1, inTangentType="auto", outTangentType="flat")
            # fix side values
            axisList = ["X", "Y", "Z"]
            for axis in axisList:
                unitConvNode = cmds.listConnections(mdNode+".output"+axis, destination=True)[0]
                if unitConvNode:
                    if cmds.objectType(unitConvNode) == "unitConversion":
                        cmds.setAttr(unitConvNode+".conversionFactor", 1)

            attrList = ['rx', 'rz', 'sx', 'sy', 'sz', 'v']
            for attr in attrList:
                cmds.setAttr(arrowCtrl+"."+attr, lock=True, keyable=False)
            cmds.setAttr(arrowCtrl+".intensityX", edit=True, keyable=False, channelBox=True)
            cmds.setAttr(arrowCtrl+".intensityY", edit=True, keyable=False, channelBox=True)
            cmds.setAttr(arrowCtrl+".intensityZ", edit=True, keyable=False, channelBox=True)
            
            # create groups
            arrowCtrlGrp = cmds.group(arrowCtrl, name=self.headName+"Deformer_Ctrl_Grp")
            cmds.setAttr(arrowCtrlGrp+".ty", -1.75*defTy)
            cmds.group((squashDefList[1], sideBendDefList[1], frontBendDefList[1], twistDefList[1]), name=self.headName+"Deformer_Data_Grp")
            
            # finish selection the arrow control
            cmds.select(arrowCtrl)
        
        else:
            mel.eval("warning \""+self.langDic[self.langName]['i034_notSelHeadDef']+"\";")
    
    
    def dpCvArrow(self, ctrlName="arrowCurve", radius=1, *args):
        """ Create an arrow control curve and returns it.
        """
        if cmds.objExists(ctrlName) == True:
            originalCtrlName = ctrlName
            i = 1
            while cmds.objExists(ctrlName) == True:
                ctrlName = originalCtrlName+str(i)
                i += 1
        r = radius*0.1
        arrowCurve = cmds.curve(name=ctrlName, d=1, p=[(0, 0, 0), (-2*r, r, 0), (-r, r, 0), (-r, 4*r, 0), (r, 4*r, 0), (r, r, 0), (2*r, r, 0), (0, 0, 0)])
        cmds.rename(cmds.listRelatives(arrowCurve, children=True, type="nurbsCurve", shapes=True), arrowCurve+"Shape")
        return arrowCurve


    def dpCheckLinearUnit(self, origRadius, defaultUnit="centimeter", *args):
        """ Verify if the Maya linear unit is in Centimeter.
            Return the radius to the new unit size using multiplying.
            Same function from dpControls module.
        """
        newRadius = 1
        linearUnit = cmds.currentUnit(query=True, linear=True, fullName=True)
        # centimeter
        if linearUnit == defaultUnit:
            newRadius = origRadius
        elif linearUnit == "meter":
            newRadius = origRadius*0.01
        elif linearUnit == "millimeter":
            newRadius = origRadius*10
        elif linearUnit == "inch":
            newRadius = origRadius*0.393701
        elif linearUnit == "foot":
            newRadius = origRadius*0.032808
        elif linearUnit == "yard":
            newRadius = origRadius*0.010936
        return newRadius
