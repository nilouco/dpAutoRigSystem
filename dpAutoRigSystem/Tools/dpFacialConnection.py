# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
import os
import json

# global variables to this module:
CLASS_NAME = "FacialConnection"
TITLE = "m085_facialConnection"
DESCRIPTION = "m086_facialConnectionDesc"
ICON = "/Icons/dp_facialConnection.png"

MIDDLE = "Middle"
SIDED = "Sided"
PRESETS = "Presets"
FACIALPRESET = "FacialJoints"

DP_FACIALCONNECTION_VERSION = 1.2


class FacialConnection(object):
    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        # defining variables:
        self.dpUIinst = dpUIinst
        self.utils = dpUIinst.utils
        self.ctrls = dpUIinst.ctrls
        self.ui = ui
        self.headFacialCtrlsGrp = self.dpUIinst.lang["c024_head"]+"_"+self.dpUIinst.lang["c059_facial"]+"_Ctrls_Grp"
        self.jntTargetList = []
        self.RmVNumber = 0
        self.bsReceptSuffix = "Recept_BS"
        self.bsSuffix = "BS"
        self.defaultTargetList = ["Base", "Recept", "Tweaks",]
        self.facialTargetList = ["L_BrowUp", "L_BrowDown", "L_BrowSad", "L_BrowFrown", "L_EyelidsClose",  "L_EyelidsOpen",
                            "L_LipsSide", "L_MouthSmile", "L_MouthSad", "L_MouthWide", "L_MouthNarrow", "L_Sneer", "L_Grimace", "L_Puff",
                            "Pucker", "LipsUp", "LipsDown", "LipsFront", "LipsBack", "UpperLipFront", "UpperLipBack", "LowerLipFront", "LowerLipBack", "SoftSmile", "BigSmile", "AAA", "OOO", "UUU", "FFF", "MMM"]
        self.combinationTargetList = ["L_MouthComb_SmileWide", "L_MouthComb_SmileNarrow", "L_MouthComb_SadWide", "L_MouthComb_SadNarrow", "L_BrowComb_UpSad", "L_BrowComb_UpFrown", "L_BrowComb_DownSad", "L_BrowComb_DownFrown"]
        self.mouthTgts = ["MouthSmile", "MouthSad", "MouthWide", "MouthNarrow"]
        self.browTgts = ["BrowUp", "BrowDown", "BrowSad", "BrowFrown"]
        self.combinationPossibleList = [('Smile', 'Wide'), ('Smile', 'Narrow'), ('Sad', 'Wide'), ('Sad', 'Narrow'), ('Up', 'Sad'), ('Up', 'Frown'), ('Down', 'Sad'), ('Down', 'Frown')]
        # call main function:
        if self.ui:
            self.dpFacialConnectionUI(self)
    

    def dpInitTweaksVariables(self, *args):
        # part names:
        mainName = self.dpUIinst.lang['c058_main']
        tweaksName = self.dpUIinst.lang['m081_tweaks']
        middleName = self.dpUIinst.lang['c029_middle']
        eyebrowName = self.dpUIinst.lang['c041_eyebrow']
        cornerName = self.dpUIinst.lang['c043_corner']
        upperName = self.dpUIinst.lang['c044_upper']
        lowerName = self.dpUIinst.lang['c045_lower']
        lipName = self.dpUIinst.lang['c039_lip']
        squintName = self.dpUIinst.lang['c054_squint']
        cheekName = self.dpUIinst.lang['c055_cheek']
        self.calibrateName = self.dpUIinst.lang["c111_calibrate"].lower()
        # eyebrows names:
        self.eyebrowMiddleName = tweaksName+"_"+middleName+"_"+eyebrowName
        self.eyebrowName1 = tweaksName+"_"+eyebrowName+"_01"
        self.eyebrowName2 = tweaksName+"_"+eyebrowName+"_02"
        self.eyebrowName3 = tweaksName+"_"+eyebrowName+"_03"
        self.eyebrowName4 = tweaksName+"_"+eyebrowName+"_04"
        # squints names:
        self.squintName1 = tweaksName+"_"+squintName+"_01"
        self.squintName2 = tweaksName+"_"+squintName+"_02"
        self.squintName3 = tweaksName+"_"+squintName+"_03"
        self.squintName4 = tweaksName+"_"+squintName+"_04"
        # cheeks names:
        self.cheekName1 = tweaksName+"_"+cheekName+"_01"
        self.cheekName2 = tweaksName+"_"+cheekName+"_02"
        # lip names:
        self.upperLipMiddleName = tweaksName+"_"+upperName+"_"+lipName+"_00"
        self.upperLipName1 = tweaksName+"_"+upperName+"_"+lipName+"_01"
        self.upperLipName2 = tweaksName+"_"+upperName+"_"+lipName+"_02"
        self.lowerLipMiddleName = tweaksName+"_"+lowerName+"_"+lipName+"_00"
        self.lowerLipName1 = tweaksName+"_"+lowerName+"_"+lipName+"_01"
        self.lowerLipName2 = tweaksName+"_"+lowerName+"_"+lipName+"_02"
        self.lipCornerName = tweaksName+"_"+cornerName+"_"+lipName
        # list:
        self.tweaksNameList = [self.eyebrowMiddleName, self.eyebrowName1, self.eyebrowName2, self.eyebrowName3, self.eyebrowName4, \
                                self.squintName1, self.squintName2, self.squintName3,\
                                self.cheekName1, self.cheekName2, \
                                self.upperLipMiddleName, self.upperLipName1, self.upperLipName2, self.lowerLipMiddleName, self.lowerLipName1, self.lowerLipName2, self.lipCornerName]
        self.tweaksNameStrList = ["eyebrowMiddleName", "eyebrowName1", "eyebrowName2", "eyebrowName3", "eyebrowName4", \
                                "squintName1", "squintName2", "squintName3", \
                                "cheekName1", "cheekName2", \
                                "upperLipMiddleName", "upperLipName1", "upperLipName2", "lowerLipMiddleName", "lowerLipName1", "lowerLipName2", "lipCornerName"]
    
    
    def dpInitTweaksDic(self, *args):
        """ Load FacialJoints json file.
            Read its content.
            Rebuild a dictionary changing string variables to current mounted language names.
            Return the presetContent
        """
        # load json file:
        path = os.path.dirname(__file__)
        jsonPath = os.path.join(path, PRESETS, "").replace("\\", "/")
        presetContent = self.dpUIinst.pipeliner.getJsonContent(jsonPath+FACIALPRESET+".json")
        if presetContent:
            # rebuild dictionary using object variables:
            for storedAttr in list(presetContent):
                for sideName in list(presetContent[storedAttr]):
                    for toNodeName in list(presetContent[storedAttr][sideName]):
                        for i, item in enumerate(self.tweaksNameStrList):
                            if toNodeName == item:
                                presetContent[storedAttr][sideName][self.tweaksNameList[i]] = presetContent[storedAttr][sideName].pop(toNodeName)
                    if sideName == "MIDDLE":
                        presetContent[storedAttr][MIDDLE] = presetContent[storedAttr].pop(sideName)
                    elif sideName == "SIDED":
                        presetContent[storedAttr][SIDED] = presetContent[storedAttr].pop(sideName)
        return presetContent
    
    
    def dpFacialConnectionUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # creating targetMirrorUI Window:
        self.utils.closeUI('dpFacialConnectionWindow')
        facialCtrl_winWidth  = 220
        facialCtrl_winHeight = 250
        dpFacialControlWin = cmds.window('dpFacialConnectionWindow', title=self.dpUIinst.lang["m085_facialConnection"]+" "+str(DP_FACIALCONNECTION_VERSION), widthHeight=(facialCtrl_winWidth, facialCtrl_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        facialCtrlLayout = cmds.columnLayout('facialCtrlLayout', columnOffset=("both", 10), rowSpacing=10)
        cmds.separator(height=5, style="in", horizontal=True, parent=facialCtrlLayout)
        cmds.button(label=self.dpUIinst.lang["m140_createTargets"], annotation=self.dpUIinst.lang['m141_createTargetsDesc'], width=220, command=self.dpCreateTargetsFromUI, align="center", parent=facialCtrlLayout)
        self.createBsNodeCB = cmds.checkBox(label="Create BlendShape node", annotation=self.dpUIinst.lang['m141_createTargetsDesc'], value=1, parent=facialCtrlLayout)
        self.combinationTgtCB = cmds.checkBox(label="Combination targets", annotation=self.dpUIinst.lang['m141_createTargetsDesc'], value=1, parent=facialCtrlLayout)
        self.tweakTgtOnlyCB = cmds.checkBox(label="Tweak target only", annotation=self.dpUIinst.lang['m141_createTargetsDesc'], value=0, changeCommand=self.dpDisableCombination, parent=facialCtrlLayout)
        cmds.separator(height=5, style="single", horizontal=True, parent=facialCtrlLayout)
        cmds.text(label=self.dpUIinst.lang['m142_connectFacialAttr'], parent=facialCtrlLayout)
        cmds.button(label=self.dpUIinst.lang['m170_blendShapes']+" - "+self.dpUIinst.lang['i185_animation'], annotation="Create selected facial controls.", width=220, command=self.dpConnectToBlendShape, parent=facialCtrlLayout)
        cmds.button(label=self.dpUIinst.lang['i181_facialJoint']+" - "+self.dpUIinst.lang['i186_gaming'], annotation="Create default facial controls package.", width=220, command=self.dpConnectToJoints, parent=facialCtrlLayout)
        # call facialControlUI Window:
        cmds.showWindow(dpFacialControlWin)
    

    def dpCreateTargetsFromUI(self, *args):
        createBsNode = cmds.checkBox(self.createBsNodeCB, query=True, value=True)
        combinationTgt = cmds.checkBox(self.combinationTgtCB, query=True, value=True)
        tweakTgtOnly = cmds.checkBox(self.tweakTgtOnlyCB, query=True, value=True)
        # call run function
        self.dpCreateTargets(fromMesh=None, baseName="Head", createBsNode=createBsNode, combinationTargets=combinationTgt,  tweakTgtOnly=tweakTgtOnly)
    
    def dpDisableCombination(self, value, *args):
        """ If the tweakTgtOnlyCB is checked, disable the combinationTgtCB.
        """
        value = cmds.checkBox(self.tweakTgtOnlyCB, query=True, value=True)
        if value:
            cmds.checkBox(self.combinationTgtCB, edit=True, enable=False)
            cmds.checkBox(self.combinationTgtCB, edit=True, value=False)
        else:
            cmds.checkBox(self.combinationTgtCB, edit=True, enable=True)
        

    def dpCreateTargets(self, fromMesh=None, baseName="Head", createBsNode=None, combinationTargets=None, tweakTgtOnly=None, *args):
        """ Creates the default blendShape targets used in the system by default.
        """
        if not fromMesh:
            fromMeshList = cmds.ls(selection=True, type="transform")
            if fromMeshList:
                for n, node in enumerate(fromMeshList):
                    fromMeshChildrenList = cmds.listRelatives(fromMeshList[n], children=True, type="mesh")
                    if fromMeshChildrenList:
                        fromMesh = fromMeshList[n]
                        break
        if fromMesh:
            geoList, resultList = [], []
            for geoBase in fromMeshList:
                print("Creating targets for:", geoBase)
                prefix = baseName
                if self.ui:
                    btContinue = self.dpUIinst.lang['i174_continue']
                    btCancel = self.dpUIinst.lang['i132_cancel']
                    result = cmds.promptDialog(
                            title=self.dpUIinst.lang['m006_name'],
                            message=self.dpUIinst.lang['i144_prefix']+":",
                            button=[btContinue, btCancel],
                            defaultButton=btContinue,
                            cancelButton=btCancel,
                            dismissString=btCancel)
                    if result == btContinue:
                        prefix = cmds.promptDialog(query=True, text=True)
                if prefix == "":
                    prefix = geoBase
                if not prefix.endswith("_"):
                    prefix = prefix+"_"
                prefix = prefix.capitalize()
                suffix = "_Tgt"
                # create target meshes
                tgtList = list(self.defaultTargetList)
                if not tweakTgtOnly:
                    tgtList.extend(self.facialTargetList)
                    if combinationTargets:
                        tgtList.extend(self.combinationTargetList)
                if len(tgtList)>3:
                    facialTgtGrp = cmds.group(empty=True, name=prefix+"Facial_Tgt_Grp")
                tgtGrp = cmds.group(empty=True, name=prefix+"Tgt_Grp")
                self.turnDeformersEnvelope(turnOn=False)
                facialTgtList = []
                createdTgts = []
                for t, tgt in enumerate(tgtList):
                    newGeo = self.dpDuplicateRenameAndInitShaderTgt(geoBase, prefix, tgt, suffix)
                    createdTgts.append(newGeo)
                    if t == 0:
                        cmds.setAttr(newGeo+".visibility", 0)
                        geoList.append(newGeo)
                        cmds.parent(newGeo, tgtGrp)
                    elif t == 1:
                        geoList.append(newGeo)
                        cmds.parent(newGeo, tgtGrp)
                    elif t == 2:
                        geoList.append(newGeo)
                        cmds.parent(newGeo, tgtGrp)
                    else:
                        cmds.parent(newGeo, facialTgtGrp)
                        facialTgtList.append(newGeo)
                if facialTgtList:
                    cmds.parent(facialTgtGrp, tgtGrp)

                self.turnDeformersEnvelope(turnOn=True)
                if createBsNode:
                    if combinationTargets:
                        self.createBlendShapeNode(geoBase, prefix, createdTgts, combTgt=True)
                    else:
                        self.createBlendShapeNode(geoBase, prefix, createdTgts, combTgt=False)
            if self.ui and resultList:
                self.dpUIinst.logger.infoWin('m085_facialConnection', 'm048_createdTgt', '\n'.join(resultList), 'center', 200, 350)
        else:
            mel.eval("warning \""+self.dpUIinst.lang["i042_notSelection"]+"\";")
        self.utils.closeUI('dpFacialConnectionWindow')
    

    def dpDuplicateRenameAndInitShaderTgt(self, fromMesh, prefix, tgt, suffix, *args):
        """ Duplicate the given mesh and rename it to the target name.
        """
        dup = cmds.duplicate(fromMesh)[0]
        newTgt = cmds.rename(dup, prefix+tgt+suffix)
        self.dpUIinst.customAttr.addAttr(0, [newTgt], descendents=True) #dpID
        cmds.addAttr(newTgt, longName="dpTarget", attributeType="bool", defaultValue=1, keyable=False)
        cmds.addAttr(newTgt, longName="targetName", dataType="string")
        cmds.setAttr(newTgt+".targetName", tgt, type="string")
        cmds.select(newTgt)
        cmds.hyperShade(newTgt, assign="initialShadingGroup")
        connectedPlug = cmds.listConnections(newTgt+".drawOverride", destination=False, source=True, plugs=True)
        if connectedPlug:
            cmds.disconnectAttr(connectedPlug[0], newTgt+".drawOverride")
        return newTgt


    def dpGetFacialCtrlDic(self, ctrlList, *args):
        """ Return the facial control dic with facialList attributes.
        """
        resultDic = {}
        if not ctrlList:
            ctrlList = self.ctrls.getControlList()
        if ctrlList:
            for ctrl in ctrlList:
                if cmds.objExists(ctrl+".facialList"):
                    resultDic[ctrl] = self.ctrls.getListFromStringAttr(ctrl, "facialList")
        return resultDic
    

    def dpGetBsNodeDic(self, bsList):
        bsDic = {}
        if bsList:
            for bsNode in bsList:
                targetList = cmds.listAttr(bsNode+".w", multi=True)
                if targetList:
                    bsDic[bsNode] = targetList
        return bsDic


    def dpConnectToBlendShape(self, ctrlList=None, bsList=None, *args):
        """ Find all dpControl and list their facial attributes to connect into existing alias in all blendShape nodes.
        """
        resultList = []
        # get facialList attr from found dpAR controls
        facialCtrlDic = self.dpGetFacialCtrlDic(ctrlList)
        # get target list from existing blendShape nodes
        if not bsList:
            bsList = cmds.ls(selection=False, type="blendShape")
        bsDic = self.dpGetBsNodeDic(bsList)
        # connect them
        if bsDic:
            if facialCtrlDic and bsDic:
                for facialCtrl in list(facialCtrlDic.keys()):
                    for bsNode in list(bsDic.keys()):
                        for facialAttr in facialCtrlDic[facialCtrl]:
                            for targetAttr in bsDic[bsNode]:
                                connectIt = False
                                if targetAttr.endswith(facialAttr+"_Tgt"):
                                    connectIt = True
                                elif targetAttr.endswith(facialAttr):
                                    connectIt = True
                                elif facialAttr == targetAttr:
                                    connectIt = True
                                # not including here the (facialAttr in targetAttr) statement to try avoid connect into combination alias
                                if connectIt:
                                    cmds.connectAttr(facialCtrl+"."+facialAttr, bsNode+"."+targetAttr, force=True)
                                    print(self.dpUIinst.lang['m143_connected'], facialCtrl+"."+facialAttr, "->", bsNode+"."+targetAttr)
                                    resultList.append(facialCtrl+"."+facialAttr+" -> "+bsNode+"."+targetAttr)
            for bsNode in list(bsDic.keys()):
                combinationsDic = self.dpFindCombinationTgtRelationship(bsNode)
                print("combinationsDic:", combinationsDic)
                self.connectCombinationTargets(bsNode, combinationsDic)
                               
                    
                            
        if self.ui and resultList:
            self.dpUIinst.logger.infoWin('m085_facialConnection', 'm143_connected', '\n'.join(resultList), 'center', 200, 350)
        self.utils.closeUI('dpFacialConnectionWindow')
    

    def dpConnectToJoints(self, ctrlList=None, *args):
        """ Connect the facial controllers attributes to the stored facial tweakers data.
        """
        self.toIDList, resultList = [], []
        # redefining Tweaks variables to get the tweaks name list
        self.dpInitTweaksVariables()
        # get joint target list
        self.jntTargetList = self.dpGetJointNodeList(self.tweaksNameList)
        if self.jntTargetList:
            facialCtrlDic = self.dpGetFacialCtrlDic(ctrlList)
            if facialCtrlDic:
                # declaring gaming dictionary:
                self.tweaksDic = self.dpInitTweaksDic()
                if self.tweaksDic:
                    for facialCtrl in list(facialCtrlDic.keys()):
                        for facialAttr in facialCtrlDic[facialCtrl]:
                            # check attribute prefix like "L_" or "R_"
                            sidePrefix = None
                            sidedAttr = facialAttr
                            if facialAttr[1] == "_":
                                sidePrefix = facialAttr[0]
                                sidedAttr = facialAttr[2:]
                            # work with Middle, L_Middle, R_Middle or Sided data
                            for middleOrSided in list(self.tweaksDic[sidedAttr].keys()):
                                nodeDataList = []
                                if middleOrSided == MIDDLE:
                                    nodeDataList.append(self.tweaksDic[sidedAttr][middleOrSided])
                                elif middleOrSided == SIDED:
                                    dic = {}
                                    for s in ["L", "R"]:
                                        if sidePrefix == None or sidePrefix == s:
                                            for n in list(self.tweaksDic[sidedAttr][middleOrSided].keys()):
                                                # add prefix to the destination joint target node
                                                dic[s+"_"+n] = self.tweaksDic[sidedAttr][middleOrSided][n]
                                    nodeDataList.append(dic)
                                else:
                                    for s in ["L", "R"]:
                                        if middleOrSided == s+"_"+MIDDLE:
                                            if sidePrefix == "L":
                                                # simple connection
                                                nodeDataList.append(self.tweaksDic[sidedAttr][middleOrSided])
                                if nodeDataList:
                                    for nodeDic in nodeDataList:
                                        for toNode in list(nodeDic.keys()):
                                            for jntTarget in self.jntTargetList:
                                                if cmds.objExists(jntTarget):
                                                    if jntTarget.startswith(toNode):
                                                        # caculate factor for scaled item:
                                                        sizeFactor = self.dpGetSizeFactor(jntTarget)
                                                        if not sizeFactor:
                                                            sizeFactor = 1
                                                        for toAttr in list(nodeDic[toNode].keys()):
                                                            # read stored values in order to call function to make the setup
                                                            oMin = nodeDic[toNode][toAttr][0]
                                                            oMax = nodeDic[toNode][toAttr][1]
                                                            self.dpCreateRemapNode(facialCtrl, facialAttr, jntTarget, toAttr, self.RmVNumber, sizeFactor, oMin, oMax)
                                                            self.RmVNumber = self.RmVNumber+1
                                                        print(self.dpUIinst.lang['m143_connected'], facialCtrl+"."+facialAttr, "->", jntTarget)
                                                        resultList.append(facialCtrl+"."+facialAttr+" -> "+jntTarget)
                    self.dpUIinst.customAttr.addAttr(0, self.toIDList) #dpID
                    if self.ui and resultList:
                        self.dpUIinst.logger.infoWin('m085_facialConnection', 'm143_connected', '\n'.join(resultList), 'center', 200, 350)
        self.utils.closeUI('dpFacialConnectionWindow')

    
    def dpGetJointNodeList(self, itemList, *args):
        """ Load the respective items to build the joint target list (offset group node) and returns it.
        """
        self.offsetSuffix = "_Ctrl_Offset_Grp"
        leftPrefix = self.dpUIinst.lang["p002_left"]+"_"
        rightPrefix = self.dpUIinst.lang["p003_right"]+"_"
        for item in itemList:
            centerName = item+self.offsetSuffix
            leftName   = leftPrefix+item+self.offsetSuffix
            rightName  = rightPrefix+item+self.offsetSuffix
            if cmds.objExists(centerName):
                self.jntTargetList.append(centerName)
            if cmds.objExists(leftName):
                self.jntTargetList.append(leftName)
            if cmds.objExists(rightName):
                self.jntTargetList.append(rightName)
        return self.jntTargetList
    
    
    def dpGetSizeFactor(self, toNode, *args):
        """ Get the child control size value and return it.
        """
        childrenList = cmds.listRelatives(toNode, children=True, type="transform")
        if childrenList:
            for child in childrenList:
                if cmds.objExists(child+".dpControl"):
                    if cmds.getAttr(child+".dpControl") == 1:
                        if cmds.objExists(child+".size"):
                            sizeValue = cmds.getAttr(child+".size")
                            return sizeValue
                        

    def dpCreateRemapNode(self, fromNode, fromAttr, jntTarget, toAttr, number, sizeFactor, oMin=0, oMax=1, iMin=0, iMax=1, *args):
        """ Creates the nodes to remap values and connect it to final output (jntTarget) item.
        """
        fromNodeName = self.utils.extractSuffix(fromNode)
        remap = cmds.createNode("remapValue", name=fromNodeName+"_"+fromAttr+"_"+str(number).zfill(2)+"_"+toAttr.upper()+"_RmV")
        self.toIDList.append(remap)
        outMaxAttr = jntTarget.split(self.offsetSuffix)[0]+"_"+str(number).zfill(2)+"_"+toAttr.upper()
        if not cmds.objExists(fromNode+"."+outMaxAttr):
            cmds.addAttr(fromNode, longName=outMaxAttr, attributeType="float", defaultValue=oMax, keyable=False)
        if "t" in toAttr:
            if not cmds.objExists(fromNode+".sizeFactor"):
                cmds.addAttr(fromNode, longName="sizeFactor", attributeType="float", defaultValue=sizeFactor, keyable=False)
            md = cmds.createNode("multiplyDivide", name=fromNodeName+"_"+fromAttr+"_"+str(number).zfill(2)+"_"+toAttr.upper()+"_SizeFactor_MD")
            self.toIDList.append(md)
            cmds.connectAttr(fromNode+"."+outMaxAttr, md+".input1X", force=True)
            cmds.connectAttr(fromNode+".sizeFactor", md+".input2X", force=True)
            cmds.connectAttr(md+".outputX", remap+".outputMax", force=True)
        else:
            cmds.connectAttr(fromNode+"."+outMaxAttr, remap+".outputMax", force=True)
        cmds.setAttr(remap+".inputMin", iMin)
        cmds.setAttr(remap+".inputMax", iMax)
        cmds.setAttr(remap+".outputMin", oMin)
        cmds.connectAttr(fromNode+"."+fromAttr, remap+".inputValue", force=True)
        # check if there's an input connection and create a plusMinusAverage if we don't have one to connect in:
        connectedList = cmds.listConnections(jntTarget+"."+toAttr, destination=False, source=True, plugs=False)
        if connectedList:
            if cmds.objectType(connectedList[0]) == "plusMinusAverage":
                inputList = cmds.listConnections(connectedList[0]+".input1D", destination=False, source=True, plugs=False)
                cmds.connectAttr(remap+".outValue", connectedList[0]+".input1D["+str(len(inputList))+"]", force=True)
            else:
                if cmds.objectType(connectedList[0]) == "unitConversion":
                    connectedAttr = cmds.listConnections(connectedList[0]+".input", destination=False, source=True, plugs=True)[0]
                else:
                    connectedAttr = cmds.listConnections(jntTarget+"."+toAttr, destination=False, source=True, plugs=True)[0]
                pma = cmds.createNode("plusMinusAverage", name=jntTarget+"_"+toAttr.upper()+"_PMA")
                self.toIDList.append(pma)
                cmds.connectAttr(connectedAttr, pma+".input1D[0]", force=True)
                cmds.connectAttr(remap+".outValue", pma+".input1D[1]", force=True)
                cmds.connectAttr(pma+".output1D", jntTarget+"."+toAttr, force=True)
                if cmds.objectType(connectedList[0]) == "unitConversion":
                    cmds.delete(connectedList[0])
        else:
            cmds.connectAttr(remap+".outValue", jntTarget+"."+toAttr, force=True)


    def nodeHasEnvelope(self, node,*args):
        if cmds.nodeType(node) != "tweak":
            return cmds.attributeQuery('envelope', node=node, exists=True)


    def envelopeIsValid(self, node, *args):
        notConnected =  not cmds.listConnections(node+".envelope", source=True, destination=False)
        nodeStateNormal = cmds.getAttr(node+".nodeState") == 0
        notUserDefined = not "envelope" in (cmds.listAttr(node, userDefined=True) or [])
        return notConnected and nodeStateNormal and notUserDefined


    def verifyEnvelope(node):
        envelopeValue = cmds.getAttr(f"{node}.envelope")
        return envelopeValue < 1


    def turnDeformersEnvelope(self, turnOn=False, *args):
        checkedObjList = []
        allNodesList = cmds.ls()
        allEnvelopedNodes = list(filter(self.nodeHasEnvelope, allNodesList))
        allValidEnvelopeNodes = list(filter(self.envelopeIsValid, allEnvelopedNodes))
        checkedObjList.extend(allValidEnvelopeNodes)
        if checkedObjList:
            if turnOn == True:
                for node in checkedObjList:
                    cmds.setAttr(f"{node}.envelope", 1)
            if turnOn == False:
                for node in checkedObjList:
                    cmds.setAttr(f"{node}.envelope", 0)
            

    def createBlendShapeNode(self, fromMesh, prefix, tgtList, combTgt=False, *args):
        """ Create a blendShape node connecting all created target meshes.
        """
        receptTgt = tgtList[1]
        tweakTarget = tgtList[2]
        tgtsForRecept = tgtList[2:]
        bsRecept = cmds.blendShape(tgtsForRecept, receptTgt, foc=True, name=prefix+self.bsReceptSuffix)[0]
        bsMain = cmds.blendShape(receptTgt, fromMesh, foc=True, name=prefix+self.bsSuffix)[0]
        cmds.setAttr(f"{bsMain}.{receptTgt}", 1)
        cmds.setAttr(f"{bsRecept}.{tweakTarget}", 1)
        if combTgt:
            combinationsDic = self.dpFindCombinationTgtRelationship(bsRecept)
            self.connectCombinationTargets(bsRecept, combinationsDic)


    def dpFindCombinationTgtRelationship(self, bsNode, *args):
        combinationTargetRelationship = {}
        if bsNode:
            targetList = cmds.listAttr(bsNode+".w", multi=True) or []
        baseTargets = []
        comboTargets = []
        for target in targetList:
            if cmds.attributeQuery("targetName", node=target, exists=True):
                name = cmds.getAttr(target+".targetName")
            nameLower = name.lower()
            if "comb" in nameLower:
                comboTargets.append(target)
            else:
                baseTargets.append(target)
        for combName in comboTargets:
            if cmds.attributeQuery("targetName", node=combName, exists=True):
                combNameAttr = cmds.getAttr(combName+".targetName")
            combLower = combNameAttr.lower()
            prefix, combPart = combLower.split("comb_")
            prefixParts = prefix.split("_", 1)
            side = prefixParts[0]
            region = prefixParts[1]
            drivers = []
            # TODO: indentify and create relation also with right side targets
            # Also consider to remove the addAttr with the targetName
            for baseName in baseTargets:
                if cmds.attributeQuery("targetName", node=baseName, exists=True):
                    baseNameAttr = cmds.getAttr(baseName+".targetName")
                baseLower = baseNameAttr.lower()
                baseSuffix = baseLower.replace(prefix, "")
                if baseSuffix and baseSuffix in combPart:
                    drivers.append(baseName)
                if len(drivers)>=2:
                    combinationTargetRelationship[combName] = drivers
        return combinationTargetRelationship
    

    def getBlendShapeTargetIndex(self, bsNode, targetName, *args):
        aliasList = cmds.aliasAttr(bsNode, q=True) or []
        for i in range(0, len(aliasList), 2):
            if aliasList[i] == targetName:
                return int(aliasList[i+1].split("[")[-1][:-1])
        return None
    

    def connectCombinationTargets(self, bsNode, combinationsDic, *args):
        for combTgt, drivers in combinationsDic.items():
            combIndex = self.getBlendShapeTargetIndex(bsNode, combTgt)
            driverIdxList = []
            for i, driverTgt in enumerate(drivers):
                driverIndex = self.getBlendShapeTargetIndex(bsNode, driverTgt)
                driverIdxList.append(driverIndex) 
            inputWeights = cmds.combinationShape(query=True, blendShape=bsNode, combinationTargetIndex=combIndex, exist=True)    
            if not inputWeights:
                cmds.combinationShape(blendShape=bsNode, combineMethod=0, combinationTargetIndex=combIndex, driverTargetIndex=driverIdxList)


    def decomposeTgtName(self, tgtName, *args):
        """ Decomposes a target name into its side and base name.
            e.g. L_MouthSmile -> L, MouthSmile
        """
        side = None
        baseName = tgtName
        if tgtName[1] == "_":
            side = tgtName[0]
            baseName = tgtName[2:]
        return side, baseName