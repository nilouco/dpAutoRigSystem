# importing libraries:
from maya import cmds
from maya import mel
from ..Modules.Library import dpControls

# global variables to this module:    
CLASS_NAME = "HeadDeformer"
TITLE = "m051_headDef"
DESCRIPTION = "m052_headDefDesc"
ICON = "/Icons/dp_headDeformer.png"
DPHEADDEFINFLUENCE = "dpHeadDeformerInfluence"
DPJAWDEFINFLUENCE = "dpJawDeformerInfluence"

DP_HEADDEFORMER_VERSION = 3.3


class HeadDeformer(object):
    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        # defining variables:
        self.dpUIinst = dpUIinst
        self.utils = dpUIinst.utils
        self.ctrls = dpControls.ControlClass(self.dpUIinst)
        self.ui = ui
        self.headCtrl = None
        self.wellDone = True
        # call main function
        if self.ui:
            self.dpHeadDeformer(self)
    
    
    def dpHeadDeformerPromptDialog(self, *args):
        """ dpDeformer prompt dialog to get the name of the deformer
        """
        btContinue = self.dpUIinst.lang['i174_continue']
        btCancel = self.dpUIinst.lang['i132_cancel']
        result = cmds.promptDialog(title="dpHeadDeformer", 
                                   message=self.dpUIinst.lang["m006_name"], 
                                   text=self.dpUIinst.lang["c024_head"], 
                                   button=[btContinue, btCancel], 
                                   defaultButton=btContinue, 
                                   cancelButton=btCancel, 
                                   dismissString=btCancel)
        if result == btContinue:
            dialogName = cmds.promptDialog(query=True, text=True)
            dialogName = dialogName[0].upper() + dialogName[1:]
            return dialogName
        elif result is None:
            return None


    def addDeformerInName(self, deformerName, deformerIn, *args):
        """ When the flag deformerIn is True, it will add the word Deformer as suffix. If it's false, it will maintain the name or take off Deformer in the name.
        """
        if deformerName:
            if deformerIn == True:
                if not "Deformer" in deformerName:
                    deformerName = deformerName+"Deformer"
                return deformerName
            if deformerIn == False:
                if "Deformer" in deformerName:
                    deformerName = deformerName.replace("Deformer", "")
                return deformerName+"_"
            

    def dpHeadDeformer(self, dialogName=None, hdList=None, *args):
        """ Create the arrow curve and deformers (squash and bends).
        """
        if self.ui:
            dialogName = self.dpHeadDeformerPromptDialog()
        if dialogName == None:
            return
        # defining variables
        deformerName = self.addDeformerInName(dialogName, True)
        clusterName = self.addDeformerInName(dialogName, False)
        mainCtrlName = deformerName+"_Main"
        centerSymmetryName = clusterName+self.dpUIinst.lang["c098_center"]+self.dpUIinst.lang["c101_symmetry"]
        topSymmetryName = clusterName+self.dpUIinst.lang["c099_top"]+self.dpUIinst.lang["c101_symmetry"]
        intensityName = clusterName+self.dpUIinst.lang["c049_intensity"]
        expandName = clusterName+self.dpUIinst.lang["c104_expand"]
        bottomCtrlName = clusterName+self.dpUIinst.lang["c100_bottom"]
        middleCtrlName = clusterName+self.dpUIinst.lang["m033_middle"]
        topCtrlName = clusterName+self.dpUIinst.lang["c099_top"]
        calibrateName = self.dpUIinst.lang["c111_calibrate"].lower()
        axisList = ["X", "Y", "Z"]
        posList = [self.dpUIinst.lang["c100_bottom"], self.dpUIinst.lang["m033_middle"], self.dpUIinst.lang["c099_top"]]
        
        # validating namming in order to be possible create more than one setup
        validName = self.utils.validateName(deformerName+"_FFD", "FFD")
        numbering = validName.replace(deformerName, "")[:-4]
        if numbering:
            deformerName = deformerName+numbering
            mainCtrlName = mainCtrlName+numbering
            centerSymmetryName = centerSymmetryName+numbering
            topSymmetryName = topSymmetryName+numbering
            bottomCtrlName = bottomCtrlName+numbering
            middleCtrlName = middleCtrlName+numbering
            topCtrlName = topCtrlName+numbering

        if not hdList:
            # get a list of selected items
            hdList = cmds.ls(selection=True)       
        if hdList:
            cmds.select(hdList)
            # lattice deformer
            latticeDefList = cmds.lattice(name=deformerName+"_FFD", divisions=(6, 6, 6), ldivisions=(6, 6, 6), outsideLattice=2, outsideFalloffDistance=1, objectCentered=True) #[Deformer/Set, Lattice, Base], mode=falloff
            latticePointsList = latticeDefList[1]+".pt[0:5][2:5][0:5]"
            # get lattice points to add sub controls
            latticeBottomPointList = latticeDefList[1]+".pt[0:5][0:1][0:5]"
            latticeMiddlePointList = latticeDefList[1]+".pt[0:5][2:3][0:5]"
            latticeTopPointList = latticeDefList[1]+".pt[0:5][4:5][0:5]"
            latticeSubPointsList = [latticeBottomPointList, latticeMiddlePointList, latticeTopPointList]
            
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
            twistDefList = cmds.nonLinear(latticePointsList, name=deformerName+"_Twist", type="twist") #[Deformer, Handle]
            cmds.setAttr(twistDefList[0]+".lowBound", 0)
            cmds.setAttr(twistDefList[0]+".highBound", bBoxSize)
            cmds.setAttr(twistDefList[1]+".ty", bBoxMinY)
            
            # squash deformer
            squashDefList = cmds.nonLinear(latticePointsList, name=deformerName+"_Squash", type="squash") #[Deformer, Handle]
            cmds.setAttr(squashDefList[0]+".highBound", 0.5*bBoxSize)
            cmds.setAttr(squashDefList[0]+".startSmoothness", 1)
            cmds.setAttr(squashDefList[1]+".ty", bBoxMidY)
            
            # side bend deformer
            sideBendDefList = cmds.nonLinear(latticePointsList, name=deformerName+"_Side_Bend", type="bend") #[Deformer, Handle]
            cmds.setAttr(sideBendDefList[0]+".lowBound", 0)
            cmds.setAttr(sideBendDefList[0]+".highBound", bBoxSize)
            cmds.setAttr(sideBendDefList[1]+".ty", bBoxMinY)
            
            # front bend deformer
            frontBendDefList = cmds.nonLinear(latticePointsList, name=deformerName+"_Front_Bend", type="bend") #[Deformer, Handle]
            cmds.setAttr(frontBendDefList[0]+".lowBound", 0)
            cmds.setAttr(frontBendDefList[0]+".highBound", bBoxSize)
            cmds.setAttr(frontBendDefList[1]+".ry", -90)
            cmds.setAttr(frontBendDefList[1]+".ty", bBoxMinY)
            
            # fix deform transforms scale to 1
            defHandleList = [twistDefList[1], squashDefList[1], sideBendDefList[1], frontBendDefList[1]]
            for defHandle in defHandleList:
                for axis in axisList:
                    cmds.setAttr(defHandle+".scale"+axis, 1)
            
            # arrow control curve
            arrowCtrl = self.ctrls.cvControl("id_053_HeadDeformer", deformerName+"_Ctrl", 0.25*bBoxSize, d=0)

            # main control curve and shape
            mainCtrl = self.ctrls.cvControl("id_097_HeadDeformerMain", mainCtrlName+"_Ctrl", 0.57*bBoxSize, d=0)
            mainCtrlShape = cmds.listRelatives(mainCtrl, shapes=True)[0]
            
            # add control intensity and calibrate attributes
            for axis in axisList:
                cmds.addAttr(arrowCtrl, longName=intensityName+axis, attributeType='float', defaultValue=1)
                cmds.setAttr(arrowCtrl+"."+intensityName+axis, edit=True, keyable=False, channelBox=True)
            cmds.addAttr(arrowCtrl, longName=expandName, attributeType='float', min=0, defaultValue=1, max=10, keyable=True)
            cmds.addAttr(arrowCtrl, longName=calibrateName+"X", attributeType='float', defaultValue=100/(3*bBoxSize), keyable=False)
            cmds.addAttr(arrowCtrl, longName=calibrateName+"Y", attributeType='float', defaultValue=300/bBoxSize, keyable=False)
            cmds.addAttr(arrowCtrl, longName=calibrateName+"Z", attributeType='float', defaultValue=100/(3*bBoxSize), keyable=False)
            cmds.addAttr(arrowCtrl, longName=calibrateName+"Reduce", attributeType='float', defaultValue=100, keyable=False)
            cmds.addAttr(arrowCtrl, longName=self.dpUIinst.lang["c021_showControls"], attributeType='long', min=0, max=1, defaultValue=0)
            cmds.setAttr(arrowCtrl+"."+self.dpUIinst.lang["c021_showControls"], edit=True, keyable=False, channelBox=True)
            
            # multiply divide in order to intensify influences
            calibrateMD = cmds.createNode("multiplyDivide", name=deformerName+"_Calibrate_MD")
            calibrateReduceMD = cmds.createNode("multiplyDivide", name=deformerName+"_CalibrateReduce_MD")
            intensityMD = cmds.createNode("multiplyDivide", name=deformerName+"_"+intensityName.capitalize()+"_MD")
            twistMD = cmds.createNode("multiplyDivide", name=deformerName+"_Twist_MD")
            cmds.setAttr(twistMD+".input2Y", -1)
            cmds.setAttr(calibrateReduceMD+".operation", 2)

            # create a remapValue node instead of a setDrivenKey
            remapV = cmds.createNode("remapValue", name=deformerName+"_Squash_RmV")
            cmds.setAttr(remapV+".inputMin", -0.25*bBoxSize)
            cmds.setAttr(remapV+".inputMax", 0.5*bBoxSize)
            cmds.setAttr(remapV+".outputMin", -1*bBoxSize)
            cmds.setAttr(remapV+".outputMax", -0.25*bBoxSize)            
            cmds.setAttr(remapV+".value[2].value_Position", 0.149408)
            cmds.setAttr(remapV+".value[2].value_FloatValue", 0.128889)
            cmds.setAttr(remapV+".value[3].value_Position", 0.397929)
            cmds.setAttr(remapV+".value[3].value_FloatValue", 0.742222)
            cmds.setAttr(remapV+".value[4].value_Position", 0.60355)
            cmds.setAttr(remapV+".value[4].value_FloatValue", 0.951111)
            for v in range(0, 5):
                cmds.setAttr(remapV+".value["+str(v)+"].value_Interp", 3) #spline
            
            # connections
            for axis in axisList:
                cmds.connectAttr(arrowCtrl+"."+intensityName+axis, calibrateMD+".input1"+axis, force=True)
                cmds.connectAttr(arrowCtrl+"."+calibrateName+axis, calibrateReduceMD+".input1"+axis, force=True)
                cmds.connectAttr(arrowCtrl+"."+calibrateName+"Reduce", calibrateReduceMD+".input2"+axis, force=True)
                cmds.connectAttr(calibrateReduceMD+".output"+axis, calibrateMD+".input2"+axis, force=True)
                cmds.connectAttr(arrowCtrl+".translate"+axis, intensityMD+".input1"+axis, force=True)
                cmds.connectAttr(calibrateMD+".output"+axis, intensityMD+".input2"+axis, force=True)
            cmds.connectAttr(intensityMD+".outputX", sideBendDefList[1]+".curvature", force=True)
            cmds.connectAttr(intensityMD+".outputY", squashDefList[1]+".factor", force=True)
            cmds.connectAttr(intensityMD+".outputZ", frontBendDefList[1]+".curvature", force=True)
            cmds.connectAttr(arrowCtrl+".ry", twistMD+".input1Y", force=True)
            cmds.connectAttr(twistMD+".outputY", twistDefList[1]+".endAngle", force=True)
            # change squash to be more cartoon
            cmds.connectAttr(intensityMD+".outputY", remapV+".inputValue", force=True)
            cmds.connectAttr(remapV+".outValue", squashDefList[0]+".lowBound", force=True)
            cmds.connectAttr(arrowCtrl+"."+expandName, squashDefList[0]+".expand", force=True)
            # fix side values
            for axis in axisList:
                unitConvNode = cmds.listConnections(intensityMD+".output"+axis, destination=True)[0]
                if unitConvNode:
                    if cmds.objectType(unitConvNode) == "unitConversion":
                        cmds.setAttr(unitConvNode+".conversionFactor", 1)
            cmds.connectAttr(arrowCtrl+"."+self.dpUIinst.lang["c021_showControls"], mainCtrlShape+".visibility")
            self.ctrls.setLockHide([arrowCtrl], ['rx', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
            
            # create symmetry setup
            centerClusterList = cmds.cluster(latticeDefList[1]+".pt[0:5][2:3][0:5]", relative=True, name=centerSymmetryName+"_Cls") #[Cluster, Handle]
            topClusterList = cmds.cluster(latticeDefList[1]+".pt[0:5][2:5][0:5]", relative=True, name=topSymmetryName+"_Cls")
            clustersZeroList = self.utils.zeroOut([centerClusterList[1], topClusterList[1]])
            cmds.matchTransform(clustersZeroList[1], centerClusterList[1])
            clusterGrp = cmds.group(clustersZeroList, name=deformerName+"_Cluster_Grp")
            # arrange lattice deform points percent
            cmds.percent(topClusterList[0], [latticeDefList[1]+".pt[0:5][2][0]", latticeDefList[1]+".pt[0:5][2][1]", latticeDefList[1]+".pt[0:5][2][2]", latticeDefList[1]+".pt[0:5][2][3]", latticeDefList[1]+".pt[0:5][2][4]", latticeDefList[1]+".pt[0:5][2][5]"], value=0.5)
            # symmetry controls
            centerSymmetryCtrl = self.ctrls.cvControl("id_068_Symmetry", centerSymmetryName+"_Ctrl", bBoxSize, d=0, rot=(-90, 0, 90))
            topSymmetryCtrl = self.ctrls.cvControl("id_068_Symmetry", topSymmetryName+"_Ctrl", bBoxSize, d=0, rot=(0, 90, 0))
            symmetryCtrlZeroList = self.utils.zeroOut([centerSymmetryCtrl, topSymmetryCtrl])
            for axis in axisList:
                cmds.connectAttr(centerSymmetryCtrl+".translate"+axis, centerClusterList[1]+".translate"+axis, force=True)
                cmds.connectAttr(centerSymmetryCtrl+".rotate"+axis, centerClusterList[1]+".rotate"+axis, force=True)
                cmds.connectAttr(centerSymmetryCtrl+".scale"+axis, centerClusterList[1]+".scale"+axis, force=True)
                cmds.connectAttr(topSymmetryCtrl+".translate"+axis, topClusterList[1]+".translate"+axis, force=True)
                cmds.connectAttr(topSymmetryCtrl+".rotate"+axis, topClusterList[1]+".rotate"+axis, force=True)
                cmds.connectAttr(topSymmetryCtrl+".scale"+axis, topClusterList[1]+".scale"+axis, force=True)

            # create subControls setup
            subCtrlList = []
            subCtrlGrpList = []
            for pos, latticeSubPoints in zip(posList, latticeSubPointsList):
                # create and connect cluster
                namePos = bottomCtrlName.replace(self.dpUIinst.lang["c100_bottom"], pos)
                subClusterList = cmds.cluster(latticeSubPoints, relative=True, name=namePos+"_Cls")
                cmds.parent(self.utils.zeroOut([subClusterList[1]])[0], clusterGrp)
                # create control and match zeroOutGrp
                subCtrl = self.ctrls.cvControl("id_098_HeadDeformerSub", namePos+"_Ctrl", 0.55*bBoxSize, d=0, rot=(90, 0, 0))
                subCtrlList.append(subCtrl)
                ctrlSubZeroList = self.utils.zeroOut([subCtrl])[0]
                subCtrlGrpList.append(ctrlSubZeroList)
                cmds.matchTransform(ctrlSubZeroList, subClusterList[1], pos=True)
                # connect atributes
                cmds.connectAttr(arrowCtrl+"."+self.dpUIinst.lang["c021_showControls"], ctrlSubZeroList+".visibility")
                for axis in axisList:
                    cmds.connectAttr(subCtrl+".translate"+axis, subClusterList[1]+".translate"+axis, force=True)
                    cmds.connectAttr(subCtrl+".rotate"+axis, subClusterList[1]+".rotate"+axis, force=True)
                    cmds.connectAttr(subCtrl+".scale"+axis, subClusterList[1]+".scale"+axis, force=True)

            # create groups
            arrowCtrlGrp = cmds.group(arrowCtrl, name=arrowCtrl+"_Grp")
            self.utils.zeroOut([arrowCtrl])
            offsetGrp = cmds.group(name=deformerName+"_Offset_Grp", empty=True)
            dataGrp = cmds.group(name=deformerName+"_Data_Grp", empty=True)
            cmds.matchTransform(arrowCtrlGrp, latticeDefList[2], position=True, rotation=True)
            arrowCtrlHeight = bBoxMaxY + (bBoxSize*0.5)
            cmds.setAttr(arrowCtrlGrp+".ty", arrowCtrlHeight)
            cmds.matchTransform(offsetGrp, latticeDefList[2], position=True, rotation=True)
            cmds.matchTransform(symmetryCtrlZeroList[0], latticeDefList[2], position=True, rotation=True)
            cmds.matchTransform(symmetryCtrlZeroList[1], latticeDefList[2], position=True, rotation=True)
            topSymmetryHeight = cmds.getAttr(symmetryCtrlZeroList[1]+".ty") - (bBoxSize*0.3)
            cmds.setAttr(symmetryCtrlZeroList[1]+".ty", topSymmetryHeight)
            cmds.parent(symmetryCtrlZeroList, arrowCtrlGrp)
            latticeGrp = cmds.group(name=latticeDefList[1]+"_Grp", empty=True)
            cmds.parent(latticeDefList[1], latticeDefList[2], latticeGrp)
            mainCtrlGrp = cmds.group(mainCtrl, name=mainCtrl+"_Grp")
            cmds.matchTransform(mainCtrlGrp, mainCtrl, pivots=True)
            cmds.matchTransform(mainCtrlGrp, latticeDefList[1], position=True, rotation=True)
            cmds.parent(arrowCtrlGrp, mainCtrl)
            cmds.parentConstraint(mainCtrl, dataGrp, maintainOffset=True, name=dataGrp+"_PaC")
            cmds.scaleConstraint(mainCtrl, dataGrp, maintainOffset=True, name=dataGrp+"_ScC")
            cmds.parent(subCtrlGrpList, arrowCtrlGrp)
            # fix topSymmetryCluster pivot
            topSymmetryCtrlPos = cmds.xform(symmetryCtrlZeroList[1], query=True, rotatePivot=True, worldSpace=True)
            cmds.xform(topClusterList[1], rotatePivot=(topSymmetryCtrlPos[0], topSymmetryCtrlPos[1], topSymmetryCtrlPos[2]), worldSpace=True)

            # workaround to add the deformer attribute on the remaining maincontrols from head and jaw control         
            childrenControlsList = []
            headSubCtrl = self.ctrls.getControlNodeById("id_093_HeadSub")
            jawCtrl = self.ctrls.getControlNodeById("id_024_HeadJaw")
            jawConditionList = [self.dpUIinst.lang["m075_upperTeeth"], self.dpUIinst.lang["m076_lowerTeeth"], self.dpUIinst.lang["m077_tongue"], self.dpUIinst.lang["c039_lip"]+"_"+self.dpUIinst.lang["c058_main"]]
            ctrlIDNotIncludeList = ["id_029_SingleIndSkin", "id_052_FacialFace", "id_068_Symmetry", "id_053_HeadDeformer", "id_098_HeadDeformerSub", "id_097_HeadDeformerMain"]
            if headSubCtrl:
                headSubCtrlChildrenList = cmds.listRelatives(headSubCtrl, allDescendents=True)
                childrenControlsList.append(headSubCtrlChildrenList)
            if jawCtrl:
                jawCtrlChildrenList = cmds.listRelatives(jawCtrl, allDescendents=True)                    
                childrenControlsList.append(jawCtrlChildrenList)
            if childrenControlsList:
                childrenControlsList = childrenControlsList[0]+childrenControlsList[1]
                for item in childrenControlsList:
                    if cmds.objExists(item+".controlID"):
                        if not cmds.objExists(item+"."+DPHEADDEFINFLUENCE):
                            if cmds.getAttr(item+".controlID") not in ctrlIDNotIncludeList:
                                self.ctrls.addDefInfluenceAttrs(item, defInfluenceType=1)
                                if not cmds.objExists(item+"."+DPJAWDEFINFLUENCE):
                                    for condition in jawConditionList:
                                        if condition in item:
                                            self.ctrls.addDefInfluenceAttrs(item, defInfluenceType=2)

            # apply influence deformer only in shape controls which have the attribute
            allTransformList = cmds.ls(selection=False, type="transform")
            if allTransformList:
                for item in allTransformList:
                    if cmds.objExists(item+".controlID"):
                        if not self.dpUIinst.lang["c025_jaw"] in arrowCtrl:
                            if cmds.objExists(item+"."+DPHEADDEFINFLUENCE) and cmds.getAttr(item+"."+DPHEADDEFINFLUENCE):
                                shape = cmds.listRelatives(item, shapes=True)
                                if shape:
                                    cmds.deformer(deformerName+"_FFD", edit=True, geometry=shape)
                        else:
                            if cmds.objExists(item+"."+DPJAWDEFINFLUENCE) and cmds.getAttr(item+"."+DPJAWDEFINFLUENCE):
                                shape = cmds.listRelatives(item, shapes=True)
                                if shape:
                                    cmds.deformer(deformerName+"_FFD", edit=True, geometry=shape)
                                
            # try to integrate to Head_Head_Ctrl
            if headSubCtrl:
                if len(headSubCtrl) > 1:
                    mel.eval("warning" + "\"" + self.dpUIinst.lang["i075_moreOne"] + " Head control.\"" + ";")
                else:
                    self.headCtrl = headSubCtrl[0]
            if self.headCtrl:
                # correcting topSymetry pivot to match headCtrl pivot
                cmds.matchTransform(topSymmetryCtrl, topClusterList[1], self.headCtrl, pivots=True)
                # setup hierarchy
                headCtrlPosList = cmds.xform(self.headCtrl, query=True, rotatePivot=True, worldSpace=True)
                cmds.xform(dataGrp, translation=(headCtrlPosList[0], headCtrlPosList[1], headCtrlPosList[2]), worldSpace=True)
                cmds.parent(mainCtrlGrp, self.headCtrl)

            else:
                mel.eval("warning" + "\"" + self.dpUIinst.lang["e020_notFoundHeadCtrl"] + "\"" + ";")
                self.wellDone = False
            
            cmds.parent(squashDefList[1], sideBendDefList[1], frontBendDefList[1], twistDefList[1], offsetGrp)
            cmds.parent(offsetGrp, clusterGrp, latticeGrp, dataGrp)
            
            # try to integrate to Scalable_Grp
            for item in allTransformList:
                if cmds.objExists(item+".masterGrp") and cmds.getAttr(item+".masterGrp") == 1:
                    scalableGrp = cmds.listConnections(item+".scalableGrp")[0]
                    cmds.parent(dataGrp, scalableGrp)
                    break
            
            # try to change deformers to get better result
            cmds.scale(1.25, 1.25, 1.25, offsetGrp)
            
            # colorize
            self.ctrls.colorShape([arrowCtrl, mainCtrl, centerSymmetryCtrl, topSymmetryCtrl, subCtrlList[0], subCtrlList[1], subCtrlList[2]], "cyan")

            # if there's Jaw in the deformerName it will configure rotate and delete symetries and subControls setup
            if self.dpUIinst.lang["c025_jaw"] in mainCtrl:
                cmds.setAttr(mainCtrlGrp+".rotateX", 145)
                cmds.delete(clusterGrp, subCtrlGrpList, symmetryCtrlZeroList)
            
            # calibration attributes:
            hdCalibrationList = [
                                    calibrateName+"X",
                                    calibrateName+"Y",
                                    calibrateName+"Z",
                                    calibrateName+"Reduce"
                                ]
            self.ctrls.setStringAttrFromList(arrowCtrl, hdCalibrationList)
            
            self.utils.addCustomAttr([latticeDefList[1], latticeDefList[2], offsetGrp, mainCtrlGrp, arrowCtrlGrp], self.utils.ignoreTransformIOAttr)

            # finish selection the arrow control
            cmds.select(arrowCtrl)
            if self.wellDone:
                print(self.dpUIinst.lang["i179_addedHeadDef"])
        
        else:
            mel.eval("warning" + "\"" + self.dpUIinst.lang["i034_notSelHeadDef"] + "\"" + ";")
