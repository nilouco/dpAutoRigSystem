# importing libraries:
import maya.cmds as cmds
import maya.mel as mel
from ..Modules.Library import dpControls as dpControls
from ..Modules.Library import dpUtils as utils

# global variables to this module:    
CLASS_NAME = "HeadDeformer"
TITLE = "m051_headDef"
DESCRIPTION = "m052_headDefDesc"
ICON = "/Icons/dp_headDeformer.png"


DPHD_VERSION = "2.2"


class HeadDeformer():
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, *args, **kwargs):
        # defining variables:
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
        self.headCtrl = None
        # call main function
        self.dpHeadDeformer(self)
    
    
    def dpHeadDeformer(self, *args):
        """ Create the arrow curve and deformers (squash and bends).
        """
        # defining variables
        headDeformerName = self.langDic[self.langName]["c024_head"]+self.langDic[self.langName]["c097_deformer"]
        centerSymmetryName = self.langDic[self.langName]["c098_center"]+self.langDic[self.langName]["c101_symmetry"]
        topSymmetryName = self.langDic[self.langName]["c099_top"]+self.langDic[self.langName]["c101_symmetry"]
        intensityName = self.langDic[self.langName]["c049_intensity"]
        axisList = ["X", "Y", "Z"]
        
        # validating namming in order to be possible create more than one setup
        validName = utils.validateName(headDeformerName+"_FFDSet", "FFDSet")
        numbering = validName.replace(headDeformerName, "")[:-7]
        if numbering:
            headDeformerName = headDeformerName+numbering
            centerSymmetryName = centerSymmetryName+numbering
            topSymmetryName = topSymmetryName+numbering
        
        # get a list of selected items
        selList = cmds.ls(selection=True)
        if selList:
            # lattice deformer
            latticeDefList = cmds.lattice(name=headDeformerName+"_FFD", divisions=(6, 6, 6), ldivisions=(6, 6, 6), outsideLattice=1, objectCentered=True) #[Set, Lattice, Base]
            latticePointsList = latticeDefList[1]+".pt[0:5][2:5][0:5]"
            
            # store initial scaleY in order to avoid lattice rotation bug on non frozen transformations
            bBoxMaxY = cmds.getAttr(latticeDefList[2]+".boundingBox.boundingBoxMax.boundingBoxMaxY")
            bBoxMinY = cmds.getAttr(latticeDefList[2]+".boundingBox.boundingBoxMin.boundingBoxMinY")
            initialSizeY = bBoxMaxY-bBoxMinY
            
            # force rotate zero to lattice in order to avoid selected non froozen transformations
            for axis in axisList:
                cmds.setAttr(latticeDefList[1]+".rotate"+axis, 0)
                cmds.setAttr(latticeDefList[2]+".rotate"+axis, 0)
            cmds.setAttr(latticeDefList[1]+".scaleY", initialSizeY)
            cmds.setAttr(latticeDefList[2]+".scaleY", initialSizeY)
            
            # getting size and distances from Lattice Bounding Box
            bBoxMaxY = cmds.getAttr(latticeDefList[2]+".boundingBox.boundingBoxMax.boundingBoxMaxY")
            bBoxMinY = cmds.getAttr(latticeDefList[2]+".boundingBox.boundingBoxMin.boundingBoxMinY")
            bBoxSize = bBoxMaxY - bBoxMinY
            bBoxMidY = bBoxMinY + (bBoxSize*0.5)
            
            # twist deformer
            twistDefList = cmds.nonLinear(latticePointsList, name=headDeformerName+"_Twist", type="twist") #[Deformer, Handle]
            cmds.setAttr(twistDefList[0]+".lowBound", 0)
            cmds.setAttr(twistDefList[0]+".highBound", bBoxSize)
            cmds.setAttr(twistDefList[1]+".ty", bBoxMinY)
            
            # squash deformer
            squashDefList = cmds.nonLinear(latticePointsList, name=headDeformerName+"_Squash", type="squash") #[Deformer, Handle]
            cmds.setAttr(squashDefList[0]+".highBound", 0.5*bBoxSize)
            cmds.setAttr(squashDefList[0]+".startSmoothness", 1)
            cmds.setAttr(squashDefList[1]+".ty", bBoxMidY)
            
            # side bend deformer
            sideBendDefList = cmds.nonLinear(latticePointsList, name=headDeformerName+"_Side_Bend", type="bend") #[Deformer, Handle]
            cmds.setAttr(sideBendDefList[0]+".lowBound", 0)
            cmds.setAttr(sideBendDefList[0]+".highBound", bBoxSize)
            cmds.setAttr(sideBendDefList[1]+".ty", bBoxMinY)
            
            # front bend deformer
            frontBendDefList = cmds.nonLinear(latticePointsList, name=headDeformerName+"_Front_Bend", type="bend") #[Deformer, Handle]
            cmds.setAttr(frontBendDefList[0]+".lowBound", 0)
            cmds.setAttr(frontBendDefList[0]+".highBound", bBoxSize)
            cmds.setAttr(frontBendDefList[1]+".ry", -90)
            cmds.setAttr(frontBendDefList[1]+".ty", bBoxMinY)
            
            # fix deform transforms scale to 1
            defHandleList = [twistDefList[1], squashDefList[1], sideBendDefList[1], frontBendDefList[1]]
            for defHandle in defHandleList:
                for axis in axisList:
                    cmds.setAttr(defHandle+".scale"+axis, 1)
            
            # force correct rename for Maya versions before 2020:
            if (int(cmds.about(version=True)[:4]) < 2020):
                if cmds.objExists(twistDefList[0]+"Set"):
                    cmds.rename(twistDefList[0]+"Set", headDeformerName+"_TwistSet")
                    twistDefList[0] = cmds.rename(twistDefList[0], headDeformerName+"_Twist")
                    twistDefList[1] = cmds.rename(twistDefList[1], headDeformerName+"_TwistHandle")
                if cmds.objExists(squashDefList[0]+"Set"):
                    cmds.rename(squashDefList[0]+"Set", headDeformerName+"_SquashSet")
                    squashDefList[0] = cmds.rename(squashDefList[0], headDeformerName+"_Squash")
                    squashDefList[1] = cmds.rename(squashDefList[1], headDeformerName+"_SquashHandle")
                if cmds.objExists(sideBendDefList[0]+"Set"):
                    cmds.rename(sideBendDefList[0]+"Set", headDeformerName+"_Side_BendSet")
                    sideBendDefList[0] = cmds.rename(sideBendDefList[0], headDeformerName+"_Side_Bend")
                    sideBendDefList[1] = cmds.rename(sideBendDefList[1], headDeformerName+"_Side_BendHandle")
                if cmds.objExists(frontBendDefList[0]+"Set"):
                    cmds.rename(frontBendDefList[0]+"Set", headDeformerName+"_Front_BendSet")
                    frontBendDefList[0] = cmds.rename(frontBendDefList[0], headDeformerName+"_Front_Bend")
                    frontBendDefList[1] = cmds.rename(frontBendDefList[1], headDeformerName+"_Front_BendHandle")
                
            # arrow control curve
            arrowCtrl = self.ctrls.cvControl("id_053_HeadDeformer", headDeformerName+"_Ctrl", 0.25*bBoxSize, d=0)
            
            # add control intensite and calibrate attributes
            for axis in axisList:
                cmds.addAttr(arrowCtrl, longName=intensityName+axis, attributeType='float', defaultValue=1)
                cmds.setAttr(arrowCtrl+"."+intensityName+axis, edit=True, keyable=False, channelBox=True)
            cmds.addAttr(arrowCtrl, longName="calibrateX", attributeType='float', defaultValue=1/(3*bBoxSize), keyable=False)
            cmds.addAttr(arrowCtrl, longName="calibrateY", attributeType='float', defaultValue=3/bBoxSize, keyable=False)
            cmds.addAttr(arrowCtrl, longName="calibrateZ", attributeType='float', defaultValue=1/(3*bBoxSize), keyable=False)
            
            # multiply divide in order to intensify influences
            calibrateMD = cmds.createNode("multiplyDivide", name=headDeformerName+"_Calibrate_MD")
            intensityMD = cmds.createNode("multiplyDivide", name=headDeformerName+"_"+intensityName.capitalize()+"_MD")
            twistMD = cmds.createNode("multiplyDivide", name=headDeformerName+"_Twist_MD")
            cmds.setAttr(twistMD+".input2Y", -1)
            
            # connections
            for axis in axisList:
                cmds.connectAttr(arrowCtrl+"."+intensityName+axis, calibrateMD+".input1"+axis, force=True)
                cmds.connectAttr(arrowCtrl+".calibrate"+axis, calibrateMD+".input2"+axis, force=True)
                cmds.connectAttr(arrowCtrl+".translate"+axis, intensityMD+".input1"+axis, force=True)
                cmds.connectAttr(calibrateMD+".output"+axis, intensityMD+".input2"+axis, force=True)
            cmds.connectAttr(intensityMD+".outputX", sideBendDefList[0]+".curvature", force=True)
            cmds.connectAttr(intensityMD+".outputY", squashDefList[0]+".factor", force=True)
            cmds.connectAttr(intensityMD+".outputZ", frontBendDefList[0]+".curvature", force=True)
            cmds.connectAttr(arrowCtrl+".ry", twistMD+".input1Y", force=True)
            cmds.connectAttr(twistMD+".outputY", twistDefList[0]+".endAngle", force=True)
            # change squash to be more cartoon
            cmds.setDrivenKeyframe(squashDefList[0]+".lowBound", currentDriver=intensityMD+".outputY", driverValue=-0.25*bBoxSize, value=-bBoxSize, inTangentType="auto", outTangentType="auto")
            cmds.setDrivenKeyframe(squashDefList[0]+".lowBound", currentDriver=intensityMD+".outputY", driverValue=0, value=-0.5*bBoxSize, inTangentType="auto", outTangentType="auto")
            cmds.setDrivenKeyframe(squashDefList[0]+".lowBound", currentDriver=intensityMD+".outputY", driverValue=0.5*bBoxSize, value=-0.25*bBoxSize, inTangentType="auto", outTangentType="flat")
            # fix side values
            for axis in axisList:
                unitConvNode = cmds.listConnections(intensityMD+".output"+axis, destination=True)[0]
                if unitConvNode:
                    if cmds.objectType(unitConvNode) == "unitConversion":
                        cmds.setAttr(unitConvNode+".conversionFactor", 1)

            self.ctrls.setLockHide([arrowCtrl], ['rx', 'rz', 'sx', 'sy', 'sz', 'v'])
            
            # create symetry setup
            centerClusterList = cmds.cluster(latticeDefList[1]+".pt[0:5][2:3][0:5]", relative=True, name=centerSymmetryName+"_Cls") #[Cluster, Handle]
            topClusterList = cmds.cluster(latticeDefList[1]+".pt[0:5][2:5][0:5]", relative=True, name=topSymmetryName+"_Cls")
            clustersZeroList = utils.zeroOut([centerClusterList[1], topClusterList[1]])
            cmds.delete(cmds.parentConstraint(centerClusterList[1], clustersZeroList[1]))
            clusterGrp = cmds.group(clustersZeroList, name=headDeformerName+"_"+self.langDic[self.langName]["c101_symmetry"]+"_Grp")
            # symmetry controls
            centerSymmetryCtrl = self.ctrls.cvControl("id_068_Symmetry", centerSymmetryName+"_Ctrl", bBoxSize, d=0, rot=(-90, 0, 90))
            topSymmetryCtrl = self.ctrls.cvControl("id_068_Symmetry", topSymmetryName+"_Ctrl", bBoxSize, d=0, rot=(0, 90, 0))
            symmetryCtrlZeroList = utils.zeroOut([centerSymmetryCtrl, topSymmetryCtrl])
            for axis in axisList:
                cmds.connectAttr(centerSymmetryCtrl+".translate"+axis, centerClusterList[1]+".translate"+axis, force=True)
                cmds.connectAttr(centerSymmetryCtrl+".rotate"+axis, centerClusterList[1]+".rotate"+axis, force=True)
                cmds.connectAttr(centerSymmetryCtrl+".scale"+axis, centerClusterList[1]+".scale"+axis, force=True)
                cmds.connectAttr(topSymmetryCtrl+".translate"+axis, topClusterList[1]+".translate"+axis, force=True)
                cmds.connectAttr(topSymmetryCtrl+".rotate"+axis, topClusterList[1]+".rotate"+axis, force=True)
                cmds.connectAttr(topSymmetryCtrl+".scale"+axis, topClusterList[1]+".scale"+axis, force=True)
            
            # create groups
            arrowCtrlGrp = cmds.group(arrowCtrl, name=arrowCtrl+"_Grp")
            offsetGrp = cmds.group(name=headDeformerName+"_Offset_Grp", empty=True)
            dataGrp = cmds.group(name=headDeformerName+"_Data_Grp", empty=True)
            cmds.delete(cmds.parentConstraint(latticeDefList[2], arrowCtrlGrp, maintainOffset=False))
            arrowCtrlHeigh = bBoxMaxY + (bBoxSize*0.5)
            cmds.setAttr(arrowCtrlGrp+".ty", arrowCtrlHeigh)
            cmds.delete(cmds.parentConstraint(latticeDefList[2], offsetGrp, maintainOffset=False))
            cmds.delete(cmds.parentConstraint(latticeDefList[2], symmetryCtrlZeroList[0], maintainOffset=False))
            cmds.delete(cmds.parentConstraint(latticeDefList[2], symmetryCtrlZeroList[1], maintainOffset=False))
            cmds.parent(symmetryCtrlZeroList, arrowCtrlGrp)
            
            # try to integrate to Head_Head_Ctrl
            allTransformList = cmds.ls(selection=False, type="transform")
            headCtrlList = self.ctrls.getControlNodeById("id_023_HeadHead")
            if headCtrlList:
                if len(headCtrlList) > 1:
                    mel.eval("warning" + "\"" + self.langDic[self.langName]["i075_moreOne"] + " Head control.\"" + ";")
                else:
                    self.headCtrl = headCtrlList[0]
            if self.headCtrl:
                # setup hierarchy
                headCtrlPosList = cmds.xform(self.headCtrl, query=True, rotatePivot=True, worldSpace=True)
                cmds.xform(dataGrp, translation=(headCtrlPosList[0], headCtrlPosList[1], headCtrlPosList[2]), worldSpace=True)
                cmds.parentConstraint(self.headCtrl, dataGrp, maintainOffset=True, name=dataGrp+"_ParentConstraint")
                cmds.scaleConstraint(self.headCtrl, dataGrp, maintainOffset=True, name=dataGrp+"_ScaleConstraint")
                # influence controls
                toHeadDefCtrlList = []
                for item in allTransformList:
                    if cmds.objExists(item+".controlID"):
                        if cmds.getAttr(item+".controlID") == "id_024_HeadJaw":
                            toHeadDefCtrlList.append(item)
                        elif cmds.getAttr(item+".controlID") == "id_027_HeadLipCorner":
                            toHeadDefCtrlList.append(item)
                headChildrenList = cmds.listRelatives(self.headCtrl, children=True, allDescendents=True, type="transform")
                if headChildrenList:
                    for item in headChildrenList:
                        if cmds.objExists(item+".controlID"):
                            if not cmds.getAttr(item+".controlID") == "id_052_FacialFace":
                                if not cmds.getAttr(item+".controlID") == "id_029_SingleIndSkin":
                                    if not cmds.getAttr(item+".controlID") == "id_054_SingleMain":
                                        toHeadDefCtrlList.append(item)
                                    else:
                                        singleMainShapeList = cmds.listRelatives(item, children=True, shapes=True)
                                        if singleMainShapeList:
                                            for mainShape in singleMainShapeList:
                                                toHeadDefCtrlList.append(mainShape)
                if toHeadDefCtrlList:
                    for item in toHeadDefCtrlList:
                        cmds.sets(item, include=headDeformerName+"_FFDSet")
                cmds.parent(arrowCtrlGrp, self.headCtrl)
            
            cmds.parent(squashDefList[1], sideBendDefList[1], frontBendDefList[1], twistDefList[1], offsetGrp)
            cmds.parent(offsetGrp, clusterGrp, latticeDefList[1], latticeDefList[2], dataGrp)
            
            # try to integrate to Scalable_Grp
            for item in allTransformList:
                if cmds.objExists(item+".masterGrp") and cmds.getAttr(item+".masterGrp") == 1:
                    scalableGrp = cmds.listConnections(item+".scalableGrp")[0]
                    cmds.parent(dataGrp, scalableGrp)
                    break
            
            # try to change deformers to get better result
            cmds.scale(1.25, 1.25, 1.25, offsetGrp)
            
            # colorize
            self.ctrls.colorShape([arrowCtrl, centerSymmetryCtrl, topSymmetryCtrl], "cyan")
            
            # finish selection the arrow control
            cmds.select(arrowCtrl)
            print self.langDic[self.langName]["i179_addedHeadDef"],
        
        else:
            mel.eval("warning" + "\"" + self.langDic[self.langName]["i034_notSelHeadDef"] + "\"" + ";")